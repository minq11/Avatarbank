<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-content">
          <!-- Badge -->
          <div class="hero-badge">
            <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0L9.937 15.5Z"/>
            </svg>
            <span>크리에이터를 위한 AI 아바타 스튜디오</span>
          </div>

          <!-- Headline -->
          <h1 class="hero-title">
            내 아바타로,<br />
            팬들을 위한 사진을 만드세요
          </h1>

          <!-- Subheadline -->
          <p class="hero-subtitle">
            사진 몇 장으로 나만의 AI 아바타를 등록하고,
            팬에게 나눠줄 일회용 생성 링크를 발급하세요.
            사용 현황은 실시간으로 확인할 수 있어요.
          </p>

          <!-- CTAs -->
          <div class="hero-actions">
            <RouterLink to="/my/avatars" class="btn-primary-hero">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
              </svg>
              내 아바타 등록하기
            </RouterLink>
            <a href="#how" class="btn-secondary-hero">
              작동 방식 보기
              <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how" class="how-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">이렇게 작동해요</h2>
          <p class="section-description">
            아바타 등록부터 팬에게 링크를 나눠주기까지, 네 단계면 충분해요
          </p>
        </div>

        <div class="steps-grid">
          <div v-for="(step, index) in steps" :key="index" class="step-card">
            <div class="step-number">{{ index + 1 }}</div>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-description">{{ step.description }}</p>
          </div>
        </div>

        <!-- 등록 심사 안내 -->
        <div class="review-notice">
          <svg class="review-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 12l2 2 4-4" />
            <circle cx="12" cy="12" r="10" />
          </svg>
          <p class="review-notice-text">
            아바타 등록은 관리자가 <strong>도용 여부를 확인</strong>한 뒤 진행되며,
            승인까지 <strong>영업일 기준 1~7일</strong>이 소요됩니다.
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const router = useRouter();

// 로그인 상태면 마케팅 랜딩 대신 바로 크리에이터 스튜디오로 보낸다.
function redirectIfLoggedIn() {
  if (authStore.isInitialized && authStore.isLoggedIn) {
    router.replace("/studio");
  }
}
onMounted(redirectIfLoggedIn);
watch(() => authStore.isInitialized, redirectIfLoggedIn);

const steps = [
  {
    title: "아바타 등록",
    description: "정면·측면·전신 사진을 올리면 나만의 아바타를 만들어요. 관리자가 도용 여부를 확인한 뒤 승인돼요.",
  },
  {
    title: "일회용 링크 발급",
    description: "아바타로 사진을 생성할 수 있는 일회용 링크를 원하는 만큼 만들어요.",
  },
  {
    title: "팬에게 공유",
    description: "링크를 팬에게 보내면, 팬은 그 링크로 바로 사진을 생성할 수 있어요.",
  },
  {
    title: "실시간 현황 확인",
    description: "사용된 링크와 아직 남은 링크를 내 페이지에서 한눈에 확인해요.",
  },
];
</script>

<style scoped>
.landing-page {
  width: 100%;
}

/* Hero Section */
.hero-section {
  padding: 8rem 0 6rem;
  background: white;
}

.hero-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (min-width: 1024px) {
  .hero-container {
    padding: 0 4rem;
  }
}

@media (min-width: 768px) {
  .hero-section {
    padding: 8rem 0 6rem;
  }
}

.hero-content {
  max-width: 56rem;
  margin: 0 auto;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #eef2ff;
  border-radius: 9999px;
  margin-bottom: 2rem;
}

.badge-icon {
  width: 1rem;
  height: 1rem;
  color: #4f46e5;
  flex-shrink: 0;
}

.hero-badge span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4f46e5;
}

