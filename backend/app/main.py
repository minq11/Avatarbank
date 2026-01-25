from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_user_by_email,
    get_user_by_nickname,
    verify_token,
)
from .config import settings
from .db import Base, engine, get_db
from .dependencies import get_current_user
from .models import Avatar, Generation, GenerationStatus, Transaction, TrainingRequest, User
from .fal_client import run_generation_sync
from .schemas import (
    AdminUpgradeRequest,
    AvatarResponse,
    AvatarUpdateRequest,
    GenerationCreateRequest,
    GenerationResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TrainingRequestResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserBase,
)

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
    existing_nickname = get_user_by_nickname(db, payload.nickname)
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nickname already in use",
        )

    # 새 사용자 생성
    new_user = User(
        email=payload.email,
        nickname=payload.nickname,
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

    user_id_raw = token_payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
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


@app.post("/auth/upgrade-to-seller", response_model=UserBase, tags=["auth"])
def upgrade_to_seller(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserBase:
    """Deprecated: user-initiated upgrade is not allowed."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only administrators can approve influencer upgrades.",
    )


def _is_admin_email(email: str) -> bool:
    whitelist = {
        value.strip().lower()
        for value in settings.ADMIN_EMAIL_WHITELIST.split(",")
        if value.strip()
    }
    return email.lower() in whitelist


@app.post("/admin/influencer-approve", response_model=UserBase, tags=["admin"])
def admin_approve_influencer(
    payload: AdminUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserBase:
    from .models import UserRole

    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    if payload.user_id is None and payload.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id or email is required.",
        )

    query = db.query(User)
    if payload.user_id is not None:
        target_user = query.filter(User.id == payload.user_id).first()
    else:
        target_user = query.filter(User.email == payload.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if target_user.role == UserRole.INFLUENCER.value:
        return UserBase.model_validate(target_user)

    target_user.role = UserRole.INFLUENCER.value
    db.commit()
    db.refresh(target_user)

    return UserBase.model_validate(target_user)


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

    if payload.avatar_id is not None:
        avatar = db.query(Avatar).filter(Avatar.id == payload.avatar_id).first()
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar not found. Please select an avatar first.",
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
    db.commit()
    db.refresh(generation)

    try:
        response_payload = run_generation_sync(payload.prompt)
        images = response_payload.get("images") or []
        if images:
            generation.image_url = images[0].get("url")
        generation.seed = (
            str(response_payload.get("seed"))
            if response_payload.get("seed") is not None
            else None
        )
        generation.nsfw_flag = any(
            response_payload.get("has_nsfw_concepts") or []
        )
        generation.status = GenerationStatus.SUCCESS.value
        db.commit()
        db.refresh(generation)
    except Exception as exc:
        generation.status = GenerationStatus.FAILED.value
        generation.fail_reason = str(exc)

        refund_before = buyer.credit_balance
        buyer.credit_balance += total_credits
        tx_refund = Transaction(
            user_id=buyer.id,
            type="refund",
            amount=total_credits,
            currency="CREDIT",
            credit_before=refund_before,
            credit_after=buyer.credit_balance,
            reference_id=str(generation.id),
        )
        db.add(tx_refund)
        db.commit()
        db.refresh(generation)

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


@app.get("/my/generations", response_model=list[GenerationResponse], tags=["generation"])
def list_my_generations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GenerationResponse]:
    """현재 로그인 사용자가 생성한 이미지 목록 (최신순)"""
    generations = (
        db.query(Generation)
        .filter(Generation.buyer_id == current_user.id)
        .order_by(Generation.created_at.desc())
        .all()
    )
    return [GenerationResponse.model_validate(g) for g in generations]


# Training Requests API
@app.get("/my/training-requests", response_model=list[TrainingRequestResponse], tags=["training"])
def list_my_training_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TrainingRequestResponse]:
    """내 학습 요청 목록 조회"""
    requests = (
        db.query(TrainingRequest)
        .filter(TrainingRequest.user_id == current_user.id)
        .order_by(TrainingRequest.created_at.desc())
        .all()
    )
    return [TrainingRequestResponse.model_validate(r) for r in requests]


@app.post(
    "/my/training-requests",
    response_model=TrainingRequestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["training"],
)
async def create_training_request(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    avatar_name: str = Form(...),
    negative_prompt: str = Form(...),
    credit_per_generation: int = Form(...),
    national: str = Form(...),
    gender: str = Form(...),
    description: str = Form(...),
    is_real_person: bool = Form(False),
    instagram_id: str = Form(None),
    preview_image: UploadFile = File(...),
    front_photos: List[UploadFile] = File(default=[]),
    side_photos: List[UploadFile] = File(default=[]),
    fullbody_photos: List[UploadFile] = File(default=[]),
    other_photos: List[UploadFile] = File(default=[]),
):
    """학습 요청 생성"""
    from fastapi import UploadFile, File, Form
    from io import BytesIO
    from .s3_utils import upload_file_to_s3, upload_multiple_files_to_s3
    from .models import TrainingRequestStatus

    # 실존인물인 경우 Instagram ID 필수
    if is_real_person is True and not instagram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instagram ID is required for real person avatars",
        )

    # 최소 사진 개수 검증
    if len(front_photos) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 4 front photos are required",
        )
    if len(side_photos) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 4 side photos are required",
        )
    if len(fullbody_photos) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 full body photo is required",
        )
    if len(other_photos) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 other photo is required",
        )

    # TrainingRequest를 먼저 생성하여 ID 획득
    training_request = TrainingRequest(
        user_id=current_user.id,
        avatar_name=avatar_name,
        negative_prompt=negative_prompt,
        credit_per_generation=credit_per_generation,
        national=national,
        gender=gender,
        description=description,
        is_real_person=is_real_person,
        instagram_id=instagram_id if is_real_person is True else None,
        status=TrainingRequestStatus.REQUESTED.value,
    )

    db.add(training_request)
    db.flush()  # ID를 얻기 위해 flush (아직 commit하지 않음)
    training_request_id = training_request.id

    # 이미지 업로드 (training_request_id 폴더에 저장)
    preview_image_url = None
    front_photos_urls = []
    side_photos_urls = []
    fullbody_photos_urls = []
    other_photos_urls = []

    try:
        # 폴더 경로: training-requests/{training_request_id}/
        folder_path = f"training-requests/{training_request_id}"

        # 대표 이미지 업로드
        preview_content = await preview_image.read()
        preview_image_url = upload_file_to_s3(
            BytesIO(preview_content),
            preview_image.filename or "preview.jpg",
            folder=folder_path,
            content_type=preview_image.content_type or "image/jpeg",
        )

        # 정면 사진들 업로드
        if front_photos:
            front_contents = [await photo.read() for photo in front_photos]
            front_filenames = [photo.filename or f"front_{i}.jpg" for i, photo in enumerate(front_photos)]
            front_photos_urls = upload_multiple_files_to_s3(
                [BytesIO(content) for content in front_contents],
                front_filenames,
                folder=folder_path,
            )

        # 측면 사진들 업로드
        if side_photos:
            side_contents = [await photo.read() for photo in side_photos]
            side_filenames = [photo.filename or f"side_{i}.jpg" for i, photo in enumerate(side_photos)]
            side_photos_urls = upload_multiple_files_to_s3(
                [BytesIO(content) for content in side_contents],
                side_filenames,
                folder=folder_path,
            )

        # 전신 사진들 업로드
        if fullbody_photos:
            fullbody_contents = [await photo.read() for photo in fullbody_photos]
            fullbody_filenames = [photo.filename or f"fullbody_{i}.jpg" for i, photo in enumerate(fullbody_photos)]
            fullbody_photos_urls = upload_multiple_files_to_s3(
                [BytesIO(content) for content in fullbody_contents],
                fullbody_filenames,
                folder=folder_path,
            )

        # 기타 사진들 업로드
        if other_photos:
            other_contents = [await photo.read() for photo in other_photos]
            other_filenames = [photo.filename or f"other_{i}.jpg" for i, photo in enumerate(other_photos)]
            other_photos_urls = upload_multiple_files_to_s3(
                [BytesIO(content) for content in other_contents],
                other_filenames,
                folder=folder_path,
            )

        # 업로드된 URL들을 TrainingRequest에 저장
        training_request.preview_image_url = preview_image_url
        training_request.front_photos_urls = front_photos_urls if front_photos_urls else None
        training_request.side_photos_urls = side_photos_urls if side_photos_urls else None
        training_request.fullbody_photos_urls = fullbody_photos_urls if fullbody_photos_urls else None
        training_request.other_photos_urls = other_photos_urls if other_photos_urls else None

    except Exception as e:
        # 이미지 업로드 실패 시 롤백
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}",
        )

    # 모든 업로드가 성공하면 commit
    db.commit()
    db.refresh(training_request)

    return TrainingRequestResponse.model_validate(training_request)


# Avatars API
@app.get("/my/avatars", response_model=list[AvatarResponse], tags=["avatars"])
def list_my_avatars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AvatarResponse]:
    """내 아바타 목록 조회"""
    avatars = (
        db.query(Avatar)
        .filter(Avatar.user_id == current_user.id)
        .order_by(Avatar.created_at.desc())
        .all()
    )
    return [AvatarResponse.model_validate(a) for a in avatars]


@app.put("/my/avatars/{avatar_id}", response_model=AvatarResponse, tags=["avatars"])
async def update_avatar(
    avatar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    title: str = Form(None),
    credit_per_generation: int = Form(None),
    description: str = Form(None),
    preview_image: UploadFile = File(None),
):
    """아바타 수정"""
    from fastapi import UploadFile, File, Form
    from io import BytesIO
    from .s3_utils import upload_file_to_s3

    # 아바타 조회 및 권한 확인
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        )

    if avatar.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this avatar",
        )

    # 수정 가능한 필드만 업데이트
    if title is not None:
        avatar.title = title
    if credit_per_generation is not None:
        avatar.credit_per_generation = credit_per_generation
    if description is not None:
        avatar.description = description

    # 이미지 업로드 (avatars/{avatar_id}/ 폴더에 저장)
    if preview_image:
        try:
            image_content = await preview_image.read()
            folder_path = f"avatars/{avatar_id}"
            preview_image_url = upload_file_to_s3(
                BytesIO(image_content),
                preview_image.filename or "preview.jpg",
                folder=folder_path,
                content_type=preview_image.content_type or "image/jpeg",
            )
            avatar.preview_image_url = preview_image_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}",
            )

    db.commit()
    db.refresh(avatar)

    return AvatarResponse.model_validate(avatar)


