<template>
  <section class="creations-section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">My creations</h2>
        <p class="section-description">
          Images you've generated with AI avatars
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="creations-loading">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p class="loading-text">Loading your creations…</p>
      </div>

      <!-- Auth required -->
      <div v-else-if="authRequired" class="creations-empty creations-auth">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h3 class="empty-title">Log in to view your creations</h3>
        <p class="empty-desc">Sign in to see all images you’ve generated.</p>
        <RouterLink to="/" class="btn-primary-empty">Go to home</RouterLink>
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
        <h3 class="empty-title">No creations yet</h3>
        <p class="empty-desc">Generate your first image with an AI avatar.</p>
        <RouterLink to="/generate" class="btn-primary-empty">Create image</RouterLink>
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
              <span v-if="g.status === 'failed'" class="placeholder-label">Failed</span>
              <span v-else class="placeholder-label">Processing…</span>
            </div>
          </div>
          <div class="card-meta">
            <p class="card-prompt" :title="g.prompt">{{ truncate(g.prompt, 48) }}</p>
            <div class="card-footer">
              <span class="card-credits">{{ g.credits_used }}C</span>
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
          <h3>Generation Details</h3>
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
              <span v-if="selectedGeneration.status === 'failed'" class="placeholder-label-large">Failed</span>
              <span v-else class="placeholder-label-large">Processing…</span>
            </div>
          </div>

          <!-- Details -->
          <div class="detail-info">
            <div class="detail-section">
              <h4 class="detail-label">Prompt</h4>
              <p class="detail-value detail-prompt">{{ selectedGeneration.prompt }}</p>
            </div>

            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-item-label">Credits Used</span>
                <span class="detail-item-value">{{ selectedGeneration.credits_used }}C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">Base Credits</span>
                <span class="detail-item-value">1C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">Option Credits</span>
                <span class="detail-item-value">{{ selectedGeneration.credits_used - 1 }}C</span>
              </div>
              <div class="detail-item">
                <span class="detail-item-label">Status</span>
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
              <h4 class="detail-label">Seed</h4>
              <p class="detail-value detail-seed">{{ selectedGeneration.seed }}</p>
            </div>

            <div v-if="selectedGeneration.avatar_id" class="detail-section">
              <h4 class="detail-label">Avatar ID</h4>
              <p class="detail-value">{{ selectedGeneration.avatar_id }}</p>
            </div>

            <div class="detail-section">
              <h4 class="detail-label">Created At</h4>
              <p class="detail-value">{{ formatDateTime(selectedGeneration.created_at) }}</p>
            </div>

            <div v-if="selectedGeneration.fail_reason" class="detail-section detail-error">
              <h4 class="detail-label">Error</h4>
              <p class="detail-value detail-error-text">{{ selectedGeneration.fail_reason }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            v-if="selectedGeneration.image_url && selectedGeneration.status === 'success'"
            class="modal-secondary"
            type="button"
            @click="openImageInNewTab"
          >
            Open in new tab
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
    return d.toLocaleDateString("en-US", {
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
    return d.toLocaleString("en-US", {
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
  color: #111827;
  margin-bottom: 0.5rem;
}

.section-description {
  font-size: 1rem;
  color: #6b7280;
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

/* Empty / Auth */
.creations-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 4rem 1.5rem;
  background: #f9fafb;
  border-radius: 1rem;
  border: 1px dashed #e5e7eb;
}

.creations-auth {
  background: #faf5ff;
  border-color: #e9d5ff;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1.25rem;
  color: #9ca3af;
}

.creations-auth .empty-icon {
  color: #7c3aed;
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
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border-radius: 0.75rem;
  text-decoration: none;
  transition: box-shadow 0.2s, transform 0.2s;
}

.btn-primary-empty:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
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
  border: 1px solid #e5e7eb;
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
  background: #f3f4f6;
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
  background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%);
}

.card-thumb-failed {
  background: linear-gradient(135deg, #fee2e2 0%, #fef3c7 100%);
}

.placeholder-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.card-thumb-failed .placeholder-label {
  color: #b45309;
}

.card-meta {
  padding: 1rem;
}

.card-prompt {
  font-size: 0.95rem;
  color: #374151;
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
  font-size: 0.8rem;
  color: #9ca3af;
}

.card-credits {
  font-weight: 500;
  color: #4f46e5;
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
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #6b7280;
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
  background: #f3f4f6;
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
  background: #f3f4f6;
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
  background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%);
}

.detail-image-failed {
  background: linear-gradient(135deg, #fee2e2 0%, #fef3c7 100%);
}

.placeholder-label-large {
  font-size: 1.25rem;
  font-weight: 500;
  color: #6b7280;
}

.detail-image-failed .placeholder-label-large {
  color: #b45309;
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
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.95rem;
  color: #111827;
  line-height: 1.5;
}

.detail-prompt {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
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
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.detail-item-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: #111827;
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
  color: #d97706;
}

.detail-seed {
  font-family: monospace;
  background: #f9fafb;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
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
  border-top: 1px solid #f3f4f6;
  position: sticky;
  bottom: 0;
  background: white;
}

.modal-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #111827;
  background: #ffffff;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.modal-secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}
</style>
