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
        </div>
      </div>
    </section>

    <!-- Showcase: 실제 학습 사진 → AI 결과 -->
    <section class="showcase-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">평소 찍은 사진이 이렇게 바뀝니다</h2>
          <p class="section-description">
            일상 사진 몇 장으로 아바타를 학습시키면, 직접 찍지 않은 장면도 내 얼굴로 만들어져요
          </p>
        </div>

        <div class="showcase-grid">
          <figure class="showcase-item">
            <div class="showcase-frame">
              <img
                :src="sourcePicturesImg"
                alt="아바타 학습에 사용한 일상 사진 아홉 장"
                loading="lazy"
                width="784"
                height="1168"
              />
            </div>
            <figcaption>
              <span class="showcase-tag">1 · 올린 사진</span>
              <p>셀카·전신·야외 등 각도와 조명이 다양할수록 학습이 잘 돼요.</p>
            </figcaption>
          </figure>

          <!-- 학습 중인 AI 모델을 홀로그램 오브로 표현 (장식) -->
          <div class="showcase-forge" aria-hidden="true">
            <svg class="forge-svg" viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <radialGradient id="fg-halo" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.38" />
                  <stop offset="55%" stop-color="#818cf8" stop-opacity="0.14" />
                  <stop offset="100%" stop-color="#818cf8" stop-opacity="0" />
                </radialGradient>
                <radialGradient id="fg-core" cx="38%" cy="32%" r="72%">
                  <stop offset="0%" stop-color="#ffffff" />
                  <stop offset="45%" stop-color="#c4b5fd" />
                  <stop offset="100%" stop-color="#6d28d9" />
                </radialGradient>
                <linearGradient id="fg-ring" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#9333ea" stop-opacity="0.15" />
                  <stop offset="50%" stop-color="#818cf8" stop-opacity="0.95" />
                  <stop offset="100%" stop-color="#9333ea" stop-opacity="0.15" />
                </linearGradient>
              </defs>

              <!-- 왼쪽 사진에서 흘러들어와 오른쪽 결과로 빠져나가는 흐름 -->
              <path
                class="forge-flow"
                d="M0 80h160"
                stroke="#c4b5fd"
                stroke-width="2"
                stroke-linecap="round"
                stroke-dasharray="5 11"
              />

              <circle cx="80" cy="80" r="72" fill="url(#fg-halo)" />

              <!-- 궤도 링 3개, 각기 다른 속도·방향 -->
              <ellipse class="forge-ring ring-a" cx="80" cy="80" rx="56" ry="21"
                       stroke="url(#fg-ring)" stroke-width="1.6" />
              <ellipse class="forge-ring ring-b" cx="80" cy="80" rx="56" ry="21"
                       stroke="url(#fg-ring)" stroke-width="1.6" />
              <ellipse class="forge-ring ring-c" cx="80" cy="80" rx="56" ry="21"
                       stroke="url(#fg-ring)" stroke-width="1.6" />

              <!-- 코어로 모여드는 입자들 -->
              <g class="forge-motes" fill="#a5b4fc">
                <circle class="mote m1" cx="30" cy="58" r="2.4" />
                <circle class="mote m2" cx="128" cy="62" r="2" />
                <circle class="mote m3" cx="42" cy="112" r="1.8" />
                <circle class="mote m4" cx="120" cy="108" r="2.6" />
                <circle class="mote m5" cx="80" cy="24" r="2" />
                <circle class="mote m6" cx="80" cy="136" r="2.2" />
              </g>

              <!-- 코어 -->
              <circle class="forge-core" cx="80" cy="80" r="17" fill="url(#fg-core)" />
              <circle class="forge-pulse" cx="80" cy="80" r="17" stroke="#a78bfa" stroke-width="1.5" />

              <!-- 홀로그램 스캔 라인 -->
              <g class="forge-scan" stroke="#ffffff" stroke-opacity="0.5" stroke-width="1">
                <path d="M66 74h28" />
                <path d="M64 80h32" />
                <path d="M67 86h26" />
              </g>
            </svg>
            <span class="forge-label">AI 아바타 학습</span>
          </div>

          <figure class="showcase-item">
            <div class="showcase-frame">
              <img
                :src="aiResultImg"
                alt="학습한 아바타로 생성한 결과 이미지"
                loading="lazy"
                width="784"
                height="1168"
              />
            </div>
            <figcaption>
              <span class="showcase-tag accent">2 · AI가 만든 결과</span>
              <p>
                촬영장, 의상, 조명까지 프롬프트로 지정한 장면.
                <strong>모든 생성물은 안전 필터를 거쳐요.</strong>
              </p>
            </figcaption>
          </figure>
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
            아바타 등록 및 학습은 관리자가 <strong>도용 여부를 확인</strong>한 뒤 진행되며,
            승인 및 학습까지 <strong>2~7일</strong>이 소요됩니다.
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
// 쇼케이스 이미지 — Vite 가 해시를 붙여 번들·캐싱한다.
import sourcePicturesImg from "@/assets/showcase/source_pictures.jpg";
import aiResultImg from "@/assets/showcase/ai_result.jpg";

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

