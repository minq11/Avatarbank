<template>
  <section class="generation">
    <div class="layout" :class="{ 'layout-no-avatar': !avatarId }">
      <div v-if="avatarId != null" class="left">
        <!-- 아바타 미리보기 (LoRA 선택 시에만 표시) -->
        <div v-if="avatar" class="avatar-preview">
          <div v-if="avatar.preview_image_url" class="preview-img-wrap">
            <img :src="getImageUrl(avatar.preview_image_url)" :alt="avatar.title" class="preview-img" />
          </div>
          <div v-else class="preview-placeholder">
            <span>No preview</span>
          </div>
          <p class="avatar-name">{{ avatar.title }}</p>
          <p v-if="avatar.credit_per_generation != null" class="avatar-credit">
            {{ avatar.credit_per_generation }} C per generation
          </p>
          <div v-if="avatar.description" class="avatar-detail-block">
            <span class="avatar-detail-label">Description</span>
            <p class="avatar-detail-value">{{ avatar.description }}</p>
          </div>
          <div v-if="avatar.negative_prompt" class="avatar-detail-block">
            <span class="avatar-detail-label">Negative prompt</span>
            <p class="avatar-detail-value avatar-detail-mono">{{ avatar.negative_prompt }}</p>
          </div>
        </div>
        <div v-else-if="avatarError" class="error-state">
          <p>{{ avatarError }}</p>
          <router-link to="/market" class="link">Browse avatars</router-link>
        </div>
        <div v-else class="loading-state">
          <p>Loading avatar...</p>
        </div>
      </div>

      <div class="right">
        <h2>AI Image Generation</h2>

        <label class="field">
          <span>Select Avatar (LoRA)</span>
          <SearchableSelect
            :model-value="avatarId ?? ''"
            :options="avatarSelectOptions"
            placeholder="— Select an avatar —"
            @update:model-value="onSelectAvatarValue"
          />
          <p v-if="avatarsList.length === 0 && !avatarsListLoading" class="field-hint">No avatars available.</p>
        </label>

        <label class="field field-prompt">
          <span>Prompt</span>
          <textarea
            v-model="prompt"
            rows="8"
            placeholder="Describe the image you want (English recommended)."
            class="prompt-textarea"
          />
        </label>

        <label class="field">
          <span>Negative prompt <span class="field-optional">(optional)</span></span>
          <textarea
            v-model="negativePrompt"
            rows="2"
            placeholder="What to avoid in the image (defaults to avatar's negative prompt if empty)."
            class="field-textarea-mono"
          />
        </label>

        <div class="options-card">
          <h4 class="options-card-title">Generation options</h4>
          <div class="options-grid">
            <div class="option-row option-row-toggle">
              <span class="option-label">Allow NSFW</span>
              <label class="option-toggle">
                <input type="checkbox" v-model="allowNsfw" class="option-checkbox" />
                <span class="option-toggle-text">{{ allowNsfw ? "On" : "Off" }}</span>
              </label>
            </div>
            <div class="option-row">
              <label class="option-label" for="opt-image-size">Image size</label>
              <select id="opt-image-size" v-model="imageSize" class="option-select">
                <option v-for="opt in imageSizeOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="option-row">
              <label class="option-label" for="opt-steps">Inference steps</label>
              <select id="opt-steps" v-model.number="numInferenceSteps" class="option-select">
                <option v-for="n in [4, 6, 8, 10, 12]" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div class="option-row">
              <label class="option-label" for="opt-format">Output format</label>
              <select id="opt-format" v-model="outputFormat" class="option-select">
                <option v-for="opt in outputFormatOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="option-row">
              <label class="option-label" for="opt-seed">Seed</label>
              <input
                id="opt-seed"
                v-model="seedInput"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                class="option-input"
                placeholder="Random"
              />
            </div>
          </div>
        </div>

        <div v-if="avatar" class="cost-info">
          <span>Base {{ baseCredit }} C + Avatar {{ avatarCredit }} C</span>
          <span>Total: {{ totalCredits }} C</span>
        </div>

        <div class="button-wrap">
        <button
          class="btn primary"
          :disabled="!canSubmit"
          @click="requestGeneration"
        >
          {{ loading ? "Generating..." : "Generate Image" }}
        </button>
        </div>

        <p v-if="!authStore.isLoggedIn && avatar && prompt.trim()" class="login-hint">
          Please log in to generate images.
        </p>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="generationId && !resultImageUrl && !error" class="info">
          Request submitted. ID: {{ generationId }}
        </p>
      </div>
    </div>

    <!-- 결과 영역 (입력 폼과 구분) -->
    <div v-if="avatarId != null" class="result-area">
      <div v-if="resultImageUrl" class="result-section">
        <div class="result-section-header">
          <h4>Generated Image</h4>
          <div class="result-actions">
            <button
              type="button"
              class="btn-result-action"
              :class="{ 'is-shared': resultIsShared }"
              :title="resultIsShared ? 'Shared to Gallery' : 'Share to Gallery'"
              @click="toggleResultShare"
            >
              <img src="@/assets/icons/shareBtn.svg" alt="" class="btn-result-icon" />
              {{ resultIsShared ? 'Shared' : 'Share' }}
            </button>
            <button
              type="button"
              class="btn-result-action btn-download"
              title="Download"
              @click="downloadResultImage"
            >
              <img src="@/assets/icons/downloadBtn.svg" alt="" class="btn-result-icon" />
              Download
            </button>
          </div>
        </div>
        <div class="result-img-wrap">
          <img :src="getImageUrl(resultImageUrl)" alt="Generated" class="result-img" />
        </div>
      </div>
      <p v-else class="note">Generated image will appear here after generation.</p>
    </div>

    <!-- 선택된 아바타로 만들어진 공유 결과물 (shared만) -->
    <div v-if="avatarId != null" class="shared-by-avatar-area">
      <div class="shared-by-avatar-container">
        <h3 class="shared-by-avatar-title">Shared creations with this avatar</h3>
        <div v-if="sharedByAvatarLoading" class="shared-loading">
          <div class="loading-spinner" aria-hidden="true"></div>
          <p class="loading-text">Loading…</p>
        </div>
        <div v-else-if="sharedByAvatar.length === 0" class="shared-empty">
          <p>No shared creations yet with this avatar.</p>
        </div>
        <div v-else class="shared-grid">
          <article
            v-for="item in sharedByAvatar"
            :key="item.id"
            class="shared-card"
          >
            <div class="shared-thumb-wrap">
              <img
                :src="item.image_url"
                :alt="item.prompt"
                class="shared-thumb"
                loading="lazy"
              />
            </div>
            <div class="shared-meta">
              <p class="shared-prompt" :title="item.prompt">{{ truncate(item.prompt, 48) }}</p>
              <div class="shared-footer">
                <span class="shared-creator">@{{ item.creator_nickname }}</span>
                <span class="shared-date">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import SearchableSelect from "@/components/SearchableSelect.vue";
