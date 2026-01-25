from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


# NeonDB 연결 설정 개선
# pool_recycle: 연결을 주기적으로 재사용하여 SSL 연결 끊김 방지
# pool_pre_ping: 연결 전에 ping을 보내서 유효한 연결인지 확인
# connect_args: SSL 연결 안정성 향상
engine = create_engine(
    settings.DATABASE_URL.unicode_string(),
    pool_pre_ping=True,
    pool_recycle=300,  # 5분마다 연결 재사용
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require",
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


