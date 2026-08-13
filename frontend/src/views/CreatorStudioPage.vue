<template>
  <div class="studio-page">
    <div class="studio-container">
      <header class="studio-head">
        <h1>크리에이터 스튜디오</h1>
        <p class="lead">
          내 AI 얼굴로 <strong>무엇이든 자유롭게</strong> 만들고, 원할 땐 팬에게 리딤 링크를 나눠주세요.
        </p>
      </header>

      <div v-if="!authStore.isLoggedIn" class="notice">
        크리에이터 스튜디오를 이용하려면 로그인해 주세요.
      </div>

      <template v-else>
        <!-- 크레딧 잔액 — 충전 패키지 선택은 팝업에서 -->
        <section class="card">
          <h2>크레딧</h2>
          <div class="credit-row">
            <div class="quota-badge">
              <span class="plan-name">보유 크레딧</span>
              <span class="quota-num">{{ credits.toLocaleString() }}</span>
              <span class="quota-label">이미지 1장 = 크레딧 1</span>
            </div>
            <button class="btn-primary" @click="openTopUp">충전하기</button>
          </div>
          <p class="muted small">
            생성에 실패하거나 안전 필터에 걸린 경우 크레딧은 자동으로 돌려드려요.
          </p>
        </section>

        <!-- Direct create — 전용 화면으로 분리됐다 (넓은 작업 공간이 필요해서) -->
        <RouterLink to="/studio/create" class="card highlight shortcut">
          <div class="shortcut-text">
            <h2>직접 만들기</h2>
            <p class="muted small">
              내 아바타로 원하는 장면을 <strong>자유롭게 프롬프트로</strong> 만드세요.
              생성 1장당 크레딧이 1 차감돼요 (건전한 이미지만 생성됩니다).
            </p>
          </div>
          <span class="shortcut-cta">만들러 가기</span>
        </RouterLink>

        <!-- Redeem codes -->
        <section class="card">
          <h2>리딤 링크</h2>
          <p class="muted small">
            팬에게 나눠주세요 (이벤트 경품, 멤버십 혜택 등). 생성이 성공할 때마다 내 크레딧에서
            1이 차감돼요.
          </p>

          <form class="code-form" @submit.prevent="createCodes">
            <div class="form-row">
              <label>아바타</label>
              <div class="avatar-pick">
                <AvatarPickPreview
                  :title="selectedCodeAvatar?.title"
                  :preview-url="selectedCodeAvatar?.preview_image_url"
                  :hidden="selectedCodeAvatar?.status === 'hidden'"
                />
                <div class="avatar-pick-controls">
                  <select v-model.number="newCode.avatar_id" required>
                    <option :value="0" disabled>아바타 선택…</option>
                    <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
                  </select>
                  <p class="muted small">
                    이 아바타로 팬 리딤 링크가 만들어져요. 팬에게도 이 얼굴이 보입니다.
                  </p>
                </div>
              </div>
            </div>
            <div class="form-row inline">
              <div>
                <label>링크당 사용 횟수</label>
                <input v-model.number="newCode.max_uses" type="number" min="1" />
              </div>
              <div>
                <label>링크 개수</label>
                <input v-model.number="newCode.count" type="number" min="1" max="500" />
              </div>
            </div>
            <button class="btn-primary" :disabled="creatingCodes || !newCode.avatar_id">
              {{ creatingCodes ? "생성 중…" : "링크 만들기" }}
            </button>
          </form>

          <!-- 필터 + 내려받기 -->
          <div v-if="codes.length" class="codes-toolbar">
            <div class="code-filters">
              <button
                v-for="f in codeFilters"
                :key="f.value"
                type="button"
                class="code-filter"
                :class="{ active: codeFilter === f.value }"
                @click="codeFilter = f.value"
              >
                {{ f.label }}
                <span class="filter-count">{{ codeCounts[f.value] }}</span>
              </button>
            </div>
            <button
              type="button"
              class="btn-outline"
              :disabled="!filteredCodes.length"
              @click="downloadCodesCsv"
            >
              ⬇ CSV 다운로드 ({{ filteredCodes.length }})
            </button>
          </div>

          <div v-if="filteredCodes.length" class="list">
            <div v-for="c in filteredCodes" :key="c.id" class="list-item">
              <div>
                <!-- 팬이 받는 건 링크다 — 링크를 앞세우고 원시 코드는 뒤로 -->
                <code class="link-primary" :title="redeemUrl(c.code)">
                  {{ redeemPath(c.code) }}
                </code>
                <span class="muted small">
                  · {{ c.used_count }}/{{ c.max_uses ?? "∞" }} 사용됨
                  <template v-if="!c.is_active"> · 비활성</template>
                </span>
              </div>
              <div class="item-actions">
                <button class="btn-text" @click="copyLink(c.code)">링크 복사</button>
                <button v-if="c.is_active" class="btn-text danger" @click="deactivateCode(c.id)">
                  비활성화
                </button>
              </div>
            </div>
          </div>
          <p v-else-if="codes.length" class="muted">이 조건에 해당하는 링크가 없어요.</p>
          <p v-else class="muted">아직 만든 링크가 없어요.</p>
        </section>
      </template>
    </div>

    <!-- 크레딧 충전 팝업 -->
    <transition name="modal">
      <div
        v-if="topUpOpen"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="topup-title"
        @click.self="closeTopUp"
      >
        <div class="modal-panel">
          <header class="modal-head">
            <h2 id="topup-title">크레딧 충전</h2>
            <button class="modal-close" aria-label="닫기" @click="closeTopUp">×</button>
          </header>

          <p class="muted small modal-lead">
            현재 보유 <strong>{{ credits.toLocaleString() }}</strong> 크레딧 · 이미지 1장 = 크레딧 1
          </p>

          <div v-if="packs.length" class="plan-grid">
            <div v-for="p in packs" :key="p.id" class="plan-card">
              <h3>{{ p.name }}</h3>
              <p class="price">{{ p.price_krw.toLocaleString() }}원</p>
              <ul>
                <li>이미지 {{ p.credits.toLocaleString() }}장</li>
                <li>장당 {{ Math.round(p.price_krw / p.credits) }}원</li>
              </ul>
              <button class="btn-primary" :disabled="purchasing" @click="buyPack(p.code)">
                {{ purchasing ? "여는 중…" : "충전하기" }}
              </button>
            </div>
          </div>
          <p v-else class="muted">충전 패키지를 불러오지 못했어요. 새로고침해 주세요.</p>

          <p class="muted small modal-foot">
            결제창은 토스페이먼츠에서 열려요. 결제가 끝나면 크레딧이 바로 반영됩니다.
          </p>
        </div>
      </div>
    </transition>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast" class="toast" :class="toast.kind">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";
