<template>
  <div v-if="item" class="modal-overlay" @click.self="close">
    <div class="modal-card detail-modal">
      <div class="modal-header">
        <h3>Generation Details</h3>
        <button class="modal-close" type="button" @click="close" aria-label="Close">×</button>
      </div>
      <div class="modal-body detail-modal-body">
        <div class="detail-image-wrapper">
          <img
            :src="displayImageUrl"
            :alt="item.prompt"
            class="detail-image"
          />
        </div>
        <div class="detail-info">
          <div class="detail-section">
            <h4 class="detail-label">Prompt</h4>
            <p class="detail-value detail-prompt">{{ item.prompt }}</p>
          </div>
          <div class="detail-section">
            <h4 class="detail-label">Creator</h4>
            <p class="detail-value">@{{ item.creator_nickname }}</p>
          </div>
          <div class="detail-section">
            <h4 class="detail-label">Created At</h4>
            <p class="detail-value">{{ formatDateTime(item.created_at) }}</p>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button
          class="modal-secondary modal-btn-download"
          type="button"
          title="Download"
          @click="downloadImage"
        >
          <img src="@/assets/icons/downloadBtn.svg" alt="" class="modal-btn-icon" />
          Download
        </button>
        <button class="modal-secondary" type="button" @click="openInNewTab">
          Open in new tab
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { GalleryItem } from "@/services/api";

const props = defineProps<{
  item: GalleryItem | null;
  /** Optional: resolve image URL (e.g. for relative paths) */
  imageUrlResolver?: (url: string) => string;
}>();

const emit = defineEmits<{
  close: [];
}>();

const displayImageUrl = computed(() => {
  if (!props.item?.image_url) return "";
  return props.imageUrlResolver ? props.imageUrlResolver(props.item.image_url) : props.item.image_url;
});

function close() {
  emit("close");
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

function openInNewTab() {
  if (props.item?.image_url) {
    const url = displayImageUrl.value || props.item.image_url;
    window.open(url, "_blank", "noopener");
  }
}

async function downloadImage() {
  if (!props.item?.image_url) return;
  const url = displayImageUrl.value || props.item.image_url;
  const filename = `generation_${props.item.id}.png`;
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

.modal-card.detail-modal {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e5e8f0;
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

.modal-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  background: #ffffff;
}

.modal-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.modal-secondary:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.modal-btn-download {
  color: #4f46e5;
  background: #eef2ff;
  border-color: #c7d2fe;
}

.modal-btn-download:hover {
  background: #e0e7ff;
  border-color: #818cf8;
}

.modal-btn-icon {
  width: 1rem;
  height: 1rem;
  opacity: 0.9;
}
</style>
