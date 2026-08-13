<template>
  <section class="creations-section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">내 생성물</h2>
        <p class="section-description">
          Images you've generated with AI avatars
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="creations-loading">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p class="loading-text">생성물 불러오는 중…</p>
      </div>

      <!-- Auth required -->
      <div v-else-if="authRequired" class="creations-empty creations-auth">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h3 class="empty-title">로그인하고 내 생성물 보기</h3>
        <p class="empty-desc">로그인하면 생성한 모든 이미지를 볼 수 있어요.</p>
        <RouterLink to="/" class="btn-primary-empty">홈으로</RouterLink>
      </div>

      <!-- Empty -->
      <div v-else-if="list.length === 0" class="creations-empty">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="m21 15-5-5L5 21"/>
          </svg>
        </div>
        <h3 class="empty-title">아직 생성물이 없어요</h3>
        <p class="empty-desc">AI 아바타로 첫 이미지를 만들어보세요.</p>
        <RouterLink to="/studio/create" class="btn-primary-empty">이미지 만들기</RouterLink>
      </div>

      <!-- Grid -->
      <div v-else class="creations-grid">
        <article
          v-for="g in list"
          :key="g.id"
          class="creation-card"
          @click="openDetailModal(g)"
        >
          <div class="card-thumb-wrap">
            <img
              v-if="g.image_url && g.status === 'success'"
              :src="g.image_url"
              :alt="g.prompt"
              class="card-thumb"
              loading="lazy"
            />
            <div
              v-else
              class="card-thumb card-thumb-placeholder"
              :class="{ 'card-thumb-failed': g.status === 'failed' }"
            >
              <span v-if="g.status === 'failed'" class="placeholder-label">실패</span>
              <span v-else class="placeholder-label">처리 중…</span>
            </div>
          </div>
          <div class="card-meta">
            <p class="card-prompt" :title="g.prompt">{{ truncate(g.prompt, 48) }}</p>
            <div class="card-footer">
              <span class="card-credits">{{ g.status === 'failed' ? 0 : g.credits_used }}C</span>
              <span class="card-date">{{ formatDate(g.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedGeneration" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-card detail-modal">
        <div class="modal-header">
          <h3>생성 상세</h3>
          <button class="modal-close" type="button" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body detail-modal-body">
          <!-- Image -->
          <div class="detail-image-wrapper">
            <img
              v-if="selectedGeneration.image_url && selectedGeneration.status === 'success'"
              :src="selectedGeneration.image_url"
              :alt="selectedGeneration.prompt"
              class="detail-image"
            />
            <div
              v-else
              class="detail-image-placeholder"
              :class="{ 'detail-image-failed': selectedGeneration.status === 'failed' }"
            >
              <span v-if="selectedGeneration.status === 'failed'" class="placeholder-label-large">실패</span>
              <span v-else class="placeholder-label-large">처리 중…</span>
            </div>
          </div>

          <!-- Details -->
          <div class="detail-info">
            <div class="detail-section">
              <h4 class="detail-label">프롬프트</h4>
              <p class="detail-value detail-prompt">{{ selectedGeneration.prompt }}</p>
            </div>

            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-item-label">사용 크레딧</span>
                <span class="detail-item-value">{{ selectedGeneration.status === 'failed' ? 0 : selectedGeneration.credits_used }}C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">기본 크레딧</span>
                <span class="detail-item-value">{{ selectedGeneration.status === 'failed' ? 0 : 1 }}C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">옵션 크레딧</span>
                <span class="detail-item-value">{{ selectedGeneration.status === 'failed' ? 0 : selectedGeneration.credits_used - 1 }}C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">상태</span>
                <span
                  class="detail-item-value detail-status"
                  :class="{
                    'status-success': selectedGeneration.status === 'success',
                    'status-failed': selectedGeneration.status === 'failed',
                    'status-pending': selectedGeneration.status === 'pending' || selectedGeneration.status === 'processing',
                  }"
                >
                  {{ selectedGeneration.status }}
                </span>
              </div>
            </div>

            <div v-if="selectedGeneration.seed" class="detail-section">
              <h4 class="detail-label">시드</h4>
              <p class="detail-value detail-seed">{{ selectedGeneration.seed }}</p>
            </div>

            <div v-if="selectedGeneration.avatar_id" class="detail-section">
              <h4 class="detail-label">아바타 ID</h4>
              <p class="detail-value">{{ selectedGeneration.avatar_id }}</p>
            </div>

            <div class="detail-section">
              <h4 class="detail-label">생성 시각</h4>
              <p class="detail-value">{{ formatDateTime(selectedGeneration.created_at) }}</p>
            </div>

            <div v-if="selectedGeneration.fail_reason" class="detail-section detail-error">
              <h4 class="detail-label">오류</h4>
              <p class="detail-value detail-error-text">{{ selectedGeneration.fail_reason }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            v-if="selectedGeneration.image_url && selectedGeneration.status === 'success'"
            class="modal-secondary modal-btn-download"
            type="button"
            title="다운로드"
            @click="downloadImage"
          >
            <img src="@/assets/icons/downloadBtn.svg" alt="" class="modal-btn-icon" />
            다운로드
          </button>
          <button
            v-if="selectedGeneration.image_url && selectedGeneration.status === 'success'"
            class="modal-secondary"
            type="button"
            @click="openImageInNewTab"
          >
            새 탭에서 열기
          </button>
        </div>
      </div>
    </div>

  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { generationsApi, type GenerationItem } from "@/services/api";

const list = ref<GenerationItem[]>([]);
const loading = ref(true);
const authRequired = ref(false);
const selectedGeneration = ref<GenerationItem | null>(null);

onMounted(async () => {
  loading.value = true;
  authRequired.value = false;
  try {
    const data = await generationsApi.getMyGenerations();
    list.value = data;
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status;
    if (status === 401) {
      authRequired.value = true;
      list.value = [];
    } else {
      list.value = [];
    }
  } finally {
    loading.value = false;
  }
});

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

function openDetailModal(g: GenerationItem): void {
  selectedGeneration.value = g;
}

function closeDetailModal(): void {
  selectedGeneration.value = null;
}

function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString("ko-KR", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function openImageInNewTab(): void {
  if (selectedGeneration.value?.image_url) {
    window.open(selectedGeneration.value.image_url, "_blank", "noopener");
  }
}

async function downloadImage(): Promise<void> {
  if (!selectedGeneration.value?.image_url) return;
  const url = selectedGeneration.value.image_url;
  const filename = `generation_${selectedGeneration.value.id}.png`;
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

</script>

<style scoped>
.creations-section {
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
  color: #0d0d0f;
  margin-bottom: 0.5rem;
}

.section-description {
  font-size: 1rem;
  color: #6e6e77;
}

/* Loading */
.creations-loading {
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
  border: 3px solid #e6e6ea;
  border-top-color: #e24e12;
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
  color: #6e6e77;
}

/* Empty / Auth */
.creations-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 4rem 1.5rem;
  background: #fafafa;
  border-radius: 1rem;
  border: 1px dashed #e6e6ea;
}

.creations-auth {
  background: #fdf5f0;
  border-color: #fbd9c6;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1.25rem;
  color: #9a9aa3;
}

.creations-auth .empty-icon {
  color: #e24e12;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0d0d0f;
  margin-bottom: 0.5rem;
}

.empty-desc {
  font-size: 0.95rem;
  color: #6e6e77;
  margin-bottom: 1.5rem;
  max-width: 20rem;
}

.btn-primary-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border-radius: 0.75rem;
  text-decoration: none;
  transition: box-shadow 0.2s, transform 0.2s;
}

.btn-primary-empty:hover {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
  transform: translateY(-1px);
}

/* Grid */
.creations-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .creations-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .creations-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.5rem;
  }
}

.creation-card {
  border-radius: 1rem;
  border: 1px solid #e6e6ea;
  overflow: hidden;
  background: #ffffff;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.creation-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-thumb-wrap {
  aspect-ratio: 1;
  background: #f2f2f4;
}

.card-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-thumb-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fce3d6 0%, #fce3d6 100%);
}