import AvatarPickPreview from "../components/AvatarPickPreview.vue";
import {
  studioApi,
  avatarsApi,
  creditsApi,
  type CreditPack,
  type CodeItem,
  type AvatarItem,
} from "../services/api";
import { openTossPayment } from "../services/tossPayment";

const authStore = useAuthStore();

const packs = ref<CreditPack[]>([]);
const credits = ref(0);
const avatars = ref<AvatarItem[]>([]);
const codes = ref<CodeItem[]>([]);

const purchasing = ref(false);
const creatingCodes = ref(false);

const newCode = ref({ avatar_id: 0, max_uses: 1, count: 1 });

const toast = ref<{ msg: string; kind: "ok" | "err" } | null>(null);
let toastTimer: ReturnType<typeof setTimeout> | null = null;
const showToast = (msg: string, kind: "ok" | "err" = "ok") => {
  toast.value = { msg, kind };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2600);
};
const errMsg = (e: any, fallback: string): string => e?.response?.data?.detail || fallback;

const redeemUrl = (code: string) => `${window.location.origin}/r/${code}`;
// 목록에는 짧은 경로만 — 전체 URL 은 title 로 붙이고, 복사는 copyLink 가 전체를 넘긴다.
const redeemPath = (code: string) => `/r/${code}`;

// 선택한 아바타를 썸네일로 보여준다 — 이름만으론 어떤 얼굴인지 확인이 안 된다.
const selectedCodeAvatar = computed(
  () => avatars.value.find((a) => a.id === newCode.value.avatar_id) ?? null
);

// --- 리딤 링크 필터 + 내보내기 ---------------------------------------------
type CodeFilter = "all" | "unused" | "used";

const codeFilters: { value: CodeFilter; label: string }[] = [
  { value: "all", label: "전체" },
  { value: "unused", label: "미사용" },
  { value: "used", label: "사용됨" },
];

