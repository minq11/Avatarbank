from datetime import datetime
from typing import List, Optional
import io
import os
import zipfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
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
from .dependencies import get_current_user, get_current_user_optional
from .models import (
    Avatar,
    AvatarComment,
    AvatarRating,
    AvatarStatus,
    Generation,
    GenerationStatus,
    Transaction,
    TrainingRequest,
    User,
)
from .fal_client import run_generation_sync
from .schemas import (
    AdminTrainingRequestResponse,
    AdminUpgradeRequest,
    AvatarCommentCreateRequest,
    AvatarCommentResponse,
    AvatarDetailResponse,
    AvatarListResponse,
    AvatarRatingResponse,
    AvatarRatingSetRequest,
    AvatarResponse,
    AvatarUpdateRequest,
    ChangeNicknameRequest,
    ChangePasswordRequest,
    GalleryItemResponse,
    GenerationCreateRequest,
    GenerationResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TrainingRequestResponse,
    TrainingRequestDetailResponse,
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

# 로컬 스토리지 사용 시 정적 파일 서빙 설정
if settings.STORAGE_TYPE == "local":
    import os
    from pathlib import Path
    
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # /static 경로로 업로드된 파일 서빙
    app.mount("/static", StaticFiles(directory=str(upload_dir)), name="static")


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


@app.put("/auth/me/password", response_model=UserBase, tags=["auth"])
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserBase:
    """비밀번호 변경"""
    from .auth import verify_password

    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    db.refresh(current_user)
    return UserBase.model_validate(current_user)


@app.put("/auth/me/nickname", response_model=UserBase, tags=["auth"])
def change_nickname(
    payload: ChangeNicknameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserBase:
    """닉네임 변경"""
    existing = get_user_by_nickname(db, payload.nickname)
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nickname is already in use.",
        )
    current_user.nickname = payload.nickname.strip()
    db.commit()
    db.refresh(current_user)
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
    """
    이미지 생성 요청. 로그인 필수.
    get_current_user로 인증 검증 - 토큰 없거나 유효하지 않으면 401 반환.
    """
    # TODO: 프롬프트 필터링, idempotency 체크 구현

    # 인증된 사용자를 buyer로 사용
    buyer = current_user

    if payload.avatar_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar is required for image generation.",
        )
    avatar = db.query(Avatar).filter(Avatar.id == payload.avatar_id).first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar not found. Please select an avatar first.",
        )
    if not avatar.lora_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This avatar has no LoRA file; image generation is not available yet.",
        )

    total_credits = 1 + (avatar.credit_per_generation or 0)
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
    db.commit()
    db.refresh(generation)

    try:
        from .s3_utils import generate_presigned_download_url

        lora_url = avatar.lora_path
        if lora_url and "s3" in lora_url.lower() and "amazonaws" in lora_url.lower():
            lora_url = generate_presigned_download_url(lora_url, expires_in=3600)
        response_payload = run_generation_sync(payload.prompt, lora_url=lora_url)
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


