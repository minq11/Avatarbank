<template>
  <div class="redeem-page">
    <div class="redeem-container">
      <!-- Loading code info -->
      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>불러오는 중…</p>
      </div>

      <!-- Invalid / expired link -->
      <div v-else-if="errorMessage && !info" class="state-box error">
        <h2>이 링크를 사용할 수 없어요</h2>
        <p>{{ errorMessage }}</p>
      </div>

      <!-- Redeem experience -->
      <template v-else-if="info">
        <!-- 아바타 얼굴은 아래 컨트롤에서 보여준다 — 여기서 또 띄우면 같은 사진이 두 번 -->
        <header class="redeem-header">
          <div class="header-text">
            <p class="eyebrow">AI 포토부스</p>
            <h1 class="title">{{ info.creator_nickname }}</h1>
            <p class="subtitle">
              <strong>{{ info.avatar_title }}</strong>(으)로 원하는 장면의 나만의 사진을
              만들어보세요.
            </p>
          </div>
          <div v-if="info.uses_left !== null" class="uses-badge">
            <span class="uses-num">{{ info.uses_left }}</span>
            <span class="uses-label">회 남음</span>
          </div>
        </header>

        <!-- 왼쪽 컨트롤 / 오른쪽 큰 결과 — 스튜디오 '직접 만들기'와 같은 구조 -->
        <div class="workspace">
          <div class="controls">
            <!-- 아바타 — 이 링크에 고정돼 있어 고르지 않는다 -->
            <div class="field">
              <label>아바타</label>
              <div class="avatar-pick">
                <AvatarPickPreview
                  :title="info.avatar_title"
                  :preview-url="info.avatar_preview_url"
                />
                <div class="avatar-pick-controls">
                  <p class="fixed-avatar">{{ info.avatar_title }}</p>
                  <p class="muted small">
                    {{ info.creator_nickname }}님이 공유한 링크의 아바타예요.
                    이 얼굴로 생성됩니다.
                  </p>
                </div>
              </div>
            </div>

            <div class="field">
              <label>참조 이미지</label>
              <p class="muted small ref-note">
                참조 이미지와 <strong>비슷한 구도·분위기</strong>의 장면을 만들어요.
                얼굴은 위 아바타로 바뀝니다.
              </p>
              <div class="source-row">
                <button type="button" class="source-thumb" @click="sourceInput?.click()">
                  <img :src="sourcePreview" alt="참조 이미지" />
                  <span v-if="usingDefaultSource" class="source-badge">기본</span>
                  <span v-if="uploadingSource" class="source-uploading">올리는 중…</span>
                </button>
                <div class="source-actions">
                  <button type="button" class="btn-outline" @click="sourceInput?.click()">
                    {{ usingDefaultSource ? "내 사진 올리기" : "사진 바꾸기" }}
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
                        ? "지금은 기본 참조 이미지가 적용돼 있어요. 내 사진을 올리면 그 사진을 참조해요."
                        : "올린 사진을 참조해요."
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
                v-model="freePrompt"
                rows="5"
                placeholder="원하는 장면·의상·분위기를 자유롭게 묘사하세요 (예: 노을 지는 해변, 리넨 셔츠, 영화 같은 조명)"
                :disabled="generating"
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

            <button
              class="btn-primary generate-btn"
              :disabled="!canGenerate || generating || uploadingSource"
              @click="generate"
            >
              <span v-if="generating" class="spinner-inline"></span>
              {{ generating ? "사진 만드는 중…" : "내 사진 만들기" }}
            </button>

            <p v-if="errorMessage" class="inline-error">{{ errorMessage }}</p>
            <p class="disclaimer">
              {{ info.creator_nickname }}님의 얼굴로 만든 AI 이미지예요. 건전한 이미지만
              생성됩니다.
            </p>
          </div>

          <section class="canvas">
            <!-- 생성 중 -->
            <div v-if="generating" class="canvas-state">
              <div class="spinner"></div>
              <p class="state-msg">{{ loadingMessage }}</p>
              <p class="state-sub">보통 몇 초 정도 걸려요.</p>
            </div>

            <!-- 결과 -->
            <div v-else-if="resultImage" class="canvas-result">
              <img :src="resultImage" alt="생성된 이미지" class="result-img" />
              <div class="result-actions">
                <a :href="resultImage" download="my-photo.png" class="btn-primary">⬇ 다운로드</a>
                <button v-if="canNativeShare" class="btn-secondary" @click="nativeShare">
                  ↗ 공유
                </button>
                <a class="btn-secondary" :href="xShareUrl" target="_blank" rel="noopener">
                  X에 공유
                </a>
                <button class="btn-secondary" @click="copyPageLink">
                  {{ linkCopied ? "✓ 복사됨" : "🔗 링크 복사" }}
                </button>
              </div>
            </div>

            <!-- 아직 아무것도 안 만든 상태 -->
            <div v-else class="canvas-empty">
              <span class="empty-icon" aria-hidden="true">📷</span>
              <p>
                왼쪽에 원하는 장면을 적고 <strong>내 사진 만들기</strong>를 눌러보세요.
              </p>
            </div>

            <!-- 이번에 만든 사진들 -->
            <div v-if="sessionResults.length > 1" class="session-strip">
              <button
                v-for="(img, i) in sessionResults"
                :key="i"
                type="button"
                class="strip-thumb"
                :class="{ active: img === resultImage }"
                @click="resultImage = img"
              >
                <img :src="img" alt="" />
              </button>
            </div>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import AvatarPickPreview from "../components/AvatarPickPreview.vue";
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

