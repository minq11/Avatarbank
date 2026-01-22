from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_user_by_email,
    verify_token,
)
from .config import settings
from .db import Base, engine, get_db
from .dependencies import get_current_user
from .models import Generation, GenerationStatus, Task, TaskStatus, Transaction, User
from .schemas import (
    GenerationCreateRequest,
    GenerationResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserBase,
)
from .tasks import run_generation_task

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:3000",  # 다른 개발 서버
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # 초기 단계에서는 자동으로 테이블을 생성하도록 두고,
    # 이후 Alembic 마이그레이션으로 전환한다.
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/auth/register", response_model=UserBase, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserBase:
    """회원가입"""
    # 이메일 중복 확인
    existing_user = get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 새 사용자 생성
    new_user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        locale=payload.locale,
        credit_balance=0,
        status="active",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserBase.model_validate(new_user)


@app.post("/auth/login", response_model=UserLoginResponse, tags=["auth"])
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> UserLoginResponse:
    """로그인"""
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # last_login_at 업데이트
    user.last_login_at = datetime.utcnow()
    db.commit()

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserBase.model_validate(user),
    )


@app.post("/auth/refresh", response_model=RefreshTokenResponse, tags=["auth"])
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> RefreshTokenResponse:
    """Refresh Token으로 새로운 Access Token 발급"""
    # Refresh Token 검증
    token_payload = verify_token(payload.refresh_token, token_type="refresh")
    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = token_payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # 새로운 Access Token 생성
    access_token = create_access_token(data={"sub": user.id})

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@app.get("/auth/me", response_model=UserBase, tags=["auth"])
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserBase:
    """현재 로그인한 사용자 정보 조회"""
    return UserBase.model_validate(current_user)


@app.post("/generations", response_model=GenerationResponse, tags=["generation"])
def create_generation(
    payload: GenerationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerationResponse:
    # TODO: 프롬프트 필터링, idempotency 체크 구현

    # 인증된 사용자를 buyer로 사용
    buyer = current_user

    total_credits = 1 + payload.option_credits
    if buyer.credit_balance < total_credits:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient credits.",
        )

    # 크레딧 선차감
    before = buyer.credit_balance
    buyer.credit_balance -= total_credits

    generation = Generation(
        avatar_id=payload.avatar_id,
        buyer_id=buyer.id,
        credits_used=total_credits,
        prompt=payload.prompt,
        status=GenerationStatus.PENDING.value,
    )
    db.add(generation)

    tx = Transaction(
        user_id=buyer.id,
        type="generation",
        amount=-total_credits,
        currency="CREDIT",
        credit_before=before,
        credit_after=buyer.credit_balance,
        reference_id=None,
    )
    db.add(tx)
    db.flush()

    # 태스크 기록
    task = Task(
        generation_id=generation.id,
        task_type="generation",
        status=TaskStatus.QUEUED.value,
    )
    db.add(task)
    db.commit()
    db.refresh(generation)

    # TODO: S3 Presigned URL 발급 후 Celery 태스크에 전달
    run_generation_task.delay(generation.id, presigned_url="")  # 스켈레톤

    return GenerationResponse.model_validate(generation)


@app.get("/generations/{generation_id}", response_model=GenerationResponse, tags=["generation"])
def get_generation(
    generation_id: int,
    db: Session = Depends(get_db),
) -> GenerationResponse:
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found.")
    return GenerationResponse.model_validate(generation)


