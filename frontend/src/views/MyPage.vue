<template>
  <section class="mypage-section">
    <div v-if="!authStore.isLoggedIn" class="auth-required">
      <p>Please log in to access My Page.</p>
      <RouterLink to="/" class="btn-primary">Go to Home</RouterLink>
    </div>
    <div v-else class="container">
      <h2 class="page-title">My Page</h2>
      <p class="page-desc">Manage your account settings.</p>

      <!-- Nickname Change -->
      <div class="card">
        <h3 class="card-title">Change Nickname</h3>
        <form class="form" @submit.prevent="handleNicknameSubmit">
          <div class="form-group">
            <label class="form-label">Current nickname</label>
            <input
              :value="authStore.user?.nickname"
              type="text"
              class="form-input"
              readonly
              disabled
            />
          </div>
          <div class="form-group">
            <label class="form-label">New nickname</label>
            <input
              v-model="nicknameForm.newNickname"
              type="text"
              class="form-input"
              placeholder="Enter new nickname"
              maxlength="50"
              required
            />
          </div>
          <button
            type="submit"
            class="btn primary"
            :disabled="nicknameForm.loading || !nicknameForm.newNickname.trim()"
          >
            {{ nicknameForm.loading ? "Updating..." : "Update Nickname" }}
          </button>
          <p v-if="nicknameForm.message" class="form-message" :class="nicknameForm.error ? 'error' : 'success'">
            {{ nicknameForm.message }}
          </p>
        </form>
      </div>

      <!-- Password Change -->
      <div class="card">
        <h3 class="card-title">Change Password</h3>
        <form class="form" @submit.prevent="handlePasswordSubmit">
          <div class="form-group">
            <label class="form-label">Current password</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              class="form-input"
              placeholder="Enter current password"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">New password</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              class="form-input"
              placeholder="Enter new password (min 6 characters)"
              minlength="6"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">Confirm new password</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              class="form-input"
              placeholder="Confirm new password"
              required
            />
          </div>
          <button
            type="submit"
            class="btn primary"
            :disabled="passwordForm.loading || !canSubmitPassword"
          >
            {{ passwordForm.loading ? "Updating..." : "Update Password" }}
          </button>
          <p v-if="passwordForm.message" class="form-message" :class="passwordForm.error ? 'error' : 'success'">
            {{ passwordForm.message }}
          </p>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { authApi } from "@/services/api";

const authStore = useAuthStore();

const nicknameForm = reactive({
  newNickname: "",
  loading: false,
  message: "",
  error: false,
});

const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
  loading: false,
  message: "",
  error: false,
});

const canSubmitPassword = computed(
  () =>
    passwordForm.currentPassword &&
    passwordForm.newPassword.length >= 6 &&
    passwordForm.newPassword === passwordForm.confirmPassword
);

async function handleNicknameSubmit() {
  const nickname = nicknameForm.newNickname.trim();
  if (!nickname) return;
  nicknameForm.loading = true;
  nicknameForm.message = "";
  nicknameForm.error = false;
  try {
    const user = await authApi.changeNickname({ nickname });
    authStore.setUser(user);
    nicknameForm.message = "Nickname updated successfully.";
    nicknameForm.newNickname = "";
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    nicknameForm.message = msg ?? "Failed to update nickname.";
    nicknameForm.error = true;
  } finally {
    nicknameForm.loading = false;
  }
}

async function handlePasswordSubmit() {
  if (!canSubmitPassword.value) return;
  passwordForm.loading = true;
  passwordForm.message = "";
  passwordForm.error = false;
  try {
    await authApi.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
    });
    passwordForm.message = "Password updated successfully.";
    passwordForm.currentPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    passwordForm.message = msg ?? "Failed to update password.";
    passwordForm.error = true;
  } finally {
    passwordForm.loading = false;
  }
}
</script>

<style scoped>
.mypage-section {
  padding: 3rem 0 5rem;
  background: #ffffff;
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 560px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.page-desc {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 2.5rem;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.4rem;
}

.form-input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  color: #111827;
}

.form-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

.form-input:disabled {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.btn.primary {
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.btn.primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-message {
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.form-message.success {
  color: #059669;
}

.form-message.error {
  color: #dc2626;
}

.auth-required {
  max-width: 560px;
  margin: 0 auto;
  padding: 4rem 1.5rem;
  text-align: center;
}

.auth-required p {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.auth-required .btn-primary {
  display: inline-block;
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border-radius: 0.5rem;
  text-decoration: none;
  transition: box-shadow 0.2s;
}

.auth-required .btn-primary:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}
</style>
