<template>
  <div class="pay-page">
    <div class="pay-card">
      <div class="icon" aria-hidden="true">!</div>
      <h1>결제가 취소됐어요</h1>
      <p class="muted">{{ message }}</p>
      <p v-if="code" class="muted small">오류 코드: {{ code }}</p>

      <p class="muted small">크레딧은 차감되지 않았고, 결제도 진행되지 않았어요.</p>

      <div class="actions">
        <RouterLink to="/studio" class="btn-primary">다시 시도하기</RouterLink>
        <RouterLink to="/support" class="btn-ghost">문의하기</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();

// 토스가 실패 리다이렉트에 code / message 를 붙여 준다.
const code = computed(() => String(route.query.code ?? ""));
const message = computed(
  () => String(route.query.message ?? "") || "결제가 완료되지 않았어요."
);
</script>

<style scoped>
.pay-page {
  min-height: calc(100vh - 80px);
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem 4rem;
}

.pay-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2.5rem 2rem;
  max-width: 26rem;
  width: 100%;
  text-align: center;
}

.pay-card h1 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #111827;
  margin: 1rem 0 0.5rem;
  word-break: keep-all;
}

.muted {
  color: #6b7280;
  margin: 0 0 0.4rem;
  word-break: keep-all;
}

.small {
  font-size: 0.8rem;
}

.icon {
  width: 3rem;
  height: 3rem;
  margin: 0 auto;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  background: #ef4444;
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.25rem;
}

.btn-primary,
.btn-ghost {
  padding: 0.65rem 1.1rem;
  border-radius: 0.6rem;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
}

.btn-ghost {
  border: 1px solid #e5e7eb;
  color: #374151;
  background: #fff;
}
</style>
