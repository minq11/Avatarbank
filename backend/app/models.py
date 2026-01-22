from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
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

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    nationality = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Numeric(5, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    special_notes = Column(Text, nullable=True)
    lora_path = Column(String, nullable=True)
    nsfw_allowed = Column(Boolean, nullable=False, default=False)
    is_public = Column(Boolean, nullable=False, default=False)
    preview_image_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default=AvatarStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credits_used = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    seed = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default=GenerationStatus.PENDING)
    fail_reason = Column(Text, nullable=True)
    nsfw_flag = Column(Boolean, nullable=False, default=False)
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


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    log_url = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)


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

