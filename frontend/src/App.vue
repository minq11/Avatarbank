<template>
  <div class="app">
    <header class="app-header">
      <div class="header-container">
        <div class="header-content">
          <!-- Logo -->
          <div class="logo-wrapper">
            <RouterLink to="/" class="logo-link">
              <img :src="logoCart" alt="AvatarClub" class="logo-img" />
              <h1 class="logo">AvatarClub</h1>
            </RouterLink>
          </div>

          <!-- Center Navigation -->
          <nav class="center-nav">
            <RouterLink to="/studio" class="nav-link">크리에이터 스튜디오</RouterLink>
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
              <button @click="openLoginModal" class="btn-login">로그인</button>
              <button @click="openRegisterModal" class="btn-signup">회원가입</button>
            </div>

            <!-- User Info (when logged in) -->
            <div v-else-if="authStore.isInitialized" class="user-info">
              <div v-if="authStore.user?.nickname" class="user-badge">
                <span class="nickname-label">{{ authStore.user.nickname }}</span>
                <span class="badge-separator">|</span>
                <img :src="diamondIcon" alt="Credit" class="diamond-icon" />
                <span class="credit-amount">{{ formatCredit(authStore.creditBalance) }} C</span>
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
                    to="/studio"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    크리에이터 스튜디오
                  </RouterLink>
                  <RouterLink
                    to="/my/avatars"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    내 아바타
                  </RouterLink>
                  <RouterLink
                    to="/my/generations"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    내 생성물
                  </RouterLink>
                  <RouterLink
                    v-if="authStore.isAdmin"
                    to="/admin/training-requests"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    관리자 · 학습 요청
                  </RouterLink>
                  <RouterLink
                    v-if="authStore.isAdmin"
                    to="/admin/inquiries"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    관리자 · 문의함
                  </RouterLink>
                  <RouterLink
                    to="/my/page"
                    class="dropdown-item"
                    @click="showProfileMenu = false"
                  >
                    계정 관리
                  </RouterLink>
                  <div class="dropdown-divider"></div>
                  <a href="#" @click.prevent="handleLogout" class="dropdown-item">로그아웃</a>
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

    <!-- Auth Modal (전역 — 상태는 auth 스토어가 들고, 어느 페이지든 openAuthModal 로 띄운다) -->
    <AuthModal
      :is-open="authStore.authModalOpen"
      :initial-mode="authStore.authModalMode"
      @close="authStore.closeAuthModal"
      @success="onAuthSuccess"
    />

    <footer class="app-footer">
      <div class="footer-container">
        <div class="footer-grid">
          <!-- Brand -->
          <div class="footer-brand">
            <h4 class="footer-brand-title">AvatarClub</h4>
            <p class="footer-brand-description">
              내 얼굴로 만드는 AI 아바타 스튜디오. 크리에이터가 직접 생성하고,
              원할 땐 팬에게 리딤 링크를 나눠 함께 만듭니다.
            </p>
          </div>

          <!-- 서비스 -->
          <div class="footer-column">
            <h5 class="footer-column-title">서비스</h5>
            <ul class="footer-links-list">
              <li><RouterLink to="/studio" class="footer-link">크리에이터 스튜디오</RouterLink></li>
              <li><RouterLink to="/my/avatars" class="footer-link">내 아바타</RouterLink></li>
              <li><RouterLink to="/guide" class="footer-link">크리에이터 가이드</RouterLink></li>
            </ul>
          </div>

          <!-- 정책 -->
          <div class="footer-column">
            <h5 class="footer-column-title">정책</h5>
            <ul class="footer-links-list">
              <li><RouterLink to="/terms" class="footer-link">이용약관</RouterLink></li>
              <li>
                <RouterLink to="/privacy" class="footer-link">
                  <strong>개인정보처리방침</strong>
                </RouterLink>
              </li>
              <li><RouterLink to="/content-policy" class="footer-link">콘텐츠·초상권 정책</RouterLink></li>
            </ul>
          </div>

          <!-- 지원 -->
          <div class="footer-column">
            <h5 class="footer-column-title">지원</h5>
            <ul class="footer-links-list">
              <li><RouterLink to="/support" class="footer-link">문의하기</RouterLink></li>
              <li>
                <RouterLink to="/support#report" class="footer-link">도용·권리침해 신고</RouterLink>
              </li>
              <li>
                <a
                  href="https://www.instagram.com/avatarclub_official/"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="footer-link"
                >
                  인스타그램
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Bottom Bar -->
        <div class="footer-bottom">
          <div class="footer-legal-bottom">
            <p class="footer-copyright">© {{ currentYear }} AvatarClub. All rights reserved.</p>
            <p class="footer-note">
              AvatarClub은 전 연령 이용 가능한(SFW) 이미지만 생성합니다.
              타인의 얼굴을 무단으로 등록하는 행위는 금지되며, 적발 시 계정이 정지됩니다.
            </p>
          </div>
          <div class="footer-social">
            <a
              href="https://www.instagram.com/avatarclub_official/"
              target="_blank"
              rel="noopener noreferrer"
              class="social-icon"
              aria-label="AvatarClub 인스타그램"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="20" rx="5" />
                <circle cx="12" cy="12" r="4" />
                <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
              </svg>
            </a>
            <RouterLink to="/support" class="social-icon" aria-label="문의하기">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="m22 7-10 6L2 7" />
              </svg>
            </RouterLink>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";
