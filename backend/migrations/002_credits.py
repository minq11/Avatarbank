"""
마이그레이션 002 — 구독(쿼터) → 장당 크레딧 전환.

변경:
  1. credit_packs / credit_orders 테이블 생성 (create_all 로 만들어지지만 여기서도 보장)
  2. 크레딧 팩 시드 (30/100/300/1,000장)
  3. subscriptions.quota_remaining → users.credit_balance 이관
     - 남은 쿼터를 그대로 크레딧으로 얹어준다. 구독 중이던 사용자가 손해 보지 않게.
     - 이관분은 transactions 에 type='adjust' 로 남긴다.
  4. 가입 보너스 소급: 크레딧이 0이고 거래 이력이 전혀 없는 기존 사용자에게 신규 가입과
     동일한 무료 크레딧을 지급한다.

plans / subscriptions 테이블은 DROP 하지 않는다 — 롤백 여지를 남긴다.

멱등: reference_id 로 이미 이관한 사용자를 건너뛴다. 여러 번 돌려도 중복 적립되지 않는다.

실행:
    backend/venv/Scripts/python.exe backend/migrations/002_credits.py
    # 실제 적용 없이 계획만 보려면
    backend/venv/Scripts/python.exe backend/migrations/002_credits.py --dry-run
"""

import os
import sys
from pathlib import Path

# Windows 기본 콘솔 코드페이지(cp949)는 em dash 등을 못 찍고 죽는다.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

# app.config 의 env_file 은 CWD 상대 경로라서, 어느 디렉터리에서 실행하든 같은 DB 를
# 보도록 저장소 루트의 .env 를 명시적으로 먼저 로드한다.
from dotenv import load_dotenv  # noqa: E402

for candidate in (REPO_ROOT / ".env", BACKEND_DIR / ".env"):
    if candidate.exists():
        load_dotenv(candidate, override=False)
        break

from sqlalchemy import create_engine, text  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402
import app.models  # noqa: E402,F401  — Base.metadata 에 모델 등록

# payments.py 와 같은 정의를 쓴다 (fastapi 의존 없이 값만 복사).
CREDIT_PACKS = [
    ("pack30", "30장", 30, 3_000, 0),
    ("pack100", "100장", 100, 9_000, 1),
    ("pack300", "300장", 300, 24_000, 2),
    ("pack1000", "1,000장", 1000, 70_000, 3),
]

MIGRATION_REF = "migration-002-quota"
SIGNUP_REF = "migration-002-signup"


def database_url() -> str:
    """.env 로 주입된 값 우선, 없으면 settings 기본값."""
    return os.environ.get("DATABASE_URL") or str(settings.DATABASE_URL)