const codeFilter = ref<CodeFilter>("all");

const matchesFilter = (c: CodeItem, f: CodeFilter) =>
  f === "all" ? true : f === "used" ? c.used_count > 0 : c.used_count === 0;

const filteredCodes = computed(() =>
  codes.value.filter((c) => matchesFilter(c, codeFilter.value))
);

const codeCounts = computed(() => ({
  all: codes.value.length,
  unused: codes.value.filter((c) => c.used_count === 0).length,
  used: codes.value.filter((c) => c.used_count > 0).length,
}));

/** 쉼표·따옴표·줄바꿈이 있어도 안전하게 CSV 필드로 감싼다. */
const csvCell = (v: unknown): string => {
  const s = v === null || v === undefined ? "" : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

const downloadCodesCsv = () => {
  const rows = filteredCodes.value;
  if (!rows.length) return;

  const header = ["링크", "코드", "사용횟수", "최대사용", "상태", "발급일"];
  const body = rows.map((c) => [
    redeemUrl(c.code),
    c.code,
    c.used_count,
    c.max_uses ?? "무제한",
    c.is_active ? "활성" : "비활성",
    new Date(c.created_at).toLocaleString("ko-KR"),
  ]);

  // 한 줄에 링크 하나 — 엑셀에서 열면 링크가 줄바꿈으로 나열된다.
  const csv = [header, ...body].map((r) => r.map(csvCell).join(",")).join("\r\n");

  // BOM 없이 저장하면 엑셀이 한글을 깨뜨린다.
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const label = codeFilters.find((f) => f.value === codeFilter.value)?.label ?? "전체";
  const stamp = new Date().toISOString().slice(0, 10);

  const a = document.createElement("a");
  a.href = url;
  a.download = `리딤링크_${label}_${stamp}.csv`;
  a.click();
  URL.revokeObjectURL(url);

  showToast(`${rows.length}개 링크를 내려받았어요`);
};

// 크레딧 충전 팝업
const topUpOpen = ref(false);
const openTopUp = () => {
  topUpOpen.value = true;
};
const closeTopUp = () => {
  topUpOpen.value = false;
};

// 팝업이 열려 있을 때만 ESC 를 듣고, 배경 스크롤을 막는다
const onTopUpKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape") closeTopUp();
};
watch(topUpOpen, (open) => {
  document.body.style.overflow = open ? "hidden" : "";
  if (open) window.addEventListener("keydown", onTopUpKeydown);
  else window.removeEventListener("keydown", onTopUpKeydown);
});
onUnmounted(() => {
  document.body.style.overflow = "";
  window.removeEventListener("keydown", onTopUpKeydown);
});

const loadAll = async () => {
  if (!authStore.isLoggedIn) return;

  // 각 항목은 서로 독립적이다. 한 엔드포인트가 500 이 나도 나머지는 그대로 채운다
  // (예전엔 순차 await 라 앞이 실패하면 뒤가 통째로 안 불러와졌다).
  const results = await Promise.allSettled([
    creditsApi.getPacks(),
    creditsApi.getMyCredits(),
    avatarsApi.getMyAvatars(),
    studioApi.getCodes(),
  ]);

  const [packsRes, creditsRes, avatarsRes, codesRes] = results;
  if (packsRes.status === "fulfilled") packs.value = packsRes.value;
  if (creditsRes.status === "fulfilled") credits.value = creditsRes.value.balance;
  if (avatarsRes.status === "fulfilled") avatars.value = avatarsRes.value;
  if (codesRes.status === "fulfilled") codes.value = codesRes.value;

  const failed = results.filter((r) => r.status === "rejected");
  if (failed.length) {
    // 조용히 빈 화면을 보여주지 않는다 — 어디가 실패했는지 콘솔에 남기고 알린다.
    failed.forEach((r) => console.error("Studio load failed:", (r as PromiseRejectedResult).reason));
    showToast(
      `일부 정보를 불러오지 못했어요 (${failed.length}건). 새로고침해 주세요.`,
      "err"
    );
  }
};

/**
 * 크레딧 충전. 서버에서 주문(금액 확정)을 받은 뒤 토스 결제창을 연다.
 * 결제 성공 시 토스가 /payments/success 로 리다이렉트하고, 거기서 승인이 일어난다.
 */
