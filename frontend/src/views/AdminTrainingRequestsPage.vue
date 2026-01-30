<template>
  <section class="admin-training-section">
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">Admin Training Requests</h2>
        <p class="page-subtitle">
          Admins can view all users' Training Requests and download photos in bulk.
        </p>
      </div>

      <div class="main-layout">
        <!-- Training Request List -->
        <div class="training-request-section">
          <div class="section-header">
            <h3 class="section-title">Training Requests</h3>
          </div>

          <!-- Loading -->
          <div v-if="loadingRequests" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading requests...</p>
          </div>

          <!-- Empty -->
          <div v-else-if="trainingRequests.length === 0" class="empty-state">
            <p>No training requests found</p>
          </div>

          <!-- Requests Grid -->
          <div v-else class="requests-grid">
            <div class="grid-header">
              <div class="grid-cell">Request ID</div>
              <div class="grid-cell">Requested by</div>
              <div class="grid-cell">Request Date</div>
              <div class="grid-cell">Status</div>
              <div class="grid-cell grid-cell-actions">Actions</div>
            </div>
            <div
              v-for="request in trainingRequests"
              :key="request.id"
              class="grid-row"
              :class="{ 'grid-row-selected': selectedRequest?.id === request.id }"
              @click="openRequestDetailModal(request)"
            >
              <div class="grid-cell">{{ request.id }}</div>
              <div class="grid-cell grid-cell-requester">
                <span class="requester-nickname">{{ request.user_nickname }}</span>
                <span class="requester-email">{{ request.user_email }}</span>
              </div>
              <div class="grid-cell">{{ formatDate(request.created_at) }}</div>
              <div class="grid-cell">
                <span :class="`status-badge status-${getStatusClass(request.status)}`">
                  {{ getStatusLabel(request.status) }}
                </span>
              </div>
              <div
                class="grid-cell grid-cell-actions"
                :class="{ 'actions-approved': isApprovedTraining(request.status) }"
                @click.stop
              >
                <button
                  v-if="isApprovedTraining(request.status)"
                  type="button"
                  class="btn-grid btn-download-lora"
                  @click="downloadLoRA(request.id)"
                >
                  Download LoRA
                </button>
                <button
                  type="button"
                  class="btn-grid btn-upload-lora"
                  @click="openLoraUploadModal(request)"
                >
                  Upload LoRA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Request Detail Modal -->
    <div v-if="selectedRequest" class="modal-overlay" @click.self="closeRequestDetailModal">
      <div class="modal-card training-detail-modal">
        <div class="modal-header">
          <h3>Training Request Details</h3>
          <button class="modal-close" type="button" @click="closeRequestDetailModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h4 class="form-section-title">Basic Information</h4>

            <div class="form-group">
              <label class="form-label">Avatar name</label>
              <input
                :value="selectedRequest.avatar_name"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">Is this avatar based on a real person?</label>
              <input
                :value="selectedRequest.is_real_person ? 'Yes' : 'No'"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div v-if="selectedRequest.is_real_person" class="form-group">
              <label class="form-label">Instagram ID</label>
              <input
                :value="selectedRequest.instagram_id || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">Negative prompt</label>
              <input
                :value="selectedRequest.negative_prompt || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">Credit per generation</label>
              <input
                :value="selectedRequest.credit_per_generation"
                type="number"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">National</label>
              <input
                :value="selectedRequest.national || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">Gender</label>
              <input
                :value="selectedRequest.gender || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea
                :value="selectedRequest.description || ''"
                class="form-textarea"
                rows="4"
                readonly
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Preview Image</label>
              <div v-if="selectedRequest.preview_image_url" class="preview-image">
                <img :src="getImageUrl(selectedRequest.preview_image_url)" alt="Preview" />
              </div>
              <div v-else class="preview-placeholder">No image</div>
            </div>
          </div>

          <!-- Training Photos -->
          <div class="form-section">
            <div class="form-section-header">
              <h4 class="form-section-title">Training Photos</h4>
              <button
                class="btn-primary btn-download"
                type="button"
                @click="downloadAllPhotos"
              >
                Download all photos
              </button>
            </div>

            <!-- Front -->
            <div
              v-if="selectedRequest.front_photos_urls && selectedRequest.front_photos_urls.length > 0"
              class="photo-category"
            >
              <label class="category-label">Front</label>
              <div class="photo-slots">
                <div
                  v-for="(url, index) in selectedRequest.front_photos_urls"
                  :key="`front-${index}`"
                  class="photo-slot readonly"
                >
                  <img :src="getImageUrl(url)" alt="Front photo" class="slot-image" />
                </div>
              </div>
            </div>

            <!-- Side -->
            <div
              v-if="selectedRequest.side_photos_urls && selectedRequest.side_photos_urls.length > 0"
              class="photo-category"
            >
              <label class="category-label">Side</label>
              <div class="photo-slots">
                <div
                  v-for="(url, index) in selectedRequest.side_photos_urls"
                  :key="`side-${index}`"
                  class="photo-slot readonly"
                >
                  <img :src="getImageUrl(url)" alt="Side photo" class="slot-image" />
                </div>
              </div>
            </div>

            <!-- Full Body -->
            <div
              v-if="selectedRequest.fullbody_photos_urls && selectedRequest.fullbody_photos_urls.length > 0"
              class="photo-category"
            >
              <label class="category-label">Full Body</label>
              <div class="photo-slots">
                <div
                  v-for="(url, index) in selectedRequest.fullbody_photos_urls"
                  :key="`fullbody-${index}`"
                  class="photo-slot readonly"
                >
                  <img :src="getImageUrl(url)" alt="Full body photo" class="slot-image" />
                </div>
              </div>
            </div>

            <!-- Other -->
            <div
              v-if="selectedRequest.other_photos_urls && selectedRequest.other_photos_urls.length > 0"
              class="photo-category"
            >
              <label class="category-label">Other</label>
              <div class="photo-slots">
                <div
                  v-for="(url, index) in selectedRequest.other_photos_urls"
                  :key="`other-${index}`"
                  class="photo-slot readonly"
                >
                  <img :src="getImageUrl(url)" alt="Other photo" class="slot-image" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            class="btn-secondary"
            type="button"
            @click="closeRequestDetailModal"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Upload LoRA Modal -->
    <div v-if="showLoraUploadModal" class="modal-overlay" @click.self="closeLoraUploadModal">
      <div class="modal-card lora-upload-modal">
        <div class="modal-header">
          <h3>Upload LoRA (.safetensors)</h3>
          <button class="modal-close" type="button" @click="closeLoraUploadModal">×</button>
        </div>
        <div class="modal-body">
          <p v-if="loraUploadRequest" class="lora-modal-context">
            Request #{{ loraUploadRequest.id }} — {{ loraUploadRequest.avatar_name }}
          </p>
          <p class="form-section-desc">
            Upload a LoRA file trained via a third-party tool. It will be stored in S3 and an Avatar linked to this request will be created or updated.
          </p>
          <input
            ref="loraModalFileInput"
            type="file"
            accept=".safetensors"
            class="hidden-file-input"
            @change="handleLoraModalFileChange"
          />
          <div v-if="uploadingLoRA" class="upload-progress-wrap">
            <div class="upload-progress-bar">
              <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span class="upload-progress-text">{{ uploadProgress }}%</span>
          </div>
          <button
            class="btn-primary btn-upload-lora"
            type="button"
            :disabled="uploadingLoRA"
            @click="loraModalFileInput?.click()"
          >
            {{ uploadingLoRA ? "Uploading..." : "Select & Upload .safetensors" }}
          </button>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" type="button" @click="closeLoraUploadModal">
            Close
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import {
  trainingRequestsApi,
  type AdminTrainingRequestItem,
  type TrainingRequestDetailItem,
} from "@/services/api";