// image-to-image: 참조 이미지 + 일치도(strength).
// 올린 사진을 그대로 되살리는 게 아니라, 그 구도·분위기를 참조해 비슷한 장면을 새로 만든다.
// 업로드 전에는 서버가 실제로 쓰는 기본 이미지를 그대로 보여준다 (이미 탑재된 상태).
const sourceInput = ref<HTMLInputElement | null>(null);
const sourceImage = ref<SourceImage | null>(null);
const uploadedPreview = ref<string | null>(null);
const uploadingSource = ref(false);
const strength = ref(0.6);

// 화면에는 "참조 이미지 일치도"로 보여준다 — strength 와 방향이 반대다.
// strength 는 참조에서 얼마나 멀어질지라서, 일치도 = 1 - strength.
// API 로는 계속 strength 를 보낸다.
const refMatch = computed({
  get: () => Number((1 - strength.value).toFixed(2)),
  set: (v: number) => {
    strength.value = Number((1 - v).toFixed(2));
  },
});
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
    errorMessage.value = extractError(e, "유효하지 않거나 만료된 링크예요.");
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
  background: linear-gradient(180deg, #fdf5f0 0%, #ffffff 40%);
  padding: 2rem 1.5rem 4rem;
}

/* 결과를 크게 보는 화면이라 넓게 쓴다 (예전 720px) */
.redeem-container {
  max-width: 1440px;
  margin: 0 auto;
}

.state-box {
  text-align: center;
  padding: 4rem 1rem;
  color: #6e6e77;
}

.state-box.error h2 {
  color: #0d0d0f;
  margin-bottom: 0.5rem;
}

/* 헤더 */
.redeem-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.header-text {
  flex: 1;
  min-width: 0;
}




.eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #e24e12;
  margin: 0 0 0.25rem;
}

.title {
  font-size: 1.9rem;
  font-weight: 800;
  color: #0d0d0f;
  margin: 0;
}

.subtitle {
  color: #52525b;
  margin: 0.35rem 0 0;
  font-size: 0.95rem;
}

.uses-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 0.25rem;
  background: linear-gradient(135deg, #fdede4, #fce3d6);
  border-radius: 0.75rem;
  padding: 0.75rem 1.15rem;
  flex-shrink: 0;
}

.uses-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #c24210;
  font-variant-numeric: tabular-nums;
}

.uses-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6e6e77;
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
  border: 1px solid #e6e6ea;
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
  color: #3a3a42;
}