@app.put("/my/generations/{generation_id}/share", response_model=GenerationResponse, tags=["generation"])
def toggle_generation_share(
    generation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerationResponse:
    """Share 토글: Gallery 노출 여부. 본인 소유이고 status=success인 경우만 가능."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found.")
    if generation.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your generation.")
    if generation.status != GenerationStatus.SUCCESS.value:
        raise HTTPException(status_code=400, detail="Only successful generations can be shared.")
    generation.is_shared = not generation.is_shared
    db.commit()
    db.refresh(generation)
    return GenerationResponse.model_validate(generation)


@app.get("/gallery/generations", response_model=List[GalleryItemResponse], tags=["gallery"])
def list_gallery_generations(
    avatar_id: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[GalleryItemResponse]:
    """Gallery에 노출되는 공유 생성물 목록 (is_shared=True, status=success). avatar_id 지정 시 해당 아바타로 생성된 것만. limit/offset 있으면 페이지네이션."""
    query = (
        db.query(Generation, User)
        .join(User, Generation.buyer_id == User.id)
        .filter(
            Generation.is_shared == True,
            Generation.status == GenerationStatus.SUCCESS.value,
            Generation.image_url.isnot(None),
        )
    )
    if avatar_id is not None:
        query = query.filter(Generation.avatar_id == avatar_id)
    query = query.order_by(Generation.created_at.desc())
    if limit is not None and offset is not None:
        limit = min(max(1, limit), 48)
        offset = max(0, offset)
        query = query.offset(offset).limit(limit)
    rows = query.all()
    return [
        GalleryItemResponse(
            id=g.id,
            image_url=g.image_url or "",
            prompt=g.prompt,
            created_at=g.created_at,
            creator_nickname=user.nickname,
        )
        for g, user in rows
    ]


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
    from .models import TrainingRequestStatus
    from .config import settings
    
    # 스토리지 타입에 따라 적절한 함수 선택
    if settings.STORAGE_TYPE == "local":
        from .local_storage import upload_file_to_local as upload_file, upload_multiple_files_to_local as upload_multiple_files
    else:
        from .s3_utils import upload_file_to_s3 as upload_file, upload_multiple_files_to_s3 as upload_multiple_files

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
        preview_image_url = upload_file(
            BytesIO(preview_content),
            preview_image.filename or "preview.jpg",
            folder=folder_path,
            content_type=preview_image.content_type or "image/jpeg",
        )

        # 정면 사진들 업로드
        if front_photos:
            front_contents = [await photo.read() for photo in front_photos]
            front_filenames = [photo.filename or f"front_{i}.jpg" for i, photo in enumerate(front_photos)]
            front_photos_urls = upload_multiple_files(
                [BytesIO(content) for content in front_contents],
                front_filenames,
                folder=folder_path,
            )

        # 측면 사진들 업로드
        if side_photos:
            side_contents = [await photo.read() for photo in side_photos]
            side_filenames = [photo.filename or f"side_{i}.jpg" for i, photo in enumerate(side_photos)]
            side_photos_urls = upload_multiple_files(
                [BytesIO(content) for content in side_contents],
                side_filenames,
                folder=folder_path,
            )

        # 전신 사진들 업로드
        if fullbody_photos:
            fullbody_contents = [await photo.read() for photo in fullbody_photos]
            fullbody_filenames = [photo.filename or f"fullbody_{i}.jpg" for i, photo in enumerate(fullbody_photos)]
            fullbody_photos_urls = upload_multiple_files(
                [BytesIO(content) for content in fullbody_contents],
                fullbody_filenames,
                folder=folder_path,
            )

        # 기타 사진들 업로드
        if other_photos:
            other_contents = [await photo.read() for photo in other_photos]
            other_filenames = [photo.filename or f"other_{i}.jpg" for i, photo in enumerate(other_photos)]
            other_photos_urls = upload_multiple_files(
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


@app.get("/my/training-requests/{request_id}", response_model=TrainingRequestDetailResponse, tags=["training"])
def get_training_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingRequestDetailResponse:
    """학습 요청 상세 조회"""
    request = (
        db.query(TrainingRequest)
        .filter(
            TrainingRequest.id == request_id,
            TrainingRequest.user_id == current_user.id,
        )
        .first()
    )
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training request not found",
        )
    
    return TrainingRequestDetailResponse.model_validate(request)


@app.patch("/my/training-requests/{request_id}/cancel", response_model=TrainingRequestResponse, tags=["training"])
def cancel_training_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingRequestResponse:
    """학습 요청 취소"""
    from .models import TrainingRequestStatus
    
    request = (
        db.query(TrainingRequest)
        .filter(
            TrainingRequest.id == request_id,
            TrainingRequest.user_id == current_user.id,
        )
        .first()
    )
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training request not found",
        )
    
    # 이미 승인되었거나 거부된 요청은 취소할 수 없음
    if request.status in [TrainingRequestStatus.APPROVED_TRAINING.value, TrainingRequestStatus.REJECTED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a request that has already been approved or rejected",
        )
    
    # 이미 취소된 요청은 다시 취소할 수 없음
    if request.status == TrainingRequestStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is already cancelled",
        )
    
    # 요청 상태를 취소로 변경
    request.status = TrainingRequestStatus.CANCELLED.value
    db.commit()
    db.refresh(request)
    
    return TrainingRequestResponse.model_validate(request)


# Admin Training Requests API
@app.get("/admin/training-requests", response_model=list[AdminTrainingRequestResponse], tags=["admin"])
def admin_list_training_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AdminTrainingRequestResponse]:
    """관리자용 학습 요청 전체 목록 조회 (요청자 정보 포함)"""
    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    rows = (
        db.query(TrainingRequest, User)
        .join(User, TrainingRequest.user_id == User.id)
        .order_by(TrainingRequest.created_at.desc())
        .all()
    )
    return [
        AdminTrainingRequestResponse(
            id=req.id,
            avatar_name=req.avatar_name,
            status=req.status,
            created_at=req.created_at,
            updated_at=req.updated_at,
            user_id=user.id,
            user_email=user.email,
            user_nickname=user.nickname,
        )
        for req, user in rows
    ]


@app.get(
    "/admin/training-requests/{request_id}",
    response_model=TrainingRequestDetailResponse,
    tags=["admin"],
)
def admin_get_training_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingRequestDetailResponse:
    """관리자용 학습 요청 상세 조회"""
    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    request = (
        db.query(TrainingRequest)
        .filter(TrainingRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training request not found",
        )

    return TrainingRequestDetailResponse.model_validate(request)


@app.get(
    "/admin/training-requests/{request_id}/photos.zip",
    tags=["admin"],
)
def admin_download_training_request_photos_zip(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """관리자용 학습 요청 사진 ZIP 다운로드"""
    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    request = (
        db.query(TrainingRequest)
        .filter(TrainingRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training request not found",
        )

    folder_name = f"training-requests/{request_id}"

    # 로컬 스토리지
    if settings.STORAGE_TYPE == "local":
        base_dir = Path(settings.UPLOAD_DIR) / folder_name
        if not base_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training photos not found",
            )

        mem_file = io.BytesIO()
        with zipfile.ZipFile(mem_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(base_dir):
                for filename in files:
                    file_path = Path(root) / filename
                    arcname = str(file_path.relative_to(base_dir))
                    zf.write(file_path, arcname)

        mem_file.seek(0)

        def file_iterator(chunk_size: int = 8192):
            while True:
                chunk = mem_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="training_request_{request_id}_photos.zip"'
            },
        )

    # S3 스토리지
    else:
        from .s3_utils import get_s3_client

        s3_client = get_s3_client()
        prefix = folder_name.rstrip("/") + "/"

        # 객체 목록 조회
        resp = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET,
            Prefix=prefix,
        )
        contents = resp.get("Contents", [])
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training photos not found in S3",
            )

        mem_file = io.BytesIO()
        with zipfile.ZipFile(mem_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for obj in contents:
                key = obj["Key"]
                # prefix 이후의 경로만 zip 내부 경로로 사용
                arcname = key[len(prefix) :] if key.startswith(prefix) else key
                s3_obj = s3_client.get_object(Bucket=settings.S3_BUCKET, Key=key)
                data = s3_obj["Body"].read()
                zf.writestr(arcname, data)

        mem_file.seek(0)

        def file_iterator(chunk_size: int = 8192):
            while True:
                chunk = mem_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="training_request_{request_id}_photos.zip"'
            },
        )


@app.post(
    "/admin/training-requests/{request_id}/upload-lora",
    response_model=AvatarResponse,
    tags=["admin"],
)
async def admin_upload_lora(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    lora_file: UploadFile = File(..., description=".safetensors LoRA 파일"),
):
    """
    관리자: Training Request에 대해 LoRA(.safetensors) 파일을 S3에 업로드하고
    Avatar 레코드를 생성/갱신하여 lora_path에 연결합니다.
    """
    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    tr = (
        db.query(TrainingRequest)
        .filter(TrainingRequest.id == request_id)
        .first()
    )
    if not tr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training request not found",
        )

    filename = lora_file.filename or "model.safetensors"
    if not filename.lower().endswith(".safetensors"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .safetensors files are allowed",
        )

    from io import BytesIO
    from .s3_utils import upload_file_to_s3

    content = await lora_file.read()
    folder = f"loras/training_request_{request_id}"
    lora_url = upload_file_to_s3(
        BytesIO(content),
        filename,
        folder=folder,
        content_type="application/octet-stream",
    )

    avatar = (
        db.query(Avatar)
        .filter(Avatar.training_request_id == request_id)
        .first()
    )

    from .models import TrainingRequestStatus

    if avatar:
        avatar.lora_path = lora_url
        avatar.title = tr.avatar_name
        avatar.description = tr.description
        avatar.nationality = tr.national
        avatar.gender = tr.gender
        avatar.negative_prompt = tr.negative_prompt
        avatar.credit_per_generation = tr.credit_per_generation
        if tr.preview_image_url:
            avatar.preview_image_url = tr.preview_image_url
    else:
        avatar = Avatar(
            user_id=tr.user_id,
            training_request_id=request_id,
            title=tr.avatar_name,
            description=tr.description,
            nationality=tr.national,
            gender=tr.gender,
            negative_prompt=tr.negative_prompt,
            credit_per_generation=tr.credit_per_generation,
            lora_path=lora_url,
            preview_image_url=tr.preview_image_url,
            status=AvatarStatus.ACTIVE.value,
        )
        db.add(avatar)

    tr.status = TrainingRequestStatus.APPROVED_TRAINING.value
    db.commit()
    db.refresh(avatar)

    return AvatarResponse.model_validate(avatar)


@app.get("/admin/training-requests/{request_id}/lora", tags=["admin"])
def admin_get_lora_download_url(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    관리자: approved_training인 Training Request의 LoRA(.safetensors) 다운로드용
    presigned URL 반환. Avatar의 lora_path가 있을 때만 사용 가능.
    """
    if not _is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    avatar = (
        db.query(Avatar)
        .filter(Avatar.training_request_id == request_id)
        .first()
    )
    if not avatar or not avatar.lora_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LoRA file not found for this training request",
        )

    from .s3_utils import generate_presigned_download_url

    url = generate_presigned_download_url(avatar.lora_path, expires_in=3600)
    return {"url": url}


