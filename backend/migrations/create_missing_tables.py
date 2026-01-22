#!/usr/bin/env python3
"""
누락된 테이블들을 개별적으로 생성

사용법:
    cd backend
    python migrations/create_missing_tables.py
"""

import sys
from pathlib import Path

# backend 폴더를 Python 경로에 추가
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine, Base
import app.models  # 모든 모델을 import하여 Base.metadata에 등록
from sqlalchemy import inspect

def create_missing_tables():
    """누락된 테이블들을 생성합니다."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # 누락된 테이블 목록
    missing_table_names = [
        'training_jobs',
        'audit_logs',
        'shared_generations',
        'likes',
        'bookmarks',
        'payout_requests',
    ]
    
    for table_name in missing_table_names:
        if table_name not in existing_tables:
            try:
                print(f"생성 중: {table_name}...")
                # Base.metadata에서 테이블 찾아서 생성
                table = Base.metadata.tables.get(table_name)
                if table:
                    table.create(bind=engine, checkfirst=True)
                    print(f"완료: {table_name}")
                else:
                    print(f"경고: {table_name} 테이블 정의를 찾을 수 없음")
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