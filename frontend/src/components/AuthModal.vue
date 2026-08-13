<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <button class="modal-close" @click="closeModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>

      <!-- Login Form -->
      <div v-if="mode === 'login'" class="auth-form">
        <h2 class="form-title">로그인</h2>
        <p class="form-subtitle">다시 만나서 반가워요! 계정으로 로그인해 주세요.</p>

        <form @submit.prevent="handleLogin" class="form">
          <div class="form-group">
            <label for="login-email">이메일</label>
            <input
              id="login-email"
              v-model="loginEmail"
              type="email"
              required
              placeholder="your@email.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="login-password">비밀번호</label>
            <input
              id="login-password"
              v-model="loginPassword"
              type="password"
              required
              placeholder="••••••••"
              class="form-input"
            />
          </div>

          <div v-if="loginError" class="error-message">
            {{ loginError }}
          </div>

          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? "로그인 중…" : "로그인" }}
          </button>

          <!-- 구글 로그인 (클라이언트 ID 설정 시에만 표시) -->
          <template v-if="googleReady">
            <div class="divider"><span>또는</span></div>
            <div ref="googleBtnLogin" class="google-btn-slot"></div>
          </template>
          <div v-if="googleError" class="error-message">{{ googleError }}</div>

          <p class="form-footer">
            아직 계정이 없나요?
            <button type="button" @click="mode = 'register'" class="link-button">
              회원가입
            </button>
          </p>
        </form>
      </div>

      <!-- Register Form -->
      <div v-else class="auth-form">
        <h2 class="form-title">회원가입</h2>
        <p class="form-subtitle">
          가입하면 무료 크레딧을 드려요. 바로 아바타를 만들어보세요.
        </p>

        <form @submit.prevent="handleRegister" class="form">
          <div class="form-group">
            <label for="register-nickname">닉네임</label>
            <input
              id="register-nickname"
              v-model="registerNickname"
              type="text"
              required
              minlength="3"
              maxlength="20"
              placeholder="닉네임 (3~20자)"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="register-email">이메일</label>
            <input
              id="register-email"
              v-model="registerEmail"
              type="email"
              required
              placeholder="your@email.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="register-password">비밀번호</label>
            <input
              id="register-password"
              v-model="registerPassword"
              type="password"
              required
              minlength="8"
              placeholder="8자 이상"
              class="form-input"
            />
          </div>

          <div v-if="registerError" class="error-message">
            {{ registerError }}
          </div>

          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? "가입 중…" : "회원가입" }}
          </button>

          <!-- 구글로 바로 가입 -->
          <template v-if="googleReady">
            <div class="divider"><span>또는</span></div>
            <div ref="googleBtnRegister" class="google-btn-slot"></div>
          </template>
          <div v-if="googleError" class="error-message">{{ googleError }}</div>

          <p class="form-footer">
            이미 계정이 있나요?
            <button type="button" @click="mode = 'login'" class="link-button">
              로그인
            </button>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { useAuthStore } from "../stores/auth";
import { authApi } from "../services/api";

const props = defineProps<{
  isOpen: boolean;
  initialMode?: "login" | "register";
}>();

const emit = defineEmits<{
  close: [];
  /** 로그인/가입이 실제로 성공했을 때 (닫기와 구분 — 리다이렉트 트리거용) */
  success: [];
}>();

const authStore = useAuthStore();

const mode = ref<"login" | "register">(props.initialMode || "login");
const isLoading = ref(false);
const loginError = ref("");
const registerError = ref("");

// Login form data
const loginEmail = ref("");
const loginPassword = ref("");

// Register form data
const registerEmail = ref("");
const registerPassword = ref("");
const registerNickname = ref("");

// ---------------------------------------------------------------------------
// 구글 로그인 (Google Identity Services)
// ---------------------------------------------------------------------------
const googleReady = ref(false);
const googleError = ref("");
const googleBtnLogin = ref<HTMLElement | null>(null);
const googleBtnRegister = ref<HTMLElement | null>(null);
let googleClientId: string | null = null; // null = 아직 안 가져옴, "" = 미설정
let googleInitialized = false;

async function fetchGoogleClientId(): Promise<string> {
  if (googleClientId !== null) return googleClientId;
  try {
    const cfg = await authApi.getAuthConfig();
    googleClientId = cfg.google_client_id || "";
  } catch {
    googleClientId = "";
  }
  return googleClientId;
}

