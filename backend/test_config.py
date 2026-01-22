#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def test_config():
    try:
        print(f"[INFO] DATABASE_URL: {settings.DATABASE_URL}")
        print(f"[INFO] JWT_SECRET_KEY: {'*' * len(settings.JWT_SECRET_KEY) if settings.JWT_SECRET_KEY else 'NOT SET'}")
        print(f"[INFO] JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
        print(f"[INFO] REDIS_URL: {settings.REDIS_URL}")
        print("[SUCCESS] 환경변수 로드 성공!")
        return True
    except Exception as e:
        print(f"[ERROR] 환경변수 로드 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_config()