<template>
  <div class="pay-page">
    <div class="pay-card">
      <!-- 승인 중 -->
      <template v-if="state === 'confirming'">
        <div class="spinner" aria-hidden="true"></div>
        <h1>결제를 확인하고 있어요</h1>
        <p class="muted">창을 닫지 말고 잠시만 기다려 주세요.</p>
      </template>

      <!-- 성공 -->
      <template v-else-if="state === 'done'">
        <div class="icon ok" aria-hidden="true">✓</div>
        <h1>충전이 완료됐어요</h1>
        <p class="muted">크레딧이 바로 반영됐어요.</p>

        <div class="balance">
          <span class="balance-num">{{ balance.toLocaleString() }}</span>
          <span class="balance-label">현재 크레딧</span>
        </div>

        <div class="actions">
          <RouterLink to="/studio/create" class="btn-primary">바로 만들러 가기</RouterLink>
          <RouterLink to="/studio" class="btn-ghost">스튜디오로</RouterLink>
        </div>
      </template>

      <!-- 실패 -->
      <template v-else>
        <div class="icon err" aria-hidden="true">!</div>
        <h1>결제를 완료하지 못했어요</h1>
        <p class="muted">{{ errorMessage }}</p>
        <p class="muted small">
          결제가 이미 처리됐는데 이 화면이 보인다면, 스튜디오에서 크레딧 내역을 먼저 확인해 주세요.
          중복으로 결제되지는 않아요.
        </p>
        <div class="actions">
          <RouterLink to="/studio" class="btn-primary">스튜디오로</RouterLink>
          <RouterLink to="/support" class="btn-ghost">문의하기</RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { creditsApi } from "../services/api";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const authStore = useAuthStore();

type State = "confirming" | "done" | "failed";
const state = ref<State>("confirming");
const balance = ref(0);
const errorMessage = ref("");

/**
 * 토스는 결제창을 통과하면 이 주소로 리다이렉트만 시킨다. 승인(confirm)을 호출해야
 * 실제로 결제가 완료되며, 호출하지 않으면 자동으로 취소된다.
 * 금액 검증은 서버가 주문에 박아둔 값으로 하므로 여기서 넘기는 amount 는 참고값이다.
 */
const confirm = async () => {
  const paymentKey = String(route.query.paymentKey ?? "");
  const orderId = String(route.query.orderId ?? "");
  const amount = Number(route.query.amount ?? 0);

  if (!paymentKey || !orderId) {
    state.value = "failed";
    errorMessage.value = "결제 정보가 올바르지 않아요.";
    return;
  }

  try {
    const result = await creditsApi.confirm({ paymentKey, orderId, amount });
    balance.value = result.balance;
    state.value = "done";
    // 헤더 등에서 쓰는 user.credit_balance 도 갱신한다.
    await authStore.fetchUser();
  } catch (e: any) {
    state.value = "failed";
    errorMessage.value =
      e?.response?.data?.detail || "결제 승인 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요.";
  }
};

onMounted(confirm);
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
  margin: 0;
  word-break: keep-all;
}

.small {
  font-size: 0.8rem;
  margin-top: 0.75rem;
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
}

.icon.ok {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}

.icon.err {
  background: #ef4444;
}

.spinner {
  width: 2.25rem;
  height: 2.25rem;
  margin: 0 auto;
  border: 3px solid #ede9fe;
  border-top-color: #7c3aed;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation-duration: 2.4s;
  }
}

.balance {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  background: linear-gradient(135deg, #ede9fe, #fae8ff);
  border-radius: 0.75rem;
  padding: 1rem;
  margin: 1.25rem 0;
}

.balance-num {
  font-size: 1.75rem;
  font-weight: 800;
  color: #111827;
}

.balance-label {
  font-size: 0.75rem;
  color: #6b7280;
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