.hero-title {
  font-size: 3rem;
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #4b5563;
  margin-bottom: 3rem;
  max-width: 36rem;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.625;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.btn-primary-hero {
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(to right, #9333ea, #4f46e5);
  border-radius: 0.75rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
}

.btn-primary-hero:hover {
  box-shadow: 0 20px 25px -5px rgba(147, 51, 234, 0.3);
}

.btn-secondary-hero {
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-secondary-hero:hover {
  border-color: #d1d5db;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.arrow-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.2s;
}

.btn-secondary-hero:hover .arrow-icon {
  transform: translateX(0.25rem);
}

/* Section shared */
.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (min-width: 1024px) {
  .container {
    padding: 0 4rem;
  }
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 1.875rem;
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1rem;
}

.section-description {
  font-size: 1.125rem;
  color: #4b5563;
  max-width: 36rem;
  margin: 0 auto;
}

/* How It Works Section */
.how-section {
  padding: 6rem 0;
  background: #f9fafb;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.5rem;
}

.step-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2rem;
  transition: box-shadow 0.2s, transform 0.2s;
}

.step-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.step-number {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: linear-gradient(to bottom right, #6366f1, #9333ea);
  color: white;
  font-weight: 700;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.step-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.step-description {
  font-size: 0.9375rem;
  color: #4b5563;
  line-height: 1.6;
}

.review-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
  padding: 1rem 1.25rem;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 0.75rem;
}

.review-notice-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #4f46e5;
  flex-shrink: 0;
}

.review-notice-text {
  font-size: 0.9375rem;
  color: #3730a3;
  line-height: 1.6;
}

.review-notice-text strong {
  font-weight: 600;
}

/* Link Dashboard Preview Section */
.links-section {
  padding: 6rem 0;
  background: white;
}

.links-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 4rem;
  align-items: center;
}

@media (min-width: 1024px) {
  .links-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.links-title {
  font-size: 2.25rem;
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1.5rem;
}

.links-description {
  font-size: 1.125rem;
  color: #4b5563;
  line-height: 1.625;
  margin-bottom: 2rem;
}

.links-visual {
  position: relative;
}

.link-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.link-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  background: #f9fafb;
}

.link-panel-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.link-panel-count {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.link-list {
  display: flex;
  flex-direction: column;
}

.link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.link-item:last-child {
  border-bottom: none;
}

.link-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.link-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #111827;
}

.link-meta {
  font-size: 0.8125rem;
  color: #9ca3af;
}

.link-status {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-used {
  background: #f3f4f6;
  color: #6b7280;
}

.status-unused {
  background: #d1fae5;
  color: #065f46;
}

/* Gallery Section */
.gallery-section {
  padding: 6rem 0;
  background: #f9fafb;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.5rem;
}

.gallery-card {
  position: relative;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  border-radius: 1rem;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.gallery-card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.gallery-image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.gallery-image-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-weight: 600;
  transition: transform 0.5s;
}

.gallery-card:hover .gallery-image-placeholder {
  transform: scale(1.05);
}

.gallery-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
  opacity: 0;
  transition: opacity 0.2s;
}

.gallery-card:hover .gallery-overlay {
  opacity: 1;
}

.instagram-badge {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.gallery-card:hover .instagram-badge {
  opacity: 1;
}

.instagram-badge:hover {
  background: white;
}

.instagram-icon {
  width: 1rem;
  height: 1rem;
  object-fit: contain;
}

.instagram-badge span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

.view-more {
  text-align: center;
  margin-top: 3rem;
}

.btn-view-all {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-view-all:hover {
  border-color: #d1d5db;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Final CTA Section */
.cta-section {
  padding: 6rem 0;
  background: white;
}

.cta-card {
  background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
  border-radius: 1.5rem;
  padding: 4rem 2rem;
  text-align: center;
}

.cta-title {
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: white;
  margin-bottom: 1rem;
}

.cta-description {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.85);
  max-width: 32rem;
  margin: 0 auto 2rem;
  line-height: 1.625;
}

.btn-cta {
  background: white;
  color: #4f46e5;
}

.btn-cta:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
}

/* Responsive */
@media (min-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-actions {
    flex-direction: row;
    justify-content: center;
  }
}

@media (min-width: 1024px) {
  .hero-title {
    font-size: 3.75rem;
  }

  .section-title {
    font-size: 2.25rem;
  }

  .gallery-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .steps-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .links-title {
    font-size: 3rem;
  }

  .cta-title {
    font-size: 2.5rem;
  }
}
</style>
