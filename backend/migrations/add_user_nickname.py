#!/usr/bin/env python3
"""
Add nickname column to users table.

Usage:
    cd backend
    python migrations/add_user_nickname.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Add backend folder to Python path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def add_nickname_column() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS nickname VARCHAR"
            )
        )
        connection.execute(
            text(
                "UPDATE users SET nickname = email "
                "WHERE nickname IS NULL"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE users "
                "ALTER COLUMN nickname SET NOT NULL"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_users_nickname ON users (nickname)"
            )
        )


if __name__ == "__main__":
    add_nickname_column()
    print("Done: added users.nickname column (if missing).")
