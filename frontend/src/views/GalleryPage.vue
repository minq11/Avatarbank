<template>
  <section class="gallery-section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">Gallery</h2>
        <p class="section-description">
          Creations shared by the community
        </p>
      </div>

      <div v-if="loading" class="gallery-loading">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p class="loading-text">Loading gallery…</p>
      </div>

      <div v-else-if="list.length === 0" class="gallery-empty">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="m21 15-5-5L5 21"/>
          </svg>
        </div>
        <h3 class="empty-title">No shared creations yet</h3>
        <p class="empty-desc">When users share from My creations, they will appear here.</p>
      </div>

      <div v-else class="gallery-grid">
        <article
          v-for="item in list"
          :key="item.id"
          class="gallery-card"
          @click="selectedItem = item"
        >
          <div class="card-thumb-wrap">
            <img
              :src="item.image_url"
              :alt="item.prompt"
              class="card-thumb"
              loading="lazy"
            />
          </div>
          <div class="card-meta">
            <p class="card-prompt" :title="item.prompt">{{ truncate(item.prompt, 48) }}</p>
            <div class="card-footer">
              <span class="card-creator">@{{ item.creator_nickname }}</span>
              <span class="card-date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <GenerationDetailModal
      :item="selectedItem"
      @close="selectedItem = null"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import GenerationDetailModal from "@/components/GenerationDetailModal.vue";
import { galleryApi, type GalleryItem } from "@/services/api";

const list = ref<GalleryItem[]>([]);
const loading = ref(true);
const selectedItem = ref<GalleryItem | null>(null);

onMounted(async () => {
  loading.value = true;
  try {
    list.value = await galleryApi.getGenerations();
  } catch {
    list.value = [];
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
</script>

<style scoped>
.gallery-section {
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

.gallery-loading {
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

.gallery-empty {
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

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.5rem;
  }
}

.gallery-card {
  cursor: pointer;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  background: #ffffff;
  transition: box-shadow 0.2s, transform 0.2s;
}

.gallery-card:hover {
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

.card-creator {
  font-weight: 500;
  color: #4f46e5;
}
</style>
