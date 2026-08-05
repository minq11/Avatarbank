<template>
  <div class="doc-page">
    <div class="admin-container">
      <header class="doc-head">
        <h1>관리자 · 문의함</h1>
        <p class="doc-lead">
          고객지원 페이지로 접수된 문의를 확인하고 답장을 보냅니다.
          답장은 문의자 이메일로 발송되며, 발송에 성공해야 "답변완료"로 바뀝니다.
        </p>
      </header>

      <div v-if="!authStore.isAdmin" class="card notice">
        관리자만 이용할 수 있는 페이지예요.
      </div>

      <template v-else>
        <!-- 필터 -->
        <section class="card filter-card">
          <div class="filter-tabs">
            <button
              v-for="f in filters"
              :key="f.value"
              class="filter-tab"
              :class="{ active: activeFilter === f.value }"
              @click="selectFilter(f.value)"
            >
              {{ f.label }}
              <span v-if="f.value === 'open' && openCount" class="tab-badge">{{ openCount }}</span>
            </button>
          </div>
          <button class="btn-text" :disabled="loading" @click="load">새로고침</button>
        </section>

        <!-- 목록 -->
        <section class="card">
          <div v-if="loading" class="empty">불러오는 중…</div>
          <div v-else-if="loadError" class="empty error">{{ loadError }}</div>
          <div v-else-if="!inquiries.length" class="empty">해당하는 문의가 없어요.</div>

          <div v-else class="inquiry-table">
            <div class="table-head">
              <div class="col-id">번호</div>
              <div class="col-cat">분류</div>
              <div class="col-subject">제목</div>
              <div class="col-from">문의자</div>
              <div class="col-date">접수일</div>
              <div class="col-status">상태</div>
            </div>
            <button
              v-for="q in inquiries"
              :key="q.id"
              class="table-row"
              @click="openDetail(q)"
            >
              <div class="col-id">#{{ q.id }}</div>
              <div class="col-cat">{{ categoryLabel(q.category) }}</div>
              <div class="col-subject">
                <span class="subject-text">{{ q.subject }}</span>
                <span class="preview-text">{{ q.message }}</span>
              </div>
              <div class="col-from">
                <span class="from-name">{{ q.name }}</span>
                <span class="from-email">{{ q.email }}</span>
              </div>
              <div class="col-date">{{ formatDate(q.created_at) }}</div>
              <div class="col-status">
                <span class="status-badge" :class="q.status">{{ statusLabel(q.status) }}</span>
              </div>
            </button>
          </div>
        </section>
      </template>
    </div>

    <!-- 상세 + 답장 모달 -->
    <div v-if="selected" class="modal-overlay" @click.self="closeDetail">
      <div class="detail-modal">
        <header class="modal-head">
          <div>
            <span class="status-badge" :class="selected.status">
              {{ statusLabel(selected.status) }}
            </span>
            <span class="modal-cat">{{ categoryLabel(selected.category) }}</span>
            <h3>#{{ selected.id }} · {{ selected.subject }}</h3>
            <p class="muted small">
              {{ selected.name }} &lt;{{ selected.email }}&gt; ·
              {{ formatDate(selected.created_at) }} ·
              {{ selected.user_id ? `회원 #${selected.user_id}` : "비회원" }}
              <template v-if="!selected.notified_at"> · 알림 메일 미발송</template>
            </p>
          </div>
          <button class="btn-text" @click="closeDetail">닫기</button>
        </header>

        <div class="modal-body">
          <div class="message-block">{{ selected.message }}</div>

          <!-- 기존 답변 -->
          <div v-if="selected.reply_body" class="reply-done">
            <h4>보낸 답장 · {{ formatDate(selected.replied_at) }}</h4>
            <div class="message-block">{{ selected.reply_body }}</div>
          </div>

          <!-- 답장 작성 -->
          <div class="reply-form">
            <label for="reply-body">
              {{ selected.reply_body ? "추가 답장 보내기" : "답장 보내기" }}
            </label>
            <textarea
              id="reply-body"
              v-model="replyBody"
              rows="8"
              maxlength="4000"
              placeholder="문의자에게 보낼 답변을 작성하세요. 원문이 함께 인용되어 발송돼요."
            ></textarea>
            <p class="muted small">
              {{ selected.email }} 으로 발송되며, 문의자가 회신하면
              {{ notifyEmail }} 으로 전달돼요.
            </p>

            <p v-if="actionError" class="form-error">{{ actionError }}</p>

            <div class="modal-actions">
              <button
                class="btn-primary"
                :disabled="replying || !replyBody.trim()"
                @click="sendReply"
              >
                <span v-if="replying" class="spinner-inline"></span>
                {{ replying ? "보내는 중…" : "답장 보내기" }}
              </button>
              <button
                v-if="selected.status !== 'closed'"
                class="btn-text danger"
                :disabled="closing"
                @click="closeInquiry"
              >
                {{ closing ? "처리 중…" : "답장 없이 종료" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast" class="toast" :class="toast.kind">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useAuthStore } from "../stores/auth";
import { inquiriesApi, type AdminInquiryItem, type InquiryCategory } from "../services/api";

const authStore = useAuthStore();

// 문의 회신 시 Reply-To 로 쓰이는 내부 주소 (백엔드 INQUIRY_NOTIFY_EMAIL 과 동일).
const notifyEmail = "gooddonutsyh@gmail.com";

const filters = [
  { value: "", label: "전체" },
  { value: "open", label: "접수" },
  { value: "answered", label: "답변완료" },
  { value: "closed", label: "종료" },
];

const CATEGORY_LABELS: Record<InquiryCategory, string> = {
  account: "계정/로그인",
  avatar: "아바타 등록·학습",
  generation: "생성/쿼터",
  code: "리딤 코드",
  billing: "결제/구독",
  report: "신고",
  etc: "기타",
};

const STATUS_LABELS: Record<string, string> = {
  open: "접수",
  answered: "답변완료",
  closed: "종료",
};

const inquiries = ref<AdminInquiryItem[]>([]);
const activeFilter = ref("");
const loading = ref(false);
const loadError = ref<string | null>(null);

const selected = ref<AdminInquiryItem | null>(null);
const replyBody = ref("");
const replying = ref(false);
const closing = ref(false);
const actionError = ref<string | null>(null);

const toast = ref<{ msg: string; kind: "ok" | "err" } | null>(null);
let toastTimer: ReturnType<typeof setTimeout> | null = null;
const showToast = (msg: string, kind: "ok" | "err" = "ok") => {
  toast.value = { msg, kind };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2800);
};

const errMsg = (e: any, fallback: string): string => {
  const detail = e?.response?.data?.detail;
  return Array.isArray(detail) ? detail[0]?.msg || fallback : detail || fallback;
};

const categoryLabel = (c: string) => CATEGORY_LABELS[c as InquiryCategory] || c;
const statusLabel = (s: string) => STATUS_LABELS[s] || s;

const openCount = computed(
  () => inquiries.value.filter((q) => q.status === "open").length
);

const formatDate = (iso: string | null) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(
    d.getDate()
  ).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(
    d.getMinutes()
  ).padStart(2, "0")}`;
};

const load = async () => {
  if (!authStore.isAdmin) return;
  loading.value = true;
  loadError.value = null;
  try {
    inquiries.value = await inquiriesApi.adminList(activeFilter.value || undefined);
  } catch (e: any) {
    loadError.value = errMsg(e, "문의 목록을 불러오지 못했어요.");
  } finally {
    loading.value = false;
  }
};

const selectFilter = (value: string) => {
  activeFilter.value = value;
  load();
};

const openDetail = (q: AdminInquiryItem) => {
  selected.value = q;
  replyBody.value = "";
  actionError.value = null;
};

const closeDetail = () => {
  selected.value = null;
  replyBody.value = "";
  actionError.value = null;
};

/** 목록에서 해당 문의를 서버 응답으로 교체 (재조회 없이 상태 반영). */
const replaceInList = (updated: AdminInquiryItem) => {
  const idx = inquiries.value.findIndex((q) => q.id === updated.id);
  if (idx !== -1) inquiries.value[idx] = updated;
};

const sendReply = async () => {
  if (!selected.value) return;
  replying.value = true;
  actionError.value = null;
  try {
    const updated = await inquiriesApi.adminReply(selected.value.id, replyBody.value.trim());
    replaceInList(updated);
    // 필터가 "접수"면 답변완료된 항목은 목록에서 빠져야 한다.
    if (activeFilter.value && updated.status !== activeFilter.value) {
      inquiries.value = inquiries.value.filter((q) => q.id !== updated.id);
    }
    closeDetail();
    showToast("답장을 보냈어요 📮");
  } catch (e: any) {
    actionError.value = errMsg(e, "답장 발송에 실패했어요.");
  } finally {
    replying.value = false;
  }
};

const closeInquiry = async () => {
  if (!selected.value) return;
  if (!confirm("답장 없이 이 문의를 종료할까요?")) return;
  closing.value = true;
  actionError.value = null;
  try {
    const updated = await inquiriesApi.adminClose(selected.value.id);
    replaceInList(updated);
    if (activeFilter.value && updated.status !== activeFilter.value) {
      inquiries.value = inquiries.value.filter((q) => q.id !== updated.id);
    }
    closeDetail();
    showToast("문의를 종료했어요");
  } catch (e: any) {
    actionError.value = errMsg(e, "종료에 실패했어요.");
  } finally {
    closing.value = false;
  }
};

onMounted(load);

// App.vue 가 onMounted 에서 인증 초기화를 await 하므로 새로고침 직후에는 이 시점에
// isAdmin 이 아직 false 다 (→ load 가 조기 반환). 초기화가 끝나면 다시 불러온다.
watch(
  () => authStore.isAdmin,
  (isAdmin) => {
    if (isAdmin) load();
  }
);
</script>

<style scoped>
@import "./doc-page.css";

.admin-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.notice {
  text-align: center;
  color: #6b7280;
  padding: 2.5rem;
}

.filter-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.filter-tab {
  background: none;
  border: 1px solid transparent;
  border-radius: 9999px;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
}

.filter-tab.active {
  background: #f5f3ff;
  border-color: #ddd6fe;
  color: #6d28d9;
}

.tab-badge {
  display: inline-block;
  margin-left: 0.35rem;
  background: #7c3aed;
  color: #fff;
  border-radius: 9999px;
  padding: 0 0.4rem;
  font-size: 0.7rem;
}

.empty {
  text-align: center;
  color: #9ca3af;
  padding: 2rem 0;
  font-size: 0.9rem;
}

.empty.error {
  color: #b91c1c;
}

/* 목록 */
.inquiry-table {
  display: flex;
  flex-direction: column;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 4rem 7rem minmax(0, 1fr) 11rem 8rem 5.5rem;
  gap: 0.75rem;
  align-items: center;
  text-align: left;
}

.table-head {
  font-size: 0.75rem;
  font-weight: 700;
  color: #9ca3af;
  padding: 0 0.5rem 0.6rem;
  border-bottom: 1px solid #e5e7eb;
}

.table-row {
  background: none;
  border: none;
  border-bottom: 1px solid #f3f4f6;
  padding: 0.8rem 0.5rem;
  font-size: 0.85rem;
  color: #4b5563;
  cursor: pointer;
  font-family: inherit;
  width: 100%;
}

.table-row:hover {
  background: #f9fafb;
}

.col-id {
  color: #9ca3af;
  font-variant-numeric: tabular-nums;
}

.col-subject {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.subject-text {
  color: #111827;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-text {
  font-size: 0.78rem;
  color: #9ca3af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-from {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.from-name {
  color: #374151;
  font-weight: 600;
}

.from-email,
.col-date {
  font-size: 0.75rem;
  color: #9ca3af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .table-head {
    display: none;
  }

  .table-row {
    grid-template-columns: 1fr auto;
    grid-template-areas:
      "subject status"
      "from date";
    row-gap: 0.35rem;
  }

  .col-id,
  .col-cat {
    display: none;
  }

  .col-subject {
    grid-area: subject;
  }
  .col-from {
    grid-area: from;
  }
  .col-date {
    grid-area: date;
    text-align: right;
  }
  .col-status {
    grid-area: status;
    justify-self: end;
  }
}

.status-badge {
  display: inline-block;
  border-radius: 9999px;
  padding: 0.2rem 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-badge.open {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.answered {
  background: #dcfce7;
  color: #166534;
}

.status-badge.closed {
  background: #f3f4f6;
  color: #6b7280;
}

/* 상세 모달 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 90;
}

.detail-modal {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem;
  max-width: 640px;
  width: 100%;
  max-height: 88vh;
  overflow-y: auto;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 1rem;
}

.modal-head h3 {
  margin: 0.5rem 0 0.35rem;
  font-size: 1.05rem;
  color: #111827;
}

.modal-cat {
  display: inline-block;
  margin-left: 0.4rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.modal-body {
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.message-block {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.6rem;
  padding: 0.9rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.reply-done h4 {
  font-size: 0.85rem;
  color: #166534;
  margin: 0 0 0.4rem;
}

.reply-form {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.reply-form label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #374151;
}

textarea {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
}

.muted {
  color: #9ca3af;
}

.small {
  font-size: 0.75rem;
}

.form-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 0.6rem;
  padding: 0.7rem 0.9rem;
  font-size: 0.85rem;
  margin: 0.35rem 0 0;
}

.modal-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.6rem;
}

.btn-primary {
  background: linear-gradient(to right, #7c3aed, #9333ea);
  color: #fff;
  border: none;
  border-radius: 0.6rem;
  padding: 0.65rem 1.3rem;
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
  color: #6d28d9;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-text.danger {
  color: #dc2626;
}

.btn-text:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.spinner-inline {
  display: inline-block;
  width: 0.9rem;
  height: 0.9rem;
  margin-right: 0.4rem;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #fff;
  border-radius: 50%;
  vertical-align: -2px;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
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
  background: #111827;
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