async function handleGoogleCredential(response: { credential: string }) {
  googleError.value = "";
  isLoading.value = true;
  const result = await authStore.loginWithGoogle(response.credential);
  isLoading.value = false;
  if (result.success) {
    emit("success");
    closeModal();
  } else {
    googleError.value = result.error || "구글 로그인에 실패했어요.";
  }
}

/** 모달이 열릴 때 구글 버튼을 렌더링 (클라이언트 ID + GIS 스크립트가 있을 때만) */
async function setupGoogleButton() {
  const clientId = await fetchGoogleClientId();
  const gsi = (window as any).google?.accounts?.id;
  if (!clientId || !gsi) {
    googleReady.value = false;
    return;
  }
  if (!googleInitialized) {
    gsi.initialize({ client_id: clientId, callback: handleGoogleCredential });
    googleInitialized = true;
  }
  googleReady.value = true;
  await nextTick();
  // 현재 보이는 폼의 슬롯에만 렌더 (탭 전환 시에도 다시 호출된다)
  const slot = mode.value === "login" ? googleBtnLogin.value : googleBtnRegister.value;
  if (slot) {
    slot.innerHTML = "";
    gsi.renderButton(slot, {
      theme: "outline",
      size: "large",
      width: 320,
      text: mode.value === "login" ? "signin_with" : "signup_with",
      locale: "ko",
    });
  }
}

// Initialize mode when modal opens
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      mode.value = props.initialMode || "login";
      loginError.value = "";
      registerError.value = "";
      googleError.value = "";
      loginEmail.value = "";
      loginPassword.value = "";
      registerNickname.value = "";
      registerEmail.value = "";
      registerPassword.value = "";
      setupGoogleButton();
    }
  }
);

// 로그인 ↔ 가입 탭 전환 시 해당 폼 슬롯에 구글 버튼 다시 렌더
watch(mode, () => {
  if (props.isOpen) setupGoogleButton();
});

const closeModal = () => {
  emit("close");
};

const handleOverlayClick = (e: MouseEvent) => {
  if (e.target === e.currentTarget) {
    closeModal();
  }
};

const handleLogin = async () => {
  isLoading.value = true;
  loginError.value = "";

  const result = await authStore.login(loginEmail.value, loginPassword.value);

  if (result.success) {
    emit("success");
    closeModal();
  } else {
    loginError.value = result.error || "로그인에 실패했어요.";
  }

  isLoading.value = false;
};

const handleRegister = async () => {
  isLoading.value = true;
  registerError.value = "";

  const result = await authStore.register(
    registerEmail.value,
    registerNickname.value,
    registerPassword.value,
    "buyer" // Always register as buyer
  );

  if (result.success) {
    emit("success");
    closeModal();
  } else {
    registerError.value = result.error || "회원가입에 실패했어요.";
  }

  isLoading.value = false;
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  position: relative;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 28rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: none;
  background: #f2f2f4;
  color: #6e6e77;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.modal-close:hover {
  background: #e6e6ea;
  color: #0d0d0f;
}

.modal-close svg {
  width: 1.25rem;
  height: 1.25rem;
}

.auth-form {
  padding: 2.5rem;
}

.form-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0d0d0f;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  font-size: 0.875rem;
  color: #6e6e77;
  margin-bottom: 2rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #3a3a42;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #0d0d0f;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #e24e12;
  box-shadow: 0 0 0 3px rgba(226, 78, 18, 0.1);
}

.form-input::placeholder {
  color: #9a9aa3;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(to right, #e24e12, #e85f26);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  color: #dc2626;
  font-size: 0.875rem;
}

.divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #9a9aa3;
  font-size: 0.8rem;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #e6e6ea;
}

.google-btn-slot {
  display: flex;
  justify-content: center;
  min-height: 44px;
}

.form-footer {
  text-align: center;
  font-size: 0.875rem;
  color: #6e6e77;
  margin-top: 1rem;
}

.link-button {
  background: none;
  border: none;
  color: #e24e12;
  font-weight: 500;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  margin-left: 0.25rem;
}

.link-button:hover {
  color: #e85f26;
}
</style>
