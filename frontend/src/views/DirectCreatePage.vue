<template>
  <div class="create-page">
    <div class="create-container">
      <header class="create-head">
        <RouterLink to="/studio" class="back-link">← 크리에이터 스튜디오</RouterLink>
        <div class="head-row">
          <div class="head-text">
            <h1>직접 만들기</h1>
            <p class="lead">
              내 아바타로 원하는 장면을 <strong>자유롭게 프롬프트로</strong> 만드세요.
              생성 1장당 크레딧이 1 차감돼요 (건전한 이미지만 생성됩니다).
            </p>
          </div>
          <RouterLink to="/studio" class="quota-badge" title="크레딧 충전하기">
            <span class="plan-name">보유 크레딧</span>
            <span class="quota-num">{{ credits.toLocaleString() }}</span>
            <span class="quota-label">이미지 1장 = 크레딧 1</span>
          </RouterLink>
        </div>
      </header>

      <div v-if="!authStore.isLoggedIn" class="notice">
        직접 만들기를 이용하려면 로그인해 주세요.
      </div>

      <div v-else-if="loading" class="notice">불러오는 중…</div>

      <div v-else-if="!avatars.length" class="notice">
        아직 아바타가 없어요.
        <RouterLink to="/my/avatars" class="inline-link">내 아바타</RouterLink>에서 먼저
        내 얼굴을 학습시켜 주세요.
      </div>

      <!-- 왼쪽 컨트롤 / 오른쪽 큰 결과 -->
      <div v-else class="workspace">
        <form class="controls" @submit.prevent="generateSelf">
          <div class="field">
            <label>아바타</label>
            <div class="avatar-pick">
              <AvatarPickPreview
                :title="selectedAvatar?.title"
                :preview-url="selectedAvatar?.preview_image_url"
                :hidden="selectedAvatar?.status === 'hidden'"
              />
              <div class="avatar-pick-controls">
                <select v-model.number="newGen.avatar_id" required>
                  <option :value="0" disabled>아바타 선택…</option>
                  <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
                </select>
                <p class="muted small">
                  고른 아바타의 얼굴로 생성돼요.
                  <RouterLink to="/my/avatars" class="inline-link">내 아바타</RouterLink>에서
                  새로 만들 수 있어요.
                </p>
              </div>
            </div>
          </div>

          <div class="field">
            <label>참조 이미지</label>
            <p class="muted small ref-note">
              참조 이미지와 <strong>비슷한 구도·분위기</strong>의 장면을 만들어요.
              얼굴은 위에서 고른 아바타로 바뀝니다.
            </p>
            <div class="source-row">
              <button type="button" class="source-thumb" @click="sourceInput?.click()">
                <img :src="sourcePreview" alt="참조 이미지" />
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
                      ? "지금은 기본 참조 이미지가 적용돼 있어요. 다른 장면을 참조하려면 올려주세요."
                      : "올린 이미지를 참조해요."
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

          <div class="field">
            <label>프롬프트</label>
            <textarea
              v-model="newGen.prompt"
              placeholder="원하는 장면·의상·배경·분위기를 자유롭게 묘사하세요 (예: 노을 지는 해변, 리넨 셔츠, 영화 같은 조명)"
              rows="5"
              required
            ></textarea>
          </div>

          <div class="field">
            <label>
              참조 이미지 일치도
              <span class="slider-value">{{ refMatch.toFixed(2) }}</span>
            </label>
            <input v-model.number="refMatch" type="range" min="0" max="0.95" step="0.05" />
            <p class="muted small">
              높을수록 참조 이미지의 구도·분위기를 그대로 따라가고, 낮을수록 프롬프트대로
              자유롭게 만들어요.
            </p>
          </div>

          <div class="field">
            <label>
              아바타 일치도
              <span class="slider-value">{{ newGen.lora_scale.toFixed(1) }}</span>
            </label>
            <input v-model.number="newGen.lora_scale" type="range" min="0" max="4" step="0.1" />
            <p class="muted small">높을수록 아바타 얼굴을 강하게 반영해요. 기본 2.0.</p>
          </div>

          <button
            class="btn-primary generate-btn"
            :disabled="generating || uploadingSource || !newGen.avatar_id || !newGen.prompt.trim()"
          >
            <span v-if="generating" class="spinner-inline"></span>
            {{ generating ? "만드는 중…" : "이미지 생성" }}
          </button>
        </form>

        <section class="canvas">
          <!-- 생성 중 -->
          <div v-if="generating" class="canvas-state">
            <div class="spinner"></div>
            <p class="state-msg">{{ loadingMessage }}</p>
            <p class="state-sub">보통 몇 초 정도 걸려요.</p>
          </div>

          <!-- 결과 -->
          <div v-else-if="result" class="canvas-result">
            <img :src="result" alt="생성 결과" class="result-img" />
            <div class="result-actions">
              <a class="btn-primary" :href="result" download="creation.png" target="_blank">
                ⬇ 다운로드
              </a>
              <RouterLink to="/my/generations" class="btn-secondary">내 생성물</RouterLink>
            </div>
          </div>

          <!-- 실패: 사라지지 않고 남으며 그대로 복사할 수 있다 -->
          <div v-else-if="genError" class="gen-error">
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

          <!-- 아직 아무것도 안 만든 상태 -->
          <div v-else class="canvas-empty">
            <span class="empty-icon" aria-hidden="true">🖼</span>
            <p>왼쪽에서 아바타와 프롬프트를 정하고 <strong>이미지 생성</strong>을 눌러보세요.</p>
          </div>

          <!-- 이번 세션에 만든 것들 -->
          <div v-if="sessionResults.length > 1" class="session-strip">
            <button
              v-for="(img, i) in sessionResults"
              :key="i"
              type="button"
              class="strip-thumb"
              :class="{ active: img === result }"
              @click="result = img"
            >
              <img :src="img" alt="" />
            </button>
          </div>
        </section>
      </div>
    </div>

    <transition name="toast">
      <div v-if="toast" class="toast" :class="toast.kind">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";
