<template>
  <section class="create-page">
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">아바타 생성 요청</h2>
        <p class="page-subtitle">
          사진 몇 장으로 나만의 AI 아바타를 만들어요. 심사 후 학습이 진행됩니다.
        </p>
      </div>

      <!-- 로그인 필요 -->
      <div v-if="authStore.isInitialized && !authStore.isLoggedIn" class="login-gate">
        <h3>회원가입하고 바로 시작하세요</h3>
        <p>아바타를 만들려면 계정이 필요해요. 가입하면 무료 크레딧을 드립니다.</p>
        <div class="login-gate-actions">
          <button class="btn-primary" type="button" @click="authStore.openAuthModal('register', '/my/avatars/new')">
            회원가입
          </button>
          <button class="btn-secondary" type="button" @click="authStore.openAuthModal('login', '/my/avatars/new')">
            로그인
          </button>
        </div>
      </div>

      <!-- 생성 폼 -->
      <div v-else-if="authStore.isLoggedIn" class="form-card">
        <div class="form-body">
          <!-- Basic Information Input -->
          <div class="form-section">
            <h4 class="form-section-title">기본 정보</h4>

            <div class="form-group">
              <label class="form-label">아바타 이름 <span class="required">*</span></label>
              <input
                v-model="trainingForm.avatarName"
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
                    v-model="trainingForm.isRealPerson"
                    type="radio"
                    :value="true"
                    class="radio-input"
                  />
                  <span>예</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="trainingForm.isRealPerson"
                    type="radio"
                    :value="false"
                    class="radio-input"
                  />
                  <span>아니오</span>
                </label>
              </div>
            </div>

            <template v-if="trainingForm.isRealPerson === true">
              <div class="form-group">
                <label class="form-label">인스타그램 ID <span class="required">*</span></label>
                <input
                  v-model="trainingForm.instagramId"
                  type="text"
                  class="form-input"
                  placeholder="인스타그램 ID를 입력하세요"
                />
              </div>
              <div class="info-box">
                <p>
                  본인 요청임을 DM으로 확인해 주세요 (<a
                    href="https://www.instagram.com/avatarclub_official/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >@avatarclub_official</a>).
                </p>
                <p>본인 요청이 아니면 학습을 진행하지 않아요.</p>
              </div>
            </template>

            <div class="form-group">
              <label class="form-label">네거티브 프롬프트 <span class="required">*</span></label>
              <input
                v-model="trainingForm.negativePrompt"
                type="text"
                class="form-input"
                placeholder="네거티브 프롬프트를 입력하세요"
              />
            </div>

            <div class="form-group">
              <label class="form-label">생성당 크레딧 <span class="required">*</span></label>
              <input
                v-model.number="trainingForm.creditPerGeneration"
                type="number"
                min="1"
                class="form-input"
                placeholder="생성당 크레딧"
              />
            </div>

            <div class="form-group">
              <label class="form-label">국가 <span class="required">*</span></label>
              <select v-model="trainingForm.national" class="form-input">
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
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="M"
                    class="radio-input"
                  />
                  <span>남성</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="W"
                    class="radio-input"
                  />
                  <span>여성</span>
                </label>
                <label class="radio-label">
                  <input
                    v-model="trainingForm.gender"
                    type="radio"
                    value="Etc"
                    class="radio-input"
                  />
                  <span>기타</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">나이 <span class="field-optional">(선택)</span></label>
              <input
                v-model.number="trainingForm.age"
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
                v-model="trainingForm.description"
                class="form-textarea"
                rows="4"
                placeholder="아바타 설명을 입력하세요"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">대표 이미지 <span class="required">*</span></label>
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
                  이미지 선택
                </button>
              </div>
            </div>
          </div>

          <!-- Training Photos Upload -->
          <div class="form-section">
            <h4 class="form-section-title">학습 사진 업로드</h4>

            <!-- Front -->
            <div class="photo-category">
              <label class="category-label">정면 <span class="required">최소 4장</span></label>
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
                  <button
                    v-if="slot.url"
                    type="button"
                    class="remove-photo-btn"
                    @click.stop="removePhoto('front', index)"
                  >
                    ×
                  </button>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('front', index, e)"
                  />
                </label>
                <input
                  ref="frontPhotosInput"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden-file-input"
                  @change="(e) => handleMultiplePhotoUpload('front', e)"
                />
                <button
                  type="button"
                  class="add-photo-btn"
                  @click="frontPhotosInput?.click()"
                >
                  + 사진 추가
                </button>
              </div>
            </div>

            <!-- Side -->
            <div class="photo-category">
              <label class="category-label">측면 <span class="required">최소 4장</span></label>
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
                  <button
                    v-if="slot.url"
                    type="button"
                    class="remove-photo-btn"
                    @click.stop="removePhoto('side', index)"
                  >
                    ×
                  </button>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('side', index, e)"
                  />
                </label>
                <input
                  ref="sidePhotosInput"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden-file-input"
                  @change="(e) => handleMultiplePhotoUpload('side', e)"
                />
                <button
                  type="button"
                  class="add-photo-btn"
                  @click="sidePhotosInput?.click()"
                >
                  + 사진 추가
                </button>
              </div>
            </div>

            <!-- Full Body -->
            <div class="photo-category">
              <label class="category-label">전신 <span class="required">최소 1장</span></label>
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
                  <button
                    v-if="slot.url"
                    type="button"
                    class="remove-photo-btn"
                    @click.stop="removePhoto('fullbody', index)"
                  >
                    ×
                  </button>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('fullbody', index, e)"
                  />
                </label>
                <input
                  ref="fullBodyPhotosInput"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden-file-input"
                  @change="(e) => handleMultiplePhotoUpload('fullbody', e)"
                />
                <button
                  type="button"
                  class="add-photo-btn"
                  @click="fullBodyPhotosInput?.click()"
                >
                  + 사진 추가
                </button>
              </div>
            </div>

            <!-- Other -->
            <div class="photo-category">
              <label class="category-label">기타 <span class="required">최소 1장</span></label>
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
                  <button
                    v-if="slot.url"
                    type="button"
                    class="remove-photo-btn"
                    @click.stop="removePhoto('other', index)"
                  >
                    ×
                  </button>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden-file-input"
                    @change="(e) => handlePhotoUpload('other', index, e)"
                  />
                </label>
                <input
                  ref="otherPhotosInput"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden-file-input"
                  @change="(e) => handleMultiplePhotoUpload('other', e)"
                />
                <button
                  type="button"
                  class="add-photo-btn"
                  @click="otherPhotosInput?.click()"
                >
                  + 사진 추가
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="form-footer">
          <button class="btn-secondary" type="button" @click="goBack">
            취소
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="!isTrainingFormValid || submitting"
            @click="submitTrainingRequest"
          >
            {{ submitting ? "제출 중…" : "요청 제출" }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { trainingRequestsApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import testfaceImage from "@/assets/testface.png";

const router = useRouter();
const authStore = useAuthStore();

// Refs for file inputs
const previewImageInput = ref<HTMLInputElement | null>(null);
const frontPhotosInput = ref<HTMLInputElement | null>(null);
const sidePhotosInput = ref<HTMLInputElement | null>(null);
const fullBodyPhotosInput = ref<HTMLInputElement | null>(null);
const otherPhotosInput = ref<HTMLInputElement | null>(null);

const submitting = ref(false);

// Training request form (MyAvatarsPage 팝업에서 페이지로 분리)
const trainingForm = ref({
  avatarName: "",
  negativePrompt: "",
  creditPerGeneration: 1,
  national: "",
  gender: "",
  age: null as number | null,
  description: "",
  previewImage: null as File | null,
  previewImageUrl: "",
  isRealPerson: null as boolean | null,
  instagramId: "",
  frontPhotos: [] as Array<{ file: File | null; url: string }>,
  sidePhotos: [] as Array<{ file: File | null; url: string }>,
  fullBodyPhotos: [] as Array<{ file: File | null; url: string }>,
  otherPhotos: [] as Array<{ file: File | null; url: string }>,
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
    form.isRealPerson !== null &&
    (form.isRealPerson === false || form.instagramId.trim() !== "") &&
    form.frontPhotos.filter(p => p.file !== null).length >= 4 &&
    form.sidePhotos.filter(p => p.file !== null).length >= 4 &&
    form.fullBodyPhotos.filter(p => p.file !== null).length >= 1 &&
    form.otherPhotos.filter(p => p.file !== null).length >= 1
  );
});

// Load default image as File
async function loadDefaultImage(): Promise<File> {
  const response = await fetch(testfaceImage);
  const blob = await response.blob();
  return new File([blob], "testface.png", { type: blob.type });
}

async function resetTrainingForm() {
  // Revoke all existing object URLs to prevent memory leaks
  trainingForm.value.frontPhotos.forEach(slot => {
    if (slot.url) URL.revokeObjectURL(slot.url);
  });
  trainingForm.value.sidePhotos.forEach(slot => {
    if (slot.url) URL.revokeObjectURL(slot.url);
  });
  trainingForm.value.fullBodyPhotos.forEach(slot => {
    if (slot.url) URL.revokeObjectURL(slot.url);
  });
  trainingForm.value.otherPhotos.forEach(slot => {
    if (slot.url) URL.revokeObjectURL(slot.url);
  });
  if (trainingForm.value.previewImageUrl) {
    URL.revokeObjectURL(trainingForm.value.previewImageUrl);
  }

  // Reset form fields
  trainingForm.value = {
    avatarName: "",
    negativePrompt: "",
    creditPerGeneration: 1,
    national: "",
    gender: "",
    age: null,
    description: "",
    previewImage: null,
    previewImageUrl: "",
    isRealPerson: null,
    instagramId: "",
    frontPhotos: [],
    sidePhotos: [],
    fullBodyPhotos: [],
    otherPhotos: [],
  };

  // Load default image for preview
  const defaultPreviewFile = await loadDefaultImage();
  trainingForm.value.previewImage = defaultPreviewFile;
  trainingForm.value.previewImageUrl = URL.createObjectURL(defaultPreviewFile);

  // Initialize with minimum required photos (pre-filled with default images)
  for (let i = 0; i < 4; i++) {
    const file = await loadDefaultImage();
    trainingForm.value.frontPhotos.push({ file, url: URL.createObjectURL(file) });
  }
  for (let i = 0; i < 4; i++) {
    const file = await loadDefaultImage();
    trainingForm.value.sidePhotos.push({ file, url: URL.createObjectURL(file) });
  }
  const fullBodyFile = await loadDefaultImage();
  trainingForm.value.fullBodyPhotos.push({ file: fullBodyFile, url: URL.createObjectURL(fullBodyFile) });
  const otherFile = await loadDefaultImage();
  trainingForm.value.otherPhotos.push({ file: otherFile, url: URL.createObjectURL(otherFile) });
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

// Photo slot management
function handleMultiplePhotoUpload(category: string, event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const files = Array.from(input.files);

    files.forEach((file) => {
      const url = URL.createObjectURL(file);

      if (category === "front") {
        trainingForm.value.frontPhotos.push({ file, url });
      } else if (category === "side") {
        trainingForm.value.sidePhotos.push({ file, url });
      } else if (category === "fullbody") {
        trainingForm.value.fullBodyPhotos.push({ file, url });
      } else if (category === "other") {
        trainingForm.value.otherPhotos.push({ file, url });
      }
    });

    // Reset input to allow selecting the same files again
    input.value = "";
  }
}

function removePhoto(category: string, index: number) {
  if (category === "front") {
    const slot = trainingForm.value.frontPhotos[index];
    if (slot.url) URL.revokeObjectURL(slot.url);
    trainingForm.value.frontPhotos.splice(index, 1);
  } else if (category === "side") {
    const slot = trainingForm.value.sidePhotos[index];
    if (slot.url) URL.revokeObjectURL(slot.url);
    trainingForm.value.sidePhotos.splice(index, 1);
  } else if (category === "fullbody") {
    const slot = trainingForm.value.fullBodyPhotos[index];
    if (slot.url) URL.revokeObjectURL(slot.url);
    trainingForm.value.fullBodyPhotos.splice(index, 1);
  } else if (category === "other") {
    const slot = trainingForm.value.otherPhotos[index];
    if (slot.url) URL.revokeObjectURL(slot.url);
    trainingForm.value.otherPhotos.splice(index, 1);
  }
}

function handlePhotoUpload(category: string, index: number, event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const url = URL.createObjectURL(file);

    // Revoke old URL if exists
    if (category === "front" && trainingForm.value.frontPhotos[index]?.url) {
      URL.revokeObjectURL(trainingForm.value.frontPhotos[index].url);
    } else if (category === "side" && trainingForm.value.sidePhotos[index]?.url) {
      URL.revokeObjectURL(trainingForm.value.sidePhotos[index].url);
    } else if (category === "fullbody" && trainingForm.value.fullBodyPhotos[index]?.url) {
      URL.revokeObjectURL(trainingForm.value.fullBodyPhotos[index].url);
    } else if (category === "other" && trainingForm.value.otherPhotos[index]?.url) {
      URL.revokeObjectURL(trainingForm.value.otherPhotos[index].url);
    }

    if (category === "front") {
      trainingForm.value.frontPhotos[index] = { file, url };
    } else if (category === "side") {
      trainingForm.value.sidePhotos[index] = { file, url };
    } else if (category === "fullbody") {
      trainingForm.value.fullBodyPhotos[index] = { file, url };
    } else if (category === "other") {
      trainingForm.value.otherPhotos[index] = { file, url };
    }

    // Reset input to allow selecting the same file again
    input.value = "";
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
      age: trainingForm.value.age,
      description: trainingForm.value.description,
      is_real_person: trainingForm.value.isRealPerson === true,
      instagram_id: trainingForm.value.isRealPerson === true ? trainingForm.value.instagramId : undefined,
      preview_image: trainingForm.value.previewImage!,
      front_photos: trainingForm.value.frontPhotos.filter(p => p.file).map(p => p.file!),
      side_photos: trainingForm.value.sidePhotos.filter(p => p.file).map(p => p.file!),
      fullbody_photos: trainingForm.value.fullBodyPhotos.filter(p => p.file).map(p => p.file!),
      other_photos: trainingForm.value.otherPhotos.filter(p => p.file).map(p => p.file!),
    });

    alert("학습 요청이 접수됐어요. 심사 후 진행 상황을 '내 아바타'에서 확인할 수 있어요.");
    router.push("/my/avatars");
  } catch (error: any) {
    console.error("Failed to submit training request:", error);
    const msg = error?.response?.data?.detail || error?.message || "요청 제출에 실패했어요.";
    alert(msg);
  } finally {
    submitting.value = false;
  }
}

