<template>
  <div class="studio-page">
    <div class="studio-container">
      <header class="studio-head">
        <h1>크리에이터 스튜디오</h1>
        <p class="lead">
          내 AI 얼굴로 <strong>무엇이든 자유롭게</strong> 만들고, 원할 땐 팬에게 리딤 코드를 나눠주세요.
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
            <div class="step" :class="{ done: hasGeneration }">
              <span class="step-dot">{{ hasGeneration ? "✓" : 3 }}</span>
              <div>
                <strong>직접 만들기</strong>
                <p class="muted small">아바타로 원하는 사진을 자유롭게 생성해요.</p>
              </div>
            </div>
            <div class="step" :class="{ done: hasCode }">
              <span class="step-dot">{{ hasCode ? "✓" : 4 }}</span>
              <div>
                <strong>팬에게 코드 공유 (선택)</strong>
                <p class="muted small">원하면 리딤 코드를 발급해 팬에게 나눠주세요.</p>
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

        <!-- Direct create (creator's own free generation) -->
        <section class="card highlight">
          <h2>직접 만들기</h2>
          <p class="muted small">
            내 아바타로 원하는 장면을 <strong>자유롭게 프롬프트로</strong> 만드세요.
            생성 1장당 쿼터가 1 차감돼요 (건전한 이미지만 생성됩니다).
          </p>

          <form class="gen-form" @submit.prevent="generateSelf">
            <div class="form-row">
              <label>아바타</label>
              <select v-model.number="newGen.avatar_id" required>
                <option :value="0" disabled>아바타 선택…</option>
                <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>원본 이미지</label>
              <div class="source-row">
                <button type="button" class="source-thumb" @click="sourceInput?.click()">
                  <img :src="sourcePreview" alt="원본 이미지" />
                  <span v-if="usingDefaultSource" class="source-badge">기본</span>
                  <span v-if="uploadingSource" class="source-uploading">업로드 중…</span>
                </button>
                <div class="source-actions">
                  <button type="button" class="btn-outline" @click="sourceInput?.click()">
                    {{ usingDefaultSource ? "다른 이미지 올리기" : "이미지 변경" }}
                  </button>
                  <button
                    v-if="!usingDefaultSource"
                    type="button"
                    class="btn-text"
                    @click="clearSourceImage"
                  >
                    기본 이미지로 되돌리기
                  </button>
                  <p class="muted small">
                    {{
                      usingDefaultSource
                        ? "기본 이미지가 원본으로 적용돼 있어요. 바꾸고 싶으면 올려주세요."
                        : "올린 이미지를 원본으로 변형해요."
                    }}
                    PNG·JPEG·WebP, 10MB 이하.
                  </p>
                </div>
              </div>
              <input
                ref="sourceInput"
                type="file"
                accept="image/png,image/jpeg,image/webp"
                style="display: none"
                @change="onSourceSelected"
              />
            </div>

            <div class="form-row">
              <label>프롬프트</label>
              <textarea
                v-model="newGen.prompt"
                placeholder="원하는 장면·의상·배경·분위기를 자유롭게 묘사하세요 (예: 노을 지는 해변, 리넨 셔츠, 영화 같은 조명)"
                rows="3"
                required
              ></textarea>
            </div>

            <div class="form-row inline">
              <div>
                <label>
                  변형 강도 (strength)
                  <span class="slider-value">{{ newGen.strength.toFixed(2) }}</span>
                </label>
                <input
                  v-model.number="newGen.strength"
                  type="range"
                  min="0.05"
                  max="1"
                  step="0.05"
                />
                <p class="muted small">낮을수록 원본 유지, 높을수록 프롬프트를 강하게 반영해요.</p>
              </div>
              <div>
                <label>
                  LoRA 강도 (scale)
                  <span class="slider-value">{{ newGen.lora_scale.toFixed(1) }}</span>
                </label>
                <input
                  v-model.number="newGen.lora_scale"
                  type="range"
                  min="0"
                  max="4"
                  step="0.1"
                />
                <p class="muted small">높을수록 아바타 얼굴을 강하게 반영해요. 기본 2.0.</p>
              </div>
            </div>

            <button
              class="btn-primary"
              :disabled="
                generatingSelf ||
                uploadingSource ||
                !newGen.avatar_id ||
                !newGen.prompt.trim()
              "
            >
              <span v-if="generatingSelf" class="spinner-inline"></span>
              {{ generatingSelf ? "만드는 중…" : "이미지 생성" }}
            </button>
          </form>

          <!-- 생성 실패: 사라지지 않고 남으며 그대로 복사할 수 있다 -->
          <div v-if="genError" class="gen-error">
            <div class="gen-error-head">
              <strong>생성에 실패했어요</strong>
              <div class="gen-error-actions">
                <button type="button" class="btn-text" @click="copyGenError">
                  {{ genErrorCopied ? "✓ 복사됨" : "복사" }}
                </button>
                <button type="button" class="btn-text" @click="genError = null">닫기</button>
              </div>
            </div>
            <pre class="gen-error-body">{{ genError }}</pre>
          </div>

          <div v-if="genResult" class="gen-result">
            <img :src="genResult" alt="생성 결과" />
            <a class="btn-text" :href="genResult" download="creation.png" target="_blank">
              다운로드
            </a>
          </div>
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
import { ref, computed, onMounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";
import {
  studioApi,
  avatarsApi,
  type Plan,
  type SubscriptionInfo,
  type CodeItem,
  type AvatarItem,
  type SourceImage,
} from "../services/api";

const authStore = useAuthStore();

const plans = ref<Plan[]>([]);
const subscription = ref<SubscriptionInfo | null>(null);
const avatars = ref<AvatarItem[]>([]);
const codes = ref<CodeItem[]>([]);

const subscribing = ref(false);
const creatingCodes = ref(false);

const newCode = ref({ avatar_id: 0, max_uses: 1, count: 1 });
// strength/lora_scale 기본값은 백엔드 스키마와 동일하게 맞춘다.
const newGen = ref({
  avatar_id: 0,
  prompt: "",
  strength: 0.6,
  lora_scale: 2.0,
});
const generatingSelf = ref(false);
const genResult = ref<string | null>(null);
// 생성 실패는 토스트로 흘려보내지 않고, 복사할 수 있게 화면에 남긴다.
const genError = ref<string | null>(null);
const genErrorCopied = ref(false);

// image-to-image 소스 이미지.
// 업로드 전에는 서버가 실제로 사용할 기본 이미지를 그대로 보여준다 (이미 탑재된 상태).
const sourceInput = ref<HTMLInputElement | null>(null);
const sourceImage = ref<SourceImage | null>(null);
const uploadedPreview = ref<string | null>(null);
const uploadingSource = ref(false);
const defaultSourceUrl = studioApi.defaultSourceImageUrl();
const sourcePreview = computed(() => uploadedPreview.value || defaultSourceUrl);
const usingDefaultSource = computed(() => !sourceImage.value);

const onSourceSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = "";
  if (!file) return;
  uploadingSource.value = true;
  try {
    const uploaded = await studioApi.uploadSourceImage(file);
    sourceImage.value = uploaded;
    uploadedPreview.value = uploaded.preview_url;
    showToast("원본 이미지를 올렸어요");
  } catch (err: any) {
    showToast(errMsg(err, "이미지 업로드에 실패했어요."), "err");
  } finally {
    uploadingSource.value = false;
  }
};

const clearSourceImage = () => {
  sourceImage.value = null;
  uploadedPreview.value = null;
};

const toast = ref<{ msg: string; kind: "ok" | "err" } | null>(null);
let toastTimer: ReturnType<typeof setTimeout> | null = null;
const showToast = (msg: string, kind: "ok" | "err" = "ok") => {
  toast.value = { msg, kind };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2600);
};
const errMsg = (e: any, fallback: string): string => e?.response?.data?.detail || fallback;

