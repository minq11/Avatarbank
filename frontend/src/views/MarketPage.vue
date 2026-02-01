<template>
  <section class="market-section" @click="showFilterDropdown = false">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">Avatar Market</h2>
        <p class="section-description">
          Select an avatar to generate images with its LoRA.
        </p>
      </div>

      <div class="market-toolbar">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search avatars…"
          class="search-input"
          @input="onSearchInput"
        />
        <div class="filter-trigger-wrap">
          <button
            type="button"
            class="filter-btn"
            :class="{ active: hasActiveFilters }"
            @click.stop="showFilterDropdown = !showFilterDropdown"
          >
            <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
            </svg>
            Filter & Sort
            <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
          </button>
          <div v-if="showFilterDropdown" class="filter-dropdown" @click.stop>
            <div class="filter-row">
              <span class="filter-label">Nationality</span>
              <select v-model="filterNationality" class="filter-select" @change="applyFilters">
                <option value="">All</option>
                <option v-for="n in filterOptions.nationalities" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div class="filter-row">
              <span class="filter-label">Gender</span>
              <select v-model="filterGender" class="filter-select" @change="applyFilters">
                <option value="">All</option>
                <option v-for="g in filterOptions.genders" :key="g" :value="g">{{ g }}</option>
              </select>
            </div>
            <div class="filter-row">
              <span class="filter-label">Sort</span>
              <select v-model="sortBy" class="filter-select" @change="applyFilters">
                <option value="newest">Newest</option>
                <option value="recommend">Most recommended</option>
                <option value="name">Name (A–Z)</option>
                <option value="comments">Most comments</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="market-loading">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p class="loading-text">Loading avatars…</p>
      </div>

      <div v-else-if="avatars.length === 0" class="market-empty">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="7" r="4"/>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          </svg>
        </div>
        <h3 class="empty-title">{{ hasActiveFilters ? 'No avatars found' : 'No avatars available yet' }}</h3>
        <p class="empty-desc">{{ hasActiveFilters ? 'Try adjusting your search or filters.' : 'Check back later for new avatars.' }}</p>
        <h3 class="empty-title">No avatars available yet</h3>
        <p class="empty-desc">Check back later for new avatars.</p>
      </div>

      <div v-else class="market-grid">
        <article
          v-for="a in avatars"
          :key="a.id"
          class="market-card"
          @click="openModal(a)"
        >
          <div class="card-thumb-wrap">
            <img
              v-if="a.preview_image_url"
              :src="getImageUrl(a.preview_image_url)"
              :alt="a.title"
              class="card-thumb"
              loading="lazy"
            />
            <div v-else class="card-thumb card-thumb-placeholder" />
          </div>
          <div class="card-meta">
            <h3 class="card-title">{{ a.title }}</h3>
            <p class="card-desc" :title="a.description || '—'">{{ truncate(a.description || "—", 48) }}</p>
            <div class="card-footer">
              <span class="card-recommend">
                <img src="@/assets/icons/thumb_upBtn.svg" alt="" class="card-recommend-icon" />
                {{ a.up_count ?? 0 }}
              </span>
              <span class="card-credits-wrap">
                <span class="card-credits">{{ a.credit_per_generation != null ? a.credit_per_generation : 1 }} C</span>
                <span class="card-label">per gen</span>
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- Avatar Detail Modal -->
    <div v-if="selectedAvatarId != null" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ modalAvatar?.title ?? 'Avatar' }}</h3>
          <button type="button" class="modal-close" aria-label="Close" @click="closeModal">×</button>
        </div>

        <template v-if="modalAvatar">
          <!-- 상단: 대표사진 + 설명 + 옵션 + 만든사람 + 인스타 -->
          <div class="modal-top">
            <div class="modal-preview-wrap">
              <img
                v-if="modalAvatar.preview_image_url"
                :src="getImageUrl(modalAvatar.preview_image_url)"
                :alt="modalAvatar.title"
                class="modal-preview-img"
              />
              <div v-else class="modal-preview-placeholder">No preview</div>
            </div>
            <div class="modal-info">
              <p v-if="modalAvatar.description" class="modal-desc">{{ modalAvatar.description }}</p>
              <div class="modal-options">
                <span v-if="modalAvatar.nationality" class="option-tag">{{ modalAvatar.nationality }}</span>
                <span v-if="modalAvatar.gender" class="option-tag">{{ modalAvatar.gender }}</span>
                <span class="option-tag credit-tag">{{ modalAvatar.credit_per_generation != null ? modalAvatar.credit_per_generation : 1 }} C / gen</span>
              </div>
              <div class="modal-creator">
                <span class="creator-label">By</span>
                <span class="creator-name">@{{ modalAvatar.creator_nickname || '—' }}</span>
                <a
                  v-if="modalAvatar.instagram_id"
                  :href="instagramUrl(modalAvatar.instagram_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="instagram-link"
                  title="Instagram"
                >
                  <img src="@/assets/icons/Instagram_logo_2016.svg" alt="Instagram" class="instagram-icon" />
                </a>
              </div>
            </div>
          </div>

          <!-- 추천/비추천 -->
          <div class="modal-rating">
            <button
              type="button"
              class="rating-btn"
              :class="{ active: modalRating?.my_vote === 'up' }"
              title="Recommend"
              @click="setRating('up')"
            >
              <img src="@/assets/icons/thumb_upBtn.svg" alt="" class="rating-icon" />
              <span>{{ modalRating?.up_count ?? 0 }}</span>
            </button>
            <button
              type="button"
              class="rating-btn"
              :class="{ active: modalRating?.my_vote === 'down' }"
              title="Not recommend"
              @click="setRating('down')"
            >
              <img src="@/assets/icons/thumb_downBtn.svg" alt="" class="rating-icon" />
              <span>{{ modalRating?.down_count ?? 0 }}</span>
            </button>
          </div>

          <!-- 댓글 -->
          <div class="modal-comments">
            <h4 class="comments-title">
              <img src="@/assets/icons/commentBtn.svg" alt="" class="comments-icon" />
              Comments ({{ modalComments.length }})
            </h4>
            <div v-if="authStore.isLoggedIn" class="comment-form">
              <textarea
                v-model="newComment"
                rows="2"
                placeholder="Write a comment…"
                class="comment-input"
              />
              <button type="button" class="btn-submit-comment" :disabled="!newComment.trim() || commentSubmitting" @click="submitComment">
                {{ commentSubmitting ? 'Sending…' : 'Post' }}
              </button>
            </div>
            <ul class="comment-list">
              <li v-for="c in modalComments" :key="c.id" class="comment-item">
                <span class="comment-author">@{{ c.creator_nickname }}</span>
                <span class="comment-content">{{ c.content }}</span>
                <span class="comment-date">{{ formatDate(c.created_at) }}</span>
              </li>
              <li v-if="modalComments.length === 0" class="comment-empty">No comments yet.</li>
            </ul>
          </div>

          <!-- 이 모델로 만든 사진들 (비동기 로드 + 무한 스크롤) -->
          <div class="modal-creations" ref="creationsContainerRef">
            <h4 class="creations-title">Creations with this avatar</h4>
            <div v-if="modalCreations.length === 0 && !modalCreationsLoading" class="creations-empty">No shared creations yet.</div>
            <div v-else class="creations-grid">
              <div v-for="item in modalCreations" :key="item.id" class="creation-thumb">
                <img :src="item.image_url" :alt="item.prompt" loading="lazy" />
                <p class="creation-prompt">{{ truncate(item.prompt, 32) }}</p>
              </div>
            </div>
            <div
              v-if="modalCreationsLoading"
              class="creations-loading-inline"
            >
              <div class="loading-spinner small" aria-hidden="true"></div>
              <span>Loading…</span>
            </div>
            <div
              v-else-if="hasMoreCreations && modalCreations.length > 0"
              ref="creationsSentinelRef"
              class="creations-sentinel"
              aria-hidden="true"
            />
          </div>

          <!-- 이 모델로 이미지 생성하기 -->
          <div class="modal-footer">
            <button type="button" class="btn-create-image" @click="goToGeneration">
              Create image with this model
            </button>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import {
  avatarsApi,
  galleryApi,
  type AvatarItem,
  type AvatarDetailItem,
  type AvatarRatingItem,
  type AvatarCommentItem,
  type GalleryItem,
  type AvatarFilterOptions,
} from "@/services/api";

