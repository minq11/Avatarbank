#!/usr/bin/env python3
"""
TrainingRequest 테이블 생성 및 Avatar 테이블 필드 추가

사용법:
    cd backend
    python migrations/add_training_request_and_avatar_fields.py
"""

import sys
from pathlib import Path

# backend 폴더를 Python 경로에 추가
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine, Base
import app.models  # 모든 모델을 import하여 Base.metadata에 등록
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError

def create_training_request_table():
    """TrainingRequest 테이블 생성"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'training_requests' not in existing_tables:
        try:
            print("Creating training_requests table...")
            table = Base.metadata.tables.get('training_requests')
            if table:
                table.create(bind=engine, checkfirst=True)
                print("[OK] Created training_requests table")
            else:
                print("[WARN] Warning: training_requests table definition not found")
        except Exception as e:
            print(f"[ERROR] Error creating training_requests table: {e}")
    else:
        print("[OK] training_requests table already exists")

def add_avatar_fields():
    """Avatar 테이블에 새 필드 추가"""
    inspector = inspect(engine)
    
    # Avatar 테이블이 존재하는지 확인
    if 'avatars' not in inspector.get_table_names():
        print("[ERROR] avatars table does not exist. Please create it first.")
        return
    
    # 기존 컬럼 확인
    existing_columns = [col['name'] for col in inspector.get_columns('avatars')]
    
    with engine.connect() as conn:
        # negative_prompt 필드 추가
        if 'negative_prompt' not in existing_columns:
            try:
                print("Adding negative_prompt column to avatars...")
                conn.execute(text("ALTER TABLE avatars ADD COLUMN negative_prompt TEXT"))
                conn.commit()
                print("[OK] Added negative_prompt column")
            except Exception as e:
                print(f"[ERROR] Error adding negative_prompt: {e}")
                conn.rollback()
        else:
            print("[OK] negative_prompt column already exists")
        
        # credit_per_generation 필드 추가
        if 'credit_per_generation' not in existing_columns:
            try:
                print("Adding credit_per_generation column to avatars...")
                conn.execute(text("ALTER TABLE avatars ADD COLUMN credit_per_generation INTEGER"))
                conn.commit()
                print("[OK] Added credit_per_generation column")
            except Exception as e:
                print(f"[ERROR] Error adding credit_per_generation: {e}")
                conn.rollback()
        else:
            print("[OK] credit_per_generation column already exists")
        
        # training_request_id 필드 추가
        if 'training_request_id' not in existing_columns:
            try:
                print("Adding training_request_id column to avatars...")
                conn.execute(text("ALTER TABLE avatars ADD COLUMN training_request_id INTEGER"))
                conn.commit()
                print("[OK] Added training_request_id column")
                
                # 외래키 제약조건 추가 (training_requests 테이블이 존재하는 경우)
                try:
                    print("Adding foreign key constraint for training_request_id...")
                    conn.execute(text("""
                        ALTER TABLE avatars 
                        ADD CONSTRAINT fk_avatars_training_request 
                        FOREIGN KEY (training_request_id) 
                        REFERENCES training_requests(id)
                    """))
                    conn.commit()
                    print("[OK] Added foreign key constraint")
                except Exception as e:
                    print(f"[WARN] Warning: Could not add foreign key constraint: {e}")
                    print("  (This is OK if training_requests table doesn't exist yet)")
                    conn.rollback()
            except Exception as e:
                print(f"[ERROR] Error adding training_request_id: {e}")
                conn.rollback()
        else:
            print("[OK] training_request_id column already exists")

def main():
    """메인 함수"""
    print("=" * 60)
    print("TrainingRequest Table & Avatar Fields Migration")
    print("=" * 60)
    print()
    
    # 1. TrainingRequest 테이블 생성
    create_training_request_table()
    print()
    
    # 2. Avatar 테이블에 필드 추가
    add_avatar_fields()
    print()
    
    # 최종 확인
    inspector = inspect(engine)
    final_tables = inspector.get_table_names()
    print("=" * 60)
    print(f"Total tables: {len(final_tables)}")
    print("=" * 60)
    
    if 'training_requests' in final_tables:
        columns = inspector.get_columns('training_requests')
        print(f"\ntraining_requests table columns:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
    
    if 'avatars' in final_tables:
        columns = inspector.get_columns('avatars')
        print(f"\navatars table columns:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")

if __name__ == '__main__':
    main()