def table_exists(conn, table: str) -> bool:
    return bool(
        conn.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = :t"
            ),
            {"t": table},
        ).scalar()
    )


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    url = database_url()
    host = url.split("@")[-1].split("/")[0] if "@" in url else url
    print(f"대상 DB: {host}")
    engine = create_engine(url)
    bonus = max(0, int(settings.SIGNUP_BONUS_CREDITS))

    with engine.begin() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        print(f"연결됨: {str(version).split(',')[0]}")
        print(f"모드: {'DRY RUN (변경 없음)' if dry_run else '적용'}\n")

        # 1) 새 테이블 --------------------------------------------------------
        print("[1] 크레딧 테이블")
        for table in ("credit_packs", "credit_orders"):
            if table_exists(conn, table):
                print(f"  [건너뜀] {table} — 이미 있음")
            elif dry_run:
                print(f"  [생성]   {table}")
            else:
                Base.metadata.tables[table].create(bind=conn)
                print(f"  [생성]   {table}")

        if dry_run and not table_exists(conn, "credit_packs"):
            # 아래 단계들이 없는 테이블을 읽게 되므로 여기서 멈춘다.
            print("\nDRY RUN: 테이블이 아직 없어 이후 단계는 생략합니다.")
            return 0

        # 2) 팩 시드 ----------------------------------------------------------
        print("\n[2] 크레딧 팩 시드")
        for code, name, credits_, price, order in CREDIT_PACKS:
            exists = conn.execute(
                text("SELECT 1 FROM credit_packs WHERE code = :c"), {"c": code}
            ).scalar()
            if exists:
                print(f"  [건너뜀] {code} — 이미 있음")
                continue
            print(f"  [추가]   {code} — {name} / {price:,}원")
            if not dry_run:
                conn.execute(
                    text(
                        "INSERT INTO credit_packs "
                        "(code, name, credits, price_krw, is_active, sort_order, created_at) "
                        "VALUES (:code, :name, :credits, :price, TRUE, :ord, NOW())"
                    ),
                    {"code": code, "name": name, "credits": credits_, "price": price, "ord": order},
                )

        # 3) 남은 쿼터 이관 ----------------------------------------------------
        print("\n[3] 구독 잔여 쿼터 → 크레딧 이관")
        if not table_exists(conn, "subscriptions"):
            print("  [건너뜀] subscriptions 테이블이 없음")
        else:
            rows = conn.execute(
                text(
                    "SELECT s.user_id, s.quota_remaining "
                    "FROM subscriptions s "
                    "WHERE s.quota_remaining > 0 "
                    "  AND NOT EXISTS ("
                    "    SELECT 1 FROM transactions t "
                    "    WHERE t.user_id = s.user_id AND t.reference_id = :ref"
                    "  )"
                ),
                {"ref": MIGRATION_REF},
            ).fetchall()
            if not rows:
                print("  [건너뜀] 이관할 잔여 쿼터가 없음 (또는 이미 이관됨)")
            for user_id, quota in rows:
                print(f"  [이관]   user {user_id}: +{quota} 크레딧")
                if dry_run:
                    continue
                before = conn.execute(
                    text("SELECT credit_balance FROM users WHERE id = :u"), {"u": user_id}
                ).scalar()
                if before is None:
                    print(f"  [건너뜀] user {user_id} — 사용자 없음")
                    continue
                conn.execute(
                    text(
                        "UPDATE users SET credit_balance = credit_balance + :q WHERE id = :u"
                    ),
                    {"q": quota, "u": user_id},
                )
                conn.execute(
                    text(
                        "INSERT INTO transactions "
                        "(user_id, type, amount, currency, credit_before, credit_after, "
                        " reference_id, created_at) "
                        "VALUES (:u, 'adjust', :q, 'CREDIT', :before, :after, :ref, NOW())"
                    ),
                    {
                        "u": user_id, "q": quota, "before": before,
                        "after": before + quota, "ref": MIGRATION_REF,
                    },
                )

        # 4) 기존 사용자 가입 보너스 소급 ---------------------------------------
        print(f"\n[4] 기존 사용자 가입 보너스 소급 ({bonus}크레딧)")
        if bonus == 0:
            print("  [건너뜀] SIGNUP_BONUS_CREDITS = 0")
        else:
            rows = conn.execute(
                text(
                    "SELECT u.id FROM users u "
                    "WHERE u.credit_balance = 0 "
                    "  AND NOT EXISTS ("
                    "    SELECT 1 FROM transactions t "
                    "    WHERE t.user_id = u.id AND t.currency = 'CREDIT'"
                    "  )"
                )
            ).fetchall()
            if not rows:
                print("  [건너뜀] 대상 사용자 없음")
            for (user_id,) in rows:
                print(f"  [지급]   user {user_id}: +{bonus} 크레딧")
                if dry_run:
                    continue
                conn.execute(
                    text("UPDATE users SET credit_balance = credit_balance + :b WHERE id = :u"),
                    {"b": bonus, "u": user_id},
                )
                conn.execute(
                    text(
                        "INSERT INTO transactions "
                        "(user_id, type, amount, currency, credit_before, credit_after, "
                        " reference_id, created_at) "
                        "VALUES (:u, 'bonus', :b, 'CREDIT', 0, :b, :ref, NOW())"
                    ),
                    {"u": user_id, "b": bonus, "ref": SIGNUP_REF},
                )

    print("\n완료." + ("  (DRY RUN — 실제 변경 없음)" if dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
