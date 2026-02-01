from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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


class GenerationCreateRequest(BaseModel):
    avatar_id: Optional[int] = None
    prompt: str = Field(..., max_length=2000)
    option_credits: int = Field(default=0, ge=0, le=100)
    idempotency_key: str


class GenerationResponse(BaseModel):
    id: int
    avatar_id: Optional[int] = None
    buyer_id: int
    credits_used: int
    prompt: str
    request_id: Optional[str] = None
    image_url: Optional[str]
    seed: Optional[str] = None
    status: str
    fail_reason: Optional[str]
    nsfw_flag: Optional[bool] = None
    is_shared: bool = False
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
    preview_image_url: Optional[str] = None
    credit_per_generation: Optional[int] = None
    negative_prompt: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvatarListResponse(AvatarResponse):
    """마켓 목록용: 추천 수, 댓글 수 포함."""

    up_count: int = 0
    down_count: int = 0
    comment_count: int = 0


class AvatarDetailResponse(AvatarResponse):
    """마켓 모달용: 만든 사람, 인스타(실제인물 시)."""

    creator_nickname: str = ""
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


