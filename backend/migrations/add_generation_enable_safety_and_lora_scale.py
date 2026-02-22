#!/usr/bin/env python3
"""
Add enable_safety_checker, lora_scale to generations table.

Usage:
    cd backend
    python migrations/add_generation_enable_safety_and_lora_scale.py
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
        for col, sql in [
            ("enable_safety_checker", "ADD COLUMN enable_safety_checker BOOLEAN"),
            ("lora_scale", "ADD COLUMN lora_scale REAL"),
        ]:
            try:
                connection.execute(text(f"ALTER TABLE generations {sql}"))
            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    pass
                else:
                    raise


if __name__ == "__main__":
    add_columns()
    print("Done: added generations.enable_safety_checker, lora_scale (if missing).")
