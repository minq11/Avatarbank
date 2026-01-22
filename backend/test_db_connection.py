#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import engine, SessionLocal
from sqlalchemy import text

def test_db_connection():
    try:
        # 엔진 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("[SUCCESS] 데이터베이스 연결 성공!")

        # 세션 테스트
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            print("[SUCCESS] 데이터베이스 세션 연결 성공!")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"[ERROR] 데이터베이스 연결 실패: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)