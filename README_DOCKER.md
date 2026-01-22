# 🐳 Docker 빠른 시작 가이드

## 로컬 개발 환경

### 1단계: 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 NeonDB와 Upstash Redis 연결 정보를 설정하세요:

```env
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
REDIS_URL=redis://default:password@xxx-xxx.upstash.io:6379
```

### 2단계: Docker 실행

```bash
# 전체 스택 실행 (프론트엔드 + 백엔드 + DB + Redis)
docker-compose up --build

# 또는 백그라운드 실행
docker-compose up -d --build
```

**✅ 실행 완료 후 브라우저에서 접속하세요:**
- 🌐 **프론트엔드**: http://localhost:3000
- 🔧 **백엔드 API**: http://localhost:8000
- 📚 **API 문서**: http://localhost:8000/docs

### 3단계: 데이터베이스 마이그레이션

```bash
docker-compose exec backend python migrations/create_tables.py
```

### 4단계: 접속 확인

**✅ Docker Compose 실행 후 다음 URL로 접속하세요:**

- 🌐 **프론트엔드**: http://localhost:3000
- 🔧 **백엔드 API**: http://localhost:8000
- 📚 **API 문서**: http://localhost:8000/docs

## 운영 환경

### 1단계: 환경 변수 설정

`.env` 파일에 운영 환경 변수를 설정하세요.

### 2단계: 빌드 및 실행

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3단계: 마이그레이션

```bash
docker-compose -f docker-compose.prod.yml exec backend python migrations/create_tables.py
```

## 유용한 명령어

```bash
# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart backend

# 컨테이너 접속
docker-compose exec backend bash
```

자세한 내용은 [DOCKER.md](./DOCKER.md)를 참고하세요.
