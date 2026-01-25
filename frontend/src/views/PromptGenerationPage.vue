<template>
  <section class="prompt-generation">
    <div class="header">
      <h1>AI Image Generation</h1>
      <p>Write a prompt to generate the image you want.</p>
    </div>

    <div class="content">
      <div class="panel">
        <label class="field">
          <span>Prompt</span>
          <textarea
            v-model="prompt"
            rows="6"
            placeholder="e.g., an influencer in a futuristic neon city"
          />
        </label>

        <div class="actions">
          <button class="btn primary" :disabled="!canSubmit" @click="handleGenerate">
            {{ isLoading ? "Submitting..." : "Generate Image" }}
          </button>
          <button class="btn ghost" type="button" @click="clearPrompt">
            Reset
          </button>
        </div>

        <p v-if="statusMessage" class="notice">
          {{ statusMessage }}
        </p>
        <p v-if="errorMessage" class="error">
          {{ errorMessage }}
        </p>

        <div v-if="imageUrl" class="result">
          <img :src="imageUrl" alt="Generated result" />
        </div>
      </div>

      <div class="tips">
        <h2>Prompt Tips</h2>
        <ul>
          <li>Be specific about background, lighting, outfit, and mood.</li>
          <li>Add style keywords (e.g., cinematic, pastel, minimal).</li>
          <li>English prompts often produce more consistent results.</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/services/api";

const route = useRoute();
const prompt = ref((route.query.prompt as string) ?? "");
const isLoading = ref(false);
const statusMessage = ref("");
const errorMessage = ref("");
const generationId = ref<number | null>(null);
const imageUrl = ref("");
let pollTimer: number | null = null;

const canSubmit = computed(() => !!prompt.value && !isLoading.value);

watch(
  () => route.query.prompt,
  (value) => {
    if (typeof value === "string") {
      prompt.value = value;
    }
  },
);

async function handleGenerate() {
  if (!canSubmit.value) return;
  isLoading.value = true;
  statusMessage.value = "";
  errorMessage.value = "";
  imageUrl.value = "";
  generationId.value = null;

  try {
    const idempotencyKey = crypto.randomUUID();
    const response = await api.post("/generations", {
      prompt: prompt.value,
      option_credits: 0,
      idempotency_key: idempotencyKey,
    });

    generationId.value = response.data.id;
    statusMessage.value = "Request submitted. Waiting for results...";
    startPolling();
  } catch (error: any) {
    if (error?.response?.status === 401) {
      errorMessage.value = "Please log in to generate images.";
    } else {
      errorMessage.value =
        error?.response?.data?.detail ?? "Failed to submit the request.";
    }
  } finally {
    isLoading.value = false;
  }
}

function clearPrompt() {
  prompt.value = "";
  statusMessage.value = "";
  errorMessage.value = "";
  imageUrl.value = "";
  generationId.value = null;
  stopPolling();
}

function startPolling() {
  stopPolling();
  if (!generationId.value) return;

  pollTimer = window.setInterval(async () => {
    if (!generationId.value) return;

    try {
      const res = await api.get(`/generations/${generationId.value}`);
      const data = res.data;
      const status = data.status;

      if (status === "success") {
        imageUrl.value = data.image_url || "";
        statusMessage.value = "Generation complete.";
        stopPolling();
      } else if (status === "failed") {
        errorMessage.value = data.fail_reason || "Generation failed.";
        statusMessage.value = "";
        stopPolling();
      } else {
        statusMessage.value = "Generating...";
      }
    } catch (error: any) {
      errorMessage.value =
        error?.response?.data?.detail ?? "Failed to fetch generation status.";
      statusMessage.value = "";
      stopPolling();
    }
  }, 2000);
}

function stopPolling() {
  if (pollTimer !== null) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.prompt-generation {
  max-width: 1100px;
  margin: 0 auto;
  padding: 4rem 2rem 6rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  color: #111827;
}

.header p {
  color: #6b7280;
  font-size: 1.1rem;
}

.content {
  display: grid;
  gap: 2rem;
}

@media (min-width: 900px) {
  .content {
    grid-template-columns: 2fr 1fr;
    align-items: start;
  }
}

.panel {
  background: white;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
  color: #111827;
}

textarea {
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  padding: 0.9rem 1rem;
  font-size: 1rem;
  resize: vertical;
  min-height: 160px;
}

textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 0.7rem 1.6rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn.primary {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
}

.btn.primary[disabled] {
  opacity: 0.6;
  cursor: default;
  box-shadow: none;
  transform: none;
}

.btn.ghost {
  background: #f3f4f6;
  color: #374151;
}

.btn:not([disabled]):hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.18);
}

.notice {
  margin-top: 1rem;
  color: #16a34a;
  font-size: 0.95rem;
}

.error {
  margin-top: 0.75rem;
  color: #dc2626;
  font-size: 0.95rem;
}

.result {
  margin-top: 1.5rem;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.result img {
  width: 100%;
  display: block;
}

.tips {
  background: #f8fafc;
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.tips h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #111827;
}

.tips ul {
  padding-left: 1.2rem;
  color: #475569;
  display: grid;
  gap: 0.5rem;
}
</style>
