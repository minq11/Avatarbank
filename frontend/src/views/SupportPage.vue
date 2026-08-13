<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>문의하기</h1>
        <p class="doc-lead">
          계정·아바타·생성·링크 무엇이든 물어보세요. 남겨주신 이메일로 답변드립니다.
          로그인하지 않아도 문의할 수 있어요.
        </p>
      </header>

      <!-- 접수 완료 -->
      <section v-if="submitted" class="card success-card">
        <div class="success-icon">✓</div>
        <h2>문의가 접수됐어요</h2>
        <p class="doc-p">
          접수번호는 <strong>#{{ submitted.id }}</strong> 입니다. 담당자가 확인한 뒤
          <strong>{{ form.email }}</strong> 으로 답변드릴게요.
        </p>
        <p v-if="!submitted.email_sent" class="doc-note">
          문의는 정상적으로 접수됐지만 내부 알림 메일 발송이 지연되고 있어요.
          답변이 평소보다 늦어질 수 있는 점 양해 부탁드립니다.
        </p>
        <button class="btn-primary" @click="resetForm">다른 문의 남기기</button>
      </section>

      <template v-else>
        <!-- 문의 폼 -->
        <section class="card">
          <h2>{{ isReport ? "도용·권리침해 신고" : "문의 남기기" }}</h2>
          <p v-if="isReport" class="doc-note report-note">
            내 얼굴이 무단으로 등록됐거나, 부적절한 생성물을 발견하셨다면 여기에 접수해 주세요.
            문제가 되는 <strong>아바타 이름·리딤 링크·이미지 링크</strong>와 상황을 함께 적어주시면
            확인이 빨라져요. 처리 절차는
            <RouterLink to="/content-policy#report" class="doc-link">콘텐츠·초상권 정책</RouterLink>에
            안내돼 있어요.
          </p>

          <form class="inquiry-form" @submit.prevent="submit">
            <div class="form-row inline">
              <div>
                <label for="iq-name">이름</label>
                <input id="iq-name" v-model="form.name" maxlength="60" required />
              </div>
              <div>
                <label for="iq-email">회신받을 이메일</label>
                <input id="iq-email" v-model="form.email" type="email" required />
              </div>
            </div>

            <div class="form-row">
              <label for="iq-category">분류</label>
              <select id="iq-category" v-model="form.category">
                <option v-for="c in categories" :key="c.value" :value="c.value">
                  {{ c.label }}
                </option>
              </select>
            </div>

            <div class="form-row">
              <label for="iq-subject">제목</label>
              <input
                id="iq-subject"
                v-model="form.subject"
                maxlength="150"
                placeholder="무엇에 대한 문의인지 한 줄로 적어주세요"
                required
              />
            </div>

            <div class="form-row">
              <label for="iq-message">내용</label>
              <textarea
                id="iq-message"
                v-model="form.message"
                rows="7"
                maxlength="4000"
                :placeholder="messagePlaceholder"
                required
              ></textarea>
              <p class="muted small char-count">{{ form.message.length }} / 4000</p>
            </div>

            <label class="consent-row">
              <input v-model="form.privacy_consent" type="checkbox" />
              <span>
                <strong>(필수)</strong> 문의 답변을 위해 이름·이메일·문의 내용을 수집하는 데 동의합니다.
                수집된 정보는 접수일로부터 3년간 보관 후 파기됩니다.
                (<RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink>)
              </span>
            </label>

            <p v-if="error" class="form-error">{{ error }}</p>

            <button class="btn-primary" :disabled="submitting || !canSubmit">
              <span v-if="submitting" class="spinner-inline"></span>
              {{ submitting ? "보내는 중…" : "문의 보내기" }}
            </button>
          </form>
        </section>

        <!-- 문의 전 확인 -->
        <section class="card">
          <h2>문의 전에 확인해 보세요</h2>
          <ul class="doc-list">
            <li>
              <strong>아바타 승인이 안 됐어요</strong> — 등록과 학습은 도용 여부 확인 후 진행되며
              2~7일이 걸려요.
            </li>
            <li>
              <strong>생성이 실패했어요</strong> — 실패한 생성은 크레딧이 차감되지 않아요 (이미
              빠졌다면 자동으로 환원돼요). 프롬프트가 안전 필터에 걸렸을 수도 있어요
              (<RouterLink to="/content-policy" class="doc-link">콘텐츠 정책</RouterLink>).
            </li>
            <li>
              <strong>크레딧이 빨리 줄어요</strong> — 팬이 리딤 링크로 만든 이미지도 크리에이터
              크레딧에서 차감돼요. 링크는 언제든 비활성화할 수 있어요.
            </li>
            <li>
              <strong>결제했는데 크레딧이 안 들어왔어요</strong> — 스튜디오에서 잔액과 내역을 먼저
              확인해 주세요. 반영이 늦어지는 경우가 있어요. 그래도 없으면 결제 일시와 금액을 적어
              문의해 주세요. 중복 결제는 되지 않습니다.
            </li>
            <li>
              <strong>사용법이 궁금해요</strong> —
              <RouterLink to="/guide" class="doc-link">크리에이터 가이드</RouterLink>에 아바타 등록부터
              링크 공유까지 정리해 두었어요.
            </li>
          </ul>
        </section>
      </template>

      <footer class="doc-foot">
        <p class="doc-meta">
          <RouterLink to="/terms" class="doc-link">이용약관</RouterLink> ·
          <RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink> ·
          <RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink>
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { inquiriesApi, type InquiryCategory, type InquiryCreateResult } from "../services/api";