// Helper function to convert static file paths to full URLs
function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("/static/")) {
    return `/api${url}`;
  }
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  return url;
}

const loadingRequests = ref(false);
const trainingRequests = ref<AdminTrainingRequestItem[]>([]);
const selectedRequest = ref<TrainingRequestDetailItem | null>(null);
const showLoraUploadModal = ref(false);
const loraUploadRequest = ref<AdminTrainingRequestItem | null>(null);
const loraModalFileInput = ref<HTMLInputElement | null>(null);
const uploadingLoRA = ref(false);
const uploadProgress = ref(0);

onMounted(async () => {
  await loadTrainingRequests();
});

async function loadTrainingRequests() {
  loadingRequests.value = true;
  try {
    trainingRequests.value = await trainingRequestsApi.getAllRequestsAdmin();
  } catch (error) {
    console.error("Failed to load training requests (admin):", error);
    trainingRequests.value = [];
  } finally {
    loadingRequests.value = false;
  }
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  } catch {
    return "";
  }
}

function getStatusLabel(status: string): string {
  const statusMap: Record<string, string> = {
    requested: "Requested",
    approved_training: "Approved - Training",
    rejected: "Rejected",
    cancelled: "Cancelled",
  };
  return statusMap[status] || status;
}

function getStatusClass(status: string): string {
  const classMap: Record<string, string> = {
    requested: "requested",
    approved_training: "approved",
    rejected: "rejected",
    cancelled: "cancelled",
  };
  return classMap[status] || "default";
}

