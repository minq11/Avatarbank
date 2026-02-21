#!/usr/bin/env python3
"""
Add negative_prompt, image_size, num_inference_steps to generations table.

Usage:
    cd backend
    python migrations/add_generation_detail_fields.py
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
            ("negative_prompt", "ADD COLUMN IF NOT EXISTS negative_prompt TEXT"),
            ("image_size", "ADD COLUMN IF NOT EXISTS image_size VARCHAR"),
            ("num_inference_steps", "ADD COLUMN IF NOT EXISTS num_inference_steps INTEGER"),
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
    print("Done: added generations.negative_prompt, image_size, num_inference_steps (if missing).")
