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
            내 얼굴로,<br />
            무엇이든 자유롭게 만드세요
          </h1>

          <!-- Subheadline -->
          <p class="hero-subtitle">
            사진 몇 장으로 나만의 AI 아바타를 등록하면,
            원하는 장면을 프롬프트로 자유롭게 생성할 수 있어요.
            원할 땐 팬에게 리딤 코드를 나눠줘 함께 만들 수도 있습니다.
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

          <!--
            서비스 흐름 일러스트: 사진 → 내 AI 아바타 → (위) 직접 생성 / (아래) 팬에게 코드 공유.
            텍스트 없이 그림만으로 표현 — 모바일에서 축소돼도 글자가 뭉개지지 않게 하기 위함.
          -->
          <div class="hero-illustration">
            <svg viewBox="0 0 740 250" fill="none" xmlns="http://www.w3.org/2000/svg" role="img">
              <title>
                사진 몇 장으로 내 AI 아바타를 만들고, 직접 생성하거나 팬에게 리딤 코드를 나눠주는 흐름
              </title>
              <defs>
                <linearGradient id="ab-grad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#9333ea" />
                  <stop offset="100%" stop-color="#4f46e5" />
                </linearGradient>
                <linearGradient id="ab-soft" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#faf5ff" />
                  <stop offset="100%" stop-color="#eef2ff" />
                </linearGradient>
                <marker
                  id="ab-arrow"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M0 1L9 5L0 9z" fill="#c4b5fd" />
                </marker>
                <clipPath id="ab-frame">
                  <rect x="496" y="26" width="68" height="80" rx="10" />
                </clipPath>
              </defs>

              <!-- 1. 올린 사진 몇 장 -->
              <g>
                <rect
                  x="46" y="70" width="90" height="110" rx="12"
                  fill="#ede9fe" transform="rotate(-10 91 125)"
                />
                <rect
                  x="50" y="70" width="90" height="110" rx="12"
                  fill="#faf5ff" stroke="#ddd6fe" stroke-width="1.5"
                  transform="rotate(-5 95 125)"
                />
                <rect
                  x="54" y="70" width="90" height="110" rx="12"
                  fill="#ffffff" stroke="#e5e7eb" stroke-width="1.5"
                />
                <circle cx="99" cy="112" r="16" fill="#c7d2fe" />
                <path d="M75 160c0-13 11-24 24-24s24 11 24 24z" fill="#c7d2fe" />
              </g>

              <path
                d="M164 125h40" stroke="#c4b5fd" stroke-width="2.5"
                stroke-linecap="round" marker-end="url(#ab-arrow)"
              />

              <!-- 2. 학습된 내 AI 아바타 -->
              <g>
                <rect
                  x="228" y="60" width="104" height="130" rx="18"
                  fill="url(#ab-soft)" stroke="url(#ab-grad)" stroke-width="2.5"
                />
                <circle cx="280" cy="116" r="21" fill="url(#ab-grad)" />
                <path d="M248 172c0-17.7 14.3-32 32-32s32 14.3 32 32z" fill="url(#ab-grad)" />
                <circle cx="330" cy="66" r="16" fill="#ffffff" />
                <circle cx="330" cy="66" r="13" fill="url(#ab-grad)" />
                <path
                  d="M330 58c1 5 2 6 7 7-5 1-6 2-7 7-1-5-2-6-7-7 5-1 6-2 7-7z"
                  fill="#ffffff"
                />
              </g>

              <!-- 갈래: 위 = 직접 생성, 아래 = 팬에게 코드 -->
              <path
                d="M344 104c30-10 52-22 84-26" stroke="#c4b5fd" stroke-width="2.5"
                stroke-linecap="round" marker-end="url(#ab-arrow)"
              />
              <path
                d="M344 150c30 12 52 24 84 28" stroke="#c4b5fd" stroke-width="2.5"
                stroke-linecap="round" marker-end="url(#ab-arrow)"
              />

              <!-- 3a. 내가 자유롭게 만든 사진들 -->
              <g>
                <rect
                  x="452" y="30" width="68" height="80" rx="10"
                  fill="#faf5ff" stroke="#ddd6fe" stroke-width="1.5"
                  transform="rotate(-6 486 70)"
                />
                <g clip-path="url(#ab-frame)">
                  <rect x="496" y="26" width="68" height="80" fill="#ffffff" />
                  <circle cx="545" cy="50" r="8" fill="#fde68a" />
                  <path d="M494 106l18-26 13 17 11-13 30 22z" fill="#c7d2fe" />
                </g>
                <rect
                  x="496" y="26" width="68" height="80" rx="10"
                  fill="none" stroke="#e5e7eb" stroke-width="1.5"
                />
                <path
                  d="M588 44c1 5 2 6 7 7-5 1-6 2-7 7-1-5-2-6-7-7 5-1 6-2 7-7z"
                  fill="#ddd6fe"
                />
                <path
                  d="M602 68c.7 3.4 1.4 4.1 4.8 4.8-3.4.7-4.1 1.4-4.8 4.8-.7-3.4-1.4-4.1-4.8-4.8 3.4-.7 4.1-1.4 4.8-4.8z"
                  fill="#ede9fe"
                />
              </g>

              <!-- 3b. 팬에게 나눠주는 리딤 코드 -->
              <g>
                <rect
                  x="452" y="150" width="116" height="72" rx="12"
                  fill="#ffffff" stroke="#e5e7eb" stroke-width="1.5"
                />
                <rect x="464" y="162" width="14" height="14" rx="3" fill="#4f46e5" />
                <rect x="482" y="162" width="14" height="14" rx="3" fill="#c7d2fe" />
                <rect x="464" y="180" width="14" height="14" rx="3" fill="#c7d2fe" />
                <rect x="482" y="180" width="14" height="14" rx="3" fill="#4f46e5" />
                <rect x="464" y="198" width="32" height="10" rx="5" fill="#ede9fe" />
                <path d="M508 158v56" stroke="#e5e7eb" stroke-width="1.5" stroke-dasharray="4 5" />
                <rect x="518" y="166" width="38" height="8" rx="4" fill="#ddd6fe" />
                <rect x="518" y="182" width="30" height="8" rx="4" fill="#ede9fe" />
                <rect x="518" y="198" width="34" height="8" rx="4" fill="#ede9fe" />
              </g>

              <path
                d="M580 186h20" stroke="#c4b5fd" stroke-width="2.5"
                stroke-linecap="round" marker-end="url(#ab-arrow)"
              />

              <!-- 팬들 -->
              <g>
                <circle cx="626" cy="186" r="17" fill="#eef2ff" stroke="#c7d2fe" stroke-width="1.5" />
                <circle cx="626" cy="181" r="5.5" fill="#818cf8" />
                <path d="M617 197c0-5 4-9 9-9s9 4 9 9z" fill="#818cf8" />

                <circle cx="666" cy="164" r="14" fill="#f5f3ff" stroke="#ddd6fe" stroke-width="1.5" />
                <circle cx="666" cy="160" r="4.5" fill="#a5b4fc" />
                <path d="M659 173c0-4 3-7 7-7s7 3 7 7z" fill="#a5b4fc" />

                <circle cx="672" cy="206" r="12" fill="#f5f3ff" stroke="#ddd6fe" stroke-width="1.5" />
                <circle cx="672" cy="203" r="4" fill="#a5b4fc" />
                <path d="M666 214c0-3.3 2.7-6 6-6s6 2.7 6 6z" fill="#a5b4fc" />
              </g>
            </svg>
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
            아바타 등록부터 자유 생성, 그리고 팬 공유까지 — 네 단계면 충분해요
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
    title: "자유롭게 직접 생성",
    description: "내 아바타로 원하는 장면·의상·분위기를 프롬프트로 자유롭게 만들어요. 완전히 내 마음대로.",
  },
  {
    title: "팬에게 코드 공유 (선택)",
    description: "원하면 리딤 코드를 발급해 팬에게 나눠주세요. 팬은 원하는 장면을 직접 묘사해 함께 만들 수 있어요.",
  },
  {
    title: "실시간 현황 확인",
    description: "내 생성물과 발급한 코드의 사용 현황을 스튜디오에서 한눈에 확인해요.",
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

/* 서비스 흐름 일러스트 */
.hero-illustration {
  max-width: 46rem;
  margin: 4rem auto 0;
}

.hero-illustration svg {
  display: block;
  width: 100%;
  height: auto;
}

@media (max-width: 640px) {
  .hero-illustration {
    margin-top: 2.5rem;
  }
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