# Avatars API (public: 마켓/이미지 생성용)
@app.get("/avatars/filter-options", tags=["avatars"])
def get_avatar_filter_options(db: Session = Depends(get_db)):
    """마켓 필터용: nationality, gender 옵션 목록."""
    base = (
        db.query(Avatar)
        .filter(
            Avatar.status == AvatarStatus.ACTIVE.value,
            Avatar.lora_path.isnot(None),
            Avatar.lora_path != "",
        )
    )
    nationalities = [r[0] for r in base.with_entities(Avatar.nationality).distinct().all() if r[0]]
    genders = [r[0] for r in base.with_entities(Avatar.gender).distinct().all() if r[0]]
    return {"nationalities": sorted(nationalities), "genders": sorted(genders)}


@app.get("/avatars", response_model=list[AvatarListResponse], tags=["avatars"])
def list_avatars_public(
    q: Optional[str] = None,
    nationality: Optional[str] = None,
    gender: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[AvatarListResponse]:
    """공개 아바타 목록. q=검색, nationality/gender=필터, sort=recommend|name|comments|newest."""
    query = (
        db.query(Avatar)
        .filter(
            Avatar.status == AvatarStatus.ACTIVE.value,
            Avatar.lora_path.isnot(None),
            Avatar.lora_path != "",
        )
    )
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(Avatar.title.ilike(term), func.coalesce(Avatar.description, "").ilike(term))
        )
    if nationality and nationality.strip():
        query = query.filter(Avatar.nationality == nationality.strip())
    if gender and gender.strip():
        query = query.filter(Avatar.gender == gender.strip())
    if sort == "name":
        query = query.order_by(Avatar.title.asc())
    else:
        query = query.order_by(Avatar.created_at.desc())
    avatars = query.all()
    avatar_ids = [a.id for a in avatars]
    counts: dict[int, dict[str, int]] = {aid: {"up": 0, "down": 0, "comments": 0} for aid in avatar_ids}
    if avatar_ids:
        up_rows = (
            db.query(AvatarRating.avatar_id, func.count().label("cnt"))
            .filter(AvatarRating.avatar_id.in_(avatar_ids), AvatarRating.is_up == True)
            .group_by(AvatarRating.avatar_id)
        ).all()
        for aid, cnt in up_rows:
            counts[aid]["up"] = cnt
        down_rows = (
            db.query(AvatarRating.avatar_id, func.count().label("cnt"))
            .filter(AvatarRating.avatar_id.in_(avatar_ids), AvatarRating.is_up == False)
            .group_by(AvatarRating.avatar_id)
        ).all()
        for aid, cnt in down_rows:
            counts[aid]["down"] = cnt
        comment_rows = (
            db.query(AvatarComment.avatar_id, func.count().label("cnt"))
            .filter(AvatarComment.avatar_id.in_(avatar_ids))
            .group_by(AvatarComment.avatar_id)
        ).all()
        for aid, cnt in comment_rows:
            counts[aid]["comments"] = cnt
    items = [
        AvatarListResponse(
            **AvatarResponse.model_validate(a).model_dump(),
            up_count=counts[a.id]["up"],
            down_count=counts[a.id]["down"],
            comment_count=counts[a.id]["comments"],
        )
        for a in avatars
    ]
    if sort == "recommend":
        items.sort(key=lambda x: x.up_count, reverse=True)
    elif sort == "comments":
        items.sort(key=lambda x: x.comment_count, reverse=True)
    return items


