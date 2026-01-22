#!/usr/bin/env python3
"""누락된 테이블들을 개별적으로 생성"""

from app.db import engine, Base
import app.models
from app.models import (
    TrainingJob, AuditLog, SharedGeneration, Like, Bookmark, PayoutRequest
)
from sqlalchemy import inspect

def create_missing_tables():
    """누락된 테이블들을 생성합니다."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    missing_models = [
        (TrainingJob, 'training_jobs'),
        (AuditLog, 'audit_logs'),
        (SharedGeneration, 'shared_generations'),
        (Like, 'likes'),
        (Bookmark, 'bookmarks'),
        (PayoutRequest, 'payout_requests'),
    ]
    
    for model, table_name in missing_models:
        if table_name not in existing_tables:
            try:
                print(f"생성 중: {table_name}...")
                model.__table__.create(bind=engine, checkfirst=True)
                print(f"완료: {table_name}")
            except Exception as e:
                print(f"오류 ({table_name}): {e}")
        else:
            print(f"이미 존재: {table_name}")
    
    # 최종 확인
    inspector = inspect(engine)
    final_tables = inspector.get_table_names()
    print(f"\n총 {len(final_tables)}개 테이블:")
    for table in sorted(final_tables):
        print(f"  - {table}")

if __name__ == '__main__':
    create_missing_tables()