import AuthModal from "./components/AuthModal.vue";
import diamondIcon from "./assets/icons/diamond_credit_icon.svg";
import logoCart from "./assets/icons/logo3D.png";

const authStore = useAuthStore();

// 푸터 저작권 표기 (연도 하드코딩 방지)
const currentYear = new Date().getFullYear();

const router = useRouter();

const locale = ref<"en" | "ko" | "ja">("en");
const showLanguageMenu = ref(false);
const showProfileMenu = ref(false);

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

// Auth modal related (상태는 스토어)
const openLoginModal = () => authStore.openAuthModal("login");
const openRegisterModal = () => authStore.openAuthModal("register");

// 로그인/가입 성공: 예약된 리다이렉트가 있으면 이동 (홈 CTA → 가입 → 생성 페이지)
const onAuthSuccess = () => {
  const redirect = authStore.consumePostAuthRedirect();
  if (redirect) router.push(redirect);
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
  border-bottom: 1px solid #f2f2f4;
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
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-img {
  height: 1.5rem;
  width: auto;
  display: block;
  flex-shrink: 0;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #e24e12;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo-link:hover .logo,
.logo-link:hover .logo-img {
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
  color: #52525b;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #0d0d0f;
}

.nav-link.router-link-active {
  color: #0d0d0f;
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
  color: #3a3a42;
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
  background: #fafafa;
  color: #0d0d0f;
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
  border: 1px solid #f2f2f4;
  padding: 0.5rem 0;
  overflow: hidden;
}

.language-option {
  width: 100%;
  padding: 0.5rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  color: #3a3a42;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-option:hover {
  background: #fafafa;
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
  color: #3a3a42;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-login:hover {
  color: #0d0d0f;
}

.btn-signup {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #e24e12, #e85f26);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-signup:hover {
  box-shadow: 0 10px 15px -3px rgba(226, 78, 18, 0.3);
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
  border: 1px solid #e6e6ea;
  box-shadow: 0 20px 35px -15px rgba(15, 23, 42, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f2f2f4;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0d0d0f;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #6e6e77;
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
  color: #3a3a42;
}

.modal-step {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.modal-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #0d0d0f;
}

.modal-box {
  background: #fafafa;
  border: 1px solid #e6e6ea;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #0d0d0f;
}

.modal-note {
  font-size: 0.85rem;
  color: #6e6e77;
}

.modal-list {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.85rem;
  color: #6e6e77;
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
  border: 1px solid #e6e6ea;
  border-radius: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0d0d0f;
  background: #ffffff;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  gap: 0.5rem;
}

.modal-secondary:hover {
  background: #fafafa;
  border-color: #d2d2d9;
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
  background: #e24e12;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.modal-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -10px rgba(226, 78, 18, 0.6);
}

/* Mobile Responsive */

.credit-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fafafa;
  border-radius: 0.5rem;
}

.diamond-icon {
  width: 1rem;
  height: 1rem;
  color: #e24e12;
}

.credit-badge span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0d0d0f;
}

.user-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: #f2f2f4;
  color: #0d0d0f;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.nickname-label {
  color: inherit;
}

.badge-separator {
  color: #9a9aa3;
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
  background: linear-gradient(to bottom right, #e85f26, #f2703a);
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
  border: 1px solid #f2f2f4;
  padding: 0.5rem 0;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #3a3a42;
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
  background: #fafafa;
}

.dropdown-divider {
  border-top: 1px solid #f2f2f4;
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
  border-top: 1px solid #e6e6ea;
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
  color: #0d0d0f;
  margin-bottom: 1rem;
}

.footer-brand-description {
  font-size: 0.875rem;
  color: #52525b;
  line-height: 1.625;
}

.footer-column-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0d0d0f;
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
  color: #52525b;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #0d0d0f;
}

.footer-bottom {
  padding-top: 2rem;
  border-top: 1px solid #e6e6ea;
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

.footer-legal-bottom {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.footer-copyright {
  font-size: 0.875rem;
  color: #52525b;
}

.footer-note {
  font-size: 0.78rem;
  color: #9a9aa3;
  max-width: 640px;
  line-height: 1.5;
}

.footer-social {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.social-icon {
  color: #9a9aa3;
  transition: color 0.2s;
}

.social-icon:hover {
  color: #52525b;
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