const buyPack = async (packCode: string) => {
  purchasing.value = true;
  try {
    const order = await creditsApi.prepare(packCode);
    await openTossPayment(order);
  } catch (e: any) {
    showToast(errMsg(e, "결제창을 열지 못했어요."), "err");
  } finally {
    purchasing.value = false;
  }
};

const createCodes = async () => {
  creatingCodes.value = true;
  try {
    const created = await studioApi.createCodes({
      avatar_id: newCode.value.avatar_id,
      max_uses: newCode.value.max_uses || 1,
      count: newCode.value.count || 1,
    });
    codes.value = await studioApi.getCodes();
    showToast(`링크 ${created.length}개를 만들었어요`);
  } catch (e: any) {
    showToast(errMsg(e, "링크 생성에 실패했어요."), "err");
  } finally {
    creatingCodes.value = false;
  }
};

const deactivateCode = async (id: number) => {
  try {
    await studioApi.deactivateCode(id);
    codes.value = await studioApi.getCodes();
    showToast("링크가 비활성화됐어요");
  } catch (e: any) {
    showToast(errMsg(e, "링크 비활성화에 실패했어요."), "err");
  }
};

const copyLink = async (code: string) => {
  try {
    await navigator.clipboard.writeText(redeemUrl(code));
    showToast("리딤 링크를 복사했어요 🔗");
  } catch {
    showToast("링크 복사에 실패했어요", "err");
  }
};

onMounted(loadAll);

// App.vue 가 onMounted 에서 authStore.initialize() 를 await 하므로, 새로고침 직후에는
// 이 컴포넌트의 onMounted 시점에 아직 isLoggedIn=false 다 (→ loadAll 이 조기 반환).
// 인증이 끝나 로그인 상태가 되면 한 번 더 불러온다. 모달 로그인 직후에도 동작.
watch(
  () => authStore.isLoggedIn,
  (loggedIn) => {
    if (loggedIn) loadAll();
  }
);
</script>

<style scoped>
.studio-page {
  min-height: calc(100vh - 80px);
  background: #fafafa;
  padding: 2.5rem 1rem 4rem;
}

.studio-container {
  max-width: 880px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.studio-head h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #0d0d0f;
  margin: 0;
}

.lead {
  color: #6e6e77;
  margin: 0.5rem 0 0;
}

.notice {
  background: #fff;
  border: 1px solid #e6e6ea;
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  color: #6e6e77;
}

.card {
  background: #fff;
  border: 1px solid #e6e6ea;
  border-radius: 1rem;
  padding: 1.5rem;
}

.card h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0d0d0f;
  margin: 0 0 0.75rem;
}

.muted {
  color: #6e6e77;
}

.small {
  font-size: 0.8rem;
}

/* 잔액과 충전 버튼을 한 줄에 — 패키지 선택은 팝업으로 넘어갔다 */
.credit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.quota-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 0.15rem;
  background: linear-gradient(135deg, #fdede4, #fce3d6);
  border-radius: 0.75rem;
  padding: 0.85rem 1.25rem;
}

.plan-name {
  font-weight: 700;
  color: #c24210;
  font-size: 0.85rem;
}

.quota-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0d0d0f;
}

.quota-label {
  font-size: 0.75rem;
  color: #6e6e77;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.plan-card {
  border: 1px solid #e6e6ea;
  border-radius: 0.85rem;
  padding: 1.1rem;
  text-align: center;
}

.plan-card h3 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  color: #0d0d0f;
}

.price {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0d0d0f;
  margin: 0 0 0.6rem;
}

.plan-card ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0.9rem;
  font-size: 0.8rem;
  color: #52525b;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.code-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.25rem;
  padding: 1rem;
  background: #fafafa;
  border-radius: 0.75rem;
}

/* 직접 만들기 바로가기 — 카드 전체가 링크다 */
.shortcut {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  text-decoration: none;
  transition: box-shadow 0.15s, transform 0.1s;
}

.shortcut:hover {
  box-shadow: 0 12px 26px -16px rgba(226, 78, 18, 0.55);
  transform: translateY(-1px);
}

.shortcut-text {
  min-width: 0;
}

.shortcut-text h2 {
  margin-bottom: 0.35rem;
}

