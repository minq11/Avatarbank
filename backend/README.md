## Avatarbank Backend (MVP 스켈레톤)

이 디렉터리는 `projectdesign.md`를 기반으로 한 **FastAPI + Celery + PostgreSQL + Redis** 백엔드의 1차 스켈레톤입니다.

### 구성

- `app/config.py`  
  - 환경변수/설정 관리 (`DATABASE_URL`, `REDIS_URL`, `S3_BUCKET`, `COMFYUI_BASE_URL` 등)
- `app/db.py`  
  - SQLAlchemy 세션/베이스 정의
- `app/models.py`  
  - 설계서의 DB 테이블 일부(`users`, `avatars`, `generations`, `transactions`, `tasks`, `error_logs`, `payment_webhooks`)에 대한 ORM 모델
- `app/schemas.py`  
  - Pydantic 스키마 (토큰, Generation 생성/응답)
- `app/celery_app.py`  
  - Celery 인스턴스 정의
- `app/tasks.py`  
  - 이미지 생성 Celery 태스크 스켈레톤 (`run_generation_task`)
- `app/main.py`  
  - FastAPI 엔트리포인트
  - `/health`
  - `/generations` (생성 요청, 크레딧 선차감 + Celery 태스크 enqueue)
  - `/generations/{id}` (상태 조회)

### 데이터베이스 마이그레이션

**새 환경에서 처음 설정할 때:**

1. 프로젝트 루트에 `.env` 파일 생성:
```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
JWT_SECRET_KEY=your-secret-key-here
```

2. 테이블 생성:
```bash
cd backend
python migrations/create_tables.py
```

**기존 테이블이 있는 경우 (인증 필드 추가):**
```bash
cd backend
python migrations/add_auth_fields.py
```

자세한 가이드는 [`migrations/README.md`](migrations/README.md)를 참고하세요.

### 인증 API

로그인, 회원가입, JWT 토큰 관리 기능이 구현되어 있습니다.

**주요 엔드포인트:**
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - Access Token 갱신
- `GET /auth/me` - 현재 사용자 정보

자세한 API 문서는 [`API_AUTH.md`](API_AUTH.md)를 참고하세요.

### 로컬 실행 (예시)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Celery Worker:

```bash
cd backend
celery -A app.celery_app.celery_app worker --loglevel=info
```

> 현재 ComfyUI/RunPods 연동, S3 업로드, 인증 등은 **스켈레톤/TODO**로 남겨져 있으며,  
> 추후 `projectdesign.md`의 세부 정책에 맞춰 단계적으로 구현할 예정이다.


