<template>
  <div class="studio-page">
    <div class="studio-container">
      <header class="studio-head">
        <h1>크리에이터 스튜디오</h1>
        <p class="lead">
          내 AI 얼굴로 콘텐츠를 만들고, 팬에게 리딤 코드를 나눠주세요.
        </p>
      </header>

      <div v-if="!authStore.isLoggedIn" class="notice">
        크리에이터 스튜디오를 이용하려면 로그인해 주세요.
      </div>

      <template v-else>
        <!-- Onboarding stepper -->
        <section v-if="!allStepsDone" class="stepper card">
          <h2>시작하기</h2>
          <div class="steps">
            <div class="step" :class="{ done: hasSubscription }">
              <span class="step-dot">{{ hasSubscription ? "✓" : 1 }}</span>
              <div>
                <strong>플랜 선택</strong>
                <p class="muted small">구독을 선택하면 월 이미지 쿼터를 받아요.</p>
              </div>
            </div>
            <div class="step" :class="{ done: hasAvatar }">
              <span class="step-dot">{{ hasAvatar ? "✓" : 2 }}</span>
              <div>
                <strong>아바타 만들기</strong>
                <p class="muted small">
                  내 AI 얼굴을 학습시키세요 —
                  <RouterLink to="/my/avatars" class="inline-link">내 아바타</RouterLink>.
                </p>
              </div>
            </div>
            <div class="step" :class="{ done: hasLook }">
              <span class="step-dot">{{ hasLook ? "✓" : 3 }}</span>
              <div>
                <strong>룩 추가</strong>
                <p class="muted small">팬이 생성할 수 있는 프리셋 룩을 만들어요 (선택).</p>
              </div>
            </div>
            <div class="step" :class="{ done: hasCode }">
              <span class="step-dot">{{ hasCode ? "✓" : 4 }}</span>
              <div>
                <strong>코드 공유</strong>
                <p class="muted small">리딤 코드를 발급해 팬에게 나눠주세요.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Subscription / Quota -->
        <section class="card">
          <h2>구독</h2>
          <div v-if="subscription" class="quota-row">
            <div class="quota-badge">
              <span class="plan-name">{{ subscription.plan_name }}</span>
              <span class="quota-num">
                {{ subscription.quota_remaining }} / {{ subscription.monthly_quota }}
              </span>
              <span class="quota-label">이번 기간 남은 이미지</span>
            </div>
          </div>
          <p v-else class="muted">아직 활성 플랜이 없어요. 아래에서 선택하세요.</p>

          <div class="plan-grid">
            <div
              v-for="p in plans"
              :key="p.id"
              class="plan-card"
              :class="{ current: subscription?.plan_code === p.code }"
            >
              <h3>{{ p.name }}</h3>
              <p class="price">${{ p.price_usd }}<span>/월</span></p>
              <ul>
                <li>{{ p.monthly_quota.toLocaleString() }} 이미지 / 월</li>
                <li>{{ p.max_avatars }}개 아바타</li>
                <li>{{ p.max_active_codes.toLocaleString() }} 활성 코드</li>
              </ul>
              <button
                class="btn-primary"
                :disabled="subscribing || subscription?.plan_code === p.code"
                @click="subscribe(p.code)"
              >
                {{ subscription?.plan_code === p.code ? "현재 플랜" : "선택" }}
              </button>
            </div>
          </div>
          <p class="muted small">
            결제는 아직 연동 전이에요 — 플랜을 고르면 쿼터가 즉시 활성화됩니다 (데모).
          </p>
        </section>

        <!-- Templates -->
        <section class="card">
          <h2>룩 (템플릿)</h2>
          <p class="muted small">
            팬은 여기 등록된 승인된 룩으로만 생성할 수 있고, 직접 프롬프트를 입력할 수 없어요.
            그래서 내 얼굴을 온전히 내가 통제할 수 있습니다.
          </p>

          <form class="template-form" @submit.prevent="createTemplate">
            <div class="form-row">
              <label>아바타</label>
              <select v-model.number="newTemplate.avatar_id" required>
                <option :value="0" disabled>아바타 선택…</option>
                <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>룩 이름</label>
              <input v-model="newTemplate.name" placeholder="예) 크리스마스, 여름 바닷가" required />
            </div>
            <div class="form-row">
              <label>프롬프트</label>
              <textarea
                v-model="newTemplate.prompt"
                placeholder="장면·의상을 묘사하세요 (팬에게는 이 룩이 보이지만 수정은 불가)"
                rows="2"
                required
              ></textarea>
            </div>
            <button class="btn-primary" :disabled="creatingTemplate || !newTemplate.avatar_id">
              {{ creatingTemplate ? "추가 중…" : "룩 추가" }}
            </button>
          </form>

          <div v-if="templates.length" class="list">
            <div v-for="t in templates" :key="t.id" class="list-item">
              <div class="tpl-row">
                <button class="tpl-thumb" @click="triggerThumb(t.id)" :title="'썸네일 설정'">
                  <img v-if="t.preview_image_url" :src="t.preview_image_url" alt="" />
                  <span v-else class="tpl-thumb-add">＋</span>
                </button>
                <div>
                  <strong>{{ t.name }}</strong>
                  <span class="muted small"> · {{ avatarTitle(t.avatar_id) }}</span>
                  <p class="muted small prompt-preview">{{ t.prompt }}</p>
                  <button class="btn-text" @click="triggerThumb(t.id)">
                    {{ t.preview_image_url ? "썸네일 변경" : "썸네일 추가" }}
                  </button>
                </div>
              </div>
              <button class="btn-text danger" @click="deleteTemplate(t.id)">삭제</button>
            </div>
          </div>
          <p v-else class="muted">아직 룩이 없어요.</p>
          <input
            ref="thumbInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="onThumbSelected"
          />
        </section>

        <!-- Redeem codes -->
        <section class="card">
          <h2>리딤 코드</h2>
          <p class="muted small">
            팬에게 나눠주세요 (이벤트 경품, 멤버십 혜택 등). 생성이 성공할 때마다 내 쿼터에서
            이미지 1장이 차감돼요.
          </p>

          <form class="code-form" @submit.prevent="createCodes">
            <div class="form-row">
              <label>아바타</label>
              <select v-model.number="newCode.avatar_id" required>
                <option :value="0" disabled>아바타 선택…</option>
                <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>룩 (선택)</label>
              <select v-model.number="newCode.template_id">
                <option :value="0">이 아바타의 모든 룩</option>
                <option v-for="t in templatesForAvatar(newCode.avatar_id)" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>
            <div class="form-row inline">
              <div>
                <label>코드당 사용 횟수</label>
                <input v-model.number="newCode.max_uses" type="number" min="1" />
              </div>
              <div>
                <label>코드 개수</label>
                <input v-model.number="newCode.count" type="number" min="1" max="500" />
              </div>
            </div>
            <button class="btn-primary" :disabled="creatingCodes || !newCode.avatar_id">
              {{ creatingCodes ? "생성 중…" : "코드 생성" }}
            </button>
          </form>

          <div v-if="codes.length" class="list">
            <div v-for="c in codes" :key="c.id" class="list-item">
              <div>
                <code class="code-chip">{{ c.code }}</code>
                <span class="muted small">
                  · {{ c.used_count }}/{{ c.max_uses ?? "∞" }} 사용됨
                  <template v-if="!c.is_active"> · 비활성</template>
                </span>
                <p class="muted small">{{ redeemUrl(c.code) }}</p>
              </div>
              <div class="item-actions">
                <button class="btn-text" @click="openQr(c.code)">QR</button>
                <button class="btn-text" @click="copyLink(c.code)">링크 복사</button>
                <button v-if="c.is_active" class="btn-text danger" @click="deactivateCode(c.id)">
                  비활성화
                </button>
              </div>
            </div>
          </div>
          <p v-else class="muted">아직 코드가 없어요.</p>
        </section>
      </template>
    </div>

    <!-- QR modal -->
    <div v-if="qrCodeStr" class="qr-overlay" @click.self="qrCodeStr = null">
      <div class="qr-modal">
        <h3>스캔해서 사용하기</h3>
        <p class="muted small">팬이 스캔하면 리딤 페이지가 열려요.</p>
        <img :src="qrImgUrl" alt="QR code" class="qr-img" />
        <code class="code-chip">{{ qrCodeStr }}</code>
        <div class="qr-actions">
          <button class="btn-primary" @click="copyLink(qrCodeStr)">링크 복사</button>
          <a class="btn-text" :href="qrImgUrl" download="redeem-qr.svg">Download QR</a>
          <button class="btn-text" @click="qrCodeStr = null">닫기</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast" class="toast" :class="toast.kind">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";