@app.get("/avatars/{avatar_id}", response_model=AvatarDetailResponse, tags=["avatars"])
def get_avatar_public(
    avatar_id: int,
    db: Session = Depends(get_db),
) -> AvatarDetailResponse:
    """공개 아바타 단건 조회 (마켓 모달·이미지 생성 페이지용). creator_nickname, instagram_id 포함."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        )
    if avatar.status != AvatarStatus.ACTIVE.value or not avatar.lora_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar is not available for image generation",
        )
    creator_nickname = ""
    instagram_id = None
    owner = db.query(User).filter(User.id == avatar.user_id).first()
    if owner:
        creator_nickname = owner.nickname or ""
    if avatar.training_request_id:
        tr = db.query(TrainingRequest).filter(TrainingRequest.id == avatar.training_request_id).first()
        if tr and tr.instagram_id:
            instagram_id = tr.instagram_id
    data = AvatarResponse.model_validate(avatar).model_dump()
    data["creator_nickname"] = creator_nickname
    data["instagram_id"] = instagram_id
    return AvatarDetailResponse(**data)


@app.get("/avatars/{avatar_id}/rating", response_model=AvatarRatingResponse, tags=["avatars"])
def get_avatar_rating(
    avatar_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AvatarRatingResponse:
    """아바타 추천/비추천 개수 및 내 투표."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    up_count = db.query(AvatarRating).filter(AvatarRating.avatar_id == avatar_id, AvatarRating.is_up == True).count()
    down_count = db.query(AvatarRating).filter(AvatarRating.avatar_id == avatar_id, AvatarRating.is_up == False).count()
    my_vote = None
    if current_user:
        r = db.query(AvatarRating).filter(
            AvatarRating.avatar_id == avatar_id,
            AvatarRating.user_id == current_user.id,
        ).first()
        if r:
            my_vote = "up" if r.is_up else "down"
    return AvatarRatingResponse(up_count=up_count, down_count=down_count, my_vote=my_vote)