.card-thumb-failed {
  background: linear-gradient(135deg, #fee2e2 0%, #f2f2f4 100%);
}

.placeholder-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6e6e77;
}

.card-thumb-failed .placeholder-label {
  color: #52525b;
}

.card-meta {
  padding: 1rem;
}

.card-prompt {
  font-size: 0.95rem;
  color: #3a3a42;
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
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #9a9aa3;
}

.card-credits {
  font-weight: 500;
  color: #e24e12;
}

.card-share-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #e24e12;
  background: transparent;
  border: 1px solid #fad3be;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.card-share-btn:hover {
  background: #fdede4;
  border-color: #f08a5d;
}

.card-share-btn.is-shared {
  color: #059669;
  border-color: #a7f3d0;
  background: #ecfdf5;
}

.card-share-icon {
  width: 0.9rem;
  height: 0.9rem;
  opacity: 0.9;
}

/* Detail Modal */
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

.detail-modal {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e6e6ea;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f2f2f4;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0d0d0f;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #6e6e77;
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background: #f2f2f4;
}

.detail-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: #ffffff;
}

.detail-image-wrapper {
  width: 100%;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #f2f2f4;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.detail-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fce3d6 0%, #fce3d6 100%);
}

.detail-image-failed {
  background: linear-gradient(135deg, #fee2e2 0%, #f2f2f4 100%);
}

.placeholder-label-large {
  font-size: 1.25rem;
  font-weight: 500;
  color: #6e6e77;
}

.detail-image-failed .placeholder-label-large {
  color: #52525b;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #3a3a42;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.95rem;
  color: #0d0d0f;
  line-height: 1.5;
}

.detail-prompt {
  background: #fafafa;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e6e6ea;
  word-break: break-word;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

@media (min-width: 640px) {
  .detail-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: #fafafa;
  border-radius: 0.5rem;
  border: 1px solid #e6e6ea;
}

.detail-item-label {
  font-size: 0.75rem;
  color: #6e6e77;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: #0d0d0f;
}

.detail-status {
  text-transform: capitalize;
}

.status-success {
  color: #059669;
}

.status-failed {
  color: #dc2626;
}

.status-pending {
  color: #6e6e77;
}

.detail-seed {
  font-family: monospace;
  background: #fafafa;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #e6e6ea;
  font-size: 0.875rem;
}

.detail-error {
  background: #fef2f2;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #fecaca;
}

.detail-error .detail-label {
  color: #dc2626;
}

.detail-error-text {
  color: #991b1b;
  font-size: 0.875rem;
}

.modal-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid #f2f2f4;
  position: sticky;
  bottom: 0;
  background: white;
}

.modal-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e6e6ea;
  border-radius: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #0d0d0f;
  background: #ffffff;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.modal-secondary:hover {
  background: #fafafa;
  border-color: #d2d2d9;
}

.modal-secondary.is-shared {
  color: #059669;
  border-color: #a7f3d0;
  background: #ecfdf5;
}

.modal-btn-download {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.modal-btn-icon {
  width: 1rem;
  height: 1rem;
}

/* Share 확인 모달 (AI Image Generation과 동일) */
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
  color: #0d0d0f;
  margin: 0 0 0.75rem;
}
.confirm-message {
  font-size: 0.9375rem;
  color: #52525b;
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
  color: #3a3a42;
  background: #fafafa;
  border: 1px solid #e6e6ea;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.btn-confirm-cancel:hover {
  background: #f2f2f4;
  border-color: #d2d2d9;
}
.btn-confirm-ok {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: #e85f26;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-confirm-ok:hover {
  background: #e24e12;
}
</style>