function isApprovedTraining(status: string): boolean {
  if (!status) return false;
  const s = String(status).toLowerCase();
  return s === "approved_training" || s.replace(/[\s-]/g, "_") === "approved_training" || s.includes("approved");
}

async function openRequestDetailModal(request: AdminTrainingRequestItem) {
  try {
    selectedRequest.value = await trainingRequestsApi.getRequestDetailAdmin(
      request.id,
    );
  } catch (error) {
    console.error("Failed to load request detail (admin):", error);
    alert("Failed to load request details.");
  }
}

function closeRequestDetailModal() {
  selectedRequest.value = null;
}

function openLoraUploadModal(request: AdminTrainingRequestItem) {
  loraUploadRequest.value = request;
  showLoraUploadModal.value = true;
}

function closeLoraUploadModal() {
  showLoraUploadModal.value = false;
  loraUploadRequest.value = null;
  uploadProgress.value = 0;
  if (loraModalFileInput.value) {
    loraModalFileInput.value.value = "";
  }
}

async function downloadLoRA(requestId: number) {
  try {
    const { url } = await trainingRequestsApi.getLoraDownloadUrlAdmin(requestId);
    const a = document.createElement("a");
    a.href = url;
    a.download = `training_request_${requestId}_lora.safetensors`;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (error: unknown) {
    console.error("Failed to get LoRA download URL:", error);
    const msg =
      (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      "Failed to download LoRA.";
    alert(msg);
  }
}

async function handleLoraModalFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file || !loraUploadRequest.value) return;
  if (!file.name.toLowerCase().endsWith(".safetensors")) {
    alert("Only .safetensors files are allowed.");
    input.value = "";
    return;
  }

  uploadingLoRA.value = true;
  uploadProgress.value = 0;
  try {
    await trainingRequestsApi.uploadLoRAAdmin(
      loraUploadRequest.value.id,
      file,
      (percent) => {
        uploadProgress.value = percent;
      }
    );
    alert("LoRA uploaded successfully. Avatar has been created or updated.");
    input.value = "";
    closeLoraUploadModal();
    await loadTrainingRequests();
  } catch (error: unknown) {
    console.error("Failed to upload LoRA:", error);
    const msg =
      (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      "Failed to upload LoRA. Please try again.";
    alert(msg);
  } finally {
    uploadingLoRA.value = false;
  }
}

async function downloadAllPhotos() {
  if (!selectedRequest.value) return;

  try {
    const blob = await trainingRequestsApi.downloadPhotosZipAdmin(
      selectedRequest.value.id,
    );
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `training_request_${selectedRequest.value.id}_photos.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Failed to download photos zip:", error);
    alert("Failed to download photos. Please try again.");
  }
}
</script>

<style scoped>
.admin-training-section {
  padding: 3rem 0 5rem;
  background: #ffffff;
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (min-width: 1024px) {
  .container {
    padding: 0 4rem;
  }
}

.page-header {
  margin-bottom: 2.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
}

.page-subtitle {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #6b7280;
}

.main-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.training-request-section {
  flex: 1;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  gap: 1rem;
  color: #6b7280;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
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

.requests-grid {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow-x: auto;
  overflow-y: visible;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.grid-header {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr minmax(260px, auto);
  min-width: min-content;
  background: #f1f5f9;
  font-weight: 600;
  font-size: 0.8125rem;
  color: #475569;
  letter-spacing: 0.02em;
}

.grid-row {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr minmax(260px, auto);
  min-width: min-content;
  border-top: 1px solid #e2e8f0;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.grid-row:hover {
  background-color: #f8fafc;
}

.grid-row-selected {
  background-color: #eff6ff;
}

.grid-cell {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
}

.grid-cell-requester {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.requester-nickname {
  font-weight: 500;
  color: #111827;
}

.requester-email {
  font-size: 0.75rem;
  color: #6b7280;
}

.grid-cell-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: nowrap;
  padding-right: 1rem;
}

.btn-grid {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2rem;
  padding: 0 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-sizing: border-box;
}

/* 기본: Upload가 주 액션 */
.btn-grid.btn-upload-lora {
  color: white;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  box-shadow: 0 1px 2px rgba(79, 70, 229, 0.2);
}

.btn-grid.btn-upload-lora:hover {
  box-shadow: 0 4px 8px -2px rgba(79, 70, 229, 0.35);
  transform: translateY(-1px);
}

.btn-grid.btn-download-lora {
  color: #475569;
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.btn-grid.btn-download-lora:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}

/* Approved 상태: Download가 주 액션, Upload는 보조 */
.grid-cell-actions.actions-approved .btn-download-lora {
  color: white;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-color: transparent;
  box-shadow: 0 1px 2px rgba(5, 150, 105, 0.25);
}

.grid-cell-actions.actions-approved .btn-download-lora:hover {
  box-shadow: 0 4px 8px -2px rgba(5, 150, 105, 0.35);
  transform: translateY(-1px);
}

.grid-cell-actions.actions-approved .btn-upload-lora {
  color: #475569;
  background: #fff;
  border-color: #cbd5e1;
  box-shadow: none;
}

.grid-cell-actions.actions-approved .btn-upload-lora:hover {
  background: #f8fafc;
  border-color: #94a3b8;
  box-shadow: none;
  transform: none;
}

.lora-modal-context {
  font-size: 0.9rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.5rem;
}

.modal-card.lora-upload-modal {
  max-width: 420px;
}

.upload-progress-wrap {
  margin-bottom: 0.75rem;
}

.upload-progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.upload-progress-fill {
  height: 100%;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border-radius: 9999px;
  transition: width 0.2s ease;
}

.upload-progress-text {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-requested {
  background: #dbeafe;
  color: #1e40af;
}

.status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status-cancelled {
  background: #f3f4f6;
  color: #6b7280;
}

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
  max-width: 900px;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.modal-header h3 {
  font-size: 1.25rem;
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
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.form-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.form-section-desc {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.hidden-file-input {
  display: none;
}

.btn-upload-lora {
  margin-top: 0.25rem;
}

.btn-upload-lora:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  color: #111827;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  transition: border-color 0.2s;
}

.form-input[readonly],
.form-textarea[readonly] {
  background-color: #f9fafb;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.preview-image {
  position: relative;
  display: inline-block;
  width: 150px;
  height: 150px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}

.photo-category {
  margin-bottom: 2rem;
}

.category-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.75rem;
}

.photo-slots {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.photo-slot {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  background: #f9fafb;
  border: 2px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: default;
  overflow: hidden;
}

.photo-slot.readonly {
  cursor: default;
}

.slot-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-download {
  font-size: 0.8rem;
  padding: 0.5rem 0.9rem;
}

@media (max-width: 768px) {
  .modal-card {
    max-width: 100%;
    max-height: 95vh;
  }
}
</style>

