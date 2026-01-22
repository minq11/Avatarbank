# 데이터베이스 마이그레이션 가이드

이 폴더는 Avatarbank 프로젝트의 데이터베이스 마이그레이션 관련 스크립트와 가이드를 포함합니다.

## 📁 폴더 구조

```
backend/
├── migrations/              # 마이그레이션 스크립트
│   ├── README.md           # 이 파일
│   ├── QUICKSTART.md       # 빠른 시작 가이드
│   ├── create_tables.py    # 모든 테이블 생성 스크립트
│   └── create_missing_tables.py  # 누락된 테이블만 생성
└── app/                    # 애플리케이션 코드
    ├── models.py           # 데이터베이스 모델
    ├── db.py               # 데이터베이스 연결
    └── config.py           # 환경 변수 설정
```

## 🚀 새 환경에서 데이터베이스 설정하기

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 NeonDB 연결 정보를 입력하세요:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

**NeonDB URL 찾는 방법:**
1. NeonDB 콘솔 접속
2. 프로젝트 선택
3. **Connection Details** 탭 클릭
4. **Connection string** 복사

### 2. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

필수 패키지:
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL 드라이버

### 3. 데이터베이스 테이블 생성

#### 방법 1: 직접 생성 (권장 - 초기 설정)

```bash
cd backend
python migrations/create_tables.py
```

이 스크립트는:
- ✅ 모든 테이블을 자동으로 생성
- ✅ 이미 존재하는 테이블은 건너뜀
- ✅ 외래키 관계를 자동으로 처리

**생성되는 테이블:**
- `users` - 사용자
- `avatars` - 아바타
- `generations` - 이미지 생성 기록
- `tasks` - 작업 관리
- `transactions` - 트랜잭션
- `error_logs` - 에러 로그
- `payment_webhooks` - 결제 웹훅
- `training_jobs` - 학습 작업
- `audit_logs` - 감사 로그
- `shared_generations` - 공유 생성
- `likes` - 좋아요
- `bookmarks` - 북마크
- `payout_requests` - 환전 요청

#### 방법 2: 누락된 테이블만 생성

일부 테이블이 누락된 경우:

```bash
cd backend
python migrations/create_missing_tables.py
```

### 4. 생성 확인

테이블이 제대로 생성되었는지 확인:

```bash
cd backend
python -c "from app.db import engine; from sqlalchemy import inspect; inspector = inspect(engine); tables = inspector.get_table_names(); print('생성된 테이블:', sorted(tables))"
```

또는 NeonDB 콘솔에서 직접 확인:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

## ⚠️ 주의사항

### 1. 프로덕션 환경

- 프로덕션에서 테이블 생성 전에 **반드시 백업**을 수행하세요
- 스키마 변경 시 신중하게 진행하세요

### 2. 환경 변수

- `.env` 파일은 **절대 Git에 커밋하지 마세요**
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요
- 각 환경(개발/스테이징/프로덕션)마다 별도의 `.env` 파일을 사용하세요

### 3. 데이터 손실 방지

- 테이블 삭제 전에 데이터 백업
- `downgrade` 명령어는 신중하게 사용
- 프로덕션에서는 `checkfirst=True` 옵션 사용

## 🐛 문제 해결

### 연결 오류

```
psycopg2.OperationalError: connection to server failed
```

**해결:**
1. `.env` 파일의 `DATABASE_URL` 확인
2. NeonDB 콘솔에서 연결 정보 확인
3. 방화벽/네트워크 설정 확인

### 테이블이 생성되지 않음

**해결:**
1. 데이터베이스 권한 확인
2. 스크립트 실행 위치 확인 (`backend/` 폴더에서 실행)
3. 에러 메시지 확인

### 외래키 제약조건 오류

```
psycopg2.errors.UndefinedTable: relation "xxx" does not exist
```

**해결:**
- `create_tables.py`를 사용하면 자동으로 순서가 처리됩니다
- 수동으로 생성하는 경우 참조되는 테이블을 먼저 생성하세요

## 📚 추가 리소스

- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [NeonDB 문서](https://neon.tech/docs/)

## 🔗 관련 파일

- `backend/app/models.py` - 데이터베이스 모델 정의
- `backend/app/db.py` - 데이터베이스 연결 설정
- `backend/app/config.py` - 환경 변수 설정