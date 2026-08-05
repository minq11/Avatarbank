<template>
  <section class="generation">
    <div class="generation-page-header">
      <h2 class="generation-page-title">AI 이미지 생성</h2>
    </div>
    <div class="layout" :class="{ 'layout-no-avatar': !avatarId }">
      <div v-if="avatarId != null" class="left">
        <!-- 아바타 미리보기 (LoRA 선택 시에만 표시) -->
        <div v-if="avatar" class="avatar-preview">
          <div v-if="avatar.is_real_person && avatar.instagram_id" class="avatar-preview-instagram">
            <a
              :href="instagramUrl(avatar.instagram_id)"
              target="_blank"
              rel="noopener noreferrer"
              class="avatar-preview-instagram-link"
              title="Instagram"
            >
              <img src="@/assets/icons/Instagram_logo_2016.svg" alt="" class="avatar-preview-instagram-icon" />
              <span>{{ formatInstagramId(avatar.instagram_id) }}</span>
            </a>
          </div>
          <div v-if="avatarPreviewUrls.primary" class="preview-img-wrap">
            <img
              :src="avatarPreviewUrls.primary"
              :alt="avatar.title"
              class="preview-img"
              @error="(e: Event) => { const t = (e.target as HTMLImageElement); if (avatarPreviewUrls.fallback) t.src = avatarPreviewUrls.fallback; }"
            />
          </div>
          <div v-else class="preview-placeholder">
            <span>미리보기 없음</span>
          </div>
          <p class="avatar-name">{{ avatar.title }}</p>
          <table class="avatar-info-table">
            <tbody>
              <tr v-if="avatar.description">
                <th scope="row">설명</th>
                <td class="avatar-detail-value">{{ avatar.description }}</td>
              </tr>
              <tr v-if="avatar.nationality">
                <th scope="row">국가</th>
                <td>{{ avatar.nationality }}</td>
              </tr>
              <tr v-if="avatar.gender">
                <th scope="row">성별</th>
                <td>{{ avatar.gender }}</td>
              </tr>
              <tr v-if="avatar.age != null">
                <th scope="row">나이</th>
                <td>{{ avatar.age }}</td>
              </tr>
              <tr v-if="avatar.height != null">
                <th scope="row">키</th>
                <td>{{ avatar.height }} cm</td>
              </tr>
              <tr v-if="avatar.weight != null">
                <th scope="row">몸무게</th>
                <td>{{ avatar.weight }} kg</td>
              </tr>
              <tr v-if="avatar.special_notes">
                <th scope="row">특이사항</th>
                <td class="avatar-detail-value">{{ avatar.special_notes }}</td>
              </tr>
              <tr>
                <th scope="row">크레딧</th>
                <td>{{ avatar.credit_per_generation != null ? avatar.credit_per_generation : 1 }} C / gen</td>
              </tr>
              <tr>
                <th scope="row">유형</th>
                <td>{{ avatar.is_real_person ? 'Real person' : 'Fictional character' }}</td>
              </tr>
              <tr v-if="avatar.is_real_person && avatar.instagram_id">
                <th scope="row">Instagram</th>
                <td>
                  <a
                    :href="instagramUrl(avatar.instagram_id)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="avatar-instagram-link"
                  >
                    {{ formatInstagramId(avatar.instagram_id) }}
                  </a>
                </td>
              </tr>
              <tr>
                <th scope="row">크리에이터</th>
                <td>@{{ avatar.creator_nickname || '—' }}</td>
              </tr>
              <tr v-if="avatar.negative_prompt">
                <th scope="row">네거티브 프롬프트</th>
                <td class="avatar-detail-value avatar-detail-mono">{{ avatar.negative_prompt }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="avatarError" class="error-state">
          <p>{{ avatarError }}</p>
          <router-link to="/my/avatars" class="link">내 아바타 보기</router-link>
        </div>
        <div v-else class="loading-state">
          <p>아바타 불러오는 중…</p>
        </div>
      </div>

      <div class="right" :class="{ 'options-collapsed': !optionsExpanded }">
        <label class="field">
          <span>아바타 선택 (LoRA)</span>
          <SearchableSelect
            :model-value="avatarId ?? ''"
            :options="avatarSelectOptions"
            placeholder="— 아바타 선택 —"
            @update:model-value="onSelectAvatarValue"
          />
          <p v-if="avatarsList.length === 0 && !avatarsListLoading" class="field-hint">사용 가능한 아바타가 없어요.</p>
        </label>

        <label class="field field-prompt">
          <span>프롬프트</span>
          <textarea
            v-model="prompt"
            rows="8"
            placeholder="원하는 이미지를 묘사하세요 (영어 권장)."
            class="prompt-textarea"
          />
        </label>

        <div class="options-card">
          <button
            type="button"
            class="options-card-header"
            @click="optionsExpanded = !optionsExpanded"
            :aria-expanded="optionsExpanded"
          >
            <h4 class="options-card-title">생성 옵션</h4>
            <svg
              class="options-card-chevron"
              :class="{ 'options-card-chevron-open': optionsExpanded }"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>
          <div v-show="optionsExpanded" class="options-grid" @click.self="openHelpOption = null">
            <div v-if="openHelpOption" class="option-help-overlay" aria-hidden="true" @click="openHelpOption = null" />
            <div class="option-row">
              <span class="option-label-wrap option-help-wrap">
                <label class="option-label" for="opt-image-size">이미지 크기</label>
                <span class="option-help" aria-label="Help" @click.stop="toggleHelp('imageSize')">?</span>
                <div v-if="openHelpOption === 'imageSize'" class="option-help-popover">{{ optionHelpText.imageSize }}</div>
              </span>
              <select id="opt-image-size" v-model="imageSize" class="option-select">
                <option v-for="opt in imageSizeOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="option-row">
              <span class="option-label-wrap option-help-wrap">
                <label class="option-label" for="opt-steps">추론 스텝</label>
                <span class="option-help" aria-label="Help" @click.stop="toggleHelp('steps')">?</span>
                <div v-if="openHelpOption === 'steps'" class="option-help-popover">{{ optionHelpText.steps }}</div>
              </span>
              <select id="opt-steps" v-model.number="numInferenceSteps" class="option-select">
                <option v-for="n in [4, 6, 8, 10, 12]" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div class="option-row">
              <span class="option-label-wrap option-help-wrap">
                <label class="option-label" for="opt-seed">시드</label>
                <span class="option-help" aria-label="Help" @click.stop="toggleHelp('seed')">?</span>
                <div v-if="openHelpOption === 'seed'" class="option-help-popover option-help-popover-above">{{ optionHelpText.seed }}</div>
              </span>
              <input
                id="opt-seed"
                :value="seedInput"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                class="option-input"
                placeholder="랜덤 (비우면 랜덤)"
                @input="onSeedInput"
              />
            </div>
            <div class="option-row">
              <span class="option-label-wrap option-help-wrap">
                <span class="option-label">LoRA 강도</span>
                <span class="option-help" aria-label="Help" @click.stop="toggleHelp('loraScale')">?</span>
                <div v-if="openHelpOption === 'loraScale'" class="option-help-popover option-help-popover-above">{{ optionHelpText.loraScale }}</div>
              </span>
              <div class="option-lora-scale">
                <input
                  id="opt-lora-scale"
                  v-model.number="loraScale"
                  type="range"
                  min="0"
                  max="4"
                  step="0.1"
                  class="option-range"
                  aria-valuemin="0"
                  aria-valuemax="4"
                  :aria-valuenow="loraScale"
                />
                <span class="option-lora-scale-value">{{ loraScale.toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="avatar" class="cost-info">
          <span>기본 {{ baseCredit }} C + 아바타 로열티 {{ avatarCredit }} C</span>
          <span>합계: {{ totalCredits }} C</span>
        </div>

        <div class="button-wrap">
        <button
          class="btn primary"
          :disabled="!canSubmit"
          @click="requestGeneration"
        >
          {{ loading ? "생성 중…" : "이미지 생성" }}
        </button>
        </div>

        <p v-if="!authStore.isLoggedIn && avatar && prompt.trim()" class="login-hint">
          이미지를 생성하려면 로그인해 주세요.
        </p>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="generationId && !resultImageUrl && !error" class="info">
          요청이 접수됐어요. ID: {{ generationId }}
        </p>
      </div>
    </div>

    <!-- Share 확인 모달 -->
    <div v-if="showShareConfirm" class="confirm-overlay" @click.self="showShareConfirm = false">
      <div class="confirm-modal">
        <h4 class="confirm-title">{{ shareConfirmIsUnshare ? '갤러리에서 내릴까요?' : '갤러리에 공유할까요?' }}</h4>
        <p class="confirm-message">
          {{ shareConfirmIsUnshare
            ? '이 작품이 공개 갤러리에서 내려가요.'
            : '이 작품이 갤러리에서 모두에게 공개돼요.' }}
        </p>
        <div class="confirm-actions">
          <button type="button" class="btn-confirm-cancel" @click="showShareConfirm = false">취소</button>
          <button type="button" class="btn-confirm-ok" @click="confirmShareAction">
            {{ shareConfirmIsUnshare ? '삭제' : '공유' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 결과 영역 (입력 폼과 구분) -->
    <div v-if="avatarId != null" class="result-area">
      <div v-if="loading" class="result-generating">
        <div class="result-generating-spinner"></div>
        <p class="result-generating-text">이미지 만드는 중…</p>
        <p class="result-generating-sub">잠시 걸릴 수 있어요</p>
      </div>
      <div v-else-if="resultImageUrl" class="result-section">
        <div class="result-section-header">
          <h4>생성된 이미지</h4>
          <div class="result-actions">
            <button
              type="button"
              class="btn-result-action"
              :class="{ 'is-shared': resultIsShared }"
              :title="resultIsShared ? '갤러리에 공유됨' : '갤러리에 공유'"
              @click="openShareConfirm"
            >
              <img src="@/assets/icons/shareBtn.svg" alt="" class="btn-result-icon" />
              {{ resultIsShared ? '공유됨' : '공유' }}
            </button>
            <button
              type="button"
              class="btn-result-action btn-download"
              title="다운로드"
              @click="downloadResultImage"
            >
              <img src="@/assets/icons/downloadBtn.svg" alt="" class="btn-result-icon" />
              다운로드
            </button>
          </div>
        </div>
        <div class="result-img-wrap">
          <img :src="getImageUrl(resultImageUrl)" alt="Generated" class="result-img" />
        </div>
      </div>
      <p v-else class="note">생성하면 여기에 이미지가 표시돼요.</p>
    </div>

    <!-- 선택된 아바타로 만들어진 공유 결과물 (shared만) -->
    <div v-if="avatarId != null" class="shared-by-avatar-area">
      <div class="shared-by-avatar-container">
        <h3 class="shared-by-avatar-title">이 아바타로 만든 공유 작품</h3>
        <div v-if="sharedByAvatarLoading" class="shared-loading">
          <div class="loading-spinner" aria-hidden="true"></div>
          <p class="loading-text">불러오는 중…</p>
        </div>
        <div v-else-if="sharedByAvatar.length === 0" class="shared-empty">
          <p>아직 이 아바타로 공유된 작품이 없어요.</p>
        </div>
        <div v-else class="shared-grid">
          <article
            v-for="item in sharedByAvatar"
            :key="item.id"
            class="shared-card"
            @click="selectedGalleryItem = item"
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

    <GenerationDetailModal
      :item="selectedGalleryItem"
      :image-url-resolver="getImageUrl"
      @close="selectedGalleryItem = null"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import SearchableSelect from "@/components/SearchableSelect.vue";
import GenerationDetailModal from "@/components/GenerationDetailModal.vue";
import { useAuthStore } from "@/stores/auth";
import {
  avatarsApi,
  generationsApi,
  galleryApi,
  type AvatarItem,
  type AvatarDetailItem,
  type GalleryItem,
  type ImageSizeOption,
} from "@/services/api";
import { getAvatarPreviewUrls } from "@/utils/avatarPreview";

const authStore = useAuthStore();

const avatarPreviewUrls = computed(() =>
  avatar.value
    ? getAvatarPreviewUrls(avatar.value.id, avatar.value.preview_image_url)
    : { primary: "", fallback: "" }
);

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

const showShareConfirm = ref(false);
const shareConfirmIsUnshare = ref(false);

function openShareConfirm() {
  shareConfirmIsUnshare.value = resultIsShared.value;
  showShareConfirm.value = true;
}

async function confirmShareAction() {
  showShareConfirm.value = false;
  const id = generationId.value;
  if (id == null) return;
  const targetShared = !shareConfirmIsUnshare.value;
  const prevShared = resultIsShared.value;
  const prevList = [...sharedByAvatar.value];
  resultIsShared.value = targetShared;
  if (targetShared) {
    const optimisticItem: GalleryItem = {
      id,
      image_url: getImageUrl(resultImageUrl.value) || "",
      prompt: prompt.value,
      created_at: new Date().toISOString(),
      creator_nickname: authStore.user?.nickname ?? "",
    };
    sharedByAvatar.value = [optimisticItem, ...sharedByAvatar.value];
  } else {
    sharedByAvatar.value = sharedByAvatar.value.filter((item) => item.id !== id);
  }
  loadSharedByAvatar();
  try {
    const updated = await generationsApi.toggleShare(id);
    resultIsShared.value = updated.is_shared === true;
    loadSharedByAvatar();
  } catch {
    resultIsShared.value = prevShared;
    sharedByAvatar.value = prevList;
    loadSharedByAvatar();
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
const avatar = ref<AvatarDetailItem | null>(null);
const avatarError = ref("");
const prompt = ref("");
const optionsExpanded = ref(true);
const imageSize = ref<ImageSizeOption>("landscape_4_3");
const numInferenceSteps = ref(8);
const seedInput = ref("1");
const loraScale = ref(1.6);
const loading = ref(false);

type HelpOptionKey = "nsfw" | "imageSize" | "steps" | "seed" | "loraScale";
const openHelpOption = ref<HelpOptionKey | null>(null);
const optionHelpText: Record<HelpOptionKey, string> = {
  imageSize: "Aspect ratio and resolution of the generated image.",
  steps: "More steps usually improve quality but take longer. 8 is a good default.",
  seed: "Same seed + same prompt gives the same image. Leave empty for random.",
  loraScale: "How strongly to apply the avatar LoRA (0–4). 1.6 is default; higher = more avatar likeness, lower = more prompt-driven.",
};
function toggleHelp(key: HelpOptionKey) {
  openHelpOption.value = openHelpOption.value === key ? null : key;
}

function onSeedInput(e: Event) {
  const target = e.target as HTMLInputElement;
  const digitsOnly = target.value.replace(/\D/g, "");
  seedInput.value = digitsOnly;
}

const imageSizeOptions: { value: ImageSizeOption; label: string }[] = [
  { value: "landscape_4_3", label: "Landscape 4:3" },
  { value: "landscape_16_9", label: "Landscape 16:9" },
  { value: "portrait_4_3", label: "Portrait 4:3" },
  { value: "portrait_16_9", label: "Portrait 16:9" },
  { value: "square", label: "Square" },
  { value: "square_hd", label: "Square HD" },
];
const error = ref("");
const generationId = ref<number | null>(null);
const resultImageUrl = ref<string | null>(null);
const resultIsShared = ref(false);

const sharedByAvatar = ref<GalleryItem[]>([]);
const sharedByAvatarLoading = ref(false);
const selectedGalleryItem = ref<GalleryItem | null>(null);

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
    return;
  }
  avatar.value = null;
  avatarError.value = "";
  try {
    const a = await avatarsApi.getById(id);
    avatar.value = a;
    /* Negative prompt (optional)는 아바타별 값으로 덮지 않고, 공통 기본값만 유지 */
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    avatarError.value = msg || "아바타를 불러오지 못했어요.";
  }
}

async function requestGeneration() {
  if (!authStore.isLoggedIn) {
    error.value = "로그인해 주세요.";
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
      option_credits: 0,
      idempotency_key: crypto.randomUUID(),
      image_size: imageSize.value,
      num_inference_steps: numInferenceSteps.value,
      output_format: "png",
      seed: seedNum !== null && !Number.isNaN(seedNum) ? seedNum : null,
      lora_scale: loraScale.value,
    });
    generationId.value = res.id;
    resultIsShared.value = res.is_shared === true;
    if (res.status === "success" && res.image_url) {
      resultImageUrl.value = res.image_url;
      error.value = "";
    } else if (res.status === "failed") {
      error.value = res.fail_reason
        ? `생성 실패: ${res.fail_reason}`
        : "생성에 실패했어요.";
    } else {
      resultImageUrl.value = res.image_url || null;
    }
    await authStore.fetchUser();
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status;
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    if (status === 401 || status === 403) {
      error.value = "로그인해 주세요.";
    } else {
      error.value = msg ?? "생성 요청 제출에 실패했어요.";
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
    return d.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

function instagramUrl(id: string): string {
  const clean = id.replace(/^@/, "").trim();
  if (!clean) return "#";
  if (clean.startsWith("http")) return clean;
  return `https://www.instagram.com/${clean}/`;
}

function formatInstagramId(id: string): string {
  const trimmed = id.trim();
  return trimmed.startsWith("@") ? trimmed : `@${trimmed}`;
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

const VALID_IMAGE_SIZES: ImageSizeOption[] = [
  "landscape_4_3", "landscape_16_9", "portrait_4_3", "portrait_16_9", "square", "square_hd",
];

function applyQueryToForm() {
  const q = route.query;
  if (typeof q.prompt === "string" && q.prompt.trim()) {
    prompt.value = q.prompt.trim();
  }
  if (typeof q.seed === "string") {
    const s = q.seed.trim().replace(/\D/g, "");
    if (s !== "") seedInput.value = s;
  }
  if (typeof q.image_size === "string" && VALID_IMAGE_SIZES.includes(q.image_size as ImageSizeOption)) {
    imageSize.value = q.image_size as ImageSizeOption;
  }
  if (typeof q.num_inference_steps === "string") {
    const n = parseInt(q.num_inference_steps, 10);
    if (!Number.isNaN(n) && n >= 4 && n <= 20) numInferenceSteps.value = n;
  }
  if (typeof q.lora_scale === "string") {
    const s = parseFloat(q.lora_scale);
    if (!Number.isNaN(s) && s >= 0 && s <= 4) loraScale.value = s;
  }
}

onMounted(() => {
  loadAvatarsList();
  applyQueryToForm();
});
watch(() => route.query, applyQueryToForm, { immediate: false });
watch(avatarId, loadAvatar, { immediate: true });
watch(avatarId, loadSharedByAvatar, { immediate: true });
</script>

<style scoped>
.generation {
  display: flex;
  flex-direction: column;
  padding: 2rem 0;
}

.generation-page-header {
  max-width: 1000px;
  margin: 0 auto 2.5rem;
  padding: 0 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.generation-page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
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

.avatar-preview-instagram {
  margin-bottom: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  border-radius: 10px;
  border: 1px solid #fbcfe8;
}
.avatar-preview-instagram-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #831843;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}
.avatar-preview-instagram-link:hover {
  text-decoration: underline;
}
.avatar-preview-instagram-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
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

.avatar-info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin-top: 0.75rem;
}

.avatar-info-table th,
.avatar-info-table td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid #e2e8f0;
}

.avatar-info-table tr:last-child th,
.avatar-info-table tr:last-child td {
  border-bottom: none;
}

.avatar-info-table th {
  font-weight: 600;
  color: #64748b;
  width: 7rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: 0.75rem;
}

.avatar-info-table td {
  color: #334155;
  font-weight: 500;
  line-height: 1.5;
  word-break: break-word;
}

.avatar-info-table .avatar-detail-value {
  font-size: 0.875rem;
  margin: 0;
  white-space: pre-wrap;
}

.avatar-info-table .avatar-detail-mono {
  font-family: ui-monospace, monospace;
  font-size: 0.8125rem;
}

.avatar-info-table .avatar-instagram-link {
  color: #6366f1;
  text-decoration: none;
}
.avatar-info-table .avatar-instagram-link:hover {
  text-decoration: underline;
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

/* 생성 중 동적 표시 */
.result-generating {
  padding: 3rem 2rem;
  text-align: center;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
}
.result-generating-spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 1.25rem;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: result-spin 0.8s linear infinite;
}
@keyframes result-spin {
  to { transform: rotate(360deg); }
}
.result-generating-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #334155;
  margin: 0 0 0.35rem;
}
.result-generating-sub {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

/* Share 확인 모달 */
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.confirm-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem 1.75rem;
  max-width: 400px;
  width: 100%;
}
.confirm-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.75rem;
}
.confirm-message {
  font-size: 0.9375rem;
  color: #4b5563;
  line-height: 1.5;
  margin: 0 0 1.25rem;
}
.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
.btn-confirm-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.btn-confirm-cancel:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}
.btn-confirm-ok {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: #6366f1;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-confirm-ok:hover {
  background: #4f46e5;
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
  max-width: 100%;
  background: #f1f5f9;
  display: inline-block;
}

.result-img {
  display: block;
  max-width: 100%;
  height: auto;
  vertical-align: top;
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

.right.options-collapsed .field-prompt .prompt-textarea {
  min-height: 22rem;
}

/* Generation options card: 접기 */
.options-card {
  margin-bottom: 1.25rem;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: visible;
}

.options-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  gap: 0.5rem;
}

.options-card-header:hover {
  background: rgba(0, 0, 0, 0.02);
}

.options-card-title {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #64748b;
}

.option-label-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
  min-width: 7rem;
}

.option-label-wrap.option-help-wrap {
  position: relative;
}

.option-label-wrap .option-label {
  min-width: 0;
}

.option-help-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: transparent;
  cursor: default;
}

.option-help-popover {
  position: absolute;
  left: 0;
  top: 100%;
  margin-top: 0.35rem;
  padding: 0.6rem 0.75rem;
  min-width: 18rem;
  max-width: 32rem;
  width: max-content;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: #374151;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 51;
  white-space: normal;
}

/* Seed 등 하단 옵션: 팝오버를 위로 표시해 카드에 잘리지 않게 */
.option-help-popover-above {
  top: auto;
  bottom: 100%;
  margin-top: 0;
  margin-bottom: 0.35rem;
}

.option-help {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.125rem;
  height: 1.125rem;
  border-radius: 50%;
  border: 1px solid #94a3b8;
  color: #64748b;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

.option-help:hover {
  background: #e2e8f0;
  color: #475569;
  border-color: #64748b;
}

.options-card-chevron {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.options-card-chevron-open {
  transform: rotate(180deg);
}

.options-grid {
  padding: 0 1.25rem 0.75rem;
  padding-top: 0;
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

.option-lora-scale {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  max-width: 12rem;
}
.option-range {
  flex: 1;
  min-width: 5rem;
  height: 0.5rem;
  accent-color: #6366f1;
}
.option-lora-scale-value {
  font-variant-numeric: tabular-nums;
  min-width: 2.25rem;
  font-size: 0.875rem;
  color: #475569;
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
  cursor: pointer;
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
