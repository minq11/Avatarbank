<template>
  <div class="studio-page">
    <div class="studio-container">
      <header class="studio-head">
        <h1>Creator Studio</h1>
        <p class="lead">
          Generate content with your own AI likeness, and share redeem codes with your fans.
        </p>
      </header>

      <div v-if="!authStore.isLoggedIn" class="notice">
        Please log in to access your Creator Studio.
      </div>

      <template v-else>
        <!-- Subscription / Quota -->
        <section class="card">
          <h2>Subscription</h2>
          <div v-if="subscription" class="quota-row">
            <div class="quota-badge">
              <span class="plan-name">{{ subscription.plan_name }}</span>
              <span class="quota-num">
                {{ subscription.quota_remaining }} / {{ subscription.monthly_quota }}
              </span>
              <span class="quota-label">images left this period</span>
            </div>
          </div>
          <p v-else class="muted">You don't have an active plan yet. Choose one below.</p>

          <div class="plan-grid">
            <div
              v-for="p in plans"
              :key="p.id"
              class="plan-card"
              :class="{ current: subscription?.plan_code === p.code }"
            >
              <h3>{{ p.name }}</h3>
              <p class="price">${{ p.price_usd }}<span>/mo</span></p>
              <ul>
                <li>{{ p.monthly_quota.toLocaleString() }} images / month</li>
                <li>{{ p.max_avatars }} avatar{{ p.max_avatars === 1 ? "" : "s" }}</li>
                <li>{{ p.max_active_codes.toLocaleString() }} active codes</li>
              </ul>
              <button
                class="btn-primary"
                :disabled="subscribing || subscription?.plan_code === p.code"
                @click="subscribe(p.code)"
              >
                {{ subscription?.plan_code === p.code ? "Current plan" : "Choose" }}
              </button>
            </div>
          </div>
          <p class="muted small">
            Payment is not yet connected — choosing a plan activates quota immediately (demo).
          </p>
        </section>

        <!-- Templates -->
        <section class="card">
          <h2>Looks (Templates)</h2>
          <p class="muted small">
            Fans can only generate from these pre-approved looks — they can't type their own
            prompts. This keeps your likeness fully under your control.
          </p>

          <form class="template-form" @submit.prevent="createTemplate">
            <div class="form-row">
              <label>Avatar</label>
              <select v-model.number="newTemplate.avatar_id" required>
                <option :value="0" disabled>Select an avatar…</option>
                <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>Look name</label>
              <input v-model="newTemplate.name" placeholder="e.g. Christmas, Summer beach" required />
            </div>
            <div class="form-row">
              <label>Prompt</label>
              <textarea
                v-model="newTemplate.prompt"
                placeholder="Describe the scene/outfit (fans see this look but can't edit it)"
                rows="2"
                required
              ></textarea>
            </div>
            <button class="btn-primary" :disabled="creatingTemplate || !newTemplate.avatar_id">
              {{ creatingTemplate ? "Adding…" : "Add look" }}
            </button>
          </form>

          <div v-if="templates.length" class="list">
            <div v-for="t in templates" :key="t.id" class="list-item">
              <div>
                <strong>{{ t.name }}</strong>
                <span class="muted small"> · {{ avatarTitle(t.avatar_id) }}</span>
                <p class="muted small prompt-preview">{{ t.prompt }}</p>
              </div>
              <button class="btn-text danger" @click="deleteTemplate(t.id)">Delete</button>
            </div>
          </div>
          <p v-else class="muted">No looks yet.</p>
        </section>

        <!-- Redeem codes -->
        <section class="card">
          <h2>Redeem codes</h2>
          <p class="muted small">
            Hand these out to fans (giveaway, membership perk…). Each successful generation uses one
            image from your quota.
          </p>

          <form class="code-form" @submit.prevent="createCodes">
            <div class="form-row">
              <label>Avatar</label>
              <select v-model.number="newCode.avatar_id" required>
                <option :value="0" disabled>Select an avatar…</option>
                <option v-for="a in avatars" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>Look (optional)</label>
              <select v-model.number="newCode.template_id">
                <option :value="0">All looks for this avatar</option>
                <option v-for="t in templatesForAvatar(newCode.avatar_id)" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>
            <div class="form-row inline">
              <div>
                <label>Uses per code</label>
                <input v-model.number="newCode.max_uses" type="number" min="1" />
              </div>
              <div>
                <label>How many codes</label>
                <input v-model.number="newCode.count" type="number" min="1" max="500" />
              </div>
            </div>
            <button class="btn-primary" :disabled="creatingCodes || !newCode.avatar_id">
              {{ creatingCodes ? "Generating…" : "Generate codes" }}
            </button>
          </form>

          <div v-if="codes.length" class="list">
            <div v-for="c in codes" :key="c.id" class="list-item">
              <div>
                <code class="code-chip">{{ c.code }}</code>
                <span class="muted small">
                  · {{ c.used_count }}/{{ c.max_uses ?? "∞" }} used
                  <template v-if="!c.is_active"> · inactive</template>
                </span>
                <p class="muted small">{{ redeemUrl(c.code) }}</p>
              </div>
              <div class="item-actions">
                <button class="btn-text" @click="copyLink(c.code)">Copy link</button>
                <button v-if="c.is_active" class="btn-text danger" @click="deactivateCode(c.id)">
                  Disable
                </button>
              </div>
            </div>
          </div>
          <p v-else class="muted">No codes yet.</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import {
  studioApi,
  avatarsApi,
  type Plan,
  type SubscriptionInfo,
  type TemplateItem,
  type CodeItem,
  type AvatarItem,
} from "../services/api";

