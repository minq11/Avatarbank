#!/usr/bin/env python3
"""
Creator Studio 피벗 마이그레이션.

- 신규 테이블 생성: plans, subscriptions, generation_templates, redeem_codes
- generations 컬럼 추가: creator_id, redeem_code_id, template_id, source
- generations.buyer_id NOT NULL 완화 (팬 비회원 생성 허용)
- 기본 요금제 시드

Usage:
    cd backend
    python migrations/add_studio_tables.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import Base, engine, SessionLocal  # noqa: E402
from app import models  # noqa: E402,F401  (테이블 메타데이터 로드)
from app.studio import seed_plans  # noqa: E402


def run() -> None:
    # 1) 신규 테이블 생성 (이미 있으면 무시)
    Base.metadata.create_all(bind=engine)

    # 2) generations 컬럼 추가
    with engine.begin() as conn:
        for sql in [
            "ADD COLUMN creator_id INTEGER",
            "ADD COLUMN redeem_code_id INTEGER",
            "ADD COLUMN template_id INTEGER",
            "ADD COLUMN source VARCHAR",
        ]:
            try:
                conn.execute(text(f"ALTER TABLE generations {sql}"))
            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    pass
                else:
                    raise

        # 3) buyer_id NOT NULL 완화
        try:
            conn.execute(text("ALTER TABLE generations ALTER COLUMN buyer_id DROP NOT NULL"))
        except Exception as e:
            if "does not exist" in str(e).lower() or "already" in str(e).lower():
                pass
            else:
                # SQLite 등 ALTER 미지원 환경은 무시
                print(f"  (buyer_id nullable skip: {e})")

    # 4) 기본 요금제 시드
    db = SessionLocal()
    try:
        seed_plans(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Done: studio tables + generation columns + default plans.")