import AvatarPickPreview from "../components/AvatarPickPreview.vue";
import {
  studioApi,
  avatarsApi,
  creditsApi,
  type AvatarItem,
  type SourceImage,
} from "../services/api";

const authStore = useAuthStore();

const loading = ref(true);
const avatars = ref<AvatarItem[]>([]);
const credits = ref(0);

// strength/lora_scale 기본값은 백엔드 스키마와 동일하게 맞춘다.
const newGen = ref({ avatar_id: 0, prompt: "", strength: 0.6, lora_scale: 2.0 });

// 화면에는 "참조 이미지 일치도"로 보여준다 — strength 와 방향이 반대다.
// strength 는 참조에서 얼마나 멀어질지라서, 일치도 = 1 - strength.
// API 로는 계속 strength 를 보낸다.
const refMatch = computed({
  get: () => Number((1 - newGen.value.strength).toFixed(2)),
  set: (v: number) => {
    newGen.value.strength = Number((1 - v).toFixed(2));
  },
});

const generating = ref(false);
const result = ref<string | null>(null);
const sessionResults = ref<string[]>([]);
// 생성 실패는 토스트로 흘려보내지 않고, 복사할 수 있게 화면에 남긴다.
const genError = ref<string | null>(null);
const genErrorCopied = ref(false);

const selectedAvatar = computed(
  () => avatars.value.find((a) => a.id === newGen.value.avatar_id) ?? null
);

// image-to-image 참조 이미지.
// 이 이미지를 "복원"하는 게 아니라, 구도·분위기를 참조해 비슷한 장면을 새로 만든다.
// 업로드 전에는 서버가 실제로 사용할 기본 이미지를 그대로 보여준다 (이미 탑재된 상태).
const sourceInput = ref<HTMLInputElement | null>(null);
const sourceImage = ref<SourceImage | null>(null);
const uploadedPreview = ref<string | null>(null);
const uploadingSource = ref(false);
const defaultSourceUrl = studioApi.defaultSourceImageUrl();
const sourcePreview = computed(() => uploadedPreview.value || defaultSourceUrl);
const usingDefaultSource = computed(() => !sourceImage.value);

const toast = ref<{ msg: string; kind: "ok" | "err" } | null>(null);
let toastTimer: ReturnType<typeof setTimeout> | null = null;
const showToast = (msg: string, kind: "ok" | "err" = "ok") => {
  toast.value = { msg, kind };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2600);
};
const errMsg = (e: any, fallback: string): string => e?.response?.data?.detail || fallback;

// 생성 대기 중 로딩 문구 로테이션
const LOADING_MESSAGES = [
  "장면을 구성하는 중…",
  "조명을 잡는 중…",
  "마무리 손질 중…",
  "거의 다 됐어요…",
];
const loadingMessage = ref(LOADING_MESSAGES[0]);
let loadingTimer: ReturnType<typeof setInterval> | null = null;
const startLoadingMessages = () => {
  let i = 0;
  loadingMessage.value = LOADING_MESSAGES[0];
  loadingTimer = setInterval(() => {
    i = (i + 1) % LOADING_MESSAGES.length;
    loadingMessage.value = LOADING_MESSAGES[i];
  }, 2500);
};
const stopLoadingMessages = () => {
  if (loadingTimer) {
    clearInterval(loadingTimer);
    loadingTimer = null;
  }
};

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
    showToast("참조 이미지를 올렸어요");
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

