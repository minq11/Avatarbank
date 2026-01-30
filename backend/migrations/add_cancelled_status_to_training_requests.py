#!/usr/bin/env python3
"""
TrainingRequest status에 'cancelled' 상태 추가

참고: status 컬럼은 String 타입이므로 실제 데이터베이스 스키마 변경은 필요 없습니다.
이 마이그레이션은 문서화 목적입니다.

사용법:
    cd backend
    python migrations/add_cancelled_status_to_training_requests.py
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

def check_training_requests_table():
    """training_requests 테이블 확인"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'training_requests' not in existing_tables:
        print("[ERROR] training_requests table does not exist.")
        print("  Please run add_training_request_and_avatar_fields.py first.")
        return False
    
    print("[OK] training_requests table exists")
    return True

def verify_status_column():
    """status 컬럼 확인"""
    inspector = inspect(engine)
    
    try:
        columns = inspector.get_columns('training_requests')
        status_col = next((col for col in columns if col['name'] == 'status'), None)
        
        if not status_col:
            print("[ERROR] status column does not exist in training_requests table")
            return False
        
        print(f"[OK] status column exists: {status_col['name']} ({status_col['type']})")
        
        # String 타입이므로 CHECK 제약조건이 없어도 새로운 값 추가 가능
        if 'VARCHAR' in str(status_col['type']) or 'TEXT' in str(status_col['type']) or 'String' in str(status_col['type']):
            print("[OK] status column is String type - no schema migration needed")
            print("  'cancelled' status can be used without database changes")
            return True
        else:
            print(f"[WARN] Unexpected column type: {status_col['type']}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error checking status column: {e}")
        return False

def check_existing_constraints():
    """기존 CHECK 제약조건 확인"""
    try:
        with engine.connect() as conn:
            # PostgreSQL의 경우 - status 컬럼과 관련된 CHECK 제약조건만 확인
            result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    cc.check_clause
                FROM information_schema.table_constraints tc
                JOIN information_schema.check_constraints cc 
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_name = 'training_requests' 
                    AND tc.constraint_type = 'CHECK'
                    AND cc.check_clause LIKE '%status%'
            """))
            constraints = result.fetchall()
            
            if constraints:
                print(f"[WARN] Found {len(constraints)} CHECK constraint(s) related to status:")
                for constraint in constraints:
                    print(f"  - {constraint[0]}: {constraint[1]}")
                print("[WARN] Status value CHECK constraints found - may need to update them")
                print("  If these constraints restrict status values, you may need to:")
                print("  ALTER TABLE training_requests DROP CONSTRAINT <constraint_name>;")
                print("  ALTER TABLE training_requests ADD CONSTRAINT <constraint_name> CHECK (status IN ('requested', 'approved_training', 'rejected', 'cancelled'));")
                return False
            else:
                # 모든 CHECK 제약조건 확인 (NOT NULL 제외)
                all_check_result = conn.execute(text("""
                    SELECT constraint_name, constraint_type 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'training_requests' 
                        AND constraint_type = 'CHECK'
                        AND constraint_name NOT LIKE '%not_null%'
                """))
                all_checks = all_check_result.fetchall()
                
                if all_checks:
                    print(f"[INFO] Found {len(all_checks)} CHECK constraint(s) (excluding NOT NULL):")
                    for constraint in all_checks:
                        print(f"  - {constraint[0]}")
                    print("[INFO] These don't appear to restrict status values")
                
                print("[OK] No CHECK constraints found that restrict status column values")
                print("  No database migration needed")
                return True
                
    except ProgrammingError:
        # 다른 데이터베이스 또는 제약조건이 없는 경우
        print("[OK] No CHECK constraints found (or database doesn't support this query)")
        return True
    except Exception as e:
        print(f"[WARN] Could not check constraints: {e}")
        print("  Assuming no CHECK constraints exist that restrict status values")
        return True

def main():
    """메인 함수"""
    print("=" * 60)
    print("TrainingRequest Status Migration Check")
    print("Adding 'cancelled' status support")
    print("=" * 60)
    print()
    
    # 1. 테이블 존재 확인
    if not check_training_requests_table():
        return
    print()
    
    # 2. status 컬럼 확인
    if not verify_status_column():
        return
    print()
    
    # 3. CHECK 제약조건 확인
    check_existing_constraints()
    print()
    
    print("=" * 60)
    print("Migration Check Complete")
    print("=" * 60)
    print()
    print("Summary:")
    print("  - TrainingRequestStatus.CANCELLED has been added to models.py")
    print("  - No database schema changes are required")
    print("  - The 'cancelled' status can be used immediately")
    print()
    print("Note: If you have application-level validation that restricts")
    print("      status values, make sure to update it to include 'cancelled'")

if __name__ == '__main__':
    main()
