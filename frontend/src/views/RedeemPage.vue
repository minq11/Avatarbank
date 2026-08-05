<template>
  <div class="redeem-page">
    <div class="redeem-container">
      <!-- Loading code info -->
      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>불러오는 중…</p>
      </div>

      <!-- Invalid / expired code -->
      <div v-else-if="errorMessage && !info" class="state-box error">
        <h2>이 코드를 사용할 수 없어요</h2>
        <p>{{ errorMessage }}</p>
      </div>

      <!-- Redeem experience -->
      <template v-else-if="info">
        <header class="redeem-header">
          <img
            v-if="info.avatar_preview_url"
            :src="info.avatar_preview_url"
            :alt="info.avatar_title"
            class="creator-avatar"
          />
          <div>
            <p class="eyebrow">AI 포토부스</p>
            <h1 class="title">{{ info.creator_nickname }}</h1>
            <p class="subtitle">
              <strong>{{ info.avatar_title }}</strong>(으)로 원하는 장면의 나만의 사진을 만들어보세요.
            </p>
            <p v-if="info.uses_left !== null" class="uses">
              {{ info.uses_left }}회 남음
            </p>
          </div>
        </header>

        <!-- Result -->
        <div v-if="resultImage" class="result-box">
          <img :src="resultImage" alt="생성된 이미지" class="result-img" />

          <div class="result-actions">
            <a :href="resultImage" download="my-photo.png" class="btn-primary">⬇ 다운로드</a>
            <button v-if="canNativeShare" class="btn-secondary" @click="nativeShare">↗ 공유</button>
            <a class="btn-secondary" :href="xShareUrl" target="_blank" rel="noopener">X에 공유</a>
            <button class="btn-secondary" @click="copyPageLink">
              {{ linkCopied ? "✓ 복사됨" : "🔗 링크 복사" }}
            </button>
          </div>

          <button class="btn-ghost" @click="makeAnother">＋ 다른 사진 만들기</button>

          <!-- 이번 세션에 만든 것들 -->
          <div v-if="sessionResults.length > 1" class="session-strip">
            <button
              v-for="(img, i) in sessionResults"
              :key="i"
              class="strip-thumb"
              :class="{ active: img === resultImage }"
              @click="resultImage = img"
            >
              <img :src="img" alt="" />
            </button>
          </div>
        </div>

        <!-- Generating overlay -->
        <div v-else-if="generating" class="generating-box">
          <div class="spinner"></div>
          <p class="gen-msg">{{ loadingMessage }}</p>
          <p class="gen-sub">보통 몇 초 정도 걸려요.</p>
        </div>

        <!-- Generate -->
        <div v-else>
          <!-- 프롬프트 -->
          <div class="prompt-box">
            <textarea
              v-model="freePrompt"
              rows="3"
              placeholder="원하는 장면·의상·분위기를 묘사해 주세요… (건전한 내용만)"
              :disabled="generating"
            ></textarea>
          </div>

          <!-- image-to-image 옵션 -->
          <div class="source-box">
            <button type="button" class="fan-source-thumb" @click="sourceInput?.click()">
              <img :src="sourcePreview" alt="원본 사진" />
              <span v-if="usingDefaultSource" class="fan-source-badge">기본</span>
              <span v-if="uploadingSource" class="fan-source-uploading">올리는 중…</span>
            </button>
            <div class="fan-source-text">
              <strong>내 사진으로 만들기 (선택)</strong>
              <p>
                {{
                  usingDefaultSource
                    ? "기본 이미지가 원본으로 적용돼 있어요. 내 사진을 올리면 그걸 원본으로 써요."
                    : "올린 사진을 원본으로 변형해요."
                }}
              </p>
              <button v-if="!usingDefaultSource" class="link-btn" @click="clearSourceImage">
                기본 이미지로 되돌리기
              </button>
            </div>
          </div>
          <input
            ref="sourceInput"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            style="display: none"
            @change="onSourceSelected"
          />

          <div class="slider-box">
            <label>
              변형 강도
              <span class="slider-value">{{ strength.toFixed(2) }}</span>
            </label>
            <input v-model.number="strength" type="range" min="0.05" max="1" step="0.05" />
            <p class="slider-hint">낮을수록 원본에 가깝고, 높을수록 프롬프트를 강하게 반영해요.</p>
          </div>

          <button
            class="btn-primary generate-btn"
            :disabled="!canGenerate || generating || uploadingSource"
            @click="generate"
          >
            <span v-if="generating" class="spinner small"></span>
            {{ generating ? "사진 만드는 중…" : "내 사진 만들기" }}
          </button>
          <p v-if="errorMessage" class="inline-error">{{ errorMessage }}</p>
          <p class="disclaimer">{{ info.creator_nickname }}님의 얼굴로 만든 AI 이미지예요. 건전한 이미지만 생성됩니다.</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { redeemApi, studioApi, type RedeemInfo, type SourceImage } from "../services/api";

