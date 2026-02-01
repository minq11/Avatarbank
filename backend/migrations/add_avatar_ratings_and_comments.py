#!/usr/bin/env python3
"""
Add avatar_ratings and avatar_comments tables.

Usage:
    cd backend
    python migrations/add_avatar_ratings_and_comments.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import engine  # noqa: E402


def run() -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS avatar_ratings (
                id SERIAL PRIMARY KEY,
                avatar_id INTEGER NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_up BOOLEAN NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                UNIQUE(avatar_id, user_id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS avatar_comments (
                id SERIAL PRIMARY KEY,
                avatar_id INTEGER NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_avatar_ratings_avatar_id ON avatar_ratings(avatar_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_avatar_ratings_user_id ON avatar_ratings(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_avatar_comments_avatar_id ON avatar_comments(avatar_id)"))


if __name__ == "__main__":
    run()
    print("Done: avatar_ratings and avatar_comments tables created (if missing).")