const authStore = useAuthStore();

const plans = ref<Plan[]>([]);
const subscription = ref<SubscriptionInfo | null>(null);
const avatars = ref<AvatarItem[]>([]);
const templates = ref<TemplateItem[]>([]);
const codes = ref<CodeItem[]>([]);

const subscribing = ref(false);
const creatingTemplate = ref(false);
const creatingCodes = ref(false);

const newTemplate = ref({ avatar_id: 0, name: "", prompt: "" });
const newCode = ref({ avatar_id: 0, template_id: 0, max_uses: 1, count: 1 });

const avatarTitle = (id: number) => avatars.value.find((a) => a.id === id)?.title || "—";
const templatesForAvatar = (avatarId: number) =>
  templates.value.filter((t) => t.avatar_id === avatarId);
const redeemUrl = (code: string) => `${window.location.origin}/r/${code}`;

const loadAll = async () => {
  if (!authStore.isLoggedIn) return;
  try {
    plans.value = await studioApi.getPlans();
    subscription.value = await studioApi.getSubscription();
    avatars.value = await avatarsApi.getMyAvatars();
    templates.value = await studioApi.getTemplates();
    codes.value = await studioApi.getCodes();
  } catch (e) {
    console.error("Failed to load studio data", e);
  }
};

const subscribe = async (planCode: string) => {
  subscribing.value = true;
  try {
    subscription.value = await studioApi.subscribe(planCode);
  } catch (e: any) {
    alert(e?.response?.data?.detail || "Failed to subscribe.");
  } finally {
    subscribing.value = false;
  }
};

const createTemplate = async () => {
  creatingTemplate.value = true;
  try {
    await studioApi.createTemplate({ ...newTemplate.value });
    newTemplate.value = { avatar_id: 0, name: "", prompt: "" };
    templates.value = await studioApi.getTemplates();
  } catch (e: any) {
    alert(e?.response?.data?.detail || "Failed to add look.");
  } finally {
    creatingTemplate.value = false;
  }
};

const deleteTemplate = async (id: number) => {
  if (!confirm("Delete this look?")) return;
  await studioApi.deleteTemplate(id);
  templates.value = await studioApi.getTemplates();
};

const createCodes = async () => {
  creatingCodes.value = true;
  try {
    await studioApi.createCodes({
      avatar_id: newCode.value.avatar_id,
      template_id: newCode.value.template_id || null,
      max_uses: newCode.value.max_uses || 1,
      count: newCode.value.count || 1,
    });
    codes.value = await studioApi.getCodes();
  } catch (e: any) {
    alert(e?.response?.data?.detail || "Failed to generate codes.");
  } finally {
    creatingCodes.value = false;
  }
};

const deactivateCode = async (id: number) => {
  await studioApi.deactivateCode(id);
  codes.value = await studioApi.getCodes();
};

const copyLink = async (code: string) => {
  try {
    await navigator.clipboard.writeText(redeemUrl(code));
    alert("Link copied!");
  } catch {
    /* ignore */
  }
};

onMounted(loadAll);
</script>

<style scoped>
.studio-page {
  min-height: calc(100vh - 80px);
  background: #f9fafb;
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
  color: #111827;
  margin: 0;
}

.lead {
  color: #6b7280;
  margin: 0.5rem 0 0;
}

.notice {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem;
}

.card h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.75rem;
}

.muted {
  color: #6b7280;
}

.small {
  font-size: 0.8rem;
}

.quota-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 0.15rem;
  background: linear-gradient(135deg, #ede9fe, #fae8ff);
  border-radius: 0.75rem;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1rem;
}

.plan-name {
  font-weight: 700;
  color: #6d28d9;
  font-size: 0.85rem;
}

.quota-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #111827;
}

.quota-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.plan-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.85rem;
  padding: 1.1rem;
  text-align: center;
}

.plan-card.current {
  border-color: #7c3aed;
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15);
}

.plan-card h3 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  color: #111827;
}

.price {
  font-size: 1.4rem;
  font-weight: 800;
  color: #111827;
  margin: 0 0 0.6rem;
}

.price span {
  font-size: 0.8rem;
  font-weight: 500;
  color: #9ca3af;
}

.plan-card ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0.9rem;
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.template-form,
.code-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.25rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
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
  color: #374151;
}

input,
select,
textarea {
  border: 1px solid #d1d5db;
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
  border-top: 1px solid #f3f4f6;
}

.prompt-preview {
  max-width: 520px;
  margin: 0.25rem 0 0;
}

.code-chip {
  background: #111827;
  color: #fff;
  border-radius: 0.4rem;
  padding: 0.15rem 0.5rem;
  font-family: ui-monospace, monospace;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-primary {
  align-self: flex-start;
  background: linear-gradient(to right, #7c3aed, #9333ea);
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
  color: #6d28d9;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-text.danger {
  color: #dc2626;
}
</style>