textarea,
input[type="range"] {
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

textarea {
  border: 1px solid #d2d2d9;
  border-radius: 0.6rem;
  padding: 0.75rem 0.9rem;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
}

input[type="range"] {
  padding: 0;
  accent-color: #e24e12;
}

.muted {
  color: #6e6e77;
}

.small {
  font-size: 0.78rem;
  line-height: 1.55;
  margin: 0;
}

.ref-note {
  margin: 0 0 0.35rem;
}

.ref-note strong {
  color: #c24210;
}

.slider-value {
  float: right;
  font-weight: 700;
  color: #c24210;
  font-variant-numeric: tabular-nums;
}

/* 아바타 — 이 화면에선 고정이라 select 대신 이름만 */
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
  gap: 0.35rem;
}

.fixed-avatar {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #0d0d0f;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 참조 이미지 — /studio/create 와 같은 규격 */
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
  border: 1px solid #e6e6ea;
  background: #fafafa;
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
  color: #c24210;
}

.source-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  min-width: 0;
}

/* 오른쪽: 결과 캔버스 */
.canvas {
  background: #fff;
  border: 1px solid #e6e6ea;
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
  box-shadow: 0 20px 40px -22px rgba(0, 0, 0, 0.35);
  display: block;
}

.result-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
  flex-wrap: wrap;
}

.canvas-state,
.canvas-empty {
  text-align: center;
  color: #9a9aa3;
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
  color: #c24210;
}

.state-msg {
  font-size: 1rem;
  font-weight: 600;
  color: #3a3a42;
  margin: 0.75rem 0 0.25rem;
}

.state-sub {
  font-size: 0.85rem;
  color: #9a9aa3;
  margin: 0;
}

.session-strip {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
  padding-top: 0.5rem;
  border-top: 1px solid #f2f2f4;
}

.strip-thumb {
  width: 76px;
  height: 96px;
  border-radius: 0.6rem;
  overflow: hidden;
  border: 2px solid transparent;
  padding: 0;
  cursor: pointer;
  background: #f2f2f4;
}

.strip-thumb.active {
  border-color: #e24e12;
}

.strip-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 버튼 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: linear-gradient(to right, #e24e12, #f2703a);
  color: #fff;
  border: none;
  border-radius: 0.7rem;
  padding: 0.8rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  text-decoration: none;
  transition: box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 12px 22px -12px rgba(226, 78, 18, 0.7);
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.generate-btn {
  width: 100%;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #d2d2d9;
  border-radius: 0.7rem;
  padding: 0.8rem 1.4rem;
  font-weight: 600;
  font-size: 0.9rem;
  font-family: inherit;
  color: #3a3a42;
  cursor: pointer;
  text-decoration: none;
}

.btn-outline {
  background: #fff;
  border: 1px solid #fbd9c6;
  color: #c24210;
  border-radius: 0.5rem;
  padding: 0.55rem 0.85rem;
  font-weight: 700;
  font-size: 0.8rem;
  font-family: inherit;
  white-space: nowrap;
  cursor: pointer;
}

.btn-outline:hover {
  background: #fdf5f0;
}

.btn-text {
  background: none;
  border: none;
  padding: 0;
  color: #c24210;
  font-size: 0.78rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
}

.inline-error {
  color: #dc2626;
  font-size: 0.85rem;
  margin: 0;
}

.disclaimer {
  font-size: 0.75rem;
  color: #9a9aa3;
  margin: 0;
  line-height: 1.6;
}

/* 스피너 */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #fbd9c6;
  border-top-color: #e24e12;
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

/* 좁은 화면에서는 컨트롤이 위, 결과가 아래 */
@media (max-width: 1024px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .controls {
    position: static;
  }

  .canvas {
    min-height: 380px;
  }

  .result-img {
    max-height: none;
  }
}

/* Mobile (fan links open mostly on phones) */
@media (max-width: 560px) {
  .redeem-page {
    padding: 1.5rem 1rem 3rem;
  }

  .redeem-header {
    gap: 0.85rem;
  }

  .title {
    font-size: 1.5rem;
  }

  .controls {
    padding: 1.25rem;
  }

  .result-actions {
    flex-direction: column;
    width: 100%;
  }

  .result-actions .btn-primary,
  .result-actions .btn-secondary {
    width: 100%;
  }
}
</style>