const router = useRouter();
const authStore = useAuthStore();

function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("/static/")) return `/api${url}`;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return url;
}

function instagramUrl(id: string): string {
  const clean = id.replace(/^@/, "").trim();
  if (!clean) return "#";
  if (clean.startsWith("http")) return clean;
  return `https://www.instagram.com/${clean}/`;
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

const avatars = ref<AvatarItem[]>([]);
const loading = ref(true);
const searchQuery = ref("");
const filterNationality = ref("");
const filterGender = ref("");
const sortBy = ref<"newest" | "recommend" | "name" | "comments">("newest");
const filterOptions = ref<AvatarFilterOptions>({ nationalities: [], genders: [] });
let searchTimeout: ReturnType<typeof setTimeout> | null = null;

const showFilterDropdown = ref(false);

const hasActiveFilters = computed(
  () => !!searchQuery.value.trim() || !!filterNationality.value || !!filterGender.value
);

const activeFilterCount = computed(() => {
  let n = 0;
  if (filterNationality.value) n++;
  if (filterGender.value) n++;
  if (sortBy.value && sortBy.value !== "newest") n++;
  return n;
});
const selectedAvatarId = ref<number | null>(null);
const modalAvatar = ref<AvatarDetailItem | null>(null);
const modalRating = ref<AvatarRatingItem | null>(null);
const modalComments = ref<AvatarCommentItem[]>([]);
const modalCreations = ref<GalleryItem[]>([]);
const modalCreationsLoading = ref(false);
const hasMoreCreations = ref(true);
const creationsContainerRef = ref<HTMLElement | null>(null);
const creationsSentinelRef = ref<HTMLElement | null>(null);
const newComment = ref("");
const commentSubmitting = ref(false);

function openModal(a: AvatarItem) {
  const avatarId = a.id;
  selectedAvatarId.value = avatarId;
  modalAvatar.value = {
    ...a,
    creator_nickname: "",
    instagram_id: null,
  };
  modalRating.value = { up_count: 0, down_count: 0, my_vote: null };
  modalComments.value = [];
  modalCreations.value = [];
  hasMoreCreations.value = true;
  newComment.value = "";
  modalCreationsLoading.value = false;
  loadModalCreations(avatarId, 0);
  Promise.all([
    avatarsApi.getById(avatarId).then((detail) => {
      if (selectedAvatarId.value === avatarId) {
        modalAvatar.value = detail;
      }
    }),
    avatarsApi.getRating(avatarId).then((r) => {
      if (selectedAvatarId.value === avatarId) modalRating.value = r;
    }).catch(() => {}),
    avatarsApi.getComments(avatarId).then((c) => {
      if (selectedAvatarId.value === avatarId) modalComments.value = c;
    }).catch(() => {}),
  ]);
}

const CREATIONS_PAGE_SIZE = 12;

async function loadModalCreations(avatarId: number, offset: number) {
  if (modalCreationsLoading.value || !hasMoreCreations.value) return;
  modalCreationsLoading.value = true;
  try {
    const items = await galleryApi.getGenerations(avatarId, CREATIONS_PAGE_SIZE, offset);
    if (offset === 0) {
      modalCreations.value = items;
    } else {
      modalCreations.value = [...modalCreations.value, ...items];
    }
    hasMoreCreations.value = items.length >= CREATIONS_PAGE_SIZE;
  } catch {
    hasMoreCreations.value = false;
    if (offset === 0) modalCreations.value = [];
  } finally {
    modalCreationsLoading.value = false;
  }
}

function loadMoreCreations() {
  const id = selectedAvatarId.value;
  if (id != null && hasMoreCreations.value && !modalCreationsLoading.value) {
    loadModalCreations(id, modalCreations.value.length);
  }
}

function closeModal() {
  selectedAvatarId.value = null;
  modalAvatar.value = null;
  modalRating.value = null;
  modalComments.value = [];
  modalCreations.value = [];
}

async function setRating(type: "up" | "down") {
  const id = selectedAvatarId.value;
  if (id == null || !authStore.isLoggedIn) {
    if (!authStore.isLoggedIn) alert("Please log in to rate.");
    return;
  }
  const prev = modalRating.value
    ? { ...modalRating.value }
    : { up_count: 0, down_count: 0, my_vote: null as "up" | "down" | null };
  const up = prev.up_count ?? 0;
  const down = prev.down_count ?? 0;
  const my = prev.my_vote;
  let nextUp = up;
  let nextDown = down;
  let nextMy: "up" | "down" | null = my;
  if (type === "up") {
    if (my === "up") {
      nextUp = Math.max(0, up - 1);
      nextMy = null;
    } else if (my === "down") {
      nextDown = Math.max(0, down - 1);
      nextUp = up + 1;
      nextMy = "up";
    } else {
      nextUp = up + 1;
      nextMy = "up";
    }
  } else {
    if (my === "down") {
      nextDown = Math.max(0, down - 1);
      nextMy = null;
    } else if (my === "up") {
      nextUp = Math.max(0, up - 1);
      nextDown = down + 1;
      nextMy = "down";
    } else {
      nextDown = down + 1;
      nextMy = "down";
    }
  }
  modalRating.value = { up_count: nextUp, down_count: nextDown, my_vote: nextMy };
  try {
    const res = await avatarsApi.setRating(id, type);
    if (selectedAvatarId.value === id) {
      modalRating.value = res;
    }
    const idx = avatars.value.findIndex((x) => x.id === id);
    if (idx !== -1) {
      avatars.value[idx] = { ...avatars.value[idx], up_count: res.up_count, down_count: res.down_count };
    }
  } catch {
    if (selectedAvatarId.value === id) {
      modalRating.value = prev;
    }
  }
}

async function submitComment() {
  const id = selectedAvatarId.value;
  if (id == null || !newComment.value.trim() || commentSubmitting.value) return;
  commentSubmitting.value = true;
  try {
    const created = await avatarsApi.createComment(id, newComment.value.trim());
    modalComments.value = [created, ...modalComments.value];
    newComment.value = "";
  } catch {
    // ignore
  } finally {
    commentSubmitting.value = false;
  }
}

function goToGeneration() {
  const id = selectedAvatarId.value;
  if (id != null) {
    closeModal();
    router.push(`/avatars/${id}`);
  }
}

let creationsObserver: IntersectionObserver | null = null;

async function fetchAvatars() {
  loading.value = true;
  try {
    avatars.value = await avatarsApi.getList({
      q: searchQuery.value.trim() || undefined,
      nationality: filterNationality.value || undefined,
      gender: filterGender.value || undefined,
      sort: sortBy.value,
    });
  } catch {
    avatars.value = [];
  } finally {
    loading.value = false;
  }
}

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(fetchAvatars, 300);
}

