# Docker 실행 가이드

이 문서는 Avatarbank 프로젝트를 Docker로 실행하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [로컬 개발 환경](#로컬-개발-환경)
- [운영 환경](#운영-환경)
- [유용한 명령어](#유용한-명령어)
- [문제 해결](#문제-해결)

## 🔧 사전 요구사항

- Docker Desktop 또는 Docker Engine 설치
- Docker Compose 설치 (Docker Desktop에 포함됨)

설치 확인:
```bash
docker --version
docker-compose --version
```

## 🚀 로컬 개발 환경

### 방법 1: 전체 스택 실행 (권장)

**참고**: 로컬 개발 환경은 NeonDB와 Upstash Redis를 사용합니다.

#### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 NeonDB와 Upstash Redis 연결 정보를 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정하세요:

```env
# NeonDB 연결 문자열
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# Upstash Redis 연결 문자열
REDIS_URL=redis://default:password@xxx-xxx.upstash.io:6379
```

**NeonDB 연결 문자열 찾는 방법:**
1. NeonDB 콘솔 접속
2. 프로젝트 선택
3. **Connection Details** 탭 클릭
4. **Connection string** 복사

**Upstash Redis 연결 문자열 찾는 방법:**
1. Upstash 콘솔 접속
2. Redis 데이터베이스 선택
3. **REST API** 또는 **Redis** 탭에서 연결 문자열 복사

#### 2. Docker 이미지 빌드 및 실행

```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

**실행 완료 후 브라우저에서 접속하세요:**
- 🌐 **프론트엔드**: http://localhost:3000
- 🔧 **백엔드 API**: http://localhost:8000
- 📚 **API 문서**: http://localhost:8000/docs

### 방법 2: 개발 모드 (Hot Reload)

코드 변경이 즉시 반영되는 개발 모드입니다.

```bash
# 개발 모드 실행
docker-compose -f docker-compose.dev.yml up --build

# 재시작
docker-compose -f docker-compose.dev.yml restart frontend
docker-compose -f docker-compose.dev.yml restart backend

# 백그라운드 실행
docker-compose -f docker-compose.dev.yml up -d --build
```

**참고**: 개발 모드는 백엔드만 포함하며, 프론트엔드는 로컬에서 `npm run dev`로 실행하는 것을 권장합니다.

### 3. 데이터베이스 마이그레이션

백엔드 컨테이너에서 마이그레이션 실행:

```bash
# 컨테이너 접속
docker-compose exec backend bash

# 마이그레이션 실행
python migrations/create_tables.py
```

또는 한 줄로:

```bash
# 기본 compose 파일 사용 시
docker-compose exec backend python migrations/create_tables.py

# 개발 모드 사용 시
docker-compose -f docker-compose.dev.yml exec backend python migrations/create_tables.py
```

### 4. 접속 확인

**✅ Docker Compose 실행 후 다음 URL로 접속하세요:**

- 🌐 **프론트엔드**: http://localhost:3000
- 🔧 **백엔드 API**: http://localhost:8000
- 📚 **API 문서 (Swagger)**: http://localhost:8000/docs
- 📖 **API 문서 (ReDoc)**: http://localhost:8000/redoc

**외부 서비스:**
- **데이터베이스**: NeonDB (외부 서비스)
- **Redis**: Upstash Redis (외부 서비스)

### 5. 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 6. 서비스 중지

```bash
# 서비스 중지 (컨테이너 유지)
docker-compose stop

# 서비스 중지 및 컨테이너 제거
docker-compose down

# 볼륨까지 제거 (데이터 삭제)
docker-compose down -v
```

## 🌐 운영 환경

### 1. 환경 변수 설정

운영 환경용 `.env` 파일을 생성하고 모든 필수 환경 변수를 설정하세요:

```bash
# .env 파일 생성
cp .env.example .env

# 중요한 설정들:
# - DATABASE_URL (NeonDB 등 실제 데이터베이스)
# - JWT_SECRET_KEY (강력한 비밀키)
# - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# - PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
```

### 2. Docker 이미지 빌드

```bash
# 운영 환경용 빌드
docker-compose -f docker-compose.prod.yml build
```

### 3. 서비스 실행

```bash
# 운영 환경 실행
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. 데이터베이스 마이그레이션

```bash
# 운영 환경 마이그레이션
docker-compose -f docker-compose.prod.yml exec backend python migrations/create_tables.py
```

### 5. 헬스체크 확인

```bash
# 백엔드 헬스체크
curl http://localhost:8000/health

# 프론트엔드 확인
curl http://localhost/
```

## 🛠️ 유용한 명령어

### 컨테이너 관리

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 특정 서비스 재시작
docker-compose restart backend

# 특정 서비스 재빌드 및 재시작
docker-compose up -d --build backend

# 컨테이너 내부 접속
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 이미지 관리

```bash
# 빌드된 이미지 확인
docker images

# 사용하지 않는 이미지 삭제
docker image prune

# 모든 미사용 리소스 정리
docker system prune -a
```

### 볼륨 관리

```bash
# 볼륨 목록 확인
docker volume ls

# 특정 볼륨 삭제
docker volume rm avatarbank_postgres_data
```

### 로그 관리

```bash
# 최근 100줄 로그
docker-compose logs --tail=100 backend

# 특정 시간 이후 로그
docker-compose logs --since 30m backend

# 로그 파일로 저장
docker-compose logs > logs.txt
```

## 🔍 문제 해결

### 포트 충돌

포트가 이미 사용 중인 경우:

```bash
# 포트 사용 확인 (Windows)
netstat -ano | findstr :8000

# docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 호스트:컨테이너
```

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs backend

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재빌드
docker-compose up -d --build --force-recreate
```

### 데이터베이스 연결 오류

```bash
# 환경 변수 확인
docker-compose exec backend env | grep DATABASE_URL

# 백엔드 로그 확인
docker-compose logs backend

# NeonDB 연결 테스트
docker-compose exec backend python -c "from app.db import engine; engine.connect(); print('DB connection OK')"

# Upstash Redis 연결 테스트
docker-compose exec backend python -c "import redis; r = redis.from_url('${REDIS_URL}'); r.ping(); print('Redis connection OK')"
```

**일반적인 문제:**
- `DATABASE_URL`이 올바르게 설정되지 않음
- NeonDB의 IP 허용 목록에 현재 IP가 없음
- Upstash Redis의 연결 문자열 형식이 잘못됨

### 프론트엔드 빌드 오류

```bash
# 캐시 없이 재빌드
docker-compose build --no-cache frontend

# Node 모듈 재설치
docker-compose exec frontend npm ci
```

### 볼륨 권한 문제

```bash
# 볼륨 권한 확인
docker volume inspect avatarbank_postgres_data

# 볼륨 재생성
docker-compose down -v
docker-compose up -d
```

## 📝 환경별 설정 차이

### 로컬 개발 환경 (`docker-compose.yml`)

- ✅ Hot reload 지원 (코드 변경 시 자동 재시작)
- ✅ NeonDB 사용 (외부 데이터베이스)
- ✅ Upstash Redis 사용 (외부 Redis)
- ✅ 개발용 환경 변수
- ✅ 볼륨 마운트로 코드 동기화

### 운영 환경 (`docker-compose.prod.yml`)

- ✅ 최적화된 프로덕션 빌드
- ✅ 자동 재시작 설정
- ✅ 로그 관리
- ✅ 외부 데이터베이스 사용 (NeonDB 등)
- ✅ 환경 변수는 `.env` 파일에서 관리

## 🔐 보안 주의사항

1. **`.env` 파일은 절대 Git에 커밋하지 마세요**
2. 운영 환경에서는 반드시 강력한 `JWT_SECRET_KEY` 사용
3. 데이터베이스 비밀번호는 복잡하게 설정
4. AWS 자격 증명은 IAM 최소 권한 원칙 적용

## 🎯 Makefile 사용 (선택사항)

프로젝트 루트에 `Makefile`이 포함되어 있어 더 간편하게 명령어를 실행할 수 있습니다:

```bash
# 도움말 보기
make help

# 로컬 개발 환경
make build      # 이미지 빌드
make up         # 서비스 시작
make down       # 서비스 중지
make logs       # 로그 확인
make migrate    # 마이그레이션 실행

# 개발 모드
make dev-up     # 개발 모드 시작
make dev-down   # 개발 모드 중지

# 운영 환경
make prod-build # 운영 이미지 빌드
make prod-up    # 운영 서비스 시작
make prod-down  # 운영 서비스 중지

# 유틸리티
make clean      # 모든 리소스 정리
make shell-backend  # 백엔드 컨테이너 접속
```

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
