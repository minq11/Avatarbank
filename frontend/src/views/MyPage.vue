<template>
  <section class="mypage-section">
    <div v-if="!authStore.isLoggedIn" class="auth-required">
      <p>내 페이지를 이용하려면 로그인해 주세요.</p>
      <RouterLink to="/" class="btn-primary">홈으로</RouterLink>
    </div>
    <div v-else class="container">
      <h2 class="page-title">계정 관리</h2>
      <p class="page-desc">계정 정보를 관리하세요.</p>

      <!-- Nickname Change -->
      <div class="card">
        <h3 class="card-title">닉네임 변경</h3>
        <form class="form" @submit.prevent="handleNicknameSubmit">
          <div class="form-group">
            <label class="form-label">현재 닉네임</label>
            <input
              :value="authStore.user?.nickname"
              type="text"
              class="form-input"
              readonly
              disabled
            />
          </div>
          <div class="form-group">
            <label class="form-label">새 닉네임</label>
            <input
              v-model="nicknameForm.newNickname"
              type="text"
              class="form-input"
              placeholder="새 닉네임을 입력하세요"
              maxlength="50"
              required
            />
          </div>
          <button
            type="submit"
            class="btn primary"
            :disabled="nicknameForm.loading || !nicknameForm.newNickname.trim()"
          >
            {{ nicknameForm.loading ? "변경 중…" : "닉네임 변경" }}
          </button>
          <p v-if="nicknameForm.message" class="form-message" :class="nicknameForm.error ? 'error' : 'success'">
            {{ nicknameForm.message }}
          </p>
        </form>
      </div>

      <!-- Password Change -->
      <div class="card">
        <h3 class="card-title">비밀번호 변경</h3>
        <form class="form" @submit.prevent="handlePasswordSubmit">
          <div class="form-group">
            <label class="form-label">현재 비밀번호</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              class="form-input"
              placeholder="현재 비밀번호를 입력하세요"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">새 비밀번호</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              class="form-input"
              placeholder="새 비밀번호 (6자 이상)"
              minlength="6"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">새 비밀번호 확인</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              class="form-input"
              placeholder="새 비밀번호를 다시 입력하세요"
              required
            />
          </div>
          <button
            type="submit"
            class="btn primary"
            :disabled="passwordForm.loading || !canSubmitPassword"
          >
            {{ passwordForm.loading ? "변경 중…" : "비밀번호 변경" }}
          </button>
          <p v-if="passwordForm.message" class="form-message" :class="passwordForm.error ? 'error' : 'success'">
            {{ passwordForm.message }}
          </p>
        </form>
      </div>

      <!--
        회원 탈퇴. 개인정보처리방침 5항이 약속한 파기를 실제로 실행하는 곳이다.
        되돌릴 수 없으므로 (1) 접힌 상태로 두고 (2) 무엇이 사라지는지 숫자로
        보여주고 (3) 확인 문구를 입력받는다.
      -->
      <div class="card danger-card">
        <h3 class="card-title">회원 탈퇴</h3>

        <p class="danger-lead">
          계정과 함께 아바타, 학습에 쓴 사진, 생성한 이미지가 모두 파기됩니다.
          <strong>되돌릴 수 없습니다.</strong>
        </p>

        <button v-if="!deleteForm.open" type="button" class="btn ghost-danger" @click="openDelete">
          탈퇴 절차 진행
        </button>

        <div v-else class="danger-body">
          <div v-if="deleteForm.loadingPreview" class="danger-loading">확인 중…</div>

          <template v-else>
            <ul v-if="deleteForm.summary" class="danger-list">
              <li>
                내 아바타 <strong>{{ deleteForm.summary.avatars }}개</strong> — 학습 사진과
                함께 파기
              </li>
              <li>
                생성한 이미지 <strong>{{ deleteForm.summary.generations }}장</strong> —
                프롬프트까지 삭제
              </li>
              <li v-if="deleteForm.summary.redeem_codes > 0">
                공유 중인 링크 <strong>{{ deleteForm.summary.redeem_codes }}개</strong> —
                즉시 사용 중단
              </li>
              <li :class="{ 'danger-highlight': deleteForm.summary.forfeited_credits > 0 }">
                남은 크레딧
                <strong>{{ deleteForm.summary.forfeited_credits }}개</strong> — 소멸되며
                환불되지 않습니다
              </li>
            </ul>

            <p v-if="hasCreditsLeft" class="danger-note">
              환불을 원하시면 탈퇴 전에
              <RouterLink to="/support" class="danger-link">고객지원</RouterLink>으로
              요청해 주세요. 미사용 크레딧은 원결제 수단으로 환불됩니다.
            </p>

            <p class="danger-note">
              전자상거래법에 따라 <strong>결제·환불 기록은 5년간</strong>, 고객 문의 기록은
              3년간 보관됩니다. 그 외 개인정보는 즉시 파기됩니다.
              (<RouterLink to="/privacy" class="danger-link">개인정보처리방침</RouterLink>)
            </p>

            <div class="form-group">
              <label class="form-label">
                확인을 위해 <strong>{{ DELETE_PHRASE }}</strong> 를 입력해 주세요
              </label>
              <input
                v-model="deleteForm.confirm"
                type="text"
                class="form-input"
                :placeholder="DELETE_PHRASE"
                autocomplete="off"
              />
            </div>

            <div class="danger-actions">
              <button
                type="button"
                class="btn danger"
                :disabled="deleteForm.loading || !canDelete"
                @click="handleDelete"
              >
                {{ deleteForm.loading ? "처리 중…" : "탈퇴하기" }}
              </button>
              <button type="button" class="btn subtle" :disabled="deleteForm.loading" @click="closeDelete">
                취소
              </button>
            </div>
          </template>

          <p v-if="deleteForm.message" class="form-message error">{{ deleteForm.message }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import {
  ACCOUNT_DELETE_PHRASE,
  accountApi,
  authApi,
  type AccountDeletionSummary,
} from "@/services/api";

const authStore = useAuthStore();
const router = useRouter();
const DELETE_PHRASE = ACCOUNT_DELETE_PHRASE;

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

const deleteForm = reactive({
  open: false,
  loadingPreview: false,
  loading: false,
  confirm: "",
  message: "",
  summary: null as AccountDeletionSummary | null,
});

const hasCreditsLeft = computed(() => (deleteForm.summary?.forfeited_credits ?? 0) > 0);
const canDelete = computed(() => deleteForm.confirm.trim() === DELETE_PHRASE);

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
    nicknameForm.message = "닉네임이 변경되었어요.";
    nicknameForm.newNickname = "";
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    nicknameForm.message = msg ?? "닉네임 변경에 실패했어요.";
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
    passwordForm.message = "비밀번호가 변경되었어요.";
    passwordForm.currentPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    passwordForm.message = msg ?? "비밀번호 변경에 실패했어요.";
    passwordForm.error = true;
  } finally {
    passwordForm.loading = false;
  }
}

