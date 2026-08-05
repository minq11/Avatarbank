"""
마이그레이션 002 — 룩(템플릿) 개념 제거.

변경:
  1. generations.template_id    삭제
  2. redeem_codes.template_id   삭제
  3. generation_templates 테이블 삭제

리딤 코드는 이제 특정 룩에 묶이지 않고, 팬은 항상 프롬프트를 직접 입력한다.

멱등: 이미 반영된 항목은 건너뛴다. 여러 번 돌려도 안전.

실행:
    backend/venv/Scripts/python.exe backend/migrations/002_remove_templates.py
    # 계획만 확인
    backend/venv/Scripts/python.exe backend/migrations/002_remove_templates.py --dry-run
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv  # noqa: E402

for candidate in (REPO_ROOT / ".env", BACKEND_DIR / ".env"):
    if candidate.exists():
        load_dotenv(candidate, override=False)
        break

from sqlalchemy import create_engine, text  # noqa: E402

from app.config import settings  # noqa: E402

DROP_COLUMNS = [
    ("generations", "template_id"),
    ("redeem_codes", "template_id"),
]
DROP_TABLES = ["generation_templates"]


def database_url() -> str:
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


def column_exists(conn, table: str, column: str) -> bool:
    return bool(
        conn.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :t AND column_name = :c"
            ),
            {"t": table, "c": column},
        ).scalar()
    )


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    url = database_url()
    host = url.split("@")[-1].split("/")[0] if "@" in url else url
    print(f"대상 DB: {host}")
    print(f"모드: {'DRY RUN (변경 없음)' if dry_run else '적용'}\n")

    engine = create_engine(url)
    applied, skipped = 0, 0

    with engine.begin() as conn:
        # 안전장치: 지워질 데이터가 남아 있으면 알린다.
        for table, column in DROP_COLUMNS:
            if table_exists(conn, table) and column_exists(conn, table, column):
                n = conn.execute(
                    text(f'SELECT count(*) FROM "{table}" WHERE "{column}" IS NOT NULL')
                ).scalar()
                if n:
                    print(f"  [주의] {table}.{column} 에 값이 있는 행 {n}건 — 삭제됩니다")

        for table in DROP_TABLES:
            if table_exists(conn, table):
                n = conn.execute(text(f'SELECT count(*) FROM "{table}"')).scalar()
                if n:
                    print(f"  [주의] {table} 에 {n}행 — 테이블과 함께 삭제됩니다")

        for table, column in DROP_COLUMNS:
            if not table_exists(conn, table):
                print(f"  [건너뜀] {table}.{column} — 테이블 없음")
                skipped += 1
                continue
            if not column_exists(conn, table, column):
                print(f"  [건너뜀] {table}.{column} — 이미 제거됨")
                skipped += 1
                continue
            sql = f'ALTER TABLE "{table}" DROP COLUMN "{column}"'
            print(f"  [삭제]   {sql}")
            if not dry_run:
                conn.execute(text(sql))
            applied += 1

        for table in DROP_TABLES:
            if not table_exists(conn, table):
                print(f"  [건너뜀] {table} — 이미 없음")
                skipped += 1
                continue
            sql = f'DROP TABLE "{table}"'
            print(f"  [삭제]   {sql}")
            if not dry_run:
                conn.execute(text(sql))
            applied += 1

    print(f"\n완료 — 적용 {applied}건, 건너뜀 {skipped}건")
    if dry_run and applied:
        print("실제 적용하려면 --dry-run 없이 다시 실행하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
