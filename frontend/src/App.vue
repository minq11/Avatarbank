<template>
  <div class="app">
    <header class="app-header">
      <div class="header-container">
        <div class="header-content">
          <!-- Logo -->
          <div class="logo-wrapper">
            <RouterLink to="/" class="logo-link">
              <h1 class="logo">Avatarbank</h1>
            </RouterLink>
          </div>

          <!-- Center Navigation -->
          <nav class="center-nav">
            <RouterLink to="/market" class="nav-link">Market</RouterLink>
            <RouterLink to="/gallery" class="nav-link">Gallery</RouterLink>
          </nav>

          <!-- Right Side - Language + Auth -->
          <div class="right-nav">
            <!-- Language Switcher -->
            <div class="language-wrapper">
              <button
                @click="showLanguageMenu = !showLanguageMenu"
                class="language-btn"
              >
                <span :class="`fi fi-${currentLanguage.flagCode}`" class="flag-icon"></span>
                {{ currentLanguage.label }}
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M6 9l6 6 6-6"/>
                </svg>
              </button>
              <div v-if="showLanguageMenu" class="language-dropdown">
                <button
                  v-for="lang in languages"
                  :key="lang.value"
                  @click="selectLanguage(lang.value)"
                  class="language-option"
                >
                  <span :class="`fi fi-${lang.flagCode}`" class="flag-icon"></span>
                  {{ lang.label }}
                </button>
              </div>
            </div>

            <!-- Auth Buttons -->
            <div v-if="!authStore.isLoggedIn" class="auth-buttons">
              <button @click="openLoginModal" class="btn-login">Login</button>
              <button @click="openRegisterModal" class="btn-signup">Sign up</button>
            </div>

            <!-- User Info (when logged in) -->
            <div v-else class="user-info">
              <!-- Seller 업그레이드 버튼 (Buyer만 보임) -->
              <button
                v-if="authStore.isBuyer"
                @click="handleUpgradeToSeller"
                :disabled="isUpgrading"
                class="upgrade-btn"
              >
                <svg class="upgrade-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                <span>{{ isUpgrading ? 'Upgrading...' : 'Become a Seller' }}</span>
                <svg v-if="!isUpgrading" class="upgrade-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>

              <div class="credit-badge">
                <svg class="coin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v12M15 9a3 3 0 1 0-6 0 3 3 0 0 0 6 0z"/>
                </svg>
                <span>{{ formatCredit(authStore.creditBalance) }}</span>
              </div>
              <div class="profile-wrapper">
                <button
                  @click="showProfileMenu = !showProfileMenu"
                  class="profile-btn"
                >
                  <svg class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </button>
                <div v-if="showProfileMenu" class="profile-dropdown">
                  <a href="#profile" class="dropdown-item">Profile</a>
                  <a href="#settings" class="dropdown-item">Settings</a>
                  <div class="dropdown-divider"></div>
                  <a href="#" @click.prevent="handleLogout" class="dropdown-item">Log out</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <!-- Auth Modal -->
    <AuthModal
      :is-open="showAuthModal"
      :initial-mode="authModalMode"
      @close="closeAuthModal"
    />

    <footer class="app-footer">
      <div class="footer-container">
        <div class="footer-grid">
          <!-- Brand -->
          <div class="footer-brand">
            <h4 class="footer-brand-title">Avatarbank</h4>
            <p class="footer-brand-description">
              The premier AI avatar marketplace connecting creators and users.
            </p>
          </div>

          <!-- Legal -->
          <div class="footer-column">
            <h5 class="footer-column-title">Legal</h5>
            <ul class="footer-links-list">
              <li><a href="#terms" class="footer-link">Terms of Service</a></li>
              <li><a href="#privacy" class="footer-link">Privacy Policy</a></li>
            </ul>
          </div>

          <!-- Resources -->
          <div class="footer-column">
            <h5 class="footer-column-title">Resources</h5>
            <ul class="footer-links-list">
              <li><a href="#guide" class="footer-link">Influencer Guide</a></li>
              <li><a href="#support" class="footer-link">Support</a></li>
            </ul>
          </div>

          <!-- Connect -->
          <div class="footer-column">
            <h5 class="footer-column-title">Connect</h5>
            <ul class="footer-links-list">
              <li><a href="#twitter" class="footer-link">Twitter</a></li>
              <li><a href="#discord" class="footer-link">Discord</a></li>
            </ul>
          </div>
        </div>

        <!-- Bottom Bar -->
        <div class="footer-bottom">
          <p class="footer-copyright">© 2026 Avatarbank. All rights reserved.</p>
          <div class="footer-social">
            <a href="#twitter" class="social-icon" aria-label="Twitter">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
              </svg>
            </a>
            <a href="#github" class="social-icon" aria-label="GitHub">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clip-rule="evenodd"
                />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "./stores/auth";
import AuthModal from "./components/AuthModal.vue";

const authStore = useAuthStore();

const locale = ref<"en" | "ko" | "ja">("en");
const showLanguageMenu = ref(false);
const showProfileMenu = ref(false);
const showAuthModal = ref(false);
const authModalMode = ref<"login" | "register">("login");
const isUpgrading = ref(false);

const languages = [
  { value: "en", label: "EN", flagCode: "gb" },
  { value: "ko", label: "KO", flagCode: "kr" },
  { value: "ja", label: "JA", flagCode: "jp" },
];

const currentLanguage = computed(() => {
  return languages.find((l) => l.value === locale.value) || languages[0];
});

const selectLanguage = (value: "en" | "ko" | "ja") => {
  locale.value = value;
  showLanguageMenu.value = false;
};

