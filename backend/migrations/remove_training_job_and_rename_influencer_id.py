#!/usr/bin/env python3
"""
TrainingJob 테이블 제거 및 avatars.influencer_id를 user_id로 변경

사용법:
    cd backend
    python migrations/remove_training_job_and_rename_influencer_id.py
"""

import sys
from pathlib import Path

# backend 폴더를 Python 경로에 추가
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError

def remove_training_job_table():
    """TrainingJob 테이블 제거"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'training_jobs' in existing_tables:
        try:
            print("Dropping training_jobs table...")
            with engine.connect() as conn:
                # 외래키 제약조건이 있을 수 있으므로 먼저 확인
                conn.execute(text("DROP TABLE IF EXISTS training_jobs CASCADE"))
                conn.commit()
            print("[OK] Dropped training_jobs table")
        except Exception as e:
            print(f"[ERROR] Error dropping training_jobs table: {e}")
    else:
        print("[OK] training_jobs table does not exist")

def rename_influencer_id_to_user_id():
    """avatars 테이블의 influencer_id를 user_id로 변경"""
    inspector = inspect(engine)
    
    # avatars 테이블이 존재하는지 확인
    if 'avatars' not in inspector.get_table_names():
        print("[ERROR] avatars table does not exist. Please create it first.")
        return
    
    # 기존 컬럼 확인
    existing_columns = [col['name'] for col in inspector.get_columns('avatars')]
    
    with engine.connect() as conn:
        # influencer_id가 있고 user_id가 없는 경우만 변경
        if 'influencer_id' in existing_columns and 'user_id' not in existing_columns:
            try:
                print("Renaming influencer_id to user_id in avatars table...")
                
                # PostgreSQL에서 컬럼명 변경
                conn.execute(text("ALTER TABLE avatars RENAME COLUMN influencer_id TO user_id"))
                conn.commit()
                print("[OK] Renamed influencer_id to user_id")
            except Exception as e:
                print(f"[ERROR] Error renaming column: {e}")
                conn.rollback()
        elif 'user_id' in existing_columns:
            print("[OK] user_id column already exists")
            # influencer_id가 남아있으면 제거
            if 'influencer_id' in existing_columns:
                try:
                    print("Removing old influencer_id column...")
                    conn.execute(text("ALTER TABLE avatars DROP COLUMN influencer_id"))
                    conn.commit()
                    print("[OK] Removed old influencer_id column")
                except Exception as e:
                    print(f"[WARN] Could not remove influencer_id: {e}")
                    conn.rollback()
        else:
            print("[WARN] Neither influencer_id nor user_id found in avatars table")

def main():
    """메인 함수"""
    print("=" * 60)
    print("Remove TrainingJob & Rename influencer_id to user_id")
    print("=" * 60)
    print()
    
    # 1. TrainingJob 테이블 제거
    remove_training_job_table()
    print()
    
    # 2. influencer_id를 user_id로 변경
    rename_influencer_id_to_user_id()
    print()
    
    # 최종 확인
    inspector = inspect(engine)
    final_tables = inspector.get_table_names()
    print("=" * 60)
    print(f"Total tables: {len(final_tables)}")
    print("=" * 60)
    
    if 'avatars' in final_tables:
        columns = inspector.get_columns('avatars')
        print(f"\navatars table columns:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        
        # influencer_id가 남아있는지 확인
        column_names = [col['name'] for col in columns]
        if 'influencer_id' in column_names:
            print("\n[WARN] influencer_id column still exists!")
        if 'user_id' in column_names:
            print("[OK] user_id column exists")

if __name__ == '__main__':
    main()
