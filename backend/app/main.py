from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .models import Generation, GenerationStatus, Task, TaskStatus, Transaction, User
from .schemas import GenerationCreateRequest, GenerationResponse
from .tasks import run_generation_task

app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def on_startup() -> None:
    # 초기 단계에서는 자동으로 테이블을 생성하도록 두고,
    # 이후 Alembic 마이그레이션으로 전환한다.
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/generations", response_model=GenerationResponse, tags=["generation"])
def create_generation(
    payload: GenerationCreateRequest,
    db: Session = Depends(get_db),
    # TODO: 실제 구현 시 current_user 의존성 추가
) -> GenerationResponse:
    # TODO: 인증/인가, 프롬프트 필터링, idempotency 체크 구현

    # 임시: 테스트용으로 첫 번째 Buyer를 사용
    buyer: User | None = db.query(User).first()
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No buyer user exists (seed data required).",
        )

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