import { useAuthStore } from "@/stores/auth";
import {
  avatarsApi,
  generationsApi,
  galleryApi,
  type AvatarItem,
  type GalleryItem,
  type ImageSizeOption,
  type OutputFormatOption,
} from "@/services/api";

const authStore = useAuthStore();

function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("/static/")) return `/api${url}`;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return url;
}

async function downloadResultImage() {
  if (!resultImageUrl.value) return;
  const url = getImageUrl(resultImageUrl.value);
  const filename = `generation_${generationId.value ?? "image"}.png`;
  await downloadImage(url, filename);
}

async function downloadImage(url: string, filename: string) {
  try {
    const res = await fetch(url, { mode: "cors" });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch {
    window.open(url, "_blank", "noopener");
  }
}

async function toggleResultShare() {
  const id = generationId.value;
  if (id == null) return;
  const message = resultIsShared.value
    ? "Remove this creation from Gallery?"
    : "Share this creation to Gallery? It will be visible to everyone.";
  if (!window.confirm(message)) return;
  try {
    const updated = await generationsApi.toggleShare(id);
    resultIsShared.value = updated.is_shared === true;
    await loadSharedByAvatar();
  } catch {
    // ignore
  }
}

const route = useRoute();
const router = useRouter();
const avatarId = computed(() => {
  const id = route.params.id;
  if (typeof id === "string" && /^\d+$/.test(id)) return parseInt(id, 10);
  return null;
});

const avatarsList = ref<AvatarItem[]>([]);
const avatarsListLoading = ref(true);
const avatar = ref<AvatarItem | null>(null);
const avatarError = ref("");
const prompt = ref("");
const DEFAULT_NEGATIVE_PROMPT = "ugly, low quality, distorted face";
const negativePrompt = ref(DEFAULT_NEGATIVE_PROMPT);
const allowNsfw = ref(false);
const imageSize = ref<ImageSizeOption>("landscape_4_3");
const numInferenceSteps = ref(8);
const outputFormat = ref<OutputFormatOption>("png");
const seedInput = ref("");
const loading = ref(false);

const imageSizeOptions: { value: ImageSizeOption; label: string }[] = [
  { value: "landscape_4_3", label: "Landscape 4:3" },
  { value: "landscape_16_9", label: "Landscape 16:9" },
  { value: "portrait_4_3", label: "Portrait 4:3" },
  { value: "portrait_16_9", label: "Portrait 16:9" },
  { value: "square", label: "Square" },
  { value: "square_hd", label: "Square HD" },
];
const outputFormatOptions: { value: OutputFormatOption; label: string }[] = [
  { value: "png", label: "PNG" },
  { value: "jpeg", label: "JPEG" },
  { value: "webp", label: "WebP" },
];
const error = ref("");
const generationId = ref<number | null>(null);
const resultImageUrl = ref<string | null>(null);
const resultIsShared = ref(false);

const sharedByAvatar = ref<GalleryItem[]>([]);
const sharedByAvatarLoading = ref(false);

const baseCredit = 1;
const avatarCredit = computed(
  () => avatar.value?.credit_per_generation ?? 0
);
const totalCredits = computed(
  () => baseCredit + (avatar.value?.credit_per_generation ?? 0)
);
const canSubmit = computed(
  () => !!avatar.value && !!prompt.value.trim() && !loading.value
);

async function loadAvatar() {
  const id = avatarId.value;
  if (id == null) {
    avatar.value = null;
    avatarError.value = "";
    negativePrompt.value = DEFAULT_NEGATIVE_PROMPT;
    return;
  }
  avatar.value = null;
  avatarError.value = "";
  try {
    const a = await avatarsApi.getById(id);
    avatar.value = a;
    negativePrompt.value = a.negative_prompt?.trim() || DEFAULT_NEGATIVE_PROMPT;
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    avatarError.value = msg || "Failed to load avatar.";
  }
}

async function requestGeneration() {
  if (!authStore.isLoggedIn) {
    error.value = "Please log in.";
    return;
  }
  if (!canSubmit.value || avatarId.value == null) return;
  loading.value = true;
  error.value = "";
  generationId.value = null;
  resultImageUrl.value = null;
  resultIsShared.value = false;

  try {
    const seedNum = seedInput.value.trim() === "" ? null : parseInt(seedInput.value, 10);
    const res = await generationsApi.create({
      avatar_id: avatarId.value,
      prompt: prompt.value.trim(),
      negative_prompt: negativePrompt.value.trim() || undefined,
      option_credits: 0,
      idempotency_key: crypto.randomUUID(),
      enable_safety_checker: !allowNsfw.value,
      image_size: imageSize.value,
      num_inference_steps: numInferenceSteps.value,
      output_format: outputFormat.value,
      seed: seedNum !== null && !Number.isNaN(seedNum) ? seedNum : null,
    });
    generationId.value = res.id;
    resultIsShared.value = res.is_shared === true;
    if (res.status === "success" && res.image_url) {
      resultImageUrl.value = res.image_url;
      error.value = "";
    } else if (res.status === "failed") {
      error.value = res.fail_reason
        ? `Generation failed: ${res.fail_reason}`
        : "Generation failed.";
    } else {
      resultImageUrl.value = res.image_url || null;
    }
    await authStore.fetchUser();
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status;
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    if (status === 401 || status === 403) {
      error.value = "Please log in.";
    } else {
      error.value = msg ?? "Failed to submit the generation request.";
    }
  } finally {
    loading.value = false;
  }
}

const avatarSelectOptions = computed(() =>
  avatarsList.value.map((a) => ({
    value: a.id,
    label: `${a.title} (${a.credit_per_generation != null ? a.credit_per_generation : 1} C)`,
    searchText: a.title,
  }))
);

function onSelectAvatarValue(value: number | string | "") {
  if (value !== "" && value != null) {
    router.push(`/avatars/${value}`);
  }
}

function truncate(s: string, max: number): string {
  if (s.length <= max) return s;
  return s.slice(0, max) + "…";
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

async function loadSharedByAvatar() {
  const id = avatarId.value;
  if (id == null) {
    sharedByAvatar.value = [];
    return;
  }
  sharedByAvatarLoading.value = true;
  try {
    sharedByAvatar.value = await galleryApi.getGenerations(id);
  } catch {
    sharedByAvatar.value = [];
  } finally {
    sharedByAvatarLoading.value = false;
  }
}

async function loadAvatarsList() {
  avatarsListLoading.value = true;
  try {
    avatarsList.value = await avatarsApi.getList();
  } catch {
    avatarsList.value = [];
  } finally {
    avatarsListLoading.value = false;
  }
}

onMounted(() => {
  loadAvatarsList();
  const q = route.query.prompt;
  if (typeof q === "string" && q.trim()) {
    prompt.value = q.trim();
  }
});
watch(avatarId, loadAvatar, { immediate: true });
watch(avatarId, loadSharedByAvatar, { immediate: true });
</script>

<style scoped>
.generation {
  display: flex;
  flex-direction: column;
  padding: 2rem 0;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.layout.layout-no-avatar {
  grid-template-columns: 1fr;
}

.left {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.avatar-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  padding: 1rem;
}

.preview-img-wrap,
.preview-placeholder {
  border-radius: 12px;
  aspect-ratio: 1;
  overflow: hidden;
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 0.9rem;
}

.avatar-name {
  font-weight: 600;
  font-size: 1.1rem;
  margin-top: 0.75rem;
  color: #111827;
}

.avatar-credit {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.avatar-detail-block {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}
.avatar-detail-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.35rem;
}
.avatar-detail-value {
  font-size: 0.875rem;
  color: #334155;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.avatar-detail-value.avatar-detail-mono {
  font-family: ui-monospace, monospace;
  font-size: 0.8125rem;
}

.result-area {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

.result-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.result-section-header h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-result-action {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.btn-result-action:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.btn-result-action.is-shared {
  color: #059669;
  border-color: #a7f3d0;
  background: #ecfdf5;
}

.btn-result-icon {
  width: 1rem;
  height: 1rem;
}

.result-img-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  aspect-ratio: 1;
  max-width: 400px;
  background: #f1f5f9;
}

.result-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.loading-state,
.error-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.error-state .link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.error-state .link:hover {
  text-decoration: underline;
}

.result-area .note {
  font-size: 0.9rem;
  color: #9ca3af;
  padding: 2rem;
  text-align: center;
  background: #f8fafc;
  border: 1px dashed #e2e8f0;
  border-radius: 12px;
}

.right h2 {
  font-size: 1.4rem;
  margin-bottom: 0.25rem;
}

.sub {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.cost-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #374151;
  margin-bottom: 1rem;
}

.button-wrap {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.field span {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
}

.field-optional {
  font-weight: 400;
  color: #94a3b8;
  font-size: 0.85rem;
}

.field-textarea-mono {
  font-family: ui-monospace, monospace;
  font-size: 0.875rem;
}

/* Prompt: 더 높게 */
.field-prompt .prompt-textarea {
  min-height: 10rem;
}

/* Generation options card: 높이 줄임 */
.options-card {
  margin-bottom: 1.25rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.options-card-title {
  margin: 0 0 0.5rem 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #64748b;
}

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 2rem;
}

.option-row-toggle {
  align-items: center;
}

.option-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  flex-shrink: 0;
  min-width: 7rem;
}

.option-select {
  flex: 1;
  max-width: 12rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #111827;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.option-select:hover {
  border-color: #cbd5e1;
}

.option-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.option-input {
  flex: 1;
  max-width: 12rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #111827;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.option-input::placeholder {
  color: #94a3b8;
}

.option-input:hover {
  border-color: #cbd5e1;
}

.option-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.option-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #475569;
  user-select: none;
}

.option-checkbox {
  width: 1.125rem;
  height: 1.125rem;
  margin: 0;
  cursor: pointer;
  accent-color: #6366f1;
}

.option-toggle-text {
  font-weight: 500;
  color: #334155;
}

.field-hint {
  font-size: 0.8rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

textarea {
  padding: 0.6rem 0.7rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-size: 0.9rem;
  resize: vertical;
}

.btn.primary {
  padding: 0.6rem 1.2rem;
  border-radius: 999px;
  background: #111827;
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn.primary:hover:not(:disabled) {
  background: #374151;
}

.btn.primary[disabled] {
  opacity: 0.5;
  cursor: default;
}

.login-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.error {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #dc2626;
}

.info {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #16a34a;
}

/* Shared creations with this avatar (below result area) */
.shared-by-avatar-area {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
  padding-bottom: 3rem;
}

.shared-by-avatar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.25rem;
}

@media (min-width: 768px) {
  .shared-by-avatar-container {
    padding: 0 2rem;
  }
}

@media (min-width: 1024px) {
  .shared-by-avatar-container {
    padding: 0 4rem;
  }
}

.shared-by-avatar-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1.5rem;
}

.shared-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  gap: 0.75rem;
}

.shared-loading .loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.shared-loading .loading-text {
  font-size: 0.9rem;
  color: #6b7280;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.shared-empty {
  padding: 2rem;
  text-align: center;
  font-size: 0.95rem;
  color: #6b7280;
}

.shared-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

@media (min-width: 640px) {
  .shared-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;
  }
}

@media (min-width: 1024px) {
  .shared-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.5rem;
  }
}

.shared-card {
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  background: #ffffff;
  transition: box-shadow 0.2s, transform 0.2s;
}

.shared-card:hover {
  box-shadow: 0 8px 20px -5px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.shared-thumb-wrap {
  aspect-ratio: 1;
  background: #f3f4f6;
}

.shared-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.shared-meta {
  padding: 0.75rem;
}

.shared-prompt {
  font-size: 0.85rem;
  color: #374151;
  line-height: 1.35;
  margin-bottom: 0.35rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shared-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #9ca3af;
}

.shared-creator {
  font-weight: 500;
  color: #4f46e5;
}

@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