const loadAll = async () => {
  if (!authStore.isLoggedIn) {
    loading.value = false;
    return;
  }
  loading.value = true;

  // 서로 독립적이다 — 한쪽이 500 이어도 나머지는 그대로 채운다.
  const [avatarsRes, creditsRes] = await Promise.allSettled([
    avatarsApi.getMyAvatars(),
    creditsApi.getMyCredits(),
  ]);
  if (avatarsRes.status === "fulfilled") {
    avatars.value = avatarsRes.value;
    // 아바타가 하나뿐이면 고르는 수고를 없앤다.
    if (avatars.value.length === 1) newGen.value.avatar_id = avatars.value[0].id;
  } else {
    console.error("아바타 로드 실패:", avatarsRes.reason);
    showToast("아바타를 불러오지 못했어요. 새로고침해 주세요.", "err");
  }
  if (creditsRes.status === "fulfilled") credits.value = creditsRes.value.balance;

  loading.value = false;
};

/** 잔액만 다시 읽는다. 실패해도 화면을 막지 않고 이전 값을 유지한다. */
const refreshCredits = async () => {
  try {
    credits.value = (await creditsApi.getMyCredits()).balance;
  } catch {
    // 잔액 표시 갱신 실패는 생성 흐름을 방해할 이유가 없다.
  }
};

