<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <button class="modal-close" @click="closeModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>

      <!-- 로그인 폼 -->
      <div v-if="mode === 'login'" class="auth-form">
        <h2 class="form-title">Login</h2>
        <p class="form-subtitle">Welcome back! Please login to your account.</p>

        <form @submit.prevent="handleLogin" class="form">
          <div class="form-group">
            <label for="login-email">Email</label>
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
            <label for="login-password">Password</label>
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
            {{ isLoading ? "Logging in..." : "Login" }}
          </button>

          <p class="form-footer">
            Don't have an account?
            <button type="button" @click="mode = 'register'" class="link-button">
              Sign up
            </button>
          </p>
        </form>
      </div>

      <!-- 회원가입 폼 -->
      <div v-else class="auth-form">
        <h2 class="form-title">Sign Up</h2>
        <p class="form-subtitle">Create a new account to get started.</p>

        <form @submit.prevent="handleRegister" class="form">
          <div class="form-group">
            <label for="register-email">Email</label>
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
            <label for="register-password">Password</label>
            <input
              id="register-password"
              v-model="registerPassword"
              type="password"
              required
              minlength="8"
              placeholder="At least 8 characters"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="register-role">I want to</label>
            <select
              id="register-role"
              v-model="registerRole"
              class="form-input"
            >
              <option value="buyer">Buy images (Buyer)</option>
              <option value="influencer">Sell my avatar (Influencer)</option>
            </select>
          </div>

          <div v-if="registerError" class="error-message">
            {{ registerError }}
          </div>

          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? "Creating account..." : "Sign Up" }}
          </button>

          <p class="form-footer">
            Already have an account?
            <button type="button" @click="mode = 'login'" class="link-button">
              Login
            </button>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useAuthStore } from "../stores/auth";

const props = defineProps<{
  isOpen: boolean;
  initialMode?: "login" | "register";
}>();

const emit = defineEmits<{
  close: [];
}>();

const authStore = useAuthStore();

const mode = ref<"login" | "register">(props.initialMode || "login");
const isLoading = ref(false);
const loginError = ref("");
const registerError = ref("");

// 로그인 폼 데이터
const loginEmail = ref("");
const loginPassword = ref("");

// 회원가입 폼 데이터
const registerEmail = ref("");
const registerPassword = ref("");
const registerRole = ref<"buyer" | "influencer">("buyer");

// 모달이 열릴 때 모드 초기화
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      mode.value = props.initialMode || "login";
      loginError.value = "";
      registerError.value = "";
      loginEmail.value = "";
      loginPassword.value = "";
      registerEmail.value = "";
      registerPassword.value = "";
      registerRole.value = "buyer";
    }
  }
);

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
    closeModal();
  } else {
    loginError.value = result.error || "Login failed";
  }

  isLoading.value = false;
};

const handleRegister = async () => {
  isLoading.value = true;
  registerError.value = "";

  const result = await authStore.register(
    registerEmail.value,
    registerPassword.value,
    registerRole.value
  );

  if (result.success) {
    closeModal();
  } else {
    registerError.value = result.error || "Registration failed";
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
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #111827;
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
  color: #111827;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
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
  color: #374151;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #111827;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(to right, #4f46e5, #6366f1);
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
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
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

.form-footer {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 1rem;
}

.link-button {
  background: none;
  border: none;
  color: #4f46e5;
  font-weight: 500;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  margin-left: 0.25rem;
}

.link-button:hover {
  color: #6366f1;
}
</style>
