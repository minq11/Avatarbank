#!/usr/bin/env python3
"""
Avatar name 유저별 유일 제약 추가

- avatars: (user_id, title) UNIQUE
- training_requests: (user_id, avatar_name) UNIQUE

사용법:
    cd backend
    python migrations/add_avatar_name_unique_constraints.py

주의: 중복 데이터가 있으면 제약 추가가 실패합니다. 먼저 중복을 수정한 뒤 실행하세요.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError


def constraint_exists(conn, table: str, name: str) -> bool:
    """PostgreSQL: 제약조건 존재 여부"""
    try:
        r = conn.execute(
            text(
                """
            SELECT 1 FROM information_schema.table_constraints
            WHERE table_name = :t AND constraint_name = :n
            """
            ),
            {"t": table, "n": name},
        )
        return r.fetchone() is not None
    except Exception:
        return False


def check_duplicates_avatars(conn) -> list:
    """avatars 테이블에서 (user_id, title) 중복 조회"""
    r = conn.execute(
        text(
            """
        SELECT user_id, title, COUNT(*) as cnt
        FROM avatars
        GROUP BY user_id, title
        HAVING COUNT(*) > 1
        """
        )
    )
    return r.fetchall()


def check_duplicates_training_requests(conn) -> list:
    """training_requests 테이블에서 (user_id, avatar_name) 중복 조회"""
    r = conn.execute(
        text(
            """
        SELECT user_id, avatar_name, COUNT(*) as cnt
        FROM training_requests
        GROUP BY user_id, avatar_name
        HAVING COUNT(*) > 1
        """
        )
    )
    return r.fetchall()


def main():
    print("=" * 60)
    print("Avatar name unique constraints migration")
    print("=" * 60)

    with engine.connect() as conn:
        # 1) 중복 확인
        dup_av = check_duplicates_avatars(conn)
        dup_tr = check_duplicates_training_requests(conn)
        if dup_av or dup_tr:
            print("\n[ERROR] Duplicate (user_id, name) found. Resolve before adding constraints.")
            if dup_av:
                print("  avatars duplicates:", dup_av)
            if dup_tr:
                print("  training_requests duplicates:", dup_tr)
            return 1

        print("\n[OK] No duplicate (user_id, name) in avatars or training_requests")

        trans = conn.begin()
        try:
            # 2) avatars (user_id, title) UNIQUE
            if not constraint_exists(conn, "avatars", "uq_avatars_user_title"):
                conn.execute(
                    text(
                        "ALTER TABLE avatars ADD CONSTRAINT uq_avatars_user_title UNIQUE (user_id, title)"
                    )
                )
                print("[OK] Added uq_avatars_user_title")
            else:
                print("[OK] uq_avatars_user_title already exists")

            # 3) training_requests (user_id, avatar_name) UNIQUE
            if not constraint_exists(conn, "training_requests", "uq_training_requests_user_avatar_name"):
                conn.execute(
                    text(
                        "ALTER TABLE training_requests ADD CONSTRAINT uq_training_requests_user_avatar_name UNIQUE (user_id, avatar_name)"
                    )
                )
                print("[OK] Added uq_training_requests_user_avatar_name")
            else:
                print("[OK] uq_training_requests_user_avatar_name already exists")

            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"[ERROR] {e}")
            return 1

    print("\nMigration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