/** 탈퇴 절차를 펼치고, 무엇이 사라지는지 서버에서 받아온다. */
async function openDelete() {
  deleteForm.open = true;
  deleteForm.message = "";
  deleteForm.loadingPreview = true;
  try {
    deleteForm.summary = await accountApi.deletionPreview();
  } catch {
    // 미리보기를 못 받아도 탈퇴 자체는 진행할 수 있어야 한다.
    // 숫자만 비고 확인 문구 입력은 그대로 뜬다.
    deleteForm.summary = null;
  } finally {
    deleteForm.loadingPreview = false;
  }
}

function closeDelete() {
  deleteForm.open = false;
  deleteForm.confirm = "";
  deleteForm.message = "";
}

async function handleDelete() {
  if (!canDelete.value) return;
  deleteForm.loading = true;
  deleteForm.message = "";
  try {
    await accountApi.delete(deleteForm.confirm.trim());
    // 서버에서 계정이 비활성화됐으므로 남아 있는 토큰은 이제 403 을 받는다.
    // 화면에 로그인 상태가 남아 있으면 클릭마다 오류가 나므로 즉시 비운다.
    authStore.logout();
    router.push({ path: "/", query: { goodbye: "1" } });
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    deleteForm.message = msg ?? "탈퇴 처리에 실패했어요. 잠시 후 다시 시도해 주세요.";
  } finally {
    deleteForm.loading = false;
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
  color: #0d0d0f;
  margin-bottom: 0.5rem;
}

.page-desc {
  font-size: 1rem;
  color: #6e6e77;
  margin-bottom: 2.5rem;
}

.card {
  background: #ffffff;
  border: 1px solid #e6e6ea;
  border-radius: 1rem;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0d0d0f;
  margin-bottom: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #3a3a42;
  margin-bottom: 0.4rem;
}

.form-input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  color: #0d0d0f;
}

.form-input:focus {
  outline: none;
  border-color: #e24e12;
  box-shadow: 0 0 0 2px rgba(226, 78, 18, 0.2);
}

.form-input:disabled {
  background: #fafafa;
  color: #6e6e77;
  cursor: not-allowed;
}

.btn.primary {
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.btn.primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}

.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 회원 탈퇴 — 되돌릴 수 없는 동작이라 다른 카드와 눈에 띄게 구분한다 */
.danger-card {
  border-color: #f0d2cb;
  background: #fffaf8;
}

.danger-lead {
  font-size: 0.925rem;
  line-height: 1.7;
  color: #6e6e77;
  margin: 0 0 1.1rem;
}

.danger-lead strong {
  color: #b91c1c;
}

.danger-body {
  margin-top: 0.25rem;
}

.danger-loading {
  font-size: 0.9rem;
  color: #6e6e77;
  padding: 0.5rem 0;
}

.danger-list {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
  font-size: 0.9rem;
  line-height: 1.85;
  color: #3a3a42;
}

.danger-highlight {
  color: #b91c1c;
}

.danger-note {
  font-size: 0.825rem;
  line-height: 1.75;
  color: #6e6e77;
  margin: 0 0 0.9rem;
  padding-left: 0.1rem;
}

.danger-link {
  color: #e24e12;
  text-decoration: underline;
}

.danger-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.btn.ghost-danger,
.btn.danger,
.btn.subtle {
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}

.btn.ghost-danger {
  color: #b91c1c;
  background: transparent;
  border: 1px solid #e7bdb5;
}

.btn.ghost-danger:hover {
  background: #fdeeea;
}

.btn.danger {
  color: #ffffff;
  background: #b91c1c;
  border: none;
}

.btn.danger:hover:not(:disabled) {
  background: #991b1b;
}

.btn.subtle {
  color: #3a3a42;
  background: #ffffff;
  border: 1px solid #d2d2d9;
}

.btn.subtle:hover:not(:disabled) {
  background: #f4f4f5;
}

.btn.danger:disabled,
.btn.subtle:disabled {
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
  color: #6e6e77;
  margin-bottom: 1.5rem;
}

.auth-required .btn-primary {
  display: inline-block;
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border-radius: 0.5rem;
  text-decoration: none;
  transition: box-shadow 0.2s;
}

.auth-required .btn-primary:hover {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}
</style>
