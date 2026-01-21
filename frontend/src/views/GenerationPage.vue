<template>
  <section class="generation">
    <div class="layout">
      <div class="left">
        <div class="preview" />
        <p class="note">샘플 프리뷰 (실제 이미지는 생성 후 표시)</p>
      </div>
      <div class="right">
        <h2>아바타 상세 / 이미지 생성</h2>
        <p class="sub">기본 1C는 플랫폼, 옵션 크레딧은 인플루언서에게 지급됩니다.</p>

        <label class="field">
          <span>프롬프트</span>
          <textarea v-model="prompt" rows="5" placeholder="원하는 이미지를 영어로 입력해 주세요." />
        </label>

        <label class="field">
          <span>옵션 크레딧 (0 ~ 10)</span>
          <input type="range" min="0" max="10" v-model.number="optionCredits" />
          <div class="range-info">
            <span>{{ optionCredits }} C</span>
            <span>총 비용: {{ 1 + optionCredits }} C</span>
          </div>
        </label>

        <button
          class="btn primary"
          :disabled="!canSubmit"
          @click="requestGeneration"
        >
          이미지 생성
        </button>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="generationId" class="info">
          생성 요청 완료. ID: {{ generationId }} (상태 조회는 추후 구현)
        </p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import axios from "axios";

const prompt = ref("");
const optionCredits = ref(4);
const loading = ref(false);
const error = ref("");
const generationId = ref<number | null>(null);

const canSubmit = computed(() => !!prompt.value && !loading.value);

async function requestGeneration() {
  if (!canSubmit.value) return;
  loading.value = true;
  error.value = "";
  generationId.value = null;

  try {
    const idempotencyKey = crypto.randomUUID();
    const res = await axios.post(
      "/api/generations",
      {
        avatar_id: 1, // TODO: 라우터 params에서 실제 ID 사용
        prompt: prompt.value,
        option_credits: optionCredits.value,
        idempotency_key: idempotencyKey,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    generationId.value = res.data.id;
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail ?? "이미지 생성 요청 중 오류가 발생했습니다.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.generation {
  display: flex;
  flex-direction: column;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
  gap: 2rem;
}

.preview {
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border-radius: 16px;
  height: 320px;
}

.note {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #9ca3af;
}

.right h2 {
  font-size: 1.4rem;
}

.sub {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

textarea {
  padding: 0.6rem 0.7rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-size: 0.9rem;
  resize: vertical;
}

input[type="range"] {
  width: 100%;
}

.range-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #6b7280;
}

.btn.primary {
  padding: 0.6rem 1.2rem;
  border-radius: 999px;
  background: #111827;
  color: white;
  border: none;
  cursor: pointer;
}

.btn.primary[disabled] {
  opacity: 0.5;
  cursor: default;
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
</style>


