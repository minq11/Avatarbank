# 인증 API 가이드

## 📋 개요

Avatarbank 백엔드의 인증 시스템은 JWT (JSON Web Token) 기반으로 동작합니다.

- **Access Token**: 1시간 유효, API 요청 시 사용
- **Refresh Token**: 7일 유효, Access Token 갱신 시 사용

## 🔐 API 엔드포인트

### 1. 회원가입

**POST** `/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "buyer",  // "buyer" 또는 "influencer"
  "locale": "en"    // "en", "ko", "ja"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "buyer",
  "locale": "en",
  "credit_balance": 0
}
```

**에러:**
- `400`: 이메일이 이미 등록됨

---

### 2. 로그인

**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer",
    "locale": "en",
    "credit_balance": 0
  }
}
```

**에러:**
- `401`: 이메일 또는 비밀번호가 잘못됨

---

### 3. Access Token 갱신

**POST** `/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**에러:**
- `401`: Refresh Token이 유효하지 않음

---

### 4. 현재 사용자 정보 조회

**GET** `/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "buyer",
  "locale": "en",
  "credit_balance": 0
}
```

**에러:**
- `401`: 인증 토큰이 없거나 유효하지 않음
- `403`: 계정이 비활성화됨

---

## 🔒 인증이 필요한 API

다음 API들은 `Authorization: Bearer <access_token>` 헤더가 필요합니다:

- `POST /generations` - 이미지 생성 요청
- `GET /auth/me` - 현재 사용자 정보

**예시:**
```bash
curl -X POST "http://localhost:8000/generations" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": 1, "prompt": "a beautiful landscape", ...}'
```

---

## 🛠️ 개발 환경 설정

### 1. 환경 변수

`.env` 파일에 JWT 시크릿 키 설정:

```env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. 데이터베이스 마이그레이션

기존 테이블이 있다면 인증 필드를 추가:

```bash
cd backend
python migrations/add_auth_fields.py
```

새로 시작하는 경우:

```bash
cd backend
python migrations/create_tables.py
```

---

## 📝 사용 예시

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# 회원가입
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "test@example.com",
        "password": "password123",
        "role": "buyer"
    }
)
print(response.json())

# 로그인
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test@example.com",
        "password": "password123"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# 인증이 필요한 API 호출
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(response.json())
```

### cURL

```bash
# 회원가입
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","role":"buyer"}'

# 로그인
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 사용자 정보 조회
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

---

## ⚠️ 보안 주의사항

1. **비밀번호**: 최소 8자 이상 권장
2. **HTTPS**: 프로덕션에서는 반드시 HTTPS 사용
3. **토큰 저장**: 
   - Access Token: 메모리 또는 안전한 스토리지
   - Refresh Token: HTTP-only 쿠키 권장 (향후 구현)
4. **JWT_SECRET_KEY**: 강력한 랜덤 문자열 사용, 환경 변수로 관리

---

## 🔗 관련 파일

- `backend/app/auth.py` - 인증 유틸리티 함수
- `backend/app/dependencies.py` - 인증 의존성
- `backend/app/models.py` - User 모델
- `backend/app/schemas.py` - 인증 스키마
- `backend/app/main.py` - API 엔드포인트