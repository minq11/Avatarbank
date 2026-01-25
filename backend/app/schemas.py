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


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUpgradeRequest(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None


class GenerationCreateRequest(BaseModel):
    avatar_id: Optional[int] = None
    prompt: str = Field(..., max_length=2000)
    option_credits: int = Field(ge=0, le=100)
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
    created_at: datetime

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


class AvatarUpdateRequest(BaseModel):
    title: Optional[str] = None
    credit_per_generation: Optional[int] = None
    description: Optional[str] = None