const authStore = useAuthStore();
const route = useRoute();

const categories: { value: InquiryCategory; label: string }[] = [
  { value: "account", label: "계정/로그인" },
  { value: "avatar", label: "아바타 등록·학습" },
  { value: "generation", label: "생성/크레딧" },
  { value: "code", label: "리딤 링크" },
  { value: "billing", label: "결제/환불" },
  { value: "report", label: "신고 (도용·권리침해)" },
  { value: "etc", label: "기타" },
];

const form = ref({
  name: "",
  email: "",
  category: "etc" as InquiryCategory,
  subject: "",
  message: "",
  privacy_consent: false,
});

const submitting = ref(false);
const submitted = ref<InquiryCreateResult | null>(null);
const error = ref<string | null>(null);

const isReport = computed(() => form.value.category === "report");

const messagePlaceholder = computed(() =>
  isReport.value
    ? "문제가 되는 아바타 이름·리딤 링크·이미지 링크와 상황을 구체적으로 적어주세요."
    : "상황을 구체적으로 적어주시면 더 빠르게 도와드릴 수 있어요."
);

const canSubmit = computed(
  () =>
    form.value.name.trim() !== "" &&
    form.value.email.trim() !== "" &&
    form.value.subject.trim() !== "" &&
    form.value.message.trim().length >= 5 &&
    form.value.privacy_consent
);

// 로그인 상태면 이름·이메일을 채워 입력을 줄인다.
const prefillFromAuth = () => {
  const user = authStore.user;
  if (!user) return;
  if (!form.value.name) form.value.name = user.nickname || "";
  if (!form.value.email) form.value.email = user.email || "";
};

// 푸터의 "도용·권리침해 신고"(/support#report)로 들어오면 분류를 신고로 미리 선택.
const applyHash = () => {
  if (route.hash === "#report") form.value.category = "report";
};

onMounted(() => {
  prefillFromAuth();
  applyHash();
});
watch(() => authStore.isInitialized, prefillFromAuth);
watch(() => route.hash, applyHash);

const submit = async () => {
  error.value = null;
  submitting.value = true;
  try {
    submitted.value = await inquiriesApi.create({
      name: form.value.name.trim(),
      email: form.value.email.trim(),
      category: form.value.category,
      subject: form.value.subject.trim(),
      message: form.value.message.trim(),
      privacy_consent: form.value.privacy_consent,
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (e: any) {
    const detail = e?.response?.data?.detail;
    // 422 는 detail 이 배열(pydantic) 로 오므로 첫 메시지만 노출.
    error.value = Array.isArray(detail)
      ? detail[0]?.msg || "입력값을 다시 확인해 주세요."
      : detail || "문의 접수에 실패했어요. 잠시 후 다시 시도해 주세요.";
  } finally {
    submitting.value = false;
  }
};

const resetForm = () => {
  submitted.value = null;
  form.value.subject = "";
  form.value.message = "";
  form.value.privacy_consent = false;
};
</script>

<style scoped>
@import "./doc-page.css";

.inquiry-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-row.inline {
  flex-direction: row;
  gap: 1rem;
}

.form-row.inline > div {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

@media (max-width: 560px) {
  .form-row.inline {
    flex-direction: column;
  }
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #3a3a42;
}

input,
select,
textarea {
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
}

.char-count {
  align-self: flex-end;
  margin: 0;
}

.muted {
  color: #9a9aa3;
}

.small {
  font-size: 0.75rem;
}

.consent-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  background: #fafafa;
  border: 1px solid #e6e6ea;
  border-radius: 0.6rem;
  padding: 0.85rem 1rem;
  font-size: 0.82rem;
  font-weight: 400;
  color: #52525b;
  line-height: 1.6;
  cursor: pointer;
}

.consent-row input {
  width: auto;
  margin-top: 0.15rem;
  flex-shrink: 0;
}

.report-note {
  border-color: #fecaca;
  background: #fef2f2;
}

.form-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 0.6rem;
  padding: 0.7rem 0.9rem;
  font-size: 0.85rem;
  margin: 0;
}

.btn-primary {
  align-self: flex-start;
  background: linear-gradient(to right, #e24e12, #f2703a);
  color: #fff;
  border: none;
  border-radius: 0.6rem;
  padding: 0.7rem 1.4rem;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.spinner-inline {
  display: inline-block;
  width: 0.9rem;
  height: 0.9rem;
  margin-right: 0.4rem;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #fff;
  border-radius: 50%;
  vertical-align: -2px;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 접수 완료 */
.success-card {
  text-align: center;
}

.success-icon {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 0.75rem;
  border-radius: 9999px;
  background: #fdede4;
  color: #c24210;
  font-size: 1.5rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-card .btn-primary {
  align-self: center;
  margin-top: 1rem;
}
</style>
