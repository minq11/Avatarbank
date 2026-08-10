from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 기본 서비스 설정
    PROJECT_NAME: str = "AvatarBank API"
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

    # S3 스토리지 (업로드 전부 S3)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "avatarbank-storage-prd"
    # 참고: local_storage.py는 미사용. 필요 시 UPLOAD_DIR/STATIC_URL_PREFIX 추가

    # RunPods / ComfyUI
    COMFYUI_BASE_URL: str = "http://runpods-comfyui:8188"
    RUNPODS_HMAC_SECRET: str = "CHANGE_ME_RUNPODS_HMAC"

    # fal.ai (text-to-image)
    FAL_API_KEY: str = ""
    FAL_API_BASE_URL: str = "https://fal.run"
    FAL_SYNC_BASE_URL: str = "https://fal.run"
    FAL_MODEL: str = "fal-ai/z-image/turbo"
    # image-to-image + LoRA 엔드포인트
    FAL_SUBPATH: str = "image-to-image/lora"
    # fal 결과 이미지 안전 검사. 현재 끔 — 켜도 입력 이미지 거절(fal 422)에는
    # 영향이 없고 결과만 폐기해서 실효가 없었다. UI 스위치 없이 여기서만 결정한다.
    # False 면 has_nsfw_concepts 기반 결과 폐기 로직도 함께 비활성화된다.
    FAL_ENABLE_SAFETY_CHECKER: bool = False

    # Admin
    ADMIN_EMAIL_WHITELIST: str = ""

    # 구글 로그인 (Google Identity Services)
    # GCP 콘솔 → OAuth 클라이언트 ID(웹). 비어 있으면 구글 로그인 버튼이 숨겨진다.
    # 클라이언트 ID 는 공개돼도 되는 값이라 프론트에 그대로 내려간다 (/auth/config).
    GOOGLE_CLIENT_ID: str = ""

    # CORS: 기본 localhost 외 추가 허용 오리진 (콤마 구분, 운영 도메인 등)
    # 예: "https://avatarbank.example.com,https://www.avatarbank.example.com"
    CORS_EXTRA_ORIGINS: str = ""

    # ------------------------------------------------------------------
    # 크레딧 / 결제 (토스페이먼츠)
    # ------------------------------------------------------------------
    # 1 크레딧 = 이미지 1장. 구독제는 제거했다.
    # 가입 축하 무료 크레딧. 생성 원가가 장당 10원대라 체험 유도용으로 지급한다.
    SIGNUP_BONUS_CREDITS: int = 10
    # 크리에이터가 동시에 활성화할 수 있는 리딤 코드 수 (플랜 한도를 대체하는 고정값).
    MAX_ACTIVE_REDEEM_CODES: int = 500

    # 토스페이먼츠. 테스트 키(test_ck_*, test_sk_*)로 심사 전에도 개발 가능.
    # 시크릿 키는 절대 프론트로 내보내지 말 것 — 승인 API 는 서버에서만 호출한다.
    TOSS_CLIENT_KEY: str = ""
    TOSS_SECRET_KEY: str = ""
    TOSS_API_BASE_URL: str = "https://api.tosspayments.com"
    # 결제 완료/실패 후 돌아올 프론트 주소 (결제창에 넘긴다)
    PAYMENT_SUCCESS_URL: str = "http://localhost:5173/payments/success"
    PAYMENT_FAIL_URL: str = "http://localhost:5173/payments/fail"

    # 공개 리딤 엔드포인트(/r/*) 레이트리밋 — IP당 분당 요청 수. 0 = 비활성.
    # 리딤 생성은 크리에이터 쿼터를 소모하므로 조회보다 훨씬 낮게 잡는다.
    REDEEM_INFO_RATE_LIMIT_PER_MINUTE: int = 30
    REDEEM_GENERATE_RATE_LIMIT_PER_MINUTE: int = 6

    # 고객 문의 메일 (고객지원 폼 접수 알림 + 관리자 답장 발송)
    # Gmail 사용 시: SMTP_HOST=smtp.gmail.com / SMTP_PORT=587 / SMTP_USER=발신 계정 /
    # SMTP_PASSWORD=앱 비밀번호(2단계 인증 후 발급). 미설정이면 메일 발송만 건너뛰고
    # 문의는 DB 에 그대로 저장된다 (관리자 페이지에서 확인 가능).
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM: str = ""  # 비우면 SMTP_USER 사용
    # 새 문의 접수 알림을 받을 내부 주소
    INQUIRY_NOTIFY_EMAIL: str = "gooddonutsyh@gmail.com"
    # 공개 문의 접수 엔드포인트 — IP당 분당 요청 수. 0 = 비활성.
    INQUIRY_RATE_LIMIT_PER_MINUTE: int = 3

    # 아바타 preview 로컬 복사 (frontend assets 또는 서빙용 디렉터리)
    # 설정 시 PUT /my/avatars/{id} preview 업로드 시 여기에도 저장하고, GET /static/preview_image/{id}.png 로 서빙
    PREVIEW_LOCAL_DIR: str = ""

    class Config:
        env_file = [".env", "../.env"]  # 현재 디렉토리 또는 상위 디렉토리에서 .env 파일 찾기
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


