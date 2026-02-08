#!/usr/bin/env python3
"""
Avatar, TrainingRequest 테이블에 deleted_at 컬럼 추가 (논리 삭제용)

사용법:
    cd backend
    python migrations/add_deleted_at_soft_delete.py
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine
from sqlalchemy import inspect, text


def add_deleted_at_if_missing(conn, table: str):
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        print(f"[SKIP] Table {table} does not exist")
        return
    existing = [c["name"] for c in inspector.get_columns(table)]
    if "deleted_at" in existing:
        print(f"[OK] {table}.deleted_at already exists")
        return
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN deleted_at TIMESTAMP"))
        conn.commit()
        print(f"[OK] Added deleted_at to {table}")
    except Exception as e:
        print(f"[ERROR] {table}: {e}")
        conn.rollback()


def main():
    print("Adding deleted_at for soft delete (avatars, training_requests)...")
    with engine.connect() as conn:
        add_deleted_at_if_missing(conn, "avatars")
        add_deleted_at_if_missing(conn, "training_requests")
    print("Done.")


if __name__ == "__main__":
    main()
