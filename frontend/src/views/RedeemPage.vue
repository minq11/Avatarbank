<template>
  <div class="redeem-page">
    <div class="redeem-container">
      <!-- Loading code info -->
      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>Loading…</p>
      </div>

      <!-- Invalid / expired code -->
      <div v-else-if="errorMessage && !info" class="state-box error">
        <h2>Can't use this code</h2>
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
            <p class="eyebrow">AI Photo Booth</p>
            <h1 class="title">{{ info.creator_nickname }}</h1>
            <p class="subtitle">
              Pick a look and create your own picture with
              <strong>{{ info.avatar_title }}</strong>.
            </p>
            <p v-if="info.uses_left !== null" class="uses">
              {{ info.uses_left }} use{{ info.uses_left === 1 ? "" : "s" }} left
            </p>
          </div>
        </header>

        <!-- Result -->
        <div v-if="resultImage" class="result-box">
          <img :src="resultImage" alt="Your generated image" class="result-img" />

          <div class="result-actions">
            <a :href="resultImage" download="my-photo.png" class="btn-primary">⬇ Download</a>
            <button v-if="canNativeShare" class="btn-secondary" @click="nativeShare">↗ Share</button>
            <a class="btn-secondary" :href="xShareUrl" target="_blank" rel="noopener">Share on X</a>
            <button class="btn-secondary" @click="copyPageLink">
              {{ linkCopied ? "✓ Copied" : "🔗 Copy link" }}
            </button>
          </div>

          <button class="btn-ghost" @click="makeAnother">＋ Make another</button>

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
          <p class="gen-sub">This usually takes a few seconds.</p>
        </div>

        <!-- Generate -->
        <div v-else>
          <!-- Mode switch (only when both options exist) -->
          <div v-if="info.free_prompt_allowed && info.templates.length" class="mode-tabs">
            <button
              class="mode-tab"
              :class="{ active: mode === 'template' }"
              @click="mode = 'template'"
            >
              Pick a look
            </button>
            <button
              class="mode-tab"
              :class="{ active: mode === 'prompt' }"
              @click="mode = 'prompt'"
            >
              Describe your own
            </button>
          </div>

          <!-- Template grid -->
          <div v-if="mode === 'template' && info.templates.length" class="template-grid">
            <button
              v-for="t in info.templates"
              :key="t.id"
              class="template-card"
              :class="{ selected: selectedTemplateId === t.id }"
              :disabled="generating"
              @click="selectedTemplateId = t.id"
            >
              <div class="template-thumb">
                <img v-if="t.preview_image_url" :src="t.preview_image_url" :alt="t.name" />
                <span v-else class="thumb-placeholder">{{ t.name.charAt(0) }}</span>
              </div>
              <span class="template-name">{{ t.name }}</span>
            </button>
          </div>

          <!-- Free prompt -->
          <div v-if="mode === 'prompt'" class="prompt-box">
            <textarea
              v-model="freePrompt"
              rows="3"
              placeholder="Describe the scene, outfit, or vibe you want… (keep it safe-for-work)"
              :disabled="generating"
            ></textarea>
          </div>

          <button
            class="btn-primary generate-btn"
            :disabled="!canGenerate || generating"
            @click="generate"
          >
            <span v-if="generating" class="spinner small"></span>
            {{ generating ? "Creating your picture…" : "Create my picture" }}
          </button>
          <p v-if="errorMessage" class="inline-error">{{ errorMessage }}</p>
          <p class="disclaimer">AI-generated image with {{ info.creator_nickname }}'s likeness. SFW only.</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { redeemApi, type RedeemInfo } from "../services/api";

const route = useRoute();
const code = String(route.params.code || "");

const loading = ref(true);
const generating = ref(false);
const info = ref<RedeemInfo | null>(null);
const mode = ref<"template" | "prompt">("template");
const selectedTemplateId = ref<number | null>(null);
const freePrompt = ref("");
const resultImage = ref<string | null>(null);
const sessionResults = ref<string[]>([]);
const errorMessage = ref<string>("");
const linkCopied = ref(false);

const canGenerate = computed(() => {
  if (mode.value === "template") return selectedTemplateId.value != null;
  return freePrompt.value.trim().length > 0;
});

// 공유 관련
const canNativeShare = typeof navigator !== "undefined" && !!(navigator as any).share;
const pageUrl = typeof window !== "undefined" ? window.location.href : "";
const xShareUrl = computed(() => {
  const text = `I just made an AI photo with ${info.value?.creator_nickname ?? "a creator"} ✨`;
  return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(pageUrl)}`;
});

const nativeShare = async () => {
  try {
    await (navigator as any).share({
      title: "My AI photo",
      text: `Made with ${info.value?.creator_nickname ?? "a creator"} ✨`,
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
  "Warming up the camera…",
  "Styling the shot…",
  "Adding the finishing touches…",
  "Almost ready…",
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
    if (data.templates.length === 1) {
      selectedTemplateId.value = data.templates[0].id;
    }
    // 템플릿이 없고 자유 프롬프트만 가능하면 프롬프트 모드로
    mode.value = data.templates.length === 0 && data.free_prompt_allowed ? "prompt" : "template";
  } catch (e: any) {
    errorMessage.value = extractError(e, "This code is invalid or has expired.");
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
    const opts =
      mode.value === "template"
        ? { templateId: selectedTemplateId.value }
        : { prompt: freePrompt.value.trim() };
    const res = await redeemApi.generate(code, opts);
    if (res.status === "success" && res.image_url) {
      resultImage.value = res.image_url;
      sessionResults.value.push(res.image_url);
      if (info.value) info.value.uses_left = res.uses_left;
    } else {
      errorMessage.value = res.fail_reason || "Generation failed. Please try again.";
    }
  } catch (e: any) {
    errorMessage.value = extractError(e, "Generation failed. Please try again.");
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

.mode-tabs {
  display: inline-flex;
  gap: 0.25rem;
  background: #f3f4f6;
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 1.25rem;
}

.mode-tab {
  border: none;
  background: transparent;
  border-radius: 0.55rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
}

.mode-tab.active {
  background: #fff;
  color: #111827;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.prompt-box {
  margin-bottom: 1.5rem;
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

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.template-card {
  border: 2px solid #e5e7eb;
  border-radius: 1rem;
  background: #fff;
  padding: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.template-card:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -12px rgba(124, 58, 237, 0.4);
}

.template-card.selected {
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.template-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.template-thumb {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 0.75rem;
  overflow: hidden;
  background: linear-gradient(135deg, #ede9fe, #fae8ff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  font-size: 2rem;
  font-weight: 700;
  color: #a78bfa;
}

.template-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  text-align: center;
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
</style>
