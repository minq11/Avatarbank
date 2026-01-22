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

### 0. Python 버전 확인

**권장 Python 버전: 3.11 ~ 3.13**

현재 프로젝트는 Python 3.11 ~ 3.13을 권장합니다. Python 3.14는 일부 패키지(pydantic-core 등)와 호환성 문제가 있을 수 있습니다.

```bash
python --version
```

Python 3.14를 사용하는 경우:
- Python 3.13 이하 버전으로 가상환경을 생성하거나
- 마이그레이션 스크립트만 실행하는 경우 최소 패키지만 설치하세요 (아래 참고)

### 1. 가상환경 생성 및 활성화

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 NeonDB 연결 정보를 입력하세요:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

**NeonDB URL 찾는 방법:**
1. NeonDB 콘솔 접속
2. 프로젝트 선택
3. **Connection Details** 탭 클릭
4. **Connection string** 복사

### 3. 의존성 설치

가상환경이 활성화된 상태에서:

#### 방법 1: 전체 패키지 설치 (권장 - Python 3.11~3.13)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 방법 2: 마이그레이션만 필요한 경우 (최소 패키지)

마이그레이션 스크립트만 실행하는 경우, 다음 패키지만 설치하면 됩니다:

```bash
pip install --upgrade pip
pip install sqlalchemy psycopg2-binary python-dotenv bcrypt passlib
```

**필수 패키지:**
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL 드라이버
- `python-dotenv` - 환경 변수 로드
- `bcrypt` - 비밀번호 해싱
- `passlib[bcrypt]` - 비밀번호 유틸리티

**참고:** 전체 애플리케이션을 실행하려면 `requirements.txt`의 모든 패키지가 필요합니다.

### 4. 데이터베이스 테이블 생성

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

#### 방법 3: 인증 필드 추가 (기존 테이블 업데이트)

기존에 테이블을 생성한 경우, 인증 기능을 위해 email과 password_hash 필드를 추가해야 합니다:

```bash
cd backend
python migrations/add_auth_fields.py
```

**주의:** 이 스크립트는 기존 사용자에게 임시 이메일을 부여합니다. 실제 운영에서는 기존 사용자에게 이메일 인증을 요청해야 합니다.

### 5. 생성 확인

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

## 💡 가상환경 사용 팁

### 가상환경 비활성화
```bash
deactivate
```

### 가상환경 재활성화
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

### 가상환경 삭제
```bash
# 가상환경 비활성화 후
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

**⚠️ 중요:** 마이그레이션 스크립트는 **반드시 가상환경이 활성화된 상태**에서 실행해야 합니다.

## ⚠️ 주의사항

### 1. 가상환경 사용
- 마이그레이션 실행 전에 가상환경이 활성화되어 있는지 확인하세요
- 가상환경이 활성화되지 않으면 패키지 버전 충돌이나 모듈을 찾을 수 없는 오류가 발생할 수 있습니다

### 2. 프로덕션 환경

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

### Python 3.14 호환성 문제

```
ERROR: Failed building wheel for pydantic-core
```

**해결:**
1. Python 3.13 이하 버전 사용 권장
2. 또는 마이그레이션만 필요한 경우 최소 패키지만 설치:
   ```bash
   pip install sqlalchemy psycopg2-binary python-dotenv bcrypt passlib
   ```
3. 가상환경에서 Python 버전 확인:
   ```bash
   python --version
   ```

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