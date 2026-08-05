"""
마이그레이션 001 — image-to-image 전환.

변경:
  1. generations           + source_image_url (VARCHAR), + strength (DOUBLE PRECISION)
  2. generation_templates  - negative_prompt   (룩에서는 네거티브 프롬프트를 쓰지 않음.
                                                생성 시엔 avatar.negative_prompt 를 그대로 사용)

멱등: information_schema 를 확인해 이미 반영된 항목은 건너뛴다. 여러 번 돌려도 안전.

실행:
    backend/venv/Scripts/python.exe backend/migrations/001_image_to_image.py
    # 실제 적용 없이 계획만 보려면
    backend/venv/Scripts/python.exe backend/migrations/001_image_to_image.py --dry-run
"""

import os
import sys
from pathlib import Path

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


def database_url() -> str:
    """.env 로 주입된 값 우선, 없으면 settings 기본값."""
    return os.environ.get("DATABASE_URL") or str(settings.DATABASE_URL)

ADD_COLUMNS = [
    ("generations", "source_image_url", "VARCHAR"),
    ("generations", "strength", "DOUBLE PRECISION"),
]
DROP_COLUMNS = [
    ("generation_templates", "negative_prompt"),
]


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
    # 자격증명은 출력하지 않는다 (호스트만 표기)
    host = url.split("@")[-1].split("/")[0] if "@" in url else url
    print(f"대상 DB: {host}")
    engine = create_engine(url)
    applied, skipped = 0, 0

    with engine.begin() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        print(f"연결됨: {str(version).split(',')[0]}")
        print(f"모드: {'DRY RUN (변경 없음)' if dry_run else '적용'}\n")

        for table, column, coltype in ADD_COLUMNS:
            if not table_exists(conn, table):
                print(f"  [건너뜀] {table}.{column} — 테이블이 아직 없음 (create_all 이 생성함)")
                skipped += 1
                continue
            if column_exists(conn, table, column):
                print(f"  [건너뜀] {table}.{column} — 이미 있음")
                skipped += 1
                continue
            sql = f'ALTER TABLE "{table}" ADD COLUMN "{column}" {coltype}'
            print(f"  [추가]   {sql}")
            if not dry_run:
                conn.execute(text(sql))
            applied += 1

        for table, column in DROP_COLUMNS:
            if not table_exists(conn, table):
                print(f"  [건너뜀] {table}.{column} — 테이블이 아직 없음")
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

    print(f"\n완료 — 적용 {applied}건, 건너뜀 {skipped}건")
    if dry_run and applied:
        print("실제 적용하려면 --dry-run 없이 다시 실행하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
