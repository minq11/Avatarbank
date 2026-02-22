#!/usr/bin/env python3
"""
Add age column to avatars and training_requests tables.

Usage:
    cd backend
    python migrations/add_avatar_and_training_request_age.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def add_columns() -> None:
    with engine.begin() as connection:
        for table, col, sql in [
            ("avatars", "age", "ADD COLUMN age INTEGER"),
            ("training_requests", "age", "ADD COLUMN age INTEGER"),
        ]:
            try:
                connection.execute(text(f"ALTER TABLE {table} {sql}"))
            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    pass
                else:
                    raise


if __name__ == "__main__":
    add_columns()
    print("Done: added age column to avatars and training_requests (if missing).")
