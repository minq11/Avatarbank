from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .db import Base


class UserRole(str, Enum):
    BUYER = "buyer"
    INFLUENCER = "influencer"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.BUYER)
    credit_balance = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default=UserStatus.ACTIVE)
    locale = Column(String, nullable=False, default="en")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at = Column(DateTime, nullable=True)


class AvatarStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class Avatar(Base):
    __tablename__ = "avatars"
    __table_args__ = (UniqueConstraint("user_id", "title", name="uq_avatars_user_title"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_request_id = Column(Integer, ForeignKey("training_requests.id"), nullable=True)  # 학습 요청과 연결
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    nationality = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Numeric(5, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    special_notes = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)  # 네거티브 프롬프트
    credit_per_generation = Column(Integer, nullable=True)  # 생성당 크레딧
    lora_path = Column(String, nullable=True)
    nsfw_allowed = Column(Boolean, nullable=False, default=False)
    is_public = Column(Boolean, nullable=False, default=False)
    preview_image_url = Column(String, nullable=True)
    is_real_person = Column(Boolean, nullable=False, default=False)
    instagram_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default=AvatarStatus.PENDING)
    deleted_at = Column(DateTime, nullable=True)  # 논리 삭제
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AvatarRating(Base):
    """아바타 추천/비추천 (유저당 1개: up 또는 down)."""

    __tablename__ = "avatar_ratings"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_up = Column(Boolean, nullable=False)  # True=추천, False=비추천
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AvatarComment(Base):
    """아바타 댓글."""

    __tablename__ = "avatar_comments"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 팬(비회원) 생성은 null
    credits_used = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    seed = Column(String, nullable=True)
    request_id = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default=GenerationStatus.PENDING)
    fail_reason = Column(Text, nullable=True)
    nsfw_flag = Column(Boolean, nullable=False, default=False)
    is_shared = Column(Boolean, nullable=False, default=False)
    image_size = Column(String, nullable=True)
    num_inference_steps = Column(Integer, nullable=True)
    enable_safety_checker = Column(Boolean, nullable=True)  # True = safety on (no NSFW)
    lora_scale = Column(Float, nullable=True)  # LoRA scale 0–4
    # Creator Studio 피벗: 쿼터 기반 생성 귀속/출처
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 쿼터 소유 크리에이터
    redeem_code_id = Column(Integer, ForeignKey("redeem_codes.id"), nullable=True)  # 팬 코드 생성 시
    template_id = Column(Integer, ForeignKey("generation_templates.id"), nullable=True)
    source = Column(String, nullable=True)  # "self" | "fan"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TransactionType(str, Enum):
    PURCHASE = "purchase"
    GENERATION = "generation"
    PAYOUT = "payout"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    credit_before = Column(Integer, nullable=True)
    credit_after = Column(Integer, nullable=True)
    reference_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=TaskStatus.QUEUED)
    worker_id = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_error_message = Column(Text, nullable=True)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    level = Column(String, nullable=False, default="error")
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    event_id = Column(String, nullable=False, unique=True)
    payload = Column(JSONB, nullable=False)
    status = Column(String, nullable=False, default="received")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=True)
    target_id = Column(Integer, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)  # DB 컬럼명은 metadata, Python 속성명은 metadata_json
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SharedGeneration(Base):
    __tablename__ = "shared_generations"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    share_token = Column(String, nullable=False, unique=True)
    is_public = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expired_at = Column(DateTime, nullable=True)


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credits_requested = Column(Integer, nullable=False)
    usd_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False, default="pending")
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    payout_tx_id = Column(String, nullable=True)


class TrainingRequestStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED_TRAINING = "approved_training"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TrainingRequest(Base):
    __tablename__ = "training_requests"
    __table_args__ = (
        UniqueConstraint("user_id", "avatar_name", name="uq_training_requests_user_avatar_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    avatar_name = Column(String, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    credit_per_generation = Column(Integer, nullable=False)
    national = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_real_person = Column(Boolean, nullable=False, default=False)
    instagram_id = Column(String, nullable=True)
    preview_image_url = Column(String, nullable=True)
    # 사진 URL들을 JSON 배열로 저장
    front_photos_urls = Column(JSONB, nullable=True)
    side_photos_urls = Column(JSONB, nullable=True)
    fullbody_photos_urls = Column(JSONB, nullable=True)
    other_photos_urls = Column(JSONB, nullable=True)
    status = Column(String, nullable=False, default=TrainingRequestStatus.REQUESTED.value)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 승인/반려한 관리자
    admin_notes = Column(Text, nullable=True)  # 관리자 메모
    deleted_at = Column(DateTime, nullable=True)  # 논리 삭제
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# ---------------------------------------------------------------------------
# Creator Studio 피벗: 구독 / 요금제 / 리딤 코드 / 생성 템플릿
# ---------------------------------------------------------------------------


class Plan(Base):
    """구독 요금제. 월 생성 쿼터(이미지 수)를 정의."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)  # free/starter/pro/studio
    name = Column(String, nullable=False)
    monthly_quota = Column(Integer, nullable=False, default=0)  # 월 생성 가능 이미지 수
    price_usd = Column(Numeric(10, 2), nullable=False, default=0)
    max_avatars = Column(Integer, nullable=False, default=1)  # 등록 가능 아바타 수
    max_active_codes = Column(Integer, nullable=False, default=0)  # 동시 활성 코드 수
    allow_nsfw = Column(Boolean, nullable=False, default=False)  # 미래 확장용. 현재 전부 False
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"


class Subscription(Base):
    """크리에이터의 현재 구독 + 남은 쿼터."""

    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id", name="uq_subscriptions_user"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String, nullable=False, default=SubscriptionStatus.ACTIVE.value)
    quota_remaining = Column(Integer, nullable=False, default=0)  # 이번 주기 남은 생성 수
    current_period_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_period_end = Column(DateTime, nullable=True)  # 다음 갱신/리셋 시점
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class GenerationTemplate(Base):
    """크리에이터가 승인한 생성 프리셋. 팬은 이 프롬프트 범위 안에서만 생성 가능 (SFW 통제)."""

    __tablename__ = "generation_templates"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    name = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)  # 고정 프롬프트 (팬에게 노출/적용)
    negative_prompt = Column(Text, nullable=True)
    image_size = Column(String, nullable=True, default="portrait_4_3")
    num_inference_steps = Column(Integer, nullable=True, default=8)
    lora_scale = Column(Float, nullable=True, default=1.6)
    preview_image_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class RedeemCode(Base):
    """팬에게 배포하는 생성 코드. 1회/다회/무제한, 만료, 연결된 아바타·템플릿."""

    __tablename__ = "redeem_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("generation_templates.id"), nullable=True)
    max_uses = Column(Integer, nullable=True)  # null = 무제한(쿼터 소진 시까지), 1 = 일회용
    used_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