function goBack() {
  router.push("/my/avatars");
}

// 로그인 상태로 진입/전환되면 폼 초기화. 비로그인 진입 시 회원가입 모달 유도.
onMounted(async () => {
  if (authStore.isLoggedIn) {
    await resetTrainingForm();
  } else if (authStore.isInitialized) {
    authStore.openAuthModal("register", "/my/avatars/new");
  }
});

watch(
  () => [authStore.isInitialized, authStore.isLoggedIn] as const,
  async ([initialized, loggedIn], [, wasLoggedIn]) => {
    if (initialized && loggedIn && !wasLoggedIn) {
      await resetTrainingForm();
    } else if (initialized && !loggedIn && !authStore.authModalOpen) {
      authStore.openAuthModal("register", "/my/avatars/new");
    }
  }
);
</script>

<style scoped>
.create-page {
  padding: 2.5rem 0 4rem;
  background: #fafafa;
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 880px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0d0d0f;
  margin: 0;
}

.page-subtitle {
  margin: 0.5rem 0 0;
  color: #6e6e77;
  font-size: 0.95rem;
}

/* 로그인 게이트 */
.login-gate {
  background: #ffffff;
  border: 1px solid #e6e6ea;
  border-radius: 1rem;
  padding: 3rem 2rem;
  text-align: center;
}

.login-gate h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0d0d0f;
  margin: 0 0 0.5rem;
}

.login-gate p {
  color: #6e6e77;
  margin: 0 0 1.5rem;
}

.login-gate-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

/* 폼 카드 */
.form-card {
  background: #ffffff;
  border: 1px solid #e6e6ea;
  border-radius: 1rem;
  overflow: hidden;
}

.form-body {
  padding: 1.75rem;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 1.75rem;
  border-top: 1px solid #f2f2f4;
  background: #fafafa;
}

/* Buttons */
.btn-primary {
  padding: 0.625rem 1.5rem;
  background: linear-gradient(to right, #e24e12, #e85f26);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1.5rem;
  background: #ffffff;
  color: #3a3a42;
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #fafafa;
}

/* Form Styles (MyAvatarsPage 팝업에서 이식) */
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

.field-optional {
  color: #9a9aa3;
  font-weight: 400;
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

.photo-slot:hover {
  border-color: #e24e12;
  background: #f2f2f4;
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

@media (max-width: 640px) {
  .container {
    padding: 0 1rem;
  }

  .form-body {
    padding: 1.25rem;
  }

  .login-gate-actions {
    flex-direction: column;
  }
}
</style>
