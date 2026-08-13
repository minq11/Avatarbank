<template>
  <section class="avatars-section">
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">내 아바타</h2>
      </div>

      <div class="main-layout">
        <!-- Training Request Section (1/3) -->
        <div class="training-request-section">
          <div class="section-header">
            <h3 class="section-title">학습 요청</h3>
            <button class="btn-new-request" type="button" @click="goToCreatePage">
              학습 요청하기
            </button>
          </div>

          <!-- Loading -->
          <div v-if="loadingRequests" class="loading-state">
            <div class="loading-spinner"></div>
            <p>요청 불러오는 중…</p>
          </div>

          <!-- Empty -->
          <div v-else-if="trainingRequests.length === 0" class="empty-state">
            <p>아직 학습 요청이 없어요</p>
          </div>

          <!-- Requests Grid -->
          <div v-else class="requests-grid">
            <div class="grid-header">
              <div class="grid-cell">요청 번호</div>
              <div class="grid-cell">요청일</div>
              <div class="grid-cell">상태</div>
            </div>
            <div
              v-for="request in trainingRequests"
              :key="request.id"
              class="grid-row"
              :class="{ 'grid-row-selected': selectedRequest?.id === request.id }"
              @click="openRequestDetailModal(request)"
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
            <h3 class="section-title">내 아바타</h3>
            <button
              v-if="authStore.isAdmin"
              class="btn-new-request"
              type="button"
              @click="openUploadLoraModal"
            >
              Upload LoRA
            </button>
          </div>

          <!-- Loading -->
          <div v-if="loadingAvatars" class="loading-state">
            <div class="loading-spinner"></div>
            <p>아바타 불러오는 중…</p>
          </div>

          <!-- Empty -->
          <div v-else-if="avatars.length === 0" class="empty-state">
            <p>아직 아바타가 없어요</p>
            <!-- 일반 사용자는 학습 요청으로만 아바타를 만든다 -->
            <button
              v-if="authStore.isAdmin"
              class="btn-new-request"
              type="button"
              @click="openUploadLoraModal"
            >
              Upload LoRA
            </button>
            <button v-else class="btn-new-request" type="button" @click="goToCreatePage">
              학습 요청하기
            </button>
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
                  v-if="getPreviewUrls(avatar).primary"
                  :src="getPreviewUrls(avatar).primary"
                  :alt="avatar.title"
                  class="avatar-image"
                  @error="(e: Event) => { const t = (e.target as HTMLImageElement); if (getPreviewUrls(avatar).fallback) t.src = getPreviewUrls(avatar).fallback; }"
                />
                <div v-else class="avatar-image-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
              </div>
              <div class="avatar-name">{{ avatar.title }}</div>
              <span :class="['avatar-status-badge', avatar.status === 'hidden' ? 'status-hidden' : 'status-active']">
                {{ avatar.status === "hidden" ? "Deactive" : "Active" }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Request Detail Modal -->
    <div v-if="selectedRequest" class="modal-overlay" @click.self="closeRequestDetailModal">
      <div class="modal-card training-detail-modal">
        <div class="modal-header">
          <h3>학습 요청 상세</h3>
          <button class="modal-close" type="button" @click="closeRequestDetailModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h4 class="form-section-title">기본 정보</h4>
            
            <div class="form-group">
              <label class="form-label">아바타 이름</label>
              <input
                :value="selectedRequest.avatar_name"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">실존 인물 기반 아바타인가요?</label>
              <input
                :value="selectedRequest.is_real_person ? '예' : '아니오'"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div v-if="selectedRequest.is_real_person" class="form-group">
              <label class="form-label">인스타그램 ID</label>
              <input
                :value="selectedRequest.instagram_id || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">네거티브 프롬프트</label>
              <input
                :value="selectedRequest.negative_prompt || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">생성당 크레딧</label>
              <input
                :value="selectedRequest.credit_per_generation"
                type="number"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">국가</label>
              <input
                :value="selectedRequest.national || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">성별</label>
              <input
                :value="selectedRequest.gender || ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">나이</label>
              <input
                :value="selectedRequest.age != null ? selectedRequest.age : ''"
                type="text"
                class="form-input"
                readonly
              />
            </div>

            <div class="form-group">
              <label class="form-label">설명</label>
              <textarea
                :value="selectedRequest.description || ''"
                class="form-textarea"
                rows="4"
                readonly
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">대표 이미지</label>
              <div v-if="selectedRequest.preview_image_url" class="preview-image">
                <img :src="getImageUrl(selectedRequest.preview_image_url)" alt="Preview" />
              </div>
              <div v-else class="preview-placeholder">이미지 없음</div>
            </div>
          </div>

          <!-- Training Photos -->
          <div class="form-section">
            <h4 class="form-section-title">학습 사진</h4>

            <!-- Front -->
            <div v-if="selectedRequest.front_photos_urls && selectedRequest.front_photos_urls.length > 0" class="photo-category">
              <label class="category-label">정면</label>
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
            <div v-if="selectedRequest.side_photos_urls && selectedRequest.side_photos_urls.length > 0" class="photo-category">
              <label class="category-label">측면</label>
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
            <div v-if="selectedRequest.fullbody_photos_urls && selectedRequest.fullbody_photos_urls.length > 0" class="photo-category">
              <label class="category-label">전신</label>
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
            <div v-if="selectedRequest.other_photos_urls && selectedRequest.other_photos_urls.length > 0" class="photo-category">
              <label class="category-label">기타</label>
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
            class="btn-danger"
            type="button"
            :disabled="deletingRequest"
            @click="deleteTrainingRequest"
          >
            {{ deletingRequest ? "Deleting..." : "Delete" }}
          </button>
          <button
            v-if="selectedRequest.status === 'requested'"
            class="btn-secondary"
            type="button"
            :disabled="cancelling"
            @click="cancelRequest"
          >
            {{ cancelling ? "취소 중…" : "요청 취소" }}
          </button>
          <button
            class="btn-secondary"
            type="button"
            @click="closeRequestDetailModal"
          >
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- Upload LoRA Modal (Training Request Details 스타일, 학습용 사진 제외) - 배경 클릭으로 닫기 비활성화 -->
    <div v-if="showUploadLoraModal" class="modal-overlay">
      <div class="modal-card training-detail-modal">
        <div class="modal-header">
          <h3>LoRA 아바타 업로드</h3>
          <button class="modal-close" type="button" @click="closeUploadLoraModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-section">
            <h4 class="form-section-title">기본 정보</h4>

            <div class="form-group">
              <label class="form-label">아바타 이름 <span class="required">*</span></label>
              <input
                v-model="uploadLoraForm.avatarName"
                type="text"
                class="form-input"
                placeholder="아바타 이름을 입력하세요"
              />
            </div>

            <div class="form-group">
              <label class="form-label">실존 인물 기반 아바타인가요? <span class="required">*</span></label>
              <div class="radio-group">
                <label class="radio-label">
                  <input
                    v-model="uploadLoraForm.isRealPerson"
                    type="radio"
                    :value="true"
                    class="radio-input"
                  />
                  <span>예</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="uploadLoraForm.isRealPerson"
                    type="radio"
                    :value="false"
                    class="radio-input"
                  />
                  <span>아니오</span>
                </label>
              </div>
            </div>

            <div v-if="uploadLoraForm.isRealPerson === true" class="form-group">
              <label class="form-label">인스타그램 ID <span class="required">*</span></label>
              <input
                v-model="uploadLoraForm.instagramId"
                type="text"
                class="form-input"
                placeholder="인스타그램 ID를 입력하세요"
              />
            </div>

            <div class="form-group">
              <label class="form-label">네거티브 프롬프트 <span class="required">*</span></label>
              <input
                v-model="uploadLoraForm.negativePrompt"
                type="text"
                class="form-input"
                placeholder="네거티브 프롬프트를 입력하세요"
              />
            </div>

            <div class="form-group">
              <label class="form-label">생성당 크레딧 <span class="required">*</span></label>
              <input
                v-model.number="uploadLoraForm.creditPerGeneration"
                type="number"
                min="0"
                class="form-input"
                placeholder="생성당 크레딧 (0 가능)"
              />
            </div>

            <div class="form-group">
              <label class="form-label">국가 <span class="required">*</span></label>
              <select v-model="uploadLoraForm.national" class="form-input">
                <option value="">국가 선택</option>
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
              <label class="form-label">성별 <span class="required">*</span></label>
              <div class="radio-group">
                <label class="radio-label">
                  <input v-model="uploadLoraForm.gender" type="radio" value="M" class="radio-input" />
                  <span>남성</span>
                </label>
                <label class="radio-label">
                  <input v-model="uploadLoraForm.gender" type="radio" value="W" class="radio-input" />
                  <span>여성</span>
                </label>
                <label class="radio-label">
                  <input v-model="uploadLoraForm.gender" type="radio" value="Etc" class="radio-input" />
                  <span>기타</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">나이 <span class="field-optional">(선택)</span></label>
              <input
                v-model.number="uploadLoraForm.age"
                type="number"
                min="1"
                max="120"
                class="form-input"
                placeholder="나이"
              />
            </div>

            <div class="form-group">
              <label class="form-label">설명 <span class="required">*</span></label>
              <textarea
                v-model="uploadLoraForm.description"
                class="form-textarea"
                rows="4"
                placeholder="설명을 입력하세요"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">대표 이미지 (선택)</label>
              <div class="file-upload-wrapper">
                <input
                  ref="uploadLoraPreviewInput"
                  type="file"
                  accept="image/*"
                  class="file-input"
                  @change="handleUploadLoraPreviewChange"
                />
                <div v-if="uploadLoraForm.previewImage" class="preview-image">
                  <img :src="uploadLoraForm.previewImageUrl" alt="Preview" />
                  <button type="button" class="remove-image-btn" @click="removeUploadLoraPreview">×</button>
                </div>
                <button
                  v-else
                  type="button"
                  class="file-upload-btn"
                  @click="() => uploadLoraPreviewInput?.click()"
                >
                  이미지 선택
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">LoRA 파일 (.safetensors) <span class="required">*</span></label>
              <div class="file-upload-wrapper">
                <input
                  ref="uploadLoraFileInput"
                  type="file"
                  accept=".safetensors"
                  class="file-input"
                  @change="handleUploadLoraFileChange"
                />
                <button
                  type="button"
                  class="file-upload-btn"
                  @click="() => uploadLoraFileInput?.click()"
                >
                  {{ uploadLoraForm.loraFile ? uploadLoraForm.loraFile.name : ".safetensors 파일 선택" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" type="button" @click="closeUploadLoraModal">
            닫기
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="!isUploadLoraFormValid || uploadingLora"
            @click="submitUploadLora"
          >
            {{ uploadingLora ? "업로드 중…" : "업로드" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Avatar Detail and Edit Modal -->
    <div v-if="selectedAvatar" class="modal-overlay" @click.self="closeAvatarDetailModal">
      <div class="modal-card avatar-detail-modal">
        <div class="modal-header">
          <h3>아바타 상세</h3>
          <button class="modal-close" type="button" @click="closeAvatarDetailModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Market visibility: 모달 맨 위 -->
          <div class="form-group form-group-block visibility-block visibility-block-top">
            <label class="form-label">마켓 노출</label>
            <div class="visibility-options">
              <label :class="['visibility-option', editForm.status === 'active' ? 'visibility-option-selected' : '']">
                <input v-model="editForm.status" type="radio" value="active" class="visibility-radio" />
                <span class="visibility-label">활성</span>
                <span class="visibility-desc">마켓에 표시</span>
              </label>
              <label :class="['visibility-option', editForm.status === 'hidden' ? 'visibility-option-selected' : '']">
                <input v-model="editForm.status" type="radio" value="hidden" class="visibility-radio" />
                <span class="visibility-label">비활성</span>
                <span class="visibility-desc">마켓에서 숨김</span>
              </label>
            </div>
          </div>

          <!-- Preview Image: 제목 라인 오른쪽에 Change -->
          <div class="detail-section preview-image-section">
            <div class="preview-image-section-header">
              <h4 class="detail-section-title">대표 이미지</h4>
              <input
                ref="editPreviewImageInput"
                type="file"
                accept="image/*"
                class="file-input file-input-hidden"
                @change="handleEditPreviewImageChange"
              />
              <button
                v-if="editForm.previewImage"
                type="button"
                class="file-upload-btn file-upload-btn-sm"
                @click="removeEditPreviewImage"
              >
                Remove
              </button>
              <button
                v-else
                type="button"
                class="file-upload-btn file-upload-btn-sm"
                @click="() => editPreviewImageInput?.click()"
              >
                Change
              </button>
            </div>
            <div class="preview-image-large">
              <img
                v-if="previewImageDisplayUrl"
                :src="previewImageDisplayUrl"
                alt="Preview"
                @error="(e: Event) => { const t = (e.target as HTMLImageElement); if (previewImageFallbackUrl) t.src = previewImageFallbackUrl; }"
              />
              <div v-else class="preview-placeholder">이미지 없음</div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="detail-section-title">정보</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label class="detail-label">아바타 이름</label>
                <p class="detail-value">{{ selectedAvatar.title }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">네거티브 프롬프트</label>
                <p class="detail-value">{{ selectedAvatar.negative_prompt || "없음" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">생성당 크레딧</label>
                <p class="detail-value">{{ selectedAvatar.credit_per_generation || "없음" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">국가</label>
                <p class="detail-value">{{ selectedAvatar.nationality || "없음" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">성별</label>
                <p class="detail-value">{{ selectedAvatar.gender || "없음" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">나이</label>
                <p class="detail-value">{{ selectedAvatar.age != null ? selectedAvatar.age : "없음" }}</p>
              </div>
              <div class="detail-item">
                <label class="detail-label">유형</label>
                <p class="detail-value">{{ selectedAvatar.is_real_person ? "실존 인물" : "가상 캐릭터" }}</p>
              </div>
              <div v-if="selectedAvatar.is_real_person && selectedAvatar.instagram_id" class="detail-item">
                <label class="detail-label">인스타그램</label>
                <p class="detail-value">
                  <a
                    :href="instagramUrl(selectedAvatar.instagram_id!)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="detail-instagram-link"
                  >
                    {{ formatInstagramId(selectedAvatar.instagram_id) }}
                  </a>
                </p>
              </div>
              <div class="detail-item">
                <label class="detail-label">설명</label>
                <p class="detail-value">{{ selectedAvatar.description || "없음" }}</p>
              </div>
            </div>
          </div>

          <!-- Editable Items -->
          <div class="edit-section">
            <h4 class="detail-section-title">수정</h4>

            <div class="form-group">
              <label class="form-label">생성당 크레딧</label>
              <input
                v-model.number="editForm.creditPerGeneration"
                type="number"
                min="1"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">아바타 이름</label>
              <input
                v-model="editForm.avatarName"
                type="text"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">설명</label>
              <textarea
                v-model="editForm.description"
                class="form-textarea"
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div v-if="saving && uploadProgress > 0" class="upload-progress-wrap">
            <div class="upload-progress-bar">
              <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span class="upload-progress-text">{{ uploadProgress }}%</span>
          </div>
          <button
            class="btn-danger"
            type="button"
            :disabled="deletingAvatar"
            @click="deleteAvatar"
          >
            {{ deletingAvatar ? "삭제 중…" : "삭제" }}
          </button>
          <button
            class="btn-secondary"
            type="button"
            @click="closeAvatarDetailModal"
          >
            닫기
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="saving"
            @click="saveAvatarChanges"
          >
            {{ saving ? "저장 중…" : "저장" }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { avatarsApi, trainingRequestsApi, type AvatarItem, type TrainingRequestItem, type TrainingRequestDetailItem } from "@/services/api";
import { getAvatarPreviewUrls } from "@/utils/avatarPreview";
import { useAuthStore } from "@/stores/auth";

// LoRA 직접 업로드는 학습 심사를 건너뛰므로 관리자에게만 노출한다.
const authStore = useAuthStore();
const router = useRouter();

// 생성 요청은 팝업이 아니라 전용 페이지에서 한다
function goToCreatePage() {
  router.push("/my/avatars/new");
}

function getPreviewUrls(avatar: { id: number; preview_image_url?: string | null }) {
  return getAvatarPreviewUrls(avatar.id, avatar.preview_image_url ?? null);
}

// Helper function to convert static file paths to full URLs
function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  // If it's already a full URL (http/https), return as is
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  // /static/ 경로: 개발 시 프록시(/api), 빌드 시 백엔드 origin 사용해 이미지 로드
  if (url.startsWith("/static/")) {
    const apiBase = import.meta.env.VITE_API_BASE_URL;
    if (apiBase) return apiBase + url;
    return `/api${url}`;
  }
  return url;
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

// 아바타 상세 모달: 큰 미리보기에 표시할 URL (새로 고른 파일 → blob, 기존 → local/API/S3)
const previewImageDisplayUrl = computed(() => {
  if (editForm.value.previewImage) return editForm.value.previewImageUrl || "";
  if (!selectedAvatar.value) return "";
  return getPreviewUrls(selectedAvatar.value).primary;
});
const previewImageFallbackUrl = computed(() => {
  if (!selectedAvatar.value) return "";
  return getPreviewUrls(selectedAvatar.value).fallback;
});

// Refs for file inputs
const editPreviewImageInput = ref<HTMLInputElement | null>(null);
const uploadLoraPreviewInput = ref<HTMLInputElement | null>(null);
const uploadLoraFileInput = ref<HTMLInputElement | null>(null);

// State
const loadingRequests = ref(false);
const loadingAvatars = ref(false);
const trainingRequests = ref<TrainingRequestItem[]>([]);
const avatars = ref<AvatarItem[]>([]);
const showUploadLoraModal = ref(false);
const selectedAvatar = ref<AvatarItem | null>(null);
const selectedRequest = ref<TrainingRequestDetailItem | null>(null);
const uploadingLora = ref(false);
const saving = ref(false);
const uploadProgress = ref(0);
const cancelling = ref(false);
const deletingRequest = ref(false);
const deletingAvatar = ref(false);
const loadingRequestDetail = ref(false);

// Edit form
const editForm = ref({
  avatarName: "",
  creditPerGeneration: 0,
  description: "",
  status: "active" as "active" | "hidden",
  previewImage: null as File | null,
  previewImageUrl: "",
});

// Upload LoRA form (Training Request Details 필드와 동일, 학습용 사진 제외)
const uploadLoraForm = ref({
  avatarName: "",
  isRealPerson: false as boolean,
  instagramId: "",
  negativePrompt: "",
  creditPerGeneration: 1,
  national: "",
  gender: "",
  age: null as number | null,
  description: "",
  previewImage: null as File | null,
  previewImageUrl: "",
  loraFile: null as File | null,
});

// Training Request와 동일 필수값 (사진 관련만 제외). Credit per generation은 0 허용.
const isUploadLoraFormValid = computed(() => {
  const form = uploadLoraForm.value;
  return (
    form.avatarName.trim() !== "" &&
    form.negativePrompt.trim() !== "" &&
    form.creditPerGeneration >= 0 &&
    form.national !== "" &&
    form.gender !== "" &&
    form.description.trim() !== "" &&
    (form.isRealPerson === false || form.instagramId.trim() !== "") &&
    form.loraFile !== null &&
    form.loraFile.name.toLowerCase().endsWith(".safetensors")
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
    requested: "요청됨",
    approved_training: "승인·학습중",
    rejected: "반려됨",
    cancelled: "취소됨",
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

// Modal management
function openUploadLoraModal() {
  uploadLoraForm.value = {
    avatarName: "",
    isRealPerson: false,
    instagramId: "",
    negativePrompt: "",
    creditPerGeneration: 1,
    national: "",
    gender: "",
    age: null,
    description: "",
    previewImage: null,
    previewImageUrl: "",
    loraFile: null,
  };
  showUploadLoraModal.value = true;
}

function closeUploadLoraModal() {
  showUploadLoraModal.value = false;
}

function handleUploadLoraPreviewChange(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    uploadLoraForm.value.previewImage = file;
    uploadLoraForm.value.previewImageUrl = URL.createObjectURL(file);
  }
}

function removeUploadLoraPreview() {
  uploadLoraForm.value.previewImage = null;
  uploadLoraForm.value.previewImageUrl = "";
  if (uploadLoraPreviewInput.value) uploadLoraPreviewInput.value.value = "";
}

function handleUploadLoraFileChange(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) uploadLoraForm.value.loraFile = file;
}

async function submitUploadLora() {
  const form = uploadLoraForm.value;
  if (!form.loraFile || !form.avatarName.trim()) return;
  uploadingLora.value = true;
  try {
    const fd = new FormData();
    fd.append("title", form.avatarName.trim());
    fd.append("is_real_person", String(form.isRealPerson));
    if (form.instagramId.trim()) fd.append("instagram_id", form.instagramId.trim());
    if (form.negativePrompt.trim()) fd.append("negative_prompt", form.negativePrompt.trim());
    fd.append("credit_per_generation", String(form.creditPerGeneration));
    if (form.national) fd.append("national", form.national);
    if (form.gender) fd.append("gender", form.gender);
    if (form.age != null) fd.append("age", String(form.age));
    if (form.description.trim()) fd.append("description", form.description.trim());
    if (form.previewImage) fd.append("preview_image", form.previewImage);
    fd.append("lora_file", form.loraFile);
    await avatarsApi.uploadLoRA(fd);
    closeUploadLoraModal();
    await loadAvatars();
  } catch (err) {
    console.error("Upload LoRA failed:", err);
    alert("LoRA 업로드에 실패했습니다. 파일 형식(.safetensors)과 필수 항목을 확인해 주세요.");
  } finally {
    uploadingLora.value = false;
  }
}

function openAvatarDetailModal(avatar: AvatarItem) {
  selectedAvatar.value = avatar;
  editForm.value = {
    avatarName: avatar.title,
    creditPerGeneration: avatar.credit_per_generation || 0,
    description: avatar.description || "",
    status: avatar.status === "hidden" ? "hidden" : "active",
    previewImage: null,
    previewImageUrl: avatar.preview_image_url || "",
  };
}

function closeAvatarDetailModal() {
  selectedAvatar.value = null;
}

async function openRequestDetailModal(request: TrainingRequestItem) {
  loadingRequestDetail.value = true;
  try {
    selectedRequest.value = await trainingRequestsApi.getRequestDetail(request.id);
  } catch (error) {
    console.error("Failed to load request detail:", error);
    alert("요청 상세를 불러오지 못했어요.");
  } finally {
    loadingRequestDetail.value = false;
  }
}

function closeRequestDetailModal() {
  selectedRequest.value = null;
}

async function cancelRequest() {
  if (!selectedRequest.value) return;
  
  if (!confirm("이 요청을 취소할까요?")) {
    return;
  }

  cancelling.value = true;
  try {
    const updatedRequest = await trainingRequestsApi.cancelRequest(selectedRequest.value.id);
    // Update the selected request status
    if (selectedRequest.value) {
      selectedRequest.value.status = updatedRequest.status;
    }
    // Update the list
    await loadTrainingRequests();
    alert("요청이 취소되었어요.");
  } catch (error: any) {
    console.error("Failed to cancel request:", error);
    const errorMessage = error?.response?.data?.detail || error?.message || "Failed to cancel request.";
    alert(errorMessage);
  } finally {
    cancelling.value = false;
  }
}

async function deleteTrainingRequest() {
  if (!selectedRequest.value) return;
  if (!confirm("이 학습 요청을 삭제할까요? 업로드한 이미지가 영구 삭제되며 되돌릴 수 없어요.")) {
    return;
  }
  deletingRequest.value = true;
  try {
    await trainingRequestsApi.deleteRequest(selectedRequest.value.id);
    closeRequestDetailModal();
    await loadTrainingRequests();
    alert("학습 요청이 삭제되었어요.");
  } catch (error: any) {
    console.error("Failed to delete training request:", error);
    const msg = error?.response?.data?.detail || error?.message || "Failed to delete.";
    alert(msg);
  } finally {
    deletingRequest.value = false;
  }
}

// Image upload handling
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

// Save avatar changes
async function saveAvatarChanges() {
  if (!selectedAvatar.value) return;

  saving.value = true;
  uploadProgress.value = 0;
  try {
    await avatarsApi.updateAvatar(
      selectedAvatar.value.id,
      {
        title: editForm.value.avatarName,
        credit_per_generation: editForm.value.creditPerGeneration,
        description: editForm.value.description,
        status: editForm.value.status,
        preview_image: editForm.value.previewImage || undefined,
      },
      editForm.value.previewImage ? (percent) => { uploadProgress.value = percent; } : undefined
    );

    closeAvatarDetailModal();
    await loadAvatars();
  } catch (error) {
    console.error("Failed to save avatar changes:", error);
    alert("저장에 실패했어요. 다시 시도해 주세요.");
  } finally {
    saving.value = false;
    uploadProgress.value = 0;
  }
}

async function deleteAvatar() {
  if (!selectedAvatar.value) return;
  if (!confirm("이 아바타를 삭제할까요? LoRA 파일이 영구 삭제되며 되돌릴 수 없어요.")) {
    return;
  }
  deletingAvatar.value = true;
  try {
    await avatarsApi.deleteAvatar(selectedAvatar.value.id);
    closeAvatarDetailModal();
    await loadAvatars();
    alert("아바타가 삭제되었어요.");
  } catch (error: any) {
    console.error("Failed to delete avatar:", error);
    const msg = error?.response?.data?.detail || error?.message || "Failed to delete.";
    alert(msg);
  } finally {
    deletingAvatar.value = false;
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
  color: #0d0d0f;
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
  color: #0d0d0f;
}

.btn-new-request {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new-request:hover {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}

/* Requests Grid */
.requests-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border: 1px solid #e6e6ea;
  border-radius: 0.5rem;
  overflow: hidden;
}

.grid-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  background: #fafafa;
  font-weight: 600;
  font-size: 0.875rem;
  color: #3a3a42;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-top: 1px solid #e6e6ea;
  cursor: pointer;
  transition: background-color 0.2s;
}

.grid-row:hover {
  background-color: #fafafa;
}

.grid-row-selected {
  background-color: #fdede4;
}

.grid-cell {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #3a3a42;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-requested {
  background: #fce3d6;
  color: #a8380d;
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
  background: #f2f2f4;
  color: #6e6e77;
}

/* Avatars Section (2/3) */
.avatars-section-content {
  flex: 2;
  min-width: 0;
}

.avatars-section-content .section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.avatars-section-content .section-header .btn-new-request {
  flex-shrink: 0;
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
  border: 1px solid #e6e6ea;
}

.avatar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.avatar-image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  background: #fafafa;
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
  color: #9a9aa3;
}

.avatar-name {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #0d0d0f;
  text-align: center;
}

.avatar-status-badge {
  display: block;
  text-align: center;
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  margin: 0 1rem 0.75rem;
  border-radius: 0.25rem;
  font-weight: 500;
}
.avatar-status-badge.status-active {
  background: #d1fae5;
  color: #065f46;
}
.avatar-status-badge.status-hidden {
  background: #f2f2f4;
  color: #52525b;
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
  color: #6e6e77;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
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
  border: 1px solid #e6e6ea;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.training-modal {
  max-width: 900px;
}

.training-detail-modal {
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
  border-bottom: 1px solid #f2f2f4;
}

.modal-header h3 {
  font-size: 1.25rem;
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
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #0d0d0f;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f2f2f4;
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
  color: #0d0d0f;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #3a3a42;
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
  color: #0d0d0f;
  background: #ffffff;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #e24e12;
  box-shadow: 0 0 0 3px rgba(226, 78, 18, 0.1);
}

.form-input[readonly],
.form-textarea[readonly] {
  background-color: #fafafa;
  cursor: default;
}

.form-input[readonly]:focus,
.form-textarea[readonly]:focus {
  border-color: #d2d2d9;
  box-shadow: none;
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
  color: #3a3a42;
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
  color: #3a3a42;
}

.checkbox-input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.info-box {
  padding: 1rem;
  background: #fdede4;
  border: 1px solid #fbd9c6;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.info-box p {
  font-size: 0.875rem;
  color: #a8380d;
  margin: 0.25rem 0;
}

.info-box a {
  color: #a8380d;
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
  color: #3a3a42;
  background: #fafafa;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.file-upload-btn:hover {
  background: #f2f2f4;
  border-color: #9a9aa3;
}

.preview-image {
  position: relative;
  display: inline-block;
  width: 150px;
  height: 150px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e6e6ea;
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
  color: #3a3a42;
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
  background: #fafafa;
  border: 2px dashed #d2d2d9;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.photo-slot:hover:not(.readonly) {
  border-color: #e24e12;
  background: #f2f2f4;
}

.photo-slot.readonly {
  cursor: default;
  border-style: solid;
}

.remove-photo-btn {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  line-height: 1;
  z-index: 10;
  transition: background 0.2s;
}

.remove-photo-btn:hover {
  background: rgba(220, 38, 38, 1);
}

.add-photo-btn {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #e24e12;
  background: #fafafa;
  border: 2px dashed #d2d2d9;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-photo-btn:hover {
  border-color: #e24e12;
  background: #f2f2f4;
  color: #b93b0e;
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
  color: #9a9aa3;
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
  color: #0d0d0f;
  margin-bottom: 1rem;
}

.preview-image-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.preview-image-section-header .detail-section-title {
  margin-bottom: 0;
}
.file-upload-btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}
.preview-image-large {
  width: 100%;
  max-width: 400px;
  height: 400px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e6e6ea;
  background: #fafafa;
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
  color: #9a9aa3;
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
  font-weight: 650;
  color: #6e6e77;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.875rem;
  color: #0d0d0f;
}
.detail-instagram-link {
  color: #e85f26;
  text-decoration: none;
}
.detail-instagram-link:hover {
  text-decoration: underline;
}

.edit-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e6e6ea;
}

.form-group-block.visibility-block {
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #fafafa;
  border: 1px solid #e6e6ea;
  border-radius: 0.5rem;
}
.visibility-block-top {
  margin-bottom: 1.5rem;
}

.visibility-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.visibility-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid #e6e6ea;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.visibility-option.visibility-option-selected {
  border-color: #e24e12;
  background: #fdede4;
}
.visibility-option:hover {
  border-color: #f7b394;
}
.visibility-radio {
  margin: 0;
  width: 1rem;
  height: 1rem;
  accent-color: #e24e12;
}
.visibility-label {
  font-weight: 600;
  color: #0d0d0f;
}
.visibility-desc {
  font-size: 0.8rem;
  color: #6e6e77;
}

.preview-image-edit-group {
  margin-top: 0.5rem;
}
.preview-image-edit-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.preview-image-edit-header .form-label {
  margin-bottom: 0;
}
.file-input.file-input-hidden {
  display: none;
}
.file-upload-btn-inline {
  flex-shrink: 0;
}
.preview-image-edit-thumb {
  margin-top: 0.75rem;
  width: 120px;
  height: 120px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e6e6ea;
}
.preview-image-edit-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Buttons */
.btn-primary {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #3a3a42;
  background: #fafafa;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f2f2f4;
  border-color: #9a9aa3;
}

.btn-danger {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: #ef4444;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.3);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer .upload-progress-wrap {
  flex-basis: 100%;
  width: 100%;
  margin-bottom: 0.5rem;
}

.upload-progress-bar {
  height: 6px;
  background: #e6e6ea;
  border-radius: 9999px;
  overflow: hidden;
}

.upload-progress-fill {
  height: 100%;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border-radius: 9999px;
  transition: width 0.2s ease;
}

.upload-progress-text {
  display: block;
  font-size: 0.75rem;
  color: #6e6e77;
  margin-top: 0.25rem;
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
