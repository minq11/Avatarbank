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
            <div v-if="authStore.isInitialized && !authStore.isLoggedIn" class="auth-buttons">
              <button @click="openLoginModal" class="btn-login">Login</button>
              <button @click="openRegisterModal" class="btn-signup">Sign up</button>
            </div>

            <!-- User Info (when logged in) -->
            <div v-else-if="authStore.isInitialized" class="user-info">
              <div v-if="authStore.user?.nickname" class="user-badge">
                <span class="nickname-label">{{ authStore.user.nickname }}</span>
                <span class="badge-separator">|</span>
                <img :src="diamondIcon" alt="Credit" class="diamond-icon" />
                <span class="credit-amount">{{ formatCredit(authStore.creditBalance) }}</span>
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
                  <RouterLink
                    to="/my/generations"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    My creations
                  </RouterLink>
                  <RouterLink
                    to="/my/avatars"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    My Avatars
                  </RouterLink>
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
import diamondIcon from "./assets/icons/diamond_credit_icon.svg";

const authStore = useAuthStore();

const locale = ref<"en" | "ko" | "ja">("en");
const showLanguageMenu = ref(false);
const showProfileMenu = ref(false);
const showAuthModal = ref(false);
const authModalMode = ref<"login" | "register">("login");

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

// Auth modal related
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

// Logout
const handleLogout = () => {
  authStore.logout();
  showProfileMenu.value = false;
};

// Credit formatting
const formatCredit = (amount: number): string => {
  return new Intl.NumberFormat("en-US").format(amount);
};

// Close dropdown on outside click
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest(".language-wrapper")) {
    showLanguageMenu.value = false;
  }
  if (!target.closest(".profile-wrapper")) {
    showProfileMenu.value = false;
  }
};

// Add event listeners and initialize auth on component mount
import { onUnmounted } from "vue";
onMounted(async () => {
  document.addEventListener("click", handleClickOutside);
  // Fetch user info if token exists
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
  color: #4f46e5;
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


.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 60;
}

.modal-card {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-lead {
  font-size: 0.95rem;
  color: #374151;
}

.modal-step {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.modal-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #111827;
}

.modal-box {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #111827;
}

.modal-note {
  font-size: 0.85rem;
  color: #6b7280;
}

.modal-list {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.85rem;
  color: #6b7280;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.modal-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.modal-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #111827;
  background: #ffffff;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  gap: 0.5rem;
}

.modal-secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.instagram-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.modal-primary {
  border: none;
  border-radius: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
  background: #4f46e5;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.modal-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -10px rgba(79, 70, 229, 0.6);
}

/* Mobile Responsive */

.credit-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.diamond-icon {
  width: 1rem;
  height: 1rem;
  color: #4f46e5;
}

.credit-badge span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

.user-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: #f3f4f6;
  color: #111827;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.nickname-label {
  color: inherit;
}

.badge-separator {
  color: #9ca3af;
}

.credit-amount {
  color: inherit;
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

.upgrade-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.upgrade-crown {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
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

@media (max-width: 768px) {
  .header-container {
    padding: 0 1rem;
  }

  .right-nav {
    gap: 0.5rem;
  }

  .user-info {
    gap: 0.5rem;
  }

  .user-badge {
    padding: 0.2rem 0.6rem;
    font-size: 0.8125rem;
  }

  .diamond-icon {
    width: 0.875rem;
    height: 0.875rem;
  }

  .profile-btn {
    width: 2.25rem;
    height: 2.25rem;
  }

  .language-btn {
    padding: 0.4rem 0.6rem;
    font-size: 0.8125rem;
  }
}
</style>