/* Showcase: 학습 사진 → AI 결과 */
.showcase-section {
  padding: 6rem 0;
  background: white;
}

.showcase-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1.5rem;
  align-items: center;
  max-width: 62rem;
  margin: 0 auto;
}

.showcase-item {
  margin: 0;
  min-width: 0;
}

.showcase-frame {
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  box-shadow: 0 18px 40px -24px rgba(17, 24, 39, 0.45);
}

.showcase-frame img {
  display: block;
  width: 100%;
  height: auto;
}

.showcase-item figcaption {
  margin-top: 1rem;
}

.showcase-tag {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
  background: #f3f4f6;
  border-radius: 9999px;
  padding: 0.25rem 0.7rem;
  margin-bottom: 0.5rem;
}

.showcase-tag.accent {
  color: #6d28d9;
  background: #f5f3ff;
}

.showcase-item figcaption p {
  font-size: 0.9rem;
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
}

/* 학습 중인 AI 모델 (홀로그램 오브) */
.showcase-forge {
  align-self: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.forge-svg {
  width: 9.5rem;
  height: 9.5rem;
  overflow: visible;
}

.forge-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6d28d9;
  white-space: nowrap;
}

/* SVG 요소는 기본 transform-origin 이 뷰포트 기준이라 fill-box 로 바꿔야
   자기 중심을 축으로 회전한다. */
.forge-ring,
.forge-core,
.forge-pulse,
.mote {
  transform-box: fill-box;
  transform-origin: center;
}

.ring-a {
  animation: forge-orbit-a 13s linear infinite;
}
.ring-b {
  animation: forge-orbit-b 9s linear infinite reverse;
}
.ring-c {
  animation: forge-orbit-c 17s linear infinite;
}

@keyframes forge-orbit-a {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes forge-orbit-b {
  from { transform: rotate(60deg); }
  to   { transform: rotate(420deg); }
}
@keyframes forge-orbit-c {
  from { transform: rotate(120deg); }
  to   { transform: rotate(480deg); }
}

.forge-core {
  animation: forge-breathe 3.4s ease-in-out infinite;
}

@keyframes forge-breathe {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.08); }
}

/* 코어에서 퍼져나가는 파동 */
.forge-pulse {
  animation: forge-ripple 3.4s ease-out infinite;
}

@keyframes forge-ripple {
  0%   { transform: scale(1); opacity: 0.7; }
  70%  { transform: scale(2.1); opacity: 0; }
  100% { transform: scale(2.1); opacity: 0; }
}

/* 흐름선: 왼쪽 → 오른쪽으로 흘러간다 */
.forge-flow {
  animation: forge-stream 1.1s linear infinite;
}

@keyframes forge-stream {
  to { stroke-dashoffset: -16; }
}

.mote {
  animation: forge-mote 4.2s ease-in-out infinite;
}
.m2 { animation-delay: 0.7s; }
.m3 { animation-delay: 1.4s; }
.m4 { animation-delay: 2.1s; }
.m5 { animation-delay: 2.8s; }
.m6 { animation-delay: 3.5s; }

/* 입자가 코어 쪽으로 빨려들어가며 옅어진다 */
@keyframes forge-mote {
  0%      { transform: scale(1); opacity: 0; }
  25%     { opacity: 0.9; }
  100%    { transform: scale(0.2) translate(0, 0); opacity: 0; }
}

.forge-scan {
  animation: forge-scan-fade 2.6s ease-in-out infinite;
}

@keyframes forge-scan-fade {
  0%, 100% { opacity: 0.25; }
  50%      { opacity: 0.75; }
}

/* 모션 최소화 설정을 켠 사용자에게는 정지된 상태로 보여준다 */
@media (prefers-reduced-motion: reduce) {
  .forge-ring,
  .forge-core,
  .forge-pulse,
  .forge-flow,
  .mote,
  .forge-scan {
    animation: none;
  }
  .forge-pulse {
    opacity: 0.35;
  }
}

@media (max-width: 768px) {
  .showcase-section {
    padding: 4rem 0;
  }

  /* 좁은 화면에서는 위아래로 쌓고, 흐름도 아래 방향으로 돌린다 */
  .showcase-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  .showcase-forge {
    justify-self: center;
  }

  /* 오브 자체는 세우고 흐름선만 회전시켜 라벨이 뒤집히지 않게 한다 */
  .forge-flow {
    transform-box: fill-box;
    transform-origin: center;
    transform: rotate(90deg);
  }

  .forge-svg {
    width: 7.5rem;
    height: 7.5rem;
  }
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
