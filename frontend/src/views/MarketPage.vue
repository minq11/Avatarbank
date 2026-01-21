<template>
  <section>
    <h2>아바타 마켓</h2>
    <p class="hint">백엔드 연동 전까지는 목업 데이터로 렌더링합니다.</p>
    <div class="filters">
      <input type="text" placeholder="인플루언서, 태그 검색" />
      <label>
        <input type="checkbox" />
        NSFW 포함
      </label>
    </div>
    <div class="grid">
      <article
        v-for="avatar in mockAvatars"
        :key="avatar.id"
        class="card"
        @click="$router.push(`/avatars/${avatar.id}`)"
      >
        <div class="thumb" />
        <h3>{{ avatar.title }}</h3>
        <p>{{ avatar.description }}</p>
        <small>기본 1C + 옵션</small>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
const mockAvatars = [
  { id: 1, title: "Influencer A", description: "패션/라이프스타일 아바타" },
  { id: 2, title: "Influencer B", description: "스포츠/피트니스 아바타" },
];
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
  background: linear-gradient(135deg, #a855f7, #ec4899);
  border-radius: 10px;
  height: 140px;
  margin-bottom: 0.6rem;
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


