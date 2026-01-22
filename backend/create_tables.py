#!/usr/bin/env python3
"""
NeonDB에 직접 테이블 생성 스크립트
Alembic 없이 SQLAlchemy로 직접 테이블 생성
"""

from app.db import engine, Base
# 모든 모델을 import하여 Base.metadata에 등록
import app.models  # 모든 모델이 자동으로 Base.metadata에 등록됨

def create_all_tables():
    """모든 테이블을 생성합니다."""
    print("테이블 생성 시작...")
    
    # 모든 모델을 import하여 Base.metadata에 등록
    # 이미 import했으므로 Base.metadata에 모든 테이블이 포함됨
    
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("모든 테이블 생성 완료!")
        
        # 생성된 테이블 목록 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n생성된 테이블 목록 ({len(tables)}개):")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        raise

if __name__ == '__main__':
    create_all_tables()