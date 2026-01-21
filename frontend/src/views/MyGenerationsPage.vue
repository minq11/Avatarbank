<template>
  <section>
    <h2>내 생성물</h2>
    <p class="hint">현재는 목업 데이터로 렌더링됩니다. 추후 /generations API 연동.</p>
    <div class="list">
      <article v-for="g in mockGenerations" :key="g.id" class="item">
        <div class="thumb" />
        <div class="meta">
          <h3>{{ g.prompt }}</h3>
          <p>{{ g.avatarTitle }} · {{ g.creditsUsed }}C 사용</p>
          <small>{{ g.createdAt }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
const mockGenerations = [
  {
    id: 1,
    prompt: "street fashion full body shot",
    avatarTitle: "Influencer A",
    creditsUsed: 5,
    createdAt: "2026-01-21 12:34",
  },
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

.list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item {
  display: flex;
  gap: 0.75rem;
  padding: 0.6rem;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.thumb {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f59e0b, #ec4899);
}

.meta h3 {
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}

.meta p {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.15rem;
}

small {
  font-size: 0.8rem;
  color: #9ca3af;
}
</style>