import {
  studioApi,
  avatarsApi,
  type Plan,
  type SubscriptionInfo,
  type TemplateItem,
  type CodeItem,
  type AvatarItem,
} from "../services/api";

const authStore = useAuthStore();

const plans = ref<Plan[]>([]);
const subscription = ref<SubscriptionInfo | null>(null);
const avatars = ref<AvatarItem[]>([]);
const templates = ref<TemplateItem[]>([]);
const codes = ref<CodeItem[]>([]);

const subscribing = ref(false);
const creatingTemplate = ref(false);
const creatingCodes = ref(false);

const newTemplate = ref({ avatar_id: 0, name: "", prompt: "" });
const newCode = ref({ avatar_id: 0, template_id: 0, max_uses: 1, count: 1 });

const toast = ref<{ msg: string; kind: "ok" | "err" } | null>(null);
let toastTimer: ReturnType<typeof setTimeout> | null = null;
const showToast = (msg: string, kind: "ok" | "err" = "ok") => {
  toast.value = { msg, kind };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2600);
};
const errMsg = (e: any, fallback: string): string => e?.response?.data?.detail || fallback;

const avatarTitle = (id: number) => avatars.value.find((a) => a.id === id)?.title || "—";
const templatesForAvatar = (avatarId: number) =>
  templates.value.filter((t) => t.avatar_id === avatarId);