// 인증 모달 관련
const openLoginModal = () => {
  authModalMode.value = "login";
  showAuthModal.value = true;
};

const openRegisterModal = () => {
  authModalMode.value = "register";
  showAuthModal.value = true;
};

const closeAuthModal = () => {
  showAuthModal.value = false;
};

// 로그아웃
const handleLogout = () => {
  authStore.logout();
  showProfileMenu.value = false;
};

// Seller로 업그레이드
const handleUpgradeToSeller = async () => {
  if (isUpgrading.value) return;
  
  isUpgrading.value = true;
  try {
    const result = await authStore.upgradeToSeller();
    if (result.success) {
      // 성공 메시지 (선택사항)
      console.log("Successfully upgraded to seller!");
    } else {
      alert(result.error || "Failed to upgrade to seller");
    }
  } catch (error) {
    console.error("Upgrade error:", error);
    alert("An error occurred while upgrading");
  } finally {
    isUpgrading.value = false;
  }
};

// 크레딧 포맷팅
const formatCredit = (amount: number): string => {
  return new Intl.NumberFormat("en-US").format(amount);
};

// 외부 클릭 시 드롭다운 닫기
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest(".language-wrapper")) {
    showLanguageMenu.value = false;
  }
  if (!target.closest(".profile-wrapper")) {
    showProfileMenu.value = false;
  }
};

// 컴포넌트 마운트 시 이벤트 리스너 추가 및 인증 초기화
import { onUnmounted } from "vue";
onMounted(async () => {
  document.addEventListener("click", handleClickOutside);
  // 저장된 토큰이 있으면 사용자 정보 가져오기
  await authStore.initialize();
});
onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #f3f4f6;
}

.header-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (min-width: 1024px) {
  .header-container {
    padding: 0 4rem;
  }
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
}

.logo-wrapper {
  flex-shrink: 0;
}

.logo-link {
  text-decoration: none;
  display: inline-block;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #111827;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo-link:hover .logo {
  opacity: 0.8;
}

.center-nav {
  display: none;
  align-items: center;
  gap: 2rem;
}

@media (min-width: 768px) {
  .center-nav {
    display: flex;
  }
}

.nav-link {
  text-decoration: none;
  color: #4b5563;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #111827;
}

.nav-link.router-link-active {
  color: #111827;
}

.right-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Language Switcher */
.language-wrapper {
  position: relative;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: none;
  background: transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: background-color 0.2s;
}

.flag-icon {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 2px;
  flex-shrink: 0;
}

.language-btn:hover {
  background: #f9fafb;
  color: #111827;
}

.chevron-icon {
  width: 1rem;
  height: 1rem;
}

.language-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  width: 8rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  padding: 0.5rem 0;
  overflow: hidden;
}

.language-option {
  width: 100%;
  padding: 0.5rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  color: #374151;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-option:hover {
  background: #f9fafb;
}

/* Auth Buttons */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-login {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-login:hover {
  color: #111827;
}

.btn-signup {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-signup:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Seller Upgrade Button */
.upgrade-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3), 0 2px 4px -1px rgba(102, 126, 234, 0.2);
}

.upgrade-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.upgrade-btn:hover::before {
  left: 100%;
}

.upgrade-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4), 0 4px 6px -2px rgba(102, 126, 234, 0.3);
}

.upgrade-btn:active {
  transform: translateY(0);
}

.upgrade-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.upgrade-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1);
  }
}

.upgrade-arrow {
  width: 0.875rem;
  height: 0.875rem;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.upgrade-btn:hover .upgrade-arrow {
  transform: translateX(4px);
}

.upgrade-btn:disabled .upgrade-arrow {
  display: none;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .upgrade-btn {
    padding: 0.625rem;
    font-size: 0.8125rem;
    border-radius: 0.5rem;
  }

  .upgrade-btn span {
    display: none;
  }

  .upgrade-icon {
    width: 1.125rem;
    height: 1.125rem;
  }
}

.credit-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.coin-icon {
  width: 1rem;
  height: 1rem;
  color: #4f46e5;
}

.credit-badge span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

.profile-wrapper {
  position: relative;
}

.profile-btn {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: linear-gradient(to bottom right, #6366f1, #9333ea);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.profile-btn:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.user-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  width: 12rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  padding: 0.5rem 0;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  text-decoration: none;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background: #f9fafb;
}

.dropdown-divider {
  border-top: 1px solid #f3f4f6;
  margin: 0.5rem 0;
}

.app-main {
  flex: 1;
  padding: 0;
  width: 100%;
  margin-top: 80px;
}

/* Footer */
.app-footer {
  border-top: 1px solid #e5e7eb;
  background: white;
}

.footer-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

@media (min-width: 1024px) {
  .footer-container {
    padding: 4rem 4rem;
  }
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

@media (min-width: 768px) {
  .footer-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .footer-grid {
    gap: 3rem;
  }
}

.footer-brand {
  grid-column: span 2;
}

@media (min-width: 768px) {
  .footer-brand {
    grid-column: span 1;
  }
}

.footer-brand-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.footer-brand-description {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.625;
}

.footer-column-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 1rem;
}

.footer-links-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-link {
  font-size: 0.875rem;
  color: #4b5563;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #111827;
}

.footer-bottom {
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

@media (min-width: 640px) {
  .footer-bottom {
    flex-direction: row;
  }
}

.footer-copyright {
  font-size: 0.875rem;
  color: #4b5563;
}

.footer-social {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.social-icon {
  color: #9ca3af;
  transition: color 0.2s;
}

.social-icon:hover {
  color: #4b5563;
}

.social-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}
</style>