.shortcut-text p {
  margin: 0;
  max-width: 62ch;
}

.shortcut-cta {
  flex-shrink: 0;
  background: linear-gradient(to right, #e24e12, #f2703a);
  color: #fff;
  border-radius: 0.6rem;
  padding: 0.65rem 1.25rem;
  font-weight: 700;
  font-size: 0.875rem;
  white-space: nowrap;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-row.inline {
  flex-direction: row;
  gap: 1rem;
}

.form-row.inline > div {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #3a3a42;
}

input,
select,
textarea {
  border: 1px solid #d2d2d9;
  border-radius: 0.5rem;
  padding: 0.55rem 0.7rem;
  font-size: 0.9rem;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
  border-top: 1px solid #f2f2f4;
}


/* 목록: 경로 자체가 코드를 담고 있어 원시 코드는 따로 보여주지 않는다 */
.link-primary {
  font-family: ui-monospace, monospace;
  font-size: 0.95rem;
  font-weight: 700;
  color: #c24210;
  letter-spacing: 0.02em;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-primary {
  align-self: flex-start;
  background: linear-gradient(to right, #e24e12, #f2703a);
  color: #fff;
  border: none;
  border-radius: 0.6rem;
  padding: 0.6rem 1.2rem;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: #c24210;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-text.danger {
  color: #dc2626;
}

.btn-outline {
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #fbd9c6;
  color: #c24210;
  border-radius: 0.5rem;
  padding: 0.55rem 0.85rem;
  font-weight: 700;
  font-size: 0.8rem;
  white-space: nowrap;
  cursor: pointer;
}

.btn-outline:hover {
  background: #fdf5f0;
}

.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 리딤 링크 필터 + 내보내기 */
.codes-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding-bottom: 0.85rem;
}

.code-filters {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.code-filter {
  background: none;
  border: 1px solid transparent;
  border-radius: 9999px;
  padding: 0.35rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #6e6e77;
  cursor: pointer;
}

.code-filter:hover {
  background: #fafafa;
}

.code-filter.active {
  background: #fdf5f0;
  border-color: #fbd9c6;
  color: #c24210;
}

.filter-count {
  margin-left: 0.3rem;
  font-variant-numeric: tabular-nums;
  opacity: 0.75;
}

/* 아바타 썸네일 + select */
.avatar-pick {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
}

.avatar-pick-controls {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

/* 이름 하나 고르는 데 폼 전체 폭을 쓸 필요는 없다 */
.avatar-pick-controls select {
  max-width: 340px;
}

.avatar-pick-controls .muted {
  margin: 0;
}










/* 크레딧 충전 팝업 */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(13, 13, 15, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  overflow-y: auto;
}

.modal-panel {
  width: 100%;
  max-width: 40rem;
  background: #fff;
  border-radius: 1.25rem;
  padding: 1.5rem;
  box-shadow: 0 30px 60px -25px rgba(13, 13, 15, 0.5);
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.modal-head h2 {
  margin: 0;
}

.modal-close {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.5rem;
  background: #f2f2f4;
  color: #52525b;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.modal-close:hover {
  background: #e6e6ea;
  color: #0d0d0f;
}

.modal-lead {
  margin: 0.35rem 0 0;
}

.modal-foot {
  margin: 0.25rem 0 0;
}

/* 팝업 등장 — 배경은 페이드, 패널은 살짝 떠오른다 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.18s ease;
}

.modal-enter-active .modal-panel,
.modal-leave-active .modal-panel {
  transition: transform 0.18s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-panel,
.modal-leave-to .modal-panel {
  transform: translateY(0.75rem);
}

@media (prefers-reduced-motion: reduce) {
  .modal-enter-active,
  .modal-leave-active,
  .modal-enter-active .modal-panel,
  .modal-leave-active .modal-panel {
    transition: none;
  }
  .modal-enter-from .modal-panel,
  .modal-leave-to .modal-panel {
    transform: none;
  }
}

/* Toast */
.toast {
  position: fixed;
  left: 50%;
  bottom: 2rem;
  transform: translateX(-50%);
  z-index: 100;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 12px 28px -12px rgba(0, 0, 0, 0.4);
}

.toast.ok {
  background: #0d0d0f;
}

.toast.err {
  background: #dc2626;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 12px);
}
</style>