function applyFilters() {
  fetchAvatars();
}

onMounted(async () => {
  try {
    filterOptions.value = await avatarsApi.getFilterOptions();
  } catch {
    // keep default empty options
  }
  await fetchAvatars();

  creationsObserver = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting) loadMoreCreations();
    },
    { root: null, rootMargin: "100px", threshold: 0 }
  );
});

watch(
  () => [creationsSentinelRef.value, selectedAvatarId.value, modalCreations.value.length],
  async ([sentinel]) => {
    creationsObserver?.disconnect();
    await nextTick();
    if (sentinel) {
      creationsObserver?.observe(sentinel as Element);
    }
  },
  { immediate: true, flush: "post" }
);
</script>

<style scoped>
.market-section {
  padding: 3rem 0 5rem;
  background: #ffffff;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.25rem;
}

@media (min-width: 768px) {
  .container {
    padding: 0 2rem;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 0 4rem;
  }
}

.section-header {
  margin-bottom: 2.5rem;
}

.section-title {
  font-size: 1.875rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 0.5rem;
}

.section-description {
  font-size: 1rem;
  color: #6b7280;
}

.market-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #f9fafb;
  transition: border-color 0.2s, background 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #c7d2fe;
  background: #fff;
}

.search-input::placeholder {
  color: #9ca3af;
}

