from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 기본 서비스 설정
    PROJECT_NAME: str = "Avatarbank API"
    ENV: str = "local"

    # 데이터베이스 (NeonDB / PostgreSQL)
    DATABASE_URL: AnyUrl = "postgresql://user:password@localhost:5432/avatarbank"

    # Redis / Celery
    REDIS_URL: AnyUrl = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1시간
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # S3
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET: str = "avatarbank-images"

    # RunPods / ComfyUI
    COMFYUI_BASE_URL: str = "http://runpods-comfyui:8188"
    RUNPODS_HMAC_SECRET: str = "CHANGE_ME_RUNPODS_HMAC"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