@app.put("/avatars/{avatar_id}/rating", response_model=AvatarRatingResponse, tags=["avatars"])
def set_avatar_rating(
    avatar_id: int,
    payload: AvatarRatingSetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvatarRatingResponse:
    """아바타 추천(up) 또는 비추천(down) 설정. 같은 버튼 다시 누르면 취소. type: 'up' | 'down'."""
    if payload.type not in ("up", "down"):
        raise HTTPException(status_code=400, detail="type must be 'up' or 'down'.")
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    existing = (
        db.query(AvatarRating)
        .filter(AvatarRating.avatar_id == avatar_id, AvatarRating.user_id == current_user.id)
        .first()
    )
    is_up = payload.type == "up"
    if existing:
        if existing.is_up == is_up:
            db.delete(existing)
            my_vote = None
        else:
            existing.is_up = is_up
            my_vote = payload.type
    else:
        db.add(AvatarRating(avatar_id=avatar_id, user_id=current_user.id, is_up=is_up))
        my_vote = payload.type
    db.commit()
    up_count = db.query(AvatarRating).filter(AvatarRating.avatar_id == avatar_id, AvatarRating.is_up == True).count()
    down_count = db.query(AvatarRating).filter(AvatarRating.avatar_id == avatar_id, AvatarRating.is_up == False).count()
    return AvatarRatingResponse(up_count=up_count, down_count=down_count, my_vote=my_vote)


@app.get("/avatars/{avatar_id}/comments", response_model=List[AvatarCommentResponse], tags=["avatars"])
def list_avatar_comments(
    avatar_id: int,
    db: Session = Depends(get_db),
) -> List[AvatarCommentResponse]:
    """아바타 댓글 목록 (최신순)."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    rows = (
        db.query(AvatarComment, User)
        .join(User, AvatarComment.user_id == User.id)
        .filter(AvatarComment.avatar_id == avatar_id)
        .order_by(AvatarComment.created_at.desc())
        .all()
    )
    return [
        AvatarCommentResponse(
            id=c.id,
            creator_nickname=u.nickname or "",
            content=c.content,
            created_at=c.created_at,
        )
        for c, u in rows
    ]


@app.post(
    "/avatars/{avatar_id}/comments",
    response_model=AvatarCommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["avatars"],
)
def create_avatar_comment(
    avatar_id: int,
    payload: AvatarCommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvatarCommentResponse:
    """아바타 댓글 작성."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    comment = AvatarComment(avatar_id=avatar_id, user_id=current_user.id, content=payload.content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    user = db.query(User).filter(User.id == current_user.id).first()
    return AvatarCommentResponse(
        id=comment.id,
        creator_nickname=user.nickname if user else "",
        content=comment.content,
        created_at=comment.created_at,
    )


# Avatars API (my)
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
    """아바타 수정 (Preview Image는 STORAGE_TYPE에 따라 로컬 또는 S3에 저장)"""
    from fastapi import UploadFile, File, Form
    from io import BytesIO
    if settings.STORAGE_TYPE == "local":
        from .local_storage import upload_file_to_local as upload_file
    else:
        from .s3_utils import upload_file_to_s3 as upload_file

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
            preview_image_url = upload_file(
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