.filter-trigger-wrap {
  position: relative;
  flex-shrink: 0;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.filter-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.filter-btn.active {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #4f46e5;
}

.filter-icon {
  width: 1rem;
  height: 1rem;
}

.filter-badge {
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.35rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #fff;
  background: #4f46e5;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.filter-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 12rem;
  padding: 0.75rem;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0;
}

.filter-row:not(:last-child) {
  border-bottom: 1px solid #f3f4f6;
}

.filter-label {
  flex-shrink: 0;
  width: 5rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.filter-select {
  flex: 1;
  min-width: 0;
  padding: 0.35rem 0.5rem;
  font-size: 0.85rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: #fff;
  color: #374151;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #818cf8;
}

.market-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 0.95rem;
  color: #6b7280;
}

.market-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 4rem 1.5rem;
  background: #f9fafb;
  border-radius: 1rem;
  border: 1px dashed #e5e7eb;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1.25rem;
  color: #9ca3af;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.empty-desc {
  font-size: 0.95rem;
  color: #6b7280;
  max-width: 20rem;
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .market-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .market-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.5rem;
  }
}

.market-card {
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  background: #ffffff;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.market-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-thumb-wrap {
  aspect-ratio: 1;
  background: #f3f4f6;
}

.card-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-thumb-placeholder {
  background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%);
}

