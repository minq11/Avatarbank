from datetime import datetime, timedelta
from typing import Optional

import httpx
from celery import shared_task
from sqlalchemy.orm import Session

from .celery_app import celery_app
from .config import settings
from .db import SessionLocal
from .models import Generation, GenerationStatus, Task, TaskStatus


def _get_db() -> Session:
    return SessionLocal()


@shared_task(name="generation.run")
def run_generation_task(generation_id: int, presigned_url: str) -> None:
    """
    이미지 생성 Celery 태스크의 1차 스켈레톤.
    - ComfyUI API 호출
    - 결과를 Presigned URL로 업로드하도록 RunPods에 지시
    실제 ComfyUI 연동/콜백 로직은 추후 구현.
    """
    db = _get_db()
    try:
        task = (
            db.query(Task)
            .filter(Task.generation_id == generation_id)
            .order_by(Task.id.desc())
            .first()
        )
        if task:
            task.status = TaskStatus.RUNNING.value
            task.started_at = datetime.utcnow()

        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if not generation:
            if task:
                task.status = TaskStatus.FAILED.value
                task.last_error_message = "Generation not found"
            db.commit()
            return

        generation.status = GenerationStatus.PROCESSING.value
        db.commit()

        # TODO: ComfyUI 워크플로우 호출 및 RunPods 연동 구현
        # 이 영역에서:
        # - settings.COMFYUI_BASE_URL 사용
        # - prompt/seed/옵션을 포함한 payload 전송
        # - RunPods가 S3 Presigned URL로 업로드하도록 정보 전달
        # 현재는 스켈레톤으로만 두고, 실제 호출은 후속 단계에서 구현한다.

    finally:
        db.close()


