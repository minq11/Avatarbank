<template>
  <section>
    <h2>Avatar Market</h2>
    <p class="hint">Select an avatar to generate images with its LoRA.</p>
    <div v-if="loading" class="loading">Loading avatars...</div>
    <div v-else-if="avatars.length === 0" class="empty">No avatars available yet.</div>
    <div v-else class="grid">
      <article
        v-for="a in avatars"
        :key="a.id"
        class="card"
        @click="$router.push(`/avatars/${a.id}`)"
      >
        <div v-if="a.preview_image_url" class="thumb">
          <img :src="getImageUrl(a.preview_image_url)" :alt="a.title" />
        </div>
        <div v-else class="thumb placeholder" />
        <h3>{{ a.title }}</h3>
        <p>{{ a.description || "—" }}</p>
        <small>{{ a.credit_per_generation != null ? a.credit_per_generation : 1 }} C per generation</small>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { avatarsApi, type AvatarItem } from "@/services/api";

function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("/static/")) return `/api${url}`;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return url;
}

const avatars = ref<AvatarItem[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    avatars.value = await avatarsApi.getList();
  } catch {
    avatars.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
h2 {
  font-size: 1.4rem;
  margin-bottom: 0.25rem;
}

.hint {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.filters input[type="text"] {
  flex: 1;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  cursor: pointer;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  transform: translateY(-1px);
}

.thumb {
  border-radius: 10px;
  height: 140px;
  margin-bottom: 0.6rem;
  overflow: hidden;
  background: linear-gradient(135deg, #a855f7, #ec4899);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb.placeholder {
  background: linear-gradient(135deg, #a855f7, #ec4899);
}

.loading,
.empty {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

h3 {
  margin-bottom: 0.25rem;
}

p {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

small {
  font-size: 0.8rem;
  color: #9ca3af;
}
</style>