const redeemUrl = (code: string) => `${window.location.origin}/r/${code}`;

// Onboarding
const hasSubscription = computed(() => !!subscription.value);
const hasAvatar = computed(() => avatars.value.length > 0);
const hasLook = computed(() => templates.value.length > 0);
const hasCode = computed(() => codes.value.length > 0);
const allStepsDone = computed(
  () => hasSubscription.value && hasAvatar.value && hasLook.value && hasCode.value
);

// Template thumbnail upload
const thumbInput = ref<HTMLInputElement | null>(null);
const pendingThumbId = ref<number | null>(null);
const triggerThumb = (id: number) => {
  pendingThumbId.value = id;
  thumbInput.value?.click();
};
const onThumbSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = "";
  if (!file || pendingThumbId.value == null) return;
  try {
    await studioApi.uploadTemplatePreview(pendingThumbId.value, file);
    templates.value = await studioApi.getTemplates();
    showToast("썸네일이 업데이트됐어요");
  } catch (err: any) {
    showToast(errMsg(err, "썸네일 업로드에 실패했어요."), "err");
  } finally {
    pendingThumbId.value = null;
  }
};

// QR modal
const qrCodeStr = ref<string | null>(null);
const qrImgUrl = computed(() =>
  qrCodeStr.value ? studioApi.qrUrl(redeemUrl(qrCodeStr.value)) : ""
);
const openQr = (code: string) => {
  qrCodeStr.value = code;
};

const loadAll = async () => {
  if (!authStore.isLoggedIn) return;
  try {
    plans.value = await studioApi.getPlans();
    subscription.value = await studioApi.getSubscription();
    avatars.value = await avatarsApi.getMyAvatars();
    templates.value = await studioApi.getTemplates();
    codes.value = await studioApi.getCodes();
  } catch (e) {
    console.error("Failed to load studio data", e);
  }
};

const subscribe = async (planCode: string) => {
  subscribing.value = true;
  try {
    subscription.value = await studioApi.subscribe(planCode);
    showToast("플랜이 활성화됐어요 🎉");
  } catch (e: any) {
    showToast(errMsg(e, "구독에 실패했어요."), "err");
  } finally {
    subscribing.value = false;
  }
};

const createTemplate = async () => {
  creatingTemplate.value = true;
  try {
    await studioApi.createTemplate({ ...newTemplate.value });
    newTemplate.value = { avatar_id: 0, name: "", prompt: "" };
    templates.value = await studioApi.getTemplates();
    showToast("룩이 추가됐어요");
  } catch (e: any) {
    showToast(errMsg(e, "룩 추가에 실패했어요."), "err");
  } finally {
    creatingTemplate.value = false;
  }
};

const deleteTemplate = async (id: number) => {
  if (!confirm("이 룩을 삭제할까요?")) return;
  try {
    await studioApi.deleteTemplate(id);
    templates.value = await studioApi.getTemplates();
    showToast("룩이 삭제됐어요");
  } catch (e: any) {
    showToast(errMsg(e, "삭제에 실패했어요."), "err");
  }
};

