<template>
  <section>
    <h2>인플루언서 대시보드</h2>
    <p class="hint">수익/생성 통계는 추후 백엔드 연동 시 실제 데이터로 교체됩니다.</p>
    <div class="stats">
      <div class="stat-card">
        <span class="label">누적 수익</span>
        <strong>120.0 USD</strong>
      </div>
      <div class="stat-card">
        <span class="label">이번 달 수익</span>
        <strong>24.0 USD</strong>
      </div>
      <div class="stat-card">
        <span class="label">총 생성 횟수</span>
        <strong>532</strong>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts"></script>

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

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.stat-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 0.9rem;
}

.label {
  font-size: 0.8rem;
  color: #6b7280;
}

strong {
  display: block;
  margin-top: 0.25rem;
  font-size: 1.1rem;
}
</style>


