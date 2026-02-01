#!/usr/bin/env python3
"""
Add is_shared column to generations table (for Gallery exposure).

Usage:
    cd backend
    python migrations/add_is_shared_to_generations.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def add_is_shared_column() -> None:
    statement = text(
        "ALTER TABLE generations "
        "ADD COLUMN IF NOT EXISTS is_shared BOOLEAN NOT NULL DEFAULT false"
    )
    with engine.begin() as connection:
        connection.execute(statement)


if __name__ == "__main__":
    add_is_shared_column()
    print("Done: added generations.is_shared column (if missing).")