const route = useRoute();
const code = String(route.params.code || "");

const loading = ref(true);
const generating = ref(false);
const info = ref<RedeemInfo | null>(null);
const freePrompt = ref("");
const resultImage = ref<string | null>(null);
const sessionResults = ref<string[]>([]);
const errorMessage = ref<string>("");
const linkCopied = ref(false);

// image-to-image: 원본 사진 + 변형 강도.
// 업로드 전에는 서버가 실제로 쓰는 기본 이미지를 그대로 보여준다 (이미 탑재된 상태).
const sourceInput = ref<HTMLInputElement | null>(null);
const sourceImage = ref<SourceImage | null>(null);
const uploadedPreview = ref<string | null>(null);
const uploadingSource = ref(false);
const strength = ref(0.6);
const defaultSourceUrl = studioApi.defaultSourceImageUrl();
const sourcePreview = computed(() => uploadedPreview.value || defaultSourceUrl);
const usingDefaultSource = computed(() => !sourceImage.value);

const onSourceSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = "";
  if (!file) return;
  uploadingSource.value = true;
  errorMessage.value = "";
  try {
    const uploaded = await redeemApi.uploadSourceImage(code, file);
    sourceImage.value = uploaded;
    uploadedPreview.value = uploaded.preview_url;
  } catch (e: any) {
    errorMessage.value = extractError(e, "이미지 업로드에 실패했어요.");
  } finally {
    uploadingSource.value = false;
  }
};

const clearSourceImage = () => {
  sourceImage.value = null;
  uploadedPreview.value = null;
};

const canGenerate = computed(() => freePrompt.value.trim().length > 0);

