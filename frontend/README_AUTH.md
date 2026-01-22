# 프론트엔드 인증 가이드

## 📋 구현된 기능

- ✅ 로그인/회원가입 모달
- ✅ JWT 토큰 관리 (Access Token + Refresh Token)
- ✅ 자동 토큰 갱신
- ✅ 인증 상태 관리 (Pinia Store)
- ✅ 로그아웃 기능

## 🏗️ 구조

```
frontend/src/
├── components/
│   └── AuthModal.vue          # 로그인/회원가입 모달
├── services/
│   └── api.ts                 # API 서비스 (axios 인스턴스)
├── stores/
│   └── auth.ts                # 인증 상태 관리 (Pinia)
└── App.vue                    # 메인 앱 (모달 연결)
```

## 🔧 사용 방법

### 1. 환경 변수 설정 (선택사항)

프로덕션 환경에서 API URL을 변경하려면 `.env` 파일 생성:

```env
VITE_API_BASE_URL=https://api.avatarbank.com
```

개발 환경에서는 Vite proxy가 자동으로 `/api`를 `http://localhost:8000`으로 프록시합니다.

### 2. 백엔드 서버 실행

```bash
cd backend
uvicorn app.main:app --reload
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm run dev
```

## 📝 주요 기능

### 인증 Store 사용

```typescript
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();

// 로그인
await authStore.login("user@example.com", "password123");

// 회원가입
await authStore.register("user@example.com", "password123", "buyer");

// 로그아웃
authStore.logout();

// 사용자 정보 가져오기
await authStore.fetchUser();

// 상태 확인
const isLoggedIn = authStore.isLoggedIn;
const user = authStore.user;
const creditBalance = authStore.creditBalance;
```

### API 호출

인증이 필요한 API 호출은 자동으로 Access Token이 헤더에 추가됩니다:

```typescript
import { api } from "./services/api";

// 자동으로 Authorization 헤더 추가됨
const response = await api.get("/generations");
```

### 모달 열기

```vue
<script setup>
import { ref } from "vue";
import AuthModal from "./components/AuthModal.vue";

const showModal = ref(false);
const modalMode = ref<"login" | "register">("login");
</script>

<template>
  <AuthModal
    :is-open="showModal"
    :initial-mode="modalMode"
    @close="showModal = false"
  />
</template>
```

## 🔐 토큰 관리

- **Access Token**: `localStorage`에 저장, 1시간 유효
- **Refresh Token**: `localStorage`에 저장, 7일 유효
- **자동 갱신**: API 호출 시 401 에러 발생 시 자동으로 Refresh Token으로 갱신 시도

## 🎨 UI/UX

- 모달 오버레이 클릭 시 닫기
- ESC 키로 닫기 (향후 추가 가능)
- 로딩 상태 표시
- 에러 메시지 표시
- 로그인/회원가입 모드 전환

## 🐛 문제 해결

### CORS 오류

백엔드에서 CORS 설정이 필요합니다:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 토큰이 저장되지 않음

브라우저 개발자 도구에서 `localStorage` 확인:
- `access_token`
- `refresh_token`

### API 호출 실패

1. 백엔드 서버가 실행 중인지 확인
2. 네트워크 탭에서 요청/응답 확인
3. 콘솔 에러 확인

## 🔗 관련 파일

- `backend/API_AUTH.md` - 백엔드 인증 API 문서
- `backend/app/main.py` - 인증 엔드포인트
- `frontend/src/stores/auth.ts` - 인증 상태 관리
- `frontend/src/services/api.ts` - API 서비스
