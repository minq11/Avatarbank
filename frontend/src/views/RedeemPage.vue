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
            <a :href="resultImage" download="my-photo.png" class="btn-primary">Download</a>
            <button class="btn-secondary" @click="resultImage = null">Make another</button>
          </div>
        </div>

        <!-- Template grid -->
        <div v-else>
          <p v-if="info.templates.length === 0" class="state-box">
            This creator hasn't published any looks yet.
          </p>
          <div v-else class="template-grid">
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

          <button
            class="btn-primary generate-btn"
            :disabled="!selectedTemplateId || generating"
            @click="generate"
          >
            <span v-if="generating" class="spinner small"></span>
            {{ generating ? "Creating your picture…" : "Create my picture" }}
          </button>
          <p v-if="errorMessage" class="inline-error">{{ errorMessage }}</p>
          <p class="disclaimer">AI-generated image. Looks are pre-approved by the creator.</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { redeemApi, type RedeemInfo } from "../services/api";

const route = useRoute();
const code = String(route.params.code || "");

const loading = ref(true);
const generating = ref(false);
const info = ref<RedeemInfo | null>(null);
const selectedTemplateId = ref<number | null>(null);
const resultImage = ref<string | null>(null);
const errorMessage = ref<string>("");

const extractError = (e: any, fallback: string): string =>
  e?.response?.data?.detail || fallback;

const loadInfo = async () => {
  loading.value = true;
  errorMessage.value = "";
  try {
    info.value = await redeemApi.getInfo(code);
    if (info.value.templates.length === 1) {
      selectedTemplateId.value = info.value.templates[0].id;
    }
  } catch (e: any) {
    errorMessage.value = extractError(e, "This code is invalid or has expired.");
    info.value = null;
  } finally {
    loading.value = false;
  }
};

const generate = async () => {
  if (!selectedTemplateId.value) return;
  generating.value = true;
  errorMessage.value = "";
  try {
    const res = await redeemApi.generate(code, selectedTemplateId.value);
    if (res.status === "success" && res.image_url) {
      resultImage.value = res.image_url;
      if (info.value) info.value.uses_left = res.uses_left;
    } else {
      errorMessage.value = res.fail_reason || "Generation failed. Please try again.";
    }
  } catch (e: any) {
    errorMessage.value = extractError(e, "Generation failed. Please try again.");
  } finally {
    generating.value = false;
  }
};

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
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1.25rem;
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
