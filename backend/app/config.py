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

    # Storage (S3 또는 로컬)
    STORAGE_TYPE: str = "local"  # "s3" 또는 "local"
    
    # S3 설정
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"  # 기본값: NeonDB와 같은 리전
    S3_BUCKET: str = "avatarbank-storage-prd"  # 기본값: 프로덕션 버킷
    
    # 로컬 스토리지 설정
    UPLOAD_DIR: str = "/app/uploads"  # 로컬 저장 디렉토리
    STATIC_URL_PREFIX: str = "/static"  # 정적 파일 URL 접두사

    # RunPods / ComfyUI
    COMFYUI_BASE_URL: str = "http://runpods-comfyui:8188"
    RUNPODS_HMAC_SECRET: str = "CHANGE_ME_RUNPODS_HMAC"

    # fal.ai (text-to-image)
    FAL_API_KEY: str = ""
    FAL_API_BASE_URL: str = "https://fal.run"
    FAL_SYNC_BASE_URL: str = "https://fal.run"
    FAL_MODEL: str = "fal-ai/z-image/turbo"
    FAL_SUBPATH: str = "lora"

    # Admin
    ADMIN_EMAIL_WHITELIST: str = ""

    class Config:
        env_file = [".env", "../.env"]  # 현재 디렉토리 또는 상위 디렉토리에서 .env 파일 찾기
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


