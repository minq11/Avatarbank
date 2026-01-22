#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# SQLite를 사용한 간단한 연결 테스트
def test_sqlite_connection():
    try:
        # SQLite 엔진 생성 (메모리 DB 사용)
        engine = create_engine("sqlite:///:memory:", echo=False)

        # 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"[SUCCESS] SQLite 연결 성공! 결과: {row[0]}")

        # 세션 테스트
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 'Hello World' as message"))
            row = result.fetchone()
            print(f"[SUCCESS] SQLite 세션 성공! 메시지: {row[0]}")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"[ERROR] SQLite 연결 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("SQLite 데이터베이스 연결 테스트 중...")
    success = test_sqlite_connection()
    if success:
        print("\n[INFO] 현재 PostgreSQL 연결 문제:")
        print("- psycopg2-binary 패키지가 PostgreSQL 개발 라이브러리와 호환되지 않음")
        print("- Python 3.14가 일부 패키지와 호환되지 않음")
        print("\n[SOLUTION] 해결 방법:")
        print("1. PostgreSQL 설치 및 환경 설정")
        print("2. Python 3.13 이하 버전 사용")
        print("3. Docker를 사용한 개발 환경 구축")
    sys.exit(0 if success else 1)