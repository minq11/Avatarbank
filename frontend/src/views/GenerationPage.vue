<template>
  <section class="generation">
    <div class="layout">
      <div class="left">
        <div class="preview" />
        <p class="note">Sample preview (actual image will appear after generation)</p>
      </div>
      <div class="right">
        <h2>Avatar Details / Image Generation</h2>
        <p class="sub">The base 1C goes to the platform; option credits go to the influencer.</p>

        <label class="field">
          <span>Prompt</span>
          <textarea v-model="prompt" rows="5" placeholder="Describe the image you want (English recommended)." />
        </label>

        <label class="field">
          <span>Option Credits (0–10)</span>
          <input type="range" min="0" max="10" v-model.number="optionCredits" />
          <div class="range-info">
            <span>{{ optionCredits }} C</span>
            <span>Total cost: {{ 1 + optionCredits }} C</span>
          </div>
        </label>

        <button
          class="btn primary"
          :disabled="!canSubmit"
          @click="requestGeneration"
        >
          Generate Image
        </button>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="generationId" class="info">
          Request submitted. ID: {{ generationId }} (status tracking coming soon)
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
      e?.response?.data?.detail ?? "Failed to submit the generation request.";
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


