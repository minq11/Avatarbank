from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    id: int
    role: str
    locale: str
    credit_balance: int

    class Config:
        from_attributes = True


class GenerationCreateRequest(BaseModel):
    avatar_id: int
    prompt: str = Field(..., max_length=2000)
    option_credits: int = Field(ge=0, le=100)
    idempotency_key: str


class GenerationResponse(BaseModel):
    id: int
    avatar_id: int
    buyer_id: int
    credits_used: int
    prompt: str
    image_url: Optional[str]
    status: str
    fail_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


