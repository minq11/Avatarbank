#!/usr/bin/env python3
"""
Add request_id column to generations table.

Usage:
    cd backend
    python migrations/add_generation_request_id.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Add backend folder to Python path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def add_request_id_column() -> None:
    statement = text(
        "ALTER TABLE generations "
        "ADD COLUMN IF NOT EXISTS request_id VARCHAR"
    )
    with engine.begin() as connection:
        connection.execute(statement)


if __name__ == "__main__":
    add_request_id_column()
    print("Done: added generations.request_id column (if missing).")