.card-meta {
  padding: 1rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.35rem;
  line-height: 1.3;
}

.card-desc {
  font-size: 0.9rem;
  color: #6b7280;
  line-height: 1.4;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #9ca3af;
}

.card-recommend {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
  color: #6b7280;
}

.card-recommend-icon {
  width: 0.9rem;
  height: 0.9rem;
  opacity: 0.85;
}

.card-credits-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.card-credits {
  font-weight: 500;
  color: #4f46e5;
}

.card-label {
  color: #9ca3af;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 60;
  overflow-y: auto;
}

.modal-card {
  width: 100%;
  max-width: 880px;
  max-height: 90vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 1;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  line-height: 1;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: background 0.2s, color 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-loading {
  padding: 3rem;
  text-align: center;
  color: #6b7280;
}

.modal-loading .loading-spinner {
  width: 2rem;
  height: 2rem;
  margin: 0 auto 0.75rem;
  border-width: 2px;
}

.modal-top {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
  padding: 1.5rem 1.5rem 1.25rem;
}

@media (max-width: 640px) {
  .modal-top {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .modal-preview-wrap {
    max-width: 320px;
    width: 100%;
  }
}

@media (min-width: 641px) and (max-width: 720px) {
  .modal-top {
    grid-template-columns: 260px 1fr;
  }
}

.modal-preview-wrap {
  aspect-ratio: 1;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #f3f4f6;
}

.modal-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #9ca3af;
}

.modal-info {
  min-width: 0;
}

.modal-desc {
  font-size: 0.95rem;
  color: #374151;
  line-height: 1.5;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.option-tag {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  color: #4b5563;
  border-radius: 0.375rem;
}

.credit-tag {
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 500;
}

.modal-creator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.creator-label {
  font-size: 0.85rem;
  color: #6b7280;
}

.creator-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #4f46e5;
}

.instagram-link {
  display: inline-flex;
  align-items: center;
  color: #6b7280;
  transition: opacity 0.2s;
}

.instagram-link:hover {
  opacity: 0.8;
}

.instagram-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-rating {
  display: flex;
  gap: 0.5rem;
  padding: 0 1.25rem 1rem;
}

.rating-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  color: #6b7280;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.rating-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.rating-btn.active {
  background: #eef2ff;
  border-color: #818cf8;
  color: #4f46e5;
}

.rating-icon {
  width: 1rem;
  height: 1rem;
}

.modal-comments {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #f3f4f6;
}

.comments-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem;
}

.comments-icon {
  width: 1rem;
  height: 1rem;
}

.comment-form {
  margin-bottom: 0.75rem;
}

.comment-input {
  width: 100%;
  padding: 0.5rem 0.6rem;
  font-size: 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  resize: vertical;
  margin-bottom: 0.35rem;
}

.btn-submit-comment {
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #ffffff;
  background: #4f46e5;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit-comment:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-submit-comment:disabled {
  opacity: 0.5;
  cursor: default;
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comment-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.9rem;
}

.comment-author {
  font-weight: 500;
  color: #4f46e5;
  margin-right: 0.35rem;
}

.comment-content {
  color: #374151;
}

.comment-date {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.2rem;
}

.comment-empty {
  padding: 0.75rem 0;
  font-size: 0.9rem;
  color: #9ca3af;
}

.modal-creations {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #f3f4f6;
}

.creations-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem;
}

.creations-empty {
  font-size: 0.9rem;
  color: #9ca3af;
  padding: 0.5rem 0;
}

.creations-loading-inline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  font-size: 0.9rem;
  color: #6b7280;
}

.creations-loading-inline .loading-spinner.small {
  width: 1.25rem;
  height: 1.25rem;
  border-width: 2px;
}

.creations-sentinel {
  height: 1px;
  width: 100%;
  pointer-events: none;
  visibility: hidden;
}

.creations-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

@media (max-width: 640px) {
  .creations-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.creation-thumb {
  aspect-ratio: 1;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f3f4f6;
}

.creation-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.creation-prompt {
  font-size: 0.7rem;
  color: #6b7280;
  margin: 0.25rem 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
  border-radius: 0 0 1rem 1rem;
}

.btn-create-image {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.btn-create-image:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
  transform: translateY(-1px);
}
</style>
