"""
테스트 공통 설비.

왜 SQLite 인가: 돈이 걸린 로직(크레딧 차감·적립, 결제 멱등성)의 회귀를 막는 것이
목적이고, 그 로직은 조건부 UPDATE 한 방으로 되어 있어 SQLite 에서도 같은 의미로
동작한다. Postgres 컨테이너를 띄우지 않고도 `make test` 한 번으로 돌 수 있는
편이 실제로 돌려지는 테스트가 된다.

주의: SQLite 로 검증할 수 없는 것도 있다. 동시 트랜잭션의 실제 잠금 동작,
JSONB 연산자, ON CONFLICT 세부 동작은 Postgres 에서만 확인된다. 그런 걸
검증하려면 별도로 Postgres 를 띄워야 한다.
"""

import os

import pytest

# app.config 는 임포트 시점에 환경변수를 읽는다. 테스트가 실제 운영 값을
# 집어가지 않도록 먼저 못 박는다.
os.environ.setdefault("DATABASE_URL", "postgresql://u:p@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("TRANSLATE_PROVIDER", "none")

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import Base  # noqa: E402
from app.models import User  # noqa: E402


# 모델이 Postgres JSONB 를 쓰므로 SQLite 에서는 JSON 으로 렌더링되게 해준다.
# 검증 대상은 잔액·주문 상태 전이지 컬럼 타입이 아니다.
@compiles(JSONB, "sqlite")
def _jsonb_on_sqlite(type_, compiler, **kw):  # noqa: ANN001, ANN201
    return "JSON"


@pytest.fixture()
def db():
    """
    테스트 하나당 새 인메모리 DB. 테스트 간 상태가 새지 않는다.

    StaticPool + check_same_thread=False 인 이유: FastAPI TestClient 는 앱을
    다른 스레드에서 돌린다. 기본 설정이면 인메모리 DB 는 연결마다 별개이고
    SQLite 연결은 만든 스레드에만 묶여 있어서, 엔드포인트 테스트가
    "SQLite objects created in a thread can only be used in that same thread"
    로 죽는다. 연결 하나를 모든 스레드가 공유하게 고정한다.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def user(db):
    """잔액 0 으로 시작하는 사용자."""
    u = User(
        email="tester@example.com",
        nickname="tester",
        password_hash="not-a-real-hash",
        role="influencer",
        credit_balance=0,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def make_user(db):
    """여러 사용자가 필요한 테스트용 팩토리."""

    def _make(email: str, nickname: str, credit_balance: int = 0) -> User:
        u = User(
            email=email,
            nickname=nickname,
            password_hash="not-a-real-hash",
            role="influencer",
            credit_balance=credit_balance,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u

    return _make