/** 요청 조건 + 실패 사유를 한 덩어리 텍스트로. 그대로 복사해 공유할 수 있게. */
const buildErrorReport = (reason: string, e?: any): string => {
  const lines = [`[생성 실패] ${new Date().toLocaleString("ko-KR")}`, "", "■ 사유", reason];

  const status = e?.response?.status;
  if (status) lines.push("", "■ 응답", `HTTP ${status}`);

  const detail = e?.response?.data?.detail;
  if (Array.isArray(detail)) {
    // pydantic 422 는 배열로 온다 — 필드별로 펼친다.
    lines.push(
      ...detail.map((d: any) => `- ${(d.loc ?? []).join(".")}: ${d.msg ?? JSON.stringify(d)}`)
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
  generating.value = true;
  genError.value = null;
  genErrorCopied.value = false;
  startLoadingMessages();
  try {
    const res = await studioApi.generateSelf({
      avatar_id: newGen.value.avatar_id,
      prompt: newGen.value.prompt.trim(),
      source_image_url: sourceImage.value?.url ?? null,
      strength: newGen.value.strength,
      lora_scale: newGen.value.lora_scale,
    });
    if (res.status === "success" && res.image_url) {
      result.value = res.image_url;
      sessionResults.value.push(res.image_url);
      showToast("이미지가 생성됐어요 🎉");
    } else {
      genError.value = buildErrorReport(res.fail_reason || "생성에 실패했어요.");
    }
  } catch (e: any) {
    genError.value = buildErrorReport(errMsg(e, "생성에 실패했어요."), e);
  } finally {
    generating.value = false;
    stopLoadingMessages();
    // 성공이든 실패든 잔액을 다시 읽는다 — 실패 시에는 환불돼 값이 되돌아온다.
    await refreshCredits();
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

onMounted(loadAll);
onUnmounted(stopLoadingMessages);

// App.vue 가 onMounted 에서 authStore.initialize() 를 await 하므로, 새로고침 직후에는
// 이 컴포넌트의 onMounted 시점에 아직 isLoggedIn=false 다 (→ loadAll 이 조기 반환).
watch(
  () => authStore.isLoggedIn,
  (loggedIn) => {
    if (loggedIn) loadAll();
  }
);
</script>

<style scoped>
.create-page {
  min-height: calc(100vh - 80px);
  background: #f9fafb;
  padding: 2rem 1.5rem 4rem;
}

/* 스튜디오(880px)보다 훨씬 넓게 — 결과를 크게 보는 게 이 화면의 목적 */
.create-container {
  max-width: 1440px;
  margin: 0 auto;
}

.back-link {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6d28d9;
  text-decoration: none;
  margin-bottom: 0.75rem;
}

.back-link:hover {
  text-decoration: underline;
}

.head-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.head-text h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.lead {
  color: #6b7280;
  margin: 0.5rem 0 0;
  max-width: 60ch;
  font-size: 0.9rem;
  line-height: 1.6;
}

/* 잔액 배지는 스튜디오(충전 화면)로 가는 링크다 — 잔액이 모자랄 때 바로 충전하러 갈 수 있게. */
.quota-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 0.15rem;
  background: linear-gradient(135deg, #ede9fe, #fae8ff);
  border-radius: 0.75rem;
  padding: 0.85rem 1.25rem;
  flex-shrink: 0;
  text-decoration: none;
  transition: box-shadow 0.2s;
}

.quota-badge:hover {
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.18);
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

.notice {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2.5rem;
  text-align: center;
  color: #6b7280;
}

/* 왼쪽 컨트롤 고정폭 / 오른쪽 결과가 남는 폭을 전부 */
.workspace {
  display: grid;
  grid-template-columns: 440px minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.controls {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: sticky;
  top: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label {
  font-size: 0.82rem;
  font-weight: 700;
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

textarea {
  resize: vertical;
  line-height: 1.6;
}

input[type="range"] {
  padding: 0;
  accent-color: #7c3aed;
}

.muted {
  color: #6b7280;
}

.small {
  font-size: 0.78rem;
  line-height: 1.55;
}

.ref-note {
  margin: 0 0 0.15rem;
}

.ref-note strong {
  color: #6d28d9;
}

.inline-link {
  color: #6d28d9;
  font-weight: 600;
}

.slider-value {
  float: right;
  font-weight: 700;
  color: #6d28d9;
  font-variant-numeric: tabular-nums;
}

/* 아바타 썸네일 + select */
.avatar-pick {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
}

.avatar-pick-controls {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.avatar-pick-controls .muted {
  margin: 0;
}

/* 참조 이미지 */
.source-row {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
}

.source-thumb {
  position: relative;
  flex-shrink: 0;
  width: 140px;
  height: 176px;
  border-radius: 0.7rem;
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

.source-badge {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.72);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 0.22rem 0;
  text-align: center;
}

.source-uploading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  font-size: 0.72rem;
  font-weight: 600;
  color: #6d28d9;
}

.source-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  min-width: 0;
}

.source-actions .muted {
  margin: 0;
}

/* 오른쪽: 결과 캔버스 */
.canvas {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem;
  min-height: 620px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
}

.canvas-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  width: 100%;
}

/* 뷰포트 높이에 맞춰 최대한 크게 */
.result-img {
  max-width: 100%;
  max-height: calc(100vh - 300px);
  border-radius: 0.85rem;
  border: 1px solid #e5e7eb;
  display: block;
}

.result-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: center;
}

.canvas-state,
.canvas-empty {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
}

.empty-icon {
  display: block;
  font-size: 3rem;
  opacity: 0.35;
  margin-bottom: 0.75rem;
}

.canvas-empty p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.7;
}

.canvas-empty strong {
  color: #6d28d9;
}

.state-msg {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0.75rem 0 0.25rem;
}

.state-sub {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0;
}

.session-strip {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
  padding-top: 0.5rem;
  border-top: 1px solid #f3f4f6;
}

.strip-thumb {
  width: 76px;
  height: 96px;
  border-radius: 0.6rem;
  overflow: hidden;
  border: 2px solid transparent;
  padding: 0;
  cursor: pointer;
  background: #f3f4f6;
}

.strip-thumb.active {
  border-color: #7c3aed;
}

.strip-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 생성 실패 리포트 — 자동으로 사라지지 않고 선택·복사 가능 */
.gen-error {
  border: 1px solid #fecaca;
  background: #fef2f2;
  border-radius: 0.75rem;
  overflow: hidden;
  width: 100%;
  max-width: 640px;
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
  user-select: text;
}

/* 버튼 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: linear-gradient(to right, #7c3aed, #9333ea);
  color: #fff;
  border: none;
  border-radius: 0.65rem;
  padding: 0.75rem 1.4rem;
  font-weight: 700;
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
  text-decoration: none;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.generate-btn {
  width: 100%;
  padding: 0.85rem 1.4rem;
  font-size: 0.95rem;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 0.65rem;
  padding: 0.75rem 1.4rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: #374151;
  cursor: pointer;
  text-decoration: none;
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
  font-family: inherit;
  white-space: nowrap;
  cursor: pointer;
}

.btn-outline:hover {
  background: #f5f3ff;
}

.btn-text {
  background: none;
  border: none;
  color: #6d28d9;
  font-weight: 600;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
}

/* 스피너 */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e9d5ff;
  border-top-color: #7c3aed;
  border-radius: 50%;
  margin: 0 auto;
  animation: spin 0.8s linear infinite;
}

.spinner-inline {
  display: inline-block;
  width: 0.9rem;
  height: 0.9rem;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

/* 좁은 화면에서는 컨트롤이 위, 결과가 아래 */
@media (max-width: 1024px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .controls {
    position: static;
  }

  .canvas {
    min-height: 420px;
  }

  .result-img {
    max-height: none;
  }
}

@media (max-width: 560px) {
  .create-page {
    padding: 1.5rem 1rem 3rem;
  }

  .head-text h1 {
    font-size: 1.6rem;
  }
}
</style>
