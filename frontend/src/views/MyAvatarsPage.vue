<template>
  <section class="avatars-section">
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">My Avatars</h2>
      </div>

      <div class="main-layout">
        <!-- Training Request Section (1/3) -->
        <div class="training-request-section">
          <div class="section-header">
            <h3 class="section-title">Training Request</h3>
            <button class="btn-new-request" type="button" @click="openTrainingRequestModal">
              New Request
            </button>
          </div>

          <!-- Loading -->
          <div v-if="loadingRequests" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading requests...</p>
          </div>

          <!-- Empty -->
          <div v-else-if="trainingRequests.length === 0" class="empty-state">
            <p>No training requests yet</p>
          </div>

          <!-- Requests Grid -->
          <div v-else class="requests-grid">
            <div class="grid-header">
              <div class="grid-cell">Request ID</div>
              <div class="grid-cell">Request Date</div>
              <div class="grid-cell">Status</div>
            </div>
            <div
              v-for="request in trainingRequests"
              :key="request.id"
              class="grid-row"
            >
              <div class="grid-cell">{{ request.id }}</div>
              <div class="grid-cell">{{ formatDate(request.created_at) }}</div>
              <div class="grid-cell">
                <span :class="`status-badge status-${getStatusClass(request.status)}`">
                  {{ getStatusLabel(request.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- My Avatars Section (2/3) -->
        <div class="avatars-section-content">
          <div class="section-header">
            <h3 class="section-title">My Avatars</h3>
          </div>

          <!-- Loading -->
          <div v-if="loadingAvatars" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading avatars...</p>
          </div>

          <!-- Empty -->
          <div v-else-if="avatars.length === 0" class="empty-state">
            <p>No avatars yet</p>
          </div>

          <!-- Avatars Grid -->
          <div v-else class="avatars-grid">
            <div
              v-for="avatar in avatars"
              :key="avatar.id"
              class="avatar-card"
              @click="openAvatarDetailModal(avatar)"
            >
              <div class="avatar-image-wrapper">
                <img
                  v-if="avatar.preview_image_url"
                  :src="avatar.preview_image_url"
                  :alt="avatar.title"
                  class="avatar-image"
                />
                <div v-else class="avatar-image-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
              </div>
              <div class="avatar-name">{{ avatar.title }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Request Modal -->
    <div v-if="showTrainingRequestModal" class="modal-overlay" @click.self="closeTrainingRequestModal">
      <div class="modal-card training-modal">
        <div class="modal-header">
          <h3>Avatar Training Request</h3>
          <button class="modal-close" type="button" @click="closeTrainingRequestModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Basic Information Input -->
          <div class="form-section">
            <h4 class="form-section-title">Basic Information</h4>
            
            <div class="form-group">
              <label class="form-label">Avatar name <span class="required">*</span></label>
              <input
                v-model="trainingForm.avatarName"
                type="text"
                class="form-input"
                placeholder="Enter avatar name"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Negative prompt <span class="required">*</span></label>
              <input
                v-model="trainingForm.negativePrompt"
                type="text"
                class="form-input"
                placeholder="Enter negative prompt"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Credit per generation <span class="required">*</span></label>
              <input
                v-model.number="trainingForm.creditPerGeneration"
                type="number"
                min="1"
                class="form-input"
                placeholder="Credits per generation"
              />
            </div>

            <div class="form-group">
              <label class="form-label">National <span class="required">*</span></label>
              <select v-model="trainingForm.national" class="form-input">
                <option value="">Select nationality</option>
                <option value="KR">Korea</option>
                <option value="US">United States</option>
                <option value="JP">Japan</option>
                <option value="CN">China</option>
                <option value="GB">United Kingdom</option>
                <option value="FR">France</option>
                <option value="DE">Germany</option>
                <option value="IT">Italy</option>
                <option value="ES">Spain</option>
                <option value="BR">Brazil</option>
                <option value="IN">India</option>
                <option value="RU">Russia</option>
                <option value="AU">Australia</option>
                <option value="CA">Canada</option>
                <option value="MX">Mexico</option>
                <option value="ETC">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Gender <span class="required">*</span></label>
              <div class="radio-group">
                <label class="radio-label">
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="M"
                    class="radio-input"
                  />
                  <span>M</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="W"
                    class="radio-input"
                  />
                  <span>W</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="Etc"
                    class="radio-input"
                  />
                  <span>Etc</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Description <span class="required">*</span></label>
              <textarea
                v-model="trainingForm.description"
                class="form-textarea"
                rows="4"
                placeholder="Enter avatar description"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Preview Image <span class="required">*</span></label>
              <div class="file-upload-wrapper">
                <input
                  ref="previewImageInput"
                  type="file"
                  accept="image/*"
                  class="file-input"
                  @change="handlePreviewImageChange"
                />
                <div v-if="trainingForm.previewImage" class="preview-image">
                  <img :src="trainingForm.previewImageUrl" alt="Preview" />
                  <button
                    type="button"
                    class="remove-image-btn"
                    @click="removePreviewImage"
                  >
                    ×
                  </button>
                </div>
                <button
                  v-else
                  type="button"
                  class="file-upload-btn"
                  @click="previewImageInput?.click()"
                >
                  Select Image
                </button>
              </div>
            </div>
          </div>

          <!-- Real Person Based Avatar -->
          <div class="form-section">
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="trainingForm.isRealPerson"
                  type="checkbox"
                  class="checkbox-input"
                />
                <span>Real Person Based Avatar</span>
              </label>
            </div>

            <template v-if="trainingForm.isRealPerson">
              <div class="form-group">
                <label class="form-label">Instagram ID <span class="required">*</span></label>
                <input
                  v-model="trainingForm.instagramId"
                  type="text"
                  class="form-input"
                  placeholder="Enter Instagram ID"
                />
              </div>
              <div class="info-box">
                <p>
                  Please confirm this is your request via DM (<a
                    href="https://www.instagram.com/avatarbank_official/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >@avatarbank_official</a>).
                </p>
                <p>We will not train if this is not your request.</p>
              </div>
            </template>
          </div>

          <!-- Training Photos Upload -->
          <div class="form-section">
            <h4 class="form-section-title">Training Photos Upload</h4>

            <!-- Front -->
            <div class="photo-category">
              <label class="category-label">Front <span class="required">Min. 4 photos</span></label>
              <div class="photo-slots">
                <label
                  v-for="(slot, index) in trainingForm.frontPhotos"
                  :key="`front-${index}`"
                  class="photo-slot"
                >
                  <img
                    v-if="slot.url"
                    :src="slot.url"
                    alt="Front photo"
                    class="slot-image"
                  />
                  <div v-else class="slot-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('front', index, e)"
                  />
                </label>
              </div>
            </div>

            <!-- Side -->
            <div class="photo-category">
              <label class="category-label">Side <span class="required">Min. 4 photos</span></label>
              <div class="photo-slots">
                <label
                  v-for="(slot, index) in trainingForm.sidePhotos"
                  :key="`side-${index}`"
                  class="photo-slot"
                >
                  <img
                    v-if="slot.url"
                    :src="slot.url"
                    alt="Side photo"
                    class="slot-image"
                  />
                  <div v-else class="slot-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('side', index, e)"
                  />
                </label>
              </div>
            </div>

            <!-- Full Body -->
            <div class="photo-category">
              <label class="category-label">Full Body <span class="required">Min. 1 photo</span></label>
              <div class="photo-slots">
                <label
                  v-for="(slot, index) in trainingForm.fullBodyPhotos"
                  :key="`fullbody-${index}`"
                  class="photo-slot"
                >
                  <img
                    v-if="slot.url"
                    :src="slot.url"
                    alt="Full body photo"
                    class="slot-image"
                  />
                  <div v-else class="slot-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('fullbody', index, e)"
                  />
                </label>
              </div>
            </div>

            <!-- Other -->
            <div class="photo-category">
              <label class="category-label">Other <span class="required">Min. 1 photo</span></label>
              <div class="photo-slots">
                <label
                  v-for="(slot, index) in trainingForm.otherPhotos"
                  :key="`other-${index}`"
                  class="photo-slot"
                >
                  <img
                    v-if="slot.url"
                    :src="slot.url"
                    alt="Other photo"
                    class="slot-image"
                  />
                  <div v-else class="slot-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('other', index, e)"
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            class="btn-secondary"
            type="button"
            @click="closeTrainingRequestModal"
          >
            Close
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="!isTrainingFormValid || submitting"
            @click="submitTrainingRequest"
          >
            {{ submitting ? "Submitting..." : "Submit Request" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Avatar Detail and Edit Modal -->
    <div v-if="selectedAvatar" class="modal-overlay" @click.self="closeAvatarDetailModal">
      <div class="modal-card avatar-detail-modal">
        <div class="modal-header">
          <h3>Avatar Details</h3>
          <button class="modal-close" type="button" @click="closeAvatarDetailModal">×</button>
        </div>

        <div class="modal-body">
          <!-- View Section -->
          <div class="detail-section">
            <h4 class="detail-section-title">Preview Image</h4>
            <div class="preview-image-large">
              <img
                v-if="selectedAvatar.preview_image_url"
                :src="selectedAvatar.preview_image_url"
                alt="Preview"
              />
              <div v-else class="preview-placeholder">No image</div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="detail-section-title">Information</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label class="detail-label">Avatar name</label>
                <p class="detail-value">{{ selectedAvatar.title }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">Negative prompt</label>
                <p class="detail-value">{{ selectedAvatar.negative_prompt || "N/A" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">Credit per generation</label>
                <p class="detail-value">{{ selectedAvatar.credit_per_generation || "N/A" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">National</label>
                <p class="detail-value">{{ selectedAvatar.nationality || "N/A" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">Gender</label>
                <p class="detail-value">{{ selectedAvatar.gender || "N/A" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">Description</label>
                <p class="detail-value">{{ selectedAvatar.description || "N/A" }}</p>
              </div>
            </div>
          </div>

          <!-- Editable Items -->
          <div class="edit-section">
            <h4 class="detail-section-title">Edit</h4>

            <div class="form-group">
              <label class="form-label">Credit per generation</label>
              <input
                v-model.number="editForm.creditPerGeneration"
                type="number"
                min="1"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Avatar name</label>
              <input
                v-model="editForm.avatarName"
                type="text"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea
                v-model="editForm.description"
                class="form-textarea"
                rows="4"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Preview Image</label>
              <div class="file-upload-wrapper">
                <input
                  ref="editPreviewImageInput"
                  type="file"
                  accept="image/*"
                  class="file-input"
                  @change="handleEditPreviewImageChange"
                />
                <div v-if="editForm.previewImage" class="preview-image">
                  <img :src="editForm.previewImageUrl" alt="Preview" />
                  <button
                    type="button"
                    class="remove-image-btn"
                    @click="removeEditPreviewImage"
                  >
                    ×
                  </button>
                </div>
                <button
                  v-else-if="selectedAvatar.preview_image_url"
                  type="button"
                  class="file-upload-btn"
                  @click="() => editPreviewImageInput?.click()"
                >
                  Change Image
                </button>
                <button
                  v-else
                  type="button"
                  class="file-upload-btn"
                  @click="() => editPreviewImageInput?.click()"
                >
                  Select Image
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            class="btn-secondary"
            type="button"
            @click="closeAvatarDetailModal"
          >
            Close
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="saving"
            @click="saveAvatarChanges"
          >
            {{ saving ? "Saving..." : "Save" }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { avatarsApi, trainingRequestsApi, type AvatarItem, type TrainingRequestItem } from "@/services/api";

// Refs for file inputs
const previewImageInput = ref<HTMLInputElement | null>(null);
const editPreviewImageInput = ref<HTMLInputElement | null>(null);

// State
const loadingRequests = ref(false);
const loadingAvatars = ref(false);
const trainingRequests = ref<TrainingRequestItem[]>([]);
const avatars = ref<AvatarItem[]>([]);
const showTrainingRequestModal = ref(false);
const selectedAvatar = ref<AvatarItem | null>(null);
const submitting = ref(false);
const saving = ref(false);

// Training request form
const trainingForm = ref({
  avatarName: "",
  negativePrompt: "",
  creditPerGeneration: 1,
  national: "",
  gender: "",
  description: "",
  previewImage: null as File | null,
  previewImageUrl: "",
  isRealPerson: false,
  instagramId: "",
  frontPhotos: Array(4).fill(null).map(() => ({ file: null as File | null, url: "" })),
  sidePhotos: Array(4).fill(null).map(() => ({ file: null as File | null, url: "" })),
  fullBodyPhotos: Array(1).fill(null).map(() => ({ file: null as File | null, url: "" })),
  otherPhotos: Array(1).fill(null).map(() => ({ file: null as File | null, url: "" })),
});

// Edit form
const editForm = ref({
  avatarName: "",
  creditPerGeneration: 0,
  description: "",
  previewImage: null as File | null,
  previewImageUrl: "",
});

// Form validation
const isTrainingFormValid = computed(() => {
  const form = trainingForm.value;
  return (
    form.avatarName.trim() !== "" &&
    form.negativePrompt.trim() !== "" &&
    form.creditPerGeneration > 0 &&
    form.national !== "" &&
    form.gender !== "" &&
    form.description.trim() !== "" &&
    form.previewImage !== null &&
    (!form.isRealPerson || form.instagramId.trim() !== "") &&
    form.frontPhotos.filter(p => p.file !== null).length >= 4 &&
    form.sidePhotos.filter(p => p.file !== null).length >= 4 &&
    form.fullBodyPhotos.filter(p => p.file !== null).length >= 1 &&
    form.otherPhotos.filter(p => p.file !== null).length >= 1
  );
});

// Load data
onMounted(async () => {
  await Promise.all([loadTrainingRequests(), loadAvatars()]);
});

async function loadTrainingRequests() {
  loadingRequests.value = true;
  try {
    trainingRequests.value = await trainingRequestsApi.getMyRequests();
  } catch (error) {
    console.error("Failed to load training requests:", error);
    trainingRequests.value = [];
  } finally {
    loadingRequests.value = false;
  }
}

async function loadAvatars() {
  loadingAvatars.value = true;
  try {
    avatars.value = await avatarsApi.getMyAvatars();
  } catch (error) {
    console.error("Failed to load avatars:", error);
    avatars.value = [];
  } finally {
    loadingAvatars.value = false;
  }
}

// Date formatting
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

// Status related
function getStatusLabel(status: string): string {
  const statusMap: Record<string, string> = {
    requested: "Requested",
    approved_training: "Approved - Training",
    rejected: "Rejected",
  };
  return statusMap[status] || status;
}

function getStatusClass(status: string): string {
  const classMap: Record<string, string> = {
    requested: "requested",
    approved_training: "approved",
    rejected: "rejected",
  };
  return classMap[status] || "default";
}

// Modal management
function openTrainingRequestModal() {
  showTrainingRequestModal.value = true;
  resetTrainingForm();
}

function closeTrainingRequestModal() {
  showTrainingRequestModal.value = false;
  resetTrainingForm();
}

function resetTrainingForm() {
  trainingForm.value = {
    avatarName: "",
    negativePrompt: "",
    creditPerGeneration: 1,
    national: "",
    gender: "",
    description: "",
    previewImage: null,
    previewImageUrl: "",
    isRealPerson: false,
    instagramId: "",
    frontPhotos: Array(4).fill(null).map(() => ({ file: null, url: "" })),
    sidePhotos: Array(4).fill(null).map(() => ({ file: null, url: "" })),
    fullBodyPhotos: Array(1).fill(null).map(() => ({ file: null, url: "" })),
    otherPhotos: Array(1).fill(null).map(() => ({ file: null, url: "" })),
  };
}

function openAvatarDetailModal(avatar: AvatarItem) {
  selectedAvatar.value = avatar;
  editForm.value = {
    avatarName: avatar.title,
    creditPerGeneration: avatar.credit_per_generation || 0,
    description: avatar.description || "",
    previewImage: null,
    previewImageUrl: avatar.preview_image_url || "",
  };
}

function closeAvatarDetailModal() {
  selectedAvatar.value = null;
}

// Image upload handling
function handlePreviewImageChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    trainingForm.value.previewImage = file;
    trainingForm.value.previewImageUrl = URL.createObjectURL(file);
  }
}

function removePreviewImage() {
  trainingForm.value.previewImage = null;
  trainingForm.value.previewImageUrl = "";
}

function handleEditPreviewImageChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    editForm.value.previewImage = file;
    editForm.value.previewImageUrl = URL.createObjectURL(file);
  }
}

function removeEditPreviewImage() {
  editForm.value.previewImage = null;
  if (selectedAvatar.value) {
    editForm.value.previewImageUrl = selectedAvatar.value.preview_image_url || "";
  }
}

// Photo slot management
function handlePhotoUpload(category: string, index: number, event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const url = URL.createObjectURL(file);
    
    if (category === "front") {
      trainingForm.value.frontPhotos[index] = { file, url };
    } else if (category === "side") {
      trainingForm.value.sidePhotos[index] = { file, url };
    } else if (category === "fullbody") {
      trainingForm.value.fullBodyPhotos[index] = { file, url };
    } else if (category === "other") {
      trainingForm.value.otherPhotos[index] = { file, url };
    }
  }
}

// Submit training request
async function submitTrainingRequest() {
  if (!isTrainingFormValid.value) return;

  submitting.value = true;
  try {
    await trainingRequestsApi.createRequest({
      avatar_name: trainingForm.value.avatarName,
      negative_prompt: trainingForm.value.negativePrompt,
      credit_per_generation: trainingForm.value.creditPerGeneration,
      national: trainingForm.value.national,
      gender: trainingForm.value.gender,
      description: trainingForm.value.description,
      is_real_person: trainingForm.value.isRealPerson,
      instagram_id: trainingForm.value.isRealPerson ? trainingForm.value.instagramId : undefined,
      preview_image: trainingForm.value.previewImage!,
      front_photos: trainingForm.value.frontPhotos.filter(p => p.file).map(p => p.file!),
      side_photos: trainingForm.value.sidePhotos.filter(p => p.file).map(p => p.file!),
      fullbody_photos: trainingForm.value.fullBodyPhotos.filter(p => p.file).map(p => p.file!),
      other_photos: trainingForm.value.otherPhotos.filter(p => p.file).map(p => p.file!),
    });

    closeTrainingRequestModal();
    await loadTrainingRequests();
  } catch (error) {
    console.error("Failed to submit training request:", error);
    alert("Failed to submit request. Please try again.");
  } finally {
    submitting.value = false;
  }
}

// Save avatar changes
async function saveAvatarChanges() {
  if (!selectedAvatar.value) return;

  saving.value = true;
  try {
    await avatarsApi.updateAvatar(selectedAvatar.value.id, {
      title: editForm.value.avatarName,
      credit_per_generation: editForm.value.creditPerGeneration,
      description: editForm.value.description,
      preview_image: editForm.value.previewImage || undefined,
    });

    closeAvatarDetailModal();
    await loadAvatars();
  } catch (error) {
    console.error("Failed to save avatar changes:", error);
    alert("Failed to save. Please try again.");
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.avatars-section {
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

.main-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .main-layout {
    flex-direction: row;
  }
}

/* Training Request Section (1/3) */
.training-request-section {
  flex: 1;
}

@media (min-width: 1024px) {
  .training-request-section {
    flex: 0 0 33.333%;
  }
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

.btn-new-request {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new-request:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

/* Requests Grid */
.requests-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.grid-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  background: #f9fafb;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-top: 1px solid #e5e7eb;
}

.grid-cell {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
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

/* Avatars Section (2/3) */
.avatars-section-content {
  flex: 2;
}

@media (min-width: 1024px) {
  .avatars-section-content {
    flex: 0 0 66.666%;
  }
}

.avatars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .avatars-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

.avatar-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.avatar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.avatar-image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  background: #f9fafb;
  overflow: hidden;
}

.avatar-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-image-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 3rem;
  height: 3rem;
  color: #9ca3af;
}

.avatar-name {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  text-align: center;
}

/* Loading & Empty States */
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

/* Modal Styles */
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
  max-width: 800px;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.training-modal {
  max-width: 900px;
}

.avatar-detail-modal {
  max-width: 700px;
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

/* Form Styles */
.form-section {
  margin-bottom: 2rem;
}

.form-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
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

.required {
  color: #ef4444;
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

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.radio-group {
  display: flex;
  gap: 1.5rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.radio-input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.checkbox-input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.info-box {
  padding: 1rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.info-box p {
  font-size: 0.875rem;
  color: #1e40af;
  margin: 0.25rem 0;
}

.info-box a {
  color: #1e40af;
  text-decoration: underline;
}

/* File Upload */
.file-upload-wrapper {
  margin-top: 0.5rem;
}

.file-input {
  display: none;
}

.file-upload-btn {
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.file-upload-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
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

.remove-image-btn {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  line-height: 1;
}

/* Photo Upload Slots */
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
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.photo-slot:hover {
  border-color: #4f46e5;
  background: #f3f4f6;
}

.slot-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slot-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 2rem;
  height: 2rem;
  color: #9ca3af;
}

.hidden-file-input {
  display: none;
}

/* Detail Modal */
.detail-section {
  margin-bottom: 2rem;
}

.detail-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.preview-image-large {
  width: 100%;
  max-width: 400px;
  height: 400px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  margin-bottom: 1rem;
}

.preview-image-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.875rem;
  color: #111827;
}

.edit-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

/* Buttons */
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

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* Responsive */
@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .training-request-section,
  .avatars-section-content {
    flex: 1;
  }

  .avatars-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal-card {
    max-width: 100%;
    max-height: 95vh;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