// 공유 관련
const canNativeShare = typeof navigator !== "undefined" && !!(navigator as any).share;
const pageUrl = typeof window !== "undefined" ? window.location.href : "";
const xShareUrl = computed(() => {
  const text = `${info.value?.creator_nickname ?? "크리에이터"}님과 AI 사진을 만들었어요 ✨`;
  return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(pageUrl)}`;
});

const nativeShare = async () => {
  try {
    await (navigator as any).share({
      title: "내 AI 사진",
      text: `${info.value?.creator_nickname ?? "크리에이터"}님과 함께 만들었어요 ✨`,
      url: pageUrl,
    });
  } catch {
    /* user cancelled */
  }
};

const copyPageLink = async () => {
  try {
    await navigator.clipboard.writeText(pageUrl);
    linkCopied.value = true;
    setTimeout(() => (linkCopied.value = false), 1800);
  } catch {
    /* ignore */
  }
};

const makeAnother = () => {
  resultImage.value = null;
  errorMessage.value = "";
};

// 생성 대기 중 로딩 문구 로테이션
const LOADING_MESSAGES = [
  "카메라를 준비하는 중…",
  "장면을 연출하는 중…",
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

const extractError = (e: any, fallback: string): string =>
  e?.response?.data?.detail || fallback;

const loadInfo = async () => {
  loading.value = true;
  errorMessage.value = "";
  try {
    const data = await redeemApi.getInfo(code);
    info.value = data;
  } catch (e: any) {
    errorMessage.value = extractError(e, "유효하지 않거나 만료된 코드예요.");
    info.value = null;
  } finally {
    loading.value = false;
  }
};

const generate = async () => {
  if (!canGenerate.value) return;
  generating.value = true;
  errorMessage.value = "";
  startLoadingMessages();
  try {
    const res = await redeemApi.generate(code, {
      prompt: freePrompt.value.trim(),
      sourceImageUrl: sourceImage.value?.url ?? null,
      strength: strength.value,
    });
    if (res.status === "success" && res.image_url) {
      resultImage.value = res.image_url;
      sessionResults.value.push(res.image_url);
      if (info.value) info.value.uses_left = res.uses_left;
    } else {
      errorMessage.value = res.fail_reason || "생성에 실패했어요. 다시 시도해 주세요.";
    }
  } catch (e: any) {
    errorMessage.value = extractError(e, "생성에 실패했어요. 다시 시도해 주세요.");
  } finally {
    generating.value = false;
    stopLoadingMessages();
  }
};

onUnmounted(stopLoadingMessages);
onMounted(loadInfo);
</script>

<style scoped>
.redeem-page {
  min-height: calc(100vh - 80px);
  background: linear-gradient(180deg, #faf5ff 0%, #ffffff 40%);
  padding: 2.5rem 1rem 4rem;
}

.redeem-container {
  max-width: 720px;
  margin: 0 auto;
}

.state-box {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.state-box.error h2 {
  color: #111827;
  margin-bottom: 0.5rem;
}

.redeem-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.creator-avatar {
  width: 84px;
  height: 84px;
  border-radius: 9999px;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 6px 18px -8px rgba(79, 70, 229, 0.5);
  flex-shrink: 0;
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c3aed;
  margin: 0 0 0.25rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #4b5563;
  margin: 0.35rem 0 0;
  font-size: 0.95rem;
}

.uses {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: #9333ea;
  font-weight: 600;
}

.prompt-box {
  margin-bottom: 1.5rem;
}

/* image-to-image: 원본 사진 + 강도 */
.source-box {
  display: flex;
  gap: 0.9rem;
  align-items: center;
  padding: 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.85rem;
  background: #f9fafb;
  margin-bottom: 1rem;
}

.fan-source-thumb {
  position: relative;
  flex-shrink: 0;
  width: 64px;
  height: 80px;
  border-radius: 0.6rem;
  border: 1px solid #e5e7eb;
  background: #fff;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fan-source-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 기본 이미지가 적용 중임을 알리는 뱃지 */
.fan-source-badge {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.72);
  color: #fff;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.12rem 0;
  text-align: center;
}

.fan-source-uploading {
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

.fan-source-text {
  min-width: 0;
}

.fan-source-text strong {
  display: block;
  font-size: 0.9rem;
  color: #111827;
}

.fan-source-text p {
  margin: 0.2rem 0 0;
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.5;
}

.link-btn {
  background: none;
  border: none;
  padding: 0;
  margin-top: 0.35rem;
  color: #6d28d9;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.slider-box {
  margin-bottom: 1.25rem;
}

.slider-box label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.35rem;
}

.slider-box input[type="range"] {
  width: 100%;
  accent-color: #7c3aed;
}

.slider-value {
  float: right;
  color: #6d28d9;
  font-variant-numeric: tabular-nums;
}

.slider-hint {
  margin: 0.25rem 0 0;
  font-size: 0.78rem;
  color: #9ca3af;
}

.prompt-box textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  padding: 0.85rem 1rem;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(to right, #7c3aed, #9333ea);
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  padding: 0.85rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: box-shadow 0.2s, transform 0.1s;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 12px 22px -12px rgba(124, 58, 237, 0.7);
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.generate-btn {
  width: 100%;
}

.btn-secondary {
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  padding: 0.85rem 1.5rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
}

.result-box {
  text-align: center;
}

.result-img {
  width: 100%;
  max-width: 480px;
  border-radius: 1rem;
  box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.3);
}

.result-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.25rem;
}

.btn-ghost {
  margin-top: 0.85rem;
  background: none;
  border: none;
  color: #7c3aed;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.session-strip {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.strip-thumb {
  width: 56px;
  height: 72px;
  border-radius: 0.5rem;
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

.generating-box {
  text-align: center;
  padding: 3rem 1rem;
}

.gen-msg {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0.5rem 0 0.25rem;
}

.gen-sub {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0;
}

.inline-error {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.75rem;
  text-align: center;
}

.disclaimer {
  margin-top: 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e9d5ff;
  border-top-color: #7c3aed;
  border-radius: 50%;
  margin: 0 auto 0.75rem;
  animation: spin 0.8s linear infinite;
}

.spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
  margin: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Mobile (fan links open mostly on phones) */
@media (max-width: 560px) {
  .redeem-page {
    padding: 1.5rem 1rem 3rem;
  }

  .redeem-header {
    flex-direction: column;
    text-align: center;
    gap: 0.85rem;
  }

  .creator-avatar {
    width: 72px;
    height: 72px;
  }

  .title {
    font-size: 1.5rem;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions .btn-primary,
  .result-actions .btn-secondary {
    width: 100%;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.9rem 1.25rem;
  }
}
</style>