const createCodes = async () => {
  creatingCodes.value = true;
  try {
    const created = await studioApi.createCodes({
      avatar_id: newCode.value.avatar_id,
      template_id: newCode.value.template_id || null,
      max_uses: newCode.value.max_uses || 1,
      count: newCode.value.count || 1,
    });
    codes.value = await studioApi.getCodes();
    showToast(`${created.length} code${created.length === 1 ? "" : "s"} generated`);
  } catch (e: any) {
    showToast(errMsg(e, "코드 생성에 실패했어요."), "err");
  } finally {
    creatingCodes.value = false;
  }
};

const deactivateCode = async (id: number) => {
  try {
    await studioApi.deactivateCode(id);
    codes.value = await studioApi.getCodes();
    showToast("코드가 비활성화됐어요");
  } catch (e: any) {
    showToast(errMsg(e, "코드 비활성화에 실패했어요."), "err");
  }
};

const copyLink = async (code: string) => {
  try {
    await navigator.clipboard.writeText(redeemUrl(code));
    showToast("리딤 링크를 복사했어요 🔗");
  } catch {
    showToast("링크 복사에 실패했어요", "err");
  }
};

onMounted(loadAll);
</script>

<style scoped>
.studio-page {
  min-height: calc(100vh - 80px);
  background: #f9fafb;
  padding: 2.5rem 1rem 4rem;
}

.studio-container {
  max-width: 880px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.studio-head h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.lead {
  color: #6b7280;
  margin: 0.5rem 0 0;
}

.notice {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem;
}

.card h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.75rem;
}

.muted {
  color: #6b7280;
}

.small {
  font-size: 0.8rem;
}

.quota-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 0.15rem;
  background: linear-gradient(135deg, #ede9fe, #fae8ff);
  border-radius: 0.75rem;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1rem;
}

.plan-name {
  font-weight: 700;
  color: #6d28d9;
  font-size: 0.85rem;
}

.quota-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #111827;
}

.quota-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.plan-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.85rem;
  padding: 1.1rem;
  text-align: center;
}

.plan-card.current {
  border-color: #7c3aed;
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15);
}

.plan-card h3 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  color: #111827;
}

.price {
  font-size: 1.4rem;
  font-weight: 800;
  color: #111827;
  margin: 0 0 0.6rem;
}

.price span {
  font-size: 0.8rem;
  font-weight: 500;
  color: #9ca3af;
}

.plan-card ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0.9rem;
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.template-form,
.code-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.25rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
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
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #374151;
}

input,
select,
textarea {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.55rem 0.7rem;
  font-size: 0.9rem;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
  border-top: 1px solid #f3f4f6;
}

.prompt-preview {
  max-width: 520px;
  margin: 0.25rem 0 0;
}

.code-chip {
  background: #111827;
  color: #fff;
  border-radius: 0.4rem;
  padding: 0.15rem 0.5rem;
  font-family: ui-monospace, monospace;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-primary {
  align-self: flex-start;
  background: linear-gradient(to right, #7c3aed, #9333ea);
  color: #fff;
  border: none;
  border-radius: 0.6rem;
  padding: 0.6rem 1.2rem;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: #6d28d9;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-text.danger {
  color: #dc2626;
}

/* Onboarding stepper */
.stepper .steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.step {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
}

.step-dot {
  flex-shrink: 0;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 9999px;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.step.done .step-dot {
  background: #7c3aed;
  color: #fff;
}

.step strong {
  font-size: 0.9rem;
  color: #111827;
}

.inline-link {
  color: #6d28d9;
  font-weight: 600;
}

/* Template thumbnails */
.tpl-row {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}

.tpl-thumb {
  flex-shrink: 0;
  width: 56px;
  height: 72px;
  border-radius: 0.6rem;
  border: 1px dashed #d1d5db;
  background: #f9fafb;
  overflow: hidden;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tpl-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tpl-thumb-add {
  font-size: 1.4rem;
  color: #9ca3af;
}

/* QR modal */
.qr-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 90;
}

.qr-modal {
  background: #fff;
  border-radius: 1rem;
  padding: 1.75rem;
  max-width: 340px;
  width: 100%;
  text-align: center;
}

.qr-modal h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  color: #111827;
}

.qr-img {
  width: 220px;
  height: 220px;
  margin: 1rem auto;
  display: block;
}

.qr-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  margin-top: 1rem;
}

.qr-actions .btn-primary {
  align-self: stretch;
}

/* Toast */
.toast {
  position: fixed;
  left: 50%;
  bottom: 2rem;
  transform: translateX(-50%);
  z-index: 100;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 12px 28px -12px rgba(0, 0, 0, 0.4);
}

.toast.ok {
  background: #111827;
}

.toast.err {
  background: #dc2626;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 12px);
}
</style>
