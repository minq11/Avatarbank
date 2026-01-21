<template>
  <div class="app">
    <header class="app-header">
      <div class="left">
        <span class="logo">Avatarbank</span>
      </div>
      <nav class="center">
        <RouterLink to="/market" class="nav-link">마켓</RouterLink>
        <RouterLink to="/gallery" class="nav-link">갤러리</RouterLink>
        <select v-model="locale" class="locale-select">
          <option value="en">EN</option>
          <option value="ko">KO</option>
          <option value="ja">JA</option>
        </select>
      </nav>
      <div class="right">
        <!-- TODO: 로그인 상태에 따라 분기 -->
        <button class="btn secondary">로그인</button>
        <button class="btn primary">회원가입</button>
      </div>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <span>© Avatarbank</span>
      <div class="footer-links">
        <a href="#">이용약관</a>
        <a href="#">개인정보처리방침</a>
        <a href="#">인플루언서 안내</a>
        <a href="#">문의</a>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink, RouterView } from "vue-router";

const locale = ref<"en" | "ko" | "ja">("en");
// TODO: 실제 i18n 연동 및 사용자 locale 저장 연동
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.logo {
  font-weight: 700;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.center {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-size: 0.95rem;
  white-space: nowrap;
}

.nav-link.router-link-active {
  font-weight: 600;
}

.locale-select {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.locale-select:hover {
  border-color: #667eea;
}

.right {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.primary {
  background: #111827;
  color: white;
}

.btn.primary:hover {
  background: #1f2937;
}

.btn.secondary {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn.secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.app-main {
  flex: 1;
  padding: 0;
  width: 100%;
}

.app-footer {
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #eee;
  font-size: 0.8rem;
  display: flex;
  justify-content: space-between;
  color: #6b7280;
}

.footer-links {
  display: flex;
  gap: 0.75rem;
}

.footer-links a {
  color: inherit;
  text-decoration: none;
}
</style>


