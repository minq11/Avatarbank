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


ImageSizeLiteral = Literal[
    "square_hd", "square", "portrait_4_3", "portrait_16_9",
    "landscape_4_3", "landscape_16_9",
]
OutputFormatLiteral = Literal["jpeg", "png", "webp"]


class GenerationCreateRequest(BaseModel):
    avatar_id: Optional[int] = None
    prompt: str = Field(..., max_length=2000)
    negative_prompt: Optional[str] = Field(default=None, max_length=2000)
    option_credits: int = Field(default=0, ge=0, le=100)
    idempotency_key: str
    enable_safety_checker: bool = True
    image_size: ImageSizeLiteral = "landscape_4_3"
    num_inference_steps: int = Field(default=8, ge=1, le=20)
    output_format: OutputFormatLiteral = "png"
    seed: Optional[int] = Field(default=None, ge=0)
    lora_scale: float = Field(default=1.6, ge=0.0, le=4.0)


class GenerationResponse(BaseModel):
    id: int
    avatar_id: Optional[int] = None
    avatar_title: Optional[str] = None
    buyer_id: int
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


class TemplateCreateRequest(BaseModel):
    avatar_id: int
    name: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=2000)
    negative_prompt: Optional[str] = Field(default=None, max_length=2000)
    image_size: ImageSizeLiteral = "portrait_4_3"
    num_inference_steps: int = Field(default=8, ge=1, le=20)
    lora_scale: float = Field(default=1.6, ge=0.0, le=4.0)


class TemplateResponse(BaseModel):
    id: int
    avatar_id: int
    name: str
    prompt: str
    negative_prompt: Optional[str] = None
    image_size: Optional[str] = None
    num_inference_steps: Optional[int] = None
    lora_scale: Optional[float] = None
    preview_image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class CodeCreateRequest(BaseModel):
    avatar_id: int
    template_id: Optional[int] = None
    max_uses: Optional[int] = Field(default=1, ge=1, le=100000)  # null 보내면 무제한
    count: int = Field(default=1, ge=1, le=500)  # 한 번에 발급할 코드 개수
    expires_at: Optional[datetime] = None


class CodeResponse(BaseModel):
    id: int
    code: str
    avatar_id: int
    template_id: Optional[int] = None
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
    negative_prompt: Optional[str] = Field(default=None, max_length=2000)
    image_size: ImageSizeLiteral = "portrait_4_3"
    num_inference_steps: int = Field(default=8, ge=1, le=20)
    output_format: OutputFormatLiteral = "png"
    seed: Optional[int] = Field(default=None, ge=0)
    lora_scale: float = Field(default=1.6, ge=0.0, le=4.0)


class RedeemInfoResponse(BaseModel):
    """팬이 코드로 진입 시 보는 정보 (공개)."""

    code: str
    creator_nickname: str
    avatar_id: int
    avatar_title: str
    avatar_preview_url: Optional[str] = None
    uses_left: Optional[int] = None  # null = 무제한
    free_prompt_allowed: bool = True  # 코드가 특정 템플릿에 묶이면 False
    templates: list[TemplateResponse] = []


class RedeemGenerateRequest(BaseModel):
    """팬 생성. 템플릿을 고르거나(template_id), 자유 프롬프트를 직접 입력(prompt)."""

    template_id: Optional[int] = None
    prompt: Optional[str] = Field(default=None, max_length=2000)
    image_size: ImageSizeLiteral = "portrait_4_3"
    seed: Optional[int] = Field(default=None, ge=0)

    @field_validator("prompt")
    @classmethod
    def _strip_prompt(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def _require_one(self) -> "RedeemGenerateRequest":
        if self.template_id is None and not self.prompt:
            raise ValueError("Either template_id or prompt is required.")
        return self


class RedeemGenerateResponse(BaseModel):
    status: str
    image_url: Optional[str] = None
    fail_reason: Optional[str] = None
    uses_left: Optional[int] = None