const avatarTitle = (id: number) => avatars.value.find((a) => a.id === id)?.title || "—";
const redeemUrl = (code: string) => `${window.location.origin}/r/${code}`;

// Onboarding
const hasSubscription = computed(() => !!subscription.value);
const hasAvatar = computed(() => avatars.value.length > 0);
const hasGeneration = ref(false);
const hasCode = computed(() => codes.value.length > 0);
// 코드 공유는 선택 단계라 온보딩 완료 조건에서 제외.
const allStepsDone = computed(
  () => hasSubscription.value && hasAvatar.value && hasGeneration.value
);

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

  // 각 항목은 서로 독립적이다. 한 엔드포인트가 500 이 나도 나머지는 그대로 채운다
  // (예전엔 순차 await 라 앞이 실패하면 뒤가 통째로 안 불러와졌다).
  const results = await Promise.allSettled([
    studioApi.getPlans(),
    studioApi.getSubscription(),
    avatarsApi.getMyAvatars(),
    studioApi.getCodes(),
  ]);

  const [plansRes, subRes, avatarsRes, codesRes] = results;
  if (plansRes.status === "fulfilled") plans.value = plansRes.value;
  if (subRes.status === "fulfilled") subscription.value = subRes.value;
  if (avatarsRes.status === "fulfilled") avatars.value = avatarsRes.value;
  if (codesRes.status === "fulfilled") codes.value = codesRes.value;

  const failed = results.filter((r) => r.status === "rejected");
  if (failed.length) {
    // 조용히 빈 화면을 보여주지 않는다 — 어디가 실패했는지 콘솔에 남기고 알린다.
    failed.forEach((r) => console.error("Studio load failed:", (r as PromiseRejectedResult).reason));
    showToast(
      `일부 정보를 불러오지 못했어요 (${failed.length}건). 새로고침해 주세요.`,
      "err"
    );
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

/** 요청 조건 + 실패 사유를 한 덩어리 텍스트로. 그대로 복사해 공유할 수 있게. */
const buildErrorReport = (reason: string, e?: any): string => {
  const lines = [
    `[생성 실패] ${new Date().toLocaleString("ko-KR")}`,
    "",
    "■ 사유",
    reason,
  ];

  const status = e?.response?.status;
  if (status) lines.push("", "■ 응답", `HTTP ${status}`);

  const detail = e?.response?.data?.detail;
  if (Array.isArray(detail)) {
    // pydantic 422 는 배열로 온다 — 필드별로 펼친다.
    lines.push(
      ...detail.map(
        (d: any) => `- ${(d.loc ?? []).join(".")}: ${d.msg ?? JSON.stringify(d)}`
      )
    );
  } else if (detail && detail !== reason) {
    lines.push(String(detail));
  }

  lines.push(
    "",
    "■ 요청 조건",
    `avatar_id: ${newGen.value.avatar_id}`,
    `source_image: ${sourceImage.value?.url ?? "(기본 이미지)"}`,
    `strength: ${newGen.value.strength}`,
    `lora_scale: ${newGen.value.lora_scale}`,
    "",
    "■ 프롬프트",
    newGen.value.prompt.trim() || "(비어 있음)"
  );
  return lines.join("\n");
};

const generateSelf = async () => {
  generatingSelf.value = true;
  genResult.value = null;
  genError.value = null;
  genErrorCopied.value = false;
  try {
    const res = await studioApi.generateSelf({
      avatar_id: newGen.value.avatar_id,
      prompt: newGen.value.prompt.trim(),
      source_image_url: sourceImage.value?.url ?? null,
      strength: newGen.value.strength,
      lora_scale: newGen.value.lora_scale,
    });
    if (res.status === "success" && res.image_url) {
      genResult.value = res.image_url;
      hasGeneration.value = true;
      subscription.value = await studioApi.getSubscription();
      showToast("이미지가 생성됐어요 🎉");
    } else {
      // 사라지는 토스트 대신, 복사 가능한 패널로 남긴다.
      genError.value = buildErrorReport(res.fail_reason || "생성에 실패했어요.");
    }
  } catch (e: any) {
    genError.value = buildErrorReport(errMsg(e, "생성에 실패했어요."), e);
  } finally {
    generatingSelf.value = false;
  }
};

const copyGenError = async () => {
  if (!genError.value) return;
  try {
    await navigator.clipboard.writeText(genError.value);
    genErrorCopied.value = true;
    setTimeout(() => (genErrorCopied.value = false), 2000);
  } catch {
    showToast("복사에 실패했어요. 텍스트를 직접 선택해 주세요.", "err");
  }
};

const createCodes = async () => {
  creatingCodes.value = true;
  try {
    const created = await studioApi.createCodes({
      avatar_id: newCode.value.avatar_id,
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

// App.vue 가 onMounted 에서 authStore.initialize() 를 await 하므로, 새로고침 직후에는
// 이 컴포넌트의 onMounted 시점에 아직 isLoggedIn=false 다 (→ loadAll 이 조기 반환).
// 인증이 끝나 로그인 상태가 되면 한 번 더 불러온다. 모달 로그인 직후에도 동작.
watch(
  () => authStore.isLoggedIn,
  (loggedIn) => {
    if (loggedIn) loadAll();
  }
);
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

.code-form,
.gen-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.25rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

/* Direct-create highlight */
.card.highlight {
  border-color: #ddd6fe;
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.08);
}

/* 생성 실패 리포트 — 자동으로 사라지지 않고 선택·복사 가능 */
.gen-error {
  border: 1px solid #fecaca;
  background: #fef2f2;
  border-radius: 0.75rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.gen-error-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem 0.9rem;
  border-bottom: 1px solid #fecaca;
}

.gen-error-head strong {
  font-size: 0.875rem;
  color: #b91c1c;
}

.gen-error-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.gen-error-actions .btn-text {
  color: #b91c1c;
}

.gen-error-body {
  margin: 0;
  padding: 0.9rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  line-height: 1.65;
  color: #7f1d1d;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 320px;
  overflow-y: auto;
  /* 드래그로 선택해 복사할 수 있게 */
  user-select: text;
}

.gen-result {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.gen-result img {
  max-width: 100%;
  width: 320px;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
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

.btn-outline {
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #ddd6fe;
  color: #6d28d9;
  border-radius: 0.5rem;
  padding: 0.55rem 0.85rem;
  font-weight: 700;
  font-size: 0.8rem;
  white-space: nowrap;
  cursor: pointer;
}

.btn-outline:hover {
  background: #f5f3ff;
}

.source-row {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
}

.source-thumb {
  position: relative;
  flex-shrink: 0;
  width: 72px;
  height: 92px;
  border-radius: 0.6rem;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
}

.source-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 기본 이미지가 적용 중임을 알리는 뱃지 */
.source-badge {
  position: absolute;
  left: 0;
  bottom: 0;
  right: 0;
  background: rgba(17, 24, 39, 0.72);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 0.15rem 0;
  text-align: center;
}

.source-uploading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  font-size: 0.7rem;
  font-weight: 600;
  color: #6d28d9;
}

.source-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
}

.source-actions .muted {
  margin: 0;
}

.slider-value {
  float: right;
  font-weight: 700;
  color: #6d28d9;
  font-variant-numeric: tabular-nums;
}

input[type="range"] {
  padding: 0;
  accent-color: #7c3aed;
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
