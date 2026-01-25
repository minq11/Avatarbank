#!/usr/bin/env python3
"""
Make generations.avatar_id nullable.

Usage:
    cd backend
    python migrations/make_generation_avatar_nullable.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Add backend folder to Python path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def make_avatar_nullable() -> None:
    statement = text("ALTER TABLE generations ALTER COLUMN avatar_id DROP NOT NULL")
    with engine.begin() as connection:
        connection.execute(statement)


if __name__ == "__main__":
    make_avatar_nullable()
    print("Done: generations.avatar_id is now nullable.")
