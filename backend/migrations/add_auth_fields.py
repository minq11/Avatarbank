#!/usr/bin/env python3
"""
인증 필드 추가 마이그레이션 스크립트
User 테이블에 email, password_hash 컬럼 추가

사용법:
    cd backend
    python migrations/add_auth_fields.py
"""

import sys
from pathlib import Path

# backend 폴더를 Python 경로에 추가
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db import engine


def add_auth_fields():
    """User 테이블에 email, password_hash 컬럼 추가"""
    print("인증 필드 추가 시작...")

    with engine.connect() as conn:
        try:
            # email 컬럼 추가 (unique, not null, index)
            print("email 컬럼 추가 중...")
            conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS email VARCHAR UNIQUE;
                    CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
                    """
                )
            )

            # password_hash 컬럼 추가
            print("password_hash 컬럼 추가 중...")
            conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS password_hash VARCHAR;
                    """
                )
            )

            # 기존 사용자가 있다면 임시 이메일과 비밀번호 설정
            # 주의: 실제 운영에서는 기존 사용자에게 이메일 인증을 요청하고
            #       비밀번호 재설정을 요청해야 합니다.
            #       이 임시 비밀번호는 "temp_password_123"을 해싱한 것입니다.
            #       (실제 사용 시에는 반드시 변경해야 함)
            from app.auth import get_password_hash
            
            temp_password_hash = get_password_hash("temp_password_123")
            conn.execute(
                text(
                    """
                    UPDATE users 
                    SET email = 'user_' || id || '@temp.local',
                        password_hash = :password_hash
                    WHERE email IS NULL;
                    """
                ),
                {"password_hash": temp_password_hash}
            )

            # email을 NOT NULL로 변경
            conn.execute(
                text(
                    """
                    ALTER TABLE users 
                    ALTER COLUMN email SET NOT NULL;
                    ALTER TABLE users 
                    ALTER COLUMN password_hash SET NOT NULL;
                    """
                )
            )

            conn.commit()
            print("인증 필드 추가 완료!")

        except Exception as e:
            conn.rollback()
            print(f"오류 발생: {e}")
            raise


if __name__ == "__main__":
    add_auth_fields()