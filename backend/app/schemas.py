from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    id: int
    email: str
    nickname: str
    role: str
    locale: str
    credit_balance: int

    class Config:
        from_attributes = True


class UserRegisterRequest(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="buyer", pattern="^(buyer|influencer)$")
    locale: str = Field(default="en", pattern="^(en|ko|ja)$")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBase


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class ChangeNicknameRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUpgradeRequest(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None


# "auto" = 소스 이미지 비율 유지 (image-to-image 기본값)
ImageSizeLiteral = Literal[
    "auto",
    "square_hd", "square", "portrait_4_3", "portrait_16_9",
    "landscape_4_3", "landscape_16_9",
]
OutputFormatLiteral = Literal["jpeg", "png", "webp"]

# image-to-image 공통 옵션 기본값 (fal 엔드포인트 제약과 동일하게)
STRENGTH_FIELD = Field(default=0.6, gt=0.0, le=1.0)
LORA_SCALE_FIELD = Field(default=2.0, ge=0.0, le=4.0)
STEPS_FIELD = Field(default=8, ge=1, le=8)


class GenerationCreateRequest(BaseModel):
    avatar_id: Optional[int] = None
    prompt: str = Field(..., max_length=2000)
    option_credits: int = Field(default=0, ge=0, le=100)
    idempotency_key: str
    image_size: ImageSizeLiteral = "auto"
    num_inference_steps: int = STEPS_FIELD
    output_format: OutputFormatLiteral = "png"
    seed: Optional[int] = Field(default=None, ge=0)
    lora_scale: float = LORA_SCALE_FIELD
    # image-to-image: 비우면 기본 이미지(itoi_example) 사용
    source_image_url: Optional[str] = Field(default=None, max_length=2000)
    strength: float = STRENGTH_FIELD


class GenerationResponse(BaseModel):
    id: int
    avatar_id: Optional[int] = None
    avatar_title: Optional[str] = None
    buyer_id: Optional[int] = None  # 팬(비회원) 리딤 생성은 null
    credits_used: int
    prompt: str
    negative_prompt: Optional[str] = None
    request_id: Optional[str] = None
    image_url: Optional[str]
    seed: Optional[str] = None
    status: str
    fail_reason: Optional[str]
    nsfw_flag: Optional[bool] = None
    is_shared: bool = False
    image_size: Optional[str] = None
    num_inference_steps: Optional[int] = None
    enable_safety_checker: Optional[bool] = None
    lora_scale: Optional[float] = None
    source_image_url: Optional[str] = None
    strength: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GalleryItemResponse(BaseModel):
    """Gallery에 노출되는 공유 생성물 (작성자 닉네임 포함)."""

    id: int
    image_url: str
    prompt: str
    created_at: datetime
    creator_nickname: str

    class Config:
        from_attributes = True


# TrainingRequest 스키마
class TrainingRequestResponse(BaseModel):
    id: int
    avatar_name: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminTrainingRequestResponse(BaseModel):
    """관리자용 학습 요청 목록 (요청자 정보 포함)"""
    id: int
    avatar_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    user_email: str
    user_nickname: str

    class Config:
        from_attributes = True


class TrainingRequestDetailResponse(BaseModel):
    id: int
    avatar_name: str
    negative_prompt: Optional[str] = None
    credit_per_generation: int
    national: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
    is_real_person: bool
    instagram_id: Optional[str] = None
    preview_image_url: Optional[str] = None
    front_photos_urls: Optional[list[str]] = None
    side_photos_urls: Optional[list[str]] = None
    fullbody_photos_urls: Optional[list[str]] = None
    other_photos_urls: Optional[list[str]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Avatar 스키마
class AvatarResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    special_notes: Optional[str] = None
    preview_image_url: Optional[str] = None
    credit_per_generation: Optional[int] = None
    negative_prompt: Optional[str] = None
    is_real_person: bool = False
    instagram_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    @field_validator("height", "weight", mode="before")
    @classmethod
    def coerce_decimal(cls, v: Optional[Decimal | float]) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v

    class Config:
        from_attributes = True


class AvatarListResponse(AvatarResponse):
    """마켓 목록용: 추천 수, 댓글 수 포함."""

    up_count: int = 0
    down_count: int = 0
    comment_count: int = 0


class AvatarDetailResponse(AvatarResponse):
    """마켓 모달용: 만든 사람, 실존인물 여부, 인스타(실제인물 시)."""

    creator_nickname: str = ""
    is_real_person: bool = False
    instagram_id: Optional[str] = None


class AvatarRatingResponse(BaseModel):
    up_count: int = 0
    down_count: int = 0
    my_vote: Optional[str] = None  # "up" | "down" | null


class AvatarRatingSetRequest(BaseModel):
    type: str  # "up" | "down"


class AvatarCommentResponse(BaseModel):
    id: int
    creator_nickname: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AvatarCommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class AvatarUpdateRequest(BaseModel):
    title: Optional[str] = None
    credit_per_generation: Optional[int] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Creator Studio 피벗 스키마
# ---------------------------------------------------------------------------


class PlanResponse(BaseModel):
    id: int
    code: str
    name: str
    monthly_quota: int
    price_usd: float
    max_avatars: int
    max_active_codes: int
    allow_nsfw: bool

    @field_validator("price_usd", mode="before")
    @classmethod
    def coerce_price(cls, v: Optional[Decimal | float]) -> float:
        if v is None:
            return 0.0
        if isinstance(v, Decimal):
            return float(v)
        return v

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    plan_code: str = Field(..., min_length=1, max_length=50)


class SubscriptionResponse(BaseModel):
    plan_code: str
    plan_name: str
    status: str
    quota_remaining: int
    monthly_quota: int
    current_period_end: Optional[datetime] = None


class CodeCreateRequest(BaseModel):
    avatar_id: int
    max_uses: Optional[int] = Field(default=1, ge=1, le=100000)  # null 보내면 무제한
    count: int = Field(default=1, ge=1, le=500)  # 한 번에 발급할 코드 개수
    expires_at: Optional[datetime] = None


class CodeResponse(BaseModel):
    id: int
    code: str
    avatar_id: int
    max_uses: Optional[int] = None
    used_count: int = 0
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StudioGenerateRequest(BaseModel):
    """크리에이터 본인 생성 (쿼터 차감, SFW 강제)."""

    avatar_id: int
    prompt: str = Field(..., max_length=2000)
    image_size: ImageSizeLiteral = "auto"
    num_inference_steps: int = STEPS_FIELD
    output_format: OutputFormatLiteral = "png"
    seed: Optional[int] = Field(default=None, ge=0)
    lora_scale: float = LORA_SCALE_FIELD
    # image-to-image: 비우면 기본 이미지(itoi_example) 사용
    source_image_url: Optional[str] = Field(default=None, max_length=2000)
    strength: float = STRENGTH_FIELD


class RedeemInfoResponse(BaseModel):
    """팬이 코드로 진입 시 보는 정보 (공개)."""

    code: str
    creator_nickname: str
    avatar_id: int
    avatar_title: str
    avatar_preview_url: Optional[str] = None
    uses_left: Optional[int] = None  # null = 무제한


class RedeemGenerateRequest(BaseModel):
    """팬 생성. 프롬프트를 직접 입력한다."""

    prompt: str = Field(..., min_length=1, max_length=2000)
    image_size: ImageSizeLiteral = "auto"
    seed: Optional[int] = Field(default=None, ge=0)
    # image-to-image: 팬이 올린 이미지. 비우면 기본 이미지 사용
    source_image_url: Optional[str] = Field(default=None, max_length=2000)
    strength: float = STRENGTH_FIELD
    lora_scale: float = LORA_SCALE_FIELD

    @field_validator("prompt")
    @classmethod
    def _strip_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("프롬프트를 입력해 주세요.")
        return v


class SourceImageResponse(BaseModel):
    """image-to-image 소스 이미지 업로드 결과."""

    url: str          # 생성 요청에 넘길 값 (S3 원본 URL)
    preview_url: str  # 브라우저 미리보기용 presigned URL


class RedeemGenerateResponse(BaseModel):
    status: str
    image_url: Optional[str] = None
    fail_reason: Optional[str] = None
    uses_left: Optional[int] = None




# ---------------------------------------------------------------------------
# 고객 문의 (고객지원 폼 / 관리자 답장)
# ---------------------------------------------------------------------------

InquiryCategoryLiteral = Literal[
    "account", "avatar", "generation", "code", "billing", "report", "etc"
]


class InquiryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    category: InquiryCategoryLiteral = "etc"
    subject: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=5, max_length=4000)
    # 개인정보 수집·이용 동의 (문의 답변 목적). 프론트 체크박스와 1:1.
    privacy_consent: bool

    @field_validator("name", "subject", "message")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("필수 항목이에요.")
        return v

    @field_validator("privacy_consent")
    @classmethod
    def _require_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("개인정보 수집·이용에 동의해야 문의를 접수할 수 있어요.")
        return v


class InquiryCreateResponse(BaseModel):
    id: int
    status: str
    # 접수 알림 메일이 실제로 나갔는지. False 여도 문의는 정상 접수된 것.
    email_sent: bool


class AdminInquiryResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    email: str
    category: str
    subject: str
    message: str
    status: str
    reply_body: Optional[str]
    replied_at: Optional[datetime]
    notified_at: Optional[datetime]
    created_at: datetime


class InquiryReplyRequest(BaseModel):
    reply_body: str = Field(min_length=1, max_length=4000)

    @field_validator("reply_body")
    @classmethod
    def _strip_reply(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("답장 내용을 입력해 주세요.")
        return v
