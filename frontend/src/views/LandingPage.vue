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
            사진 몇 장이 아바타가 되고,<br class="wide-only" />
            무한한 콘텐츠가 된다.
          </h1>

        </div>
      </div>
    </section>

    <!-- Showcase: 실제 학습 사진 → AI 결과. 히어로 제목이 곧 이 섹션의 설명이라 별도 헤더 없음 -->
    <section class="showcase-section">
      <div class="container">
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
                  <stop offset="0%" stop-color="#f5a57f" stop-opacity="0.38" />
                  <stop offset="55%" stop-color="#f08a5d" stop-opacity="0.14" />
                  <stop offset="100%" stop-color="#f08a5d" stop-opacity="0" />
                </radialGradient>
                <radialGradient id="fg-core" cx="38%" cy="32%" r="72%">
                  <stop offset="0%" stop-color="#ffffff" />
                  <stop offset="45%" stop-color="#f9c4a8" />
                  <stop offset="100%" stop-color="#c24210" />
                </radialGradient>
                <linearGradient id="fg-ring" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#f2703a" stop-opacity="0.15" />
                  <stop offset="50%" stop-color="#f08a5d" stop-opacity="0.95" />
                  <stop offset="100%" stop-color="#f2703a" stop-opacity="0.15" />
                </linearGradient>
              </defs>

              <!-- 왼쪽 사진에서 흘러들어와 오른쪽 결과로 빠져나가는 흐름 -->
              <path
                class="forge-flow"
                d="M0 80h160"
                stroke="#f9c4a8"
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
              <g class="forge-motes" fill="#f7b394">
                <circle class="mote m1" cx="30" cy="58" r="2.4" />
                <circle class="mote m2" cx="128" cy="62" r="2" />
                <circle class="mote m3" cx="42" cy="112" r="1.8" />
                <circle class="mote m4" cx="120" cy="108" r="2.6" />
                <circle class="mote m5" cx="80" cy="24" r="2" />
                <circle class="mote m6" cx="80" cy="136" r="2.2" />
              </g>

              <!-- 코어 -->
              <circle class="forge-core" cx="80" cy="80" r="17" fill="url(#fg-core)" />
              <circle class="forge-pulse" cx="80" cy="80" r="17" stroke="#f5a57f" stroke-width="1.5" />

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

        <!-- 등록 심사 · 안전 정책 안내 -->
        <div class="notice-stack">
          <div class="review-notice">
            <svg class="review-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 12l2 2 4-4" />
              <circle cx="12" cy="12" r="10" />
            </svg>
            <p class="review-notice-text">
              학습을 요청하시면 관리자가 <strong>공식 인스타그램 DM</strong>으로 본인 확인을 진행해요.
              DM으로 <strong>본인임이 인증된 뒤에만</strong> 학습이 시작되며, 승인 및 학습까지
              <strong>2~7일</strong>이 소요됩니다.
            </p>
          </div>

          <div class="review-notice review-notice--safety">
            <svg class="review-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <p class="review-notice-text">
              <strong>음란물·범죄적 이미지는 등록도 생성도 허용하지 않아요.</strong>
              업로드한 사진과 생성 결과는 상시 검수되며, 위반 시 즉시 삭제되고 이용이 제한됩니다.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 고정형 CTA — 스크롤 위치와 무관하게 항상 화면 하단에 떠 있는 유일한 전환 지점 -->
    <div class="sticky-cta">
      <button type="button" class="btn-cta" @click="goCreateAvatar">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
        </svg>
        아바타 생성 요청하기
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
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

// 고정 CTA 가 푸터 마지막 줄을 가리지 않도록 문서 아래에 그만큼 자리를 비운다.
// 푸터는 App.vue 에 있어 scoped 스타일로는 닿지 않으므로 body 에 직접 준다.
const STICKY_CTA_CLEARANCE = "6.5rem";
onMounted(() => {
  document.body.style.paddingBottom = STICKY_CTA_CLEARANCE;
});
onUnmounted(() => {
  document.body.style.paddingBottom = "";
});

// 메인 CTA: 아바타 생성으로 유인.
// 로그인 상태면 바로 생성 페이지로, 아니면 회원가입 모달 → 성공 시 생성 페이지로 리다이렉트.
function goCreateAvatar() {
  if (authStore.isLoggedIn) {
    router.push("/my/avatars/new");
  } else {
    authStore.openAuthModal("register", "/my/avatars/new");
  }
}

const steps = [
  {
    title: "아바타 등록 · 본인 인증",
    description: "정면·측면·전신 사진을 올려 학습을 요청하면, 공식 인스타그램 DM으로 본인임을 인증한 뒤 학습이 진행돼요.",
  },
  {
    title: "자유롭게 직접 생성",
    description: "내 아바타로 원하는 장면·의상·분위기를 프롬프트로 자유롭게 만들어요. 완전히 내 마음대로.",
  },
  {
    title: "팬에게 링크 공유 (선택)",
    description: "원하면 리딤 링크를 발급해 팬에게 나눠주세요. 팬은 원하는 장면을 직접 묘사해 함께 만들 수 있어요.",
  },
  {
    title: "실시간 현황 확인",
    description: "내 생성물과 발급한 링크의 사용 현황을 스튜디오에서 한눈에 확인해요.",
  },
];
</script>

<style scoped>
.landing-page {
  width: 100%;
}

/*
 * 한국어 줄바꿈 규칙 (페이지 전역)
 * - keep-all: 어절(띄어쓰기) 단위로만 끊어 "자유롭게 만드 / 세요" 같은 어색한 분리를 막는다.
 * - overflow-wrap: 끊을 공백이 없는 긴 URL·영문만 예외적으로 강제 줄바꿈.
 * - balance/pretty: 마지막 줄에 한 단어만 남는 고아 줄을 브라우저가 알아서 없애준다.
 */
.landing-page :where(h1, h2, h3, h4, p, span, a, li, figcaption, strong, label) {
  word-break: keep-all;
  overflow-wrap: break-word;
}

.landing-page :where(h1, h2, h3, h4) {
  text-wrap: balance;
}

.landing-page :where(p, figcaption, li) {
  text-wrap: pretty;
}

/* 좁은 화면에서는 고정 <br /> 대신 브라우저가 알아서 줄을 나누게 둔다 */
.wide-only {
  display: none;
}

@media (min-width: 640px) {
  .wide-only {
    display: inline;
  }
}

/* Hero Section */
.hero-section {
  position: relative;
  /* 제목 바로 아래에 쇼케이스 사진이 붙는다 — 아래 여백을 최소로 */
  padding: 6rem 0 2rem;
  /* 흰 배경 위에 아주 옅은 주황 광원 두 개 — 평평한 흰 화면보다 깊이가 생긴다 */
  background:
    radial-gradient(60rem 30rem at 18% -10%, rgba(242, 112, 58, 0.08), transparent 60%),
    radial-gradient(52rem 28rem at 88% 8%, rgba(226, 78, 18, 0.06), transparent 60%),
    #ffffff;
  overflow: hidden;
}

/* 히어로 하단을 다음 섹션(흰색)으로 부드럽게 녹인다 */
.hero-section::after {
  content: "";
  position: absolute;
  inset: auto 0 0 0;
  height: 4rem;
  background: linear-gradient(to bottom, transparent, #ffffff);
  pointer-events: none;
}

.hero-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

@media (min-width: 768px) {
  .hero-section {
    padding: 7.5rem 0 2.5rem;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 52rem;
  margin: 0 auto;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.375rem 0.875rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #fce3d6;
  border-radius: 9999px;
  box-shadow: 0 1px 2px rgba(13, 13, 15, 0.04);
  backdrop-filter: blur(6px);
  margin-bottom: 1.5rem;
}

.badge-icon {
  width: 0.875rem;
  height: 0.875rem;
  color: #e24e12;
  flex-shrink: 0;
}

.hero-badge span {
  font-size: 0.8125rem;
  font-weight: 600;
  /* 한글은 라틴만큼 조이면 글자가 붙어 보인다 — 자간은 얕게 */
  letter-spacing: -0.005em;
  color: #b93b0e;
}

.hero-title {
  /* 좁은 화면에서 한 어절이 통째로 넘쳐 줄이 지저분해지지 않도록 화면 폭에 맞춰 줄인다 */
  font-size: clamp(2.125rem, 7.5vw, 3.5rem);
  /* 한글 제목은 라틴보다 행간이 조금 더 필요하다 (받침·초성이 위아래로 길다) */
  line-height: 1.28;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0d0d0f;
  margin: 0;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

/*
 * Section shared
 * 본문 폭을 1120px 로 좁혔다 — 1440px 에서는 4단 카드가 한 줄에 늘어지고
 * 쇼케이스(992px)와 폭이 어긋나 페이지가 두 개의 그리드처럼 보였다.
 */
.container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: clamp(1.5rem, 5vw, 2.125rem);
  line-height: 1.35;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0d0d0f;
  margin-bottom: 0.75rem;
}

.section-description {
  font-size: 1.0625rem;
  line-height: 1.75;
  letter-spacing: -0.005em;
  color: #52525b;
  max-width: 34rem;
  margin: 0 auto;
}

/* Showcase: 학습 사진 → AI 결과 */
.showcase-section {
  /* 섹션 헤더가 없어 히어로 제목이 그대로 이어진다 — 위 여백은 거의 두지 않는다 */
  padding: 0 0 6rem;
  background: white;
}

.showcase-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
  max-width: 58rem;
  margin: 0 auto;
}

.showcase-item {
  margin: 0;
  min-width: 0;
}

.showcase-frame {
  border-radius: 1.25rem;
  overflow: hidden;
  border: 1px solid #e6e6ea;
  background: #fafafa;
  box-shadow:
    0 1px 2px rgba(17, 24, 39, 0.04),
    0 24px 48px -28px rgba(17, 24, 39, 0.4);
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}

.showcase-item:hover .showcase-frame {
  transform: translateY(-3px);
  box-shadow:
    0 1px 2px rgba(17, 24, 39, 0.04),
    0 32px 60px -30px rgba(194, 66, 16, 0.45);
}

.showcase-frame img {
  display: block;
  width: 100%;
  height: auto;
}

.showcase-item figcaption {
  margin-top: 1.125rem;
}

.showcase-tag {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: -0.005em;
  color: #6e6e77;
  background: #f2f2f4;
  border-radius: 9999px;
  padding: 0.25rem 0.7rem;
  margin-bottom: 0.5rem;
}

.showcase-tag.accent {
  color: #c24210;
  background: #fdf5f0;
}

.showcase-item figcaption p {
  font-size: 0.9375rem;
  color: #52525b;
  line-height: 1.75;
  letter-spacing: -0.005em;
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
  color: #c24210;
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
    padding: 0 0 4rem;
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
  background: #fafafa;
  border-top: 1px solid #f0f0f3;
  border-bottom: 1px solid #f0f0f3;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

.step-card {
  background: white;
  border: 1px solid #e6e6ea;
  border-radius: 1.125rem;
  padding: 1.625rem 1.5rem;
  transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
}

.step-card:hover {
  border-color: #fbd9c6;
  box-shadow: 0 22px 44px -28px rgba(168, 56, 13, 0.45);
  transform: translateY(-3px);
}

.step-number {
  width: 2rem;
  height: 2rem;
  border-radius: 0.625rem;
  background: linear-gradient(135deg, #e85f26, #f2703a);
  color: white;
  font-weight: 700;
  font-size: 0.9375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  box-shadow: 0 6px 14px -6px rgba(232, 95, 38, 0.7);
}

.step-title {
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: #0d0d0f;
  margin-bottom: 0.4rem;
}

.step-description {
  font-size: 0.9375rem;
  color: #52525b;
  line-height: 1.75;
  letter-spacing: -0.005em;
}

.notice-stack {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  margin-top: 2.25rem;
}

.review-notice {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1rem 1.25rem;
  background: #fdf5f0;
  border: 1px solid #fce3d6;
  border-radius: 0.875rem;
}

/*
 * 안전 정책 — 성공 메시지가 아니라 금지 규정이라 초록을 쓰지 않는다.
 * 심사 안내(Soft 오렌지)와 구분되도록 중성 면으로 두고, 문장 무게로 강조한다.
 */
.review-notice--safety {
  background: #fafafa;
  border-color: #e6e6ea;
}

.review-notice--safety .review-notice-icon {
  color: #52525b;
}

.review-notice--safety .review-notice-text {
  color: #3a3a42;
}

.review-notice--safety .review-notice-text strong {
  color: #0d0d0f;
  font-weight: 700;
}

.review-notice-icon {
  width: 1.375rem;
  height: 1.375rem;
  color: #e24e12;
  flex-shrink: 0;
}

.review-notice-text {
  font-size: 0.9062rem;
  color: #a8380d;
  line-height: 1.7;
  letter-spacing: -0.005em;
}

.review-notice-text strong {
  font-weight: 700;
}

/* 고정형 CTA — 스크롤과 무관하게 화면 하단에 항상 떠 있다 */
.sticky-cta {
  position: fixed;
  /* 홈 화면 제스처 바가 있는 기기에서 버튼이 가려지지 않도록 안전영역만큼 더 띄운다 */
  bottom: calc(1.25rem + env(safe-area-inset-bottom, 0px));
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  padding: 0 1.25rem;
  /* 헤더(50)·인증 모달(1000) 아래, 본문 위 */
  z-index: 40;
  /* 바 영역은 클릭을 통과시키고 버튼만 받는다 */
  pointer-events: none;
}

.btn-cta {
  pointer-events: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1.0625rem 2.5rem;
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: white;
  background: linear-gradient(135deg, #e24e12 0%, #e24e12 55%, #f2703a 100%);
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  box-shadow:
    0 2px 6px rgba(15, 23, 42, 0.12),
    0 18px 36px -12px rgba(226, 78, 18, 0.75);
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}

.btn-cta:hover {
  transform: translateY(-2px);
  box-shadow:
    0 2px 6px rgba(15, 23, 42, 0.12),
    0 26px 48px -14px rgba(226, 78, 18, 0.85);
}

.btn-cta:active {
  transform: translateY(0);
}

.btn-cta:focus-visible {
  outline: 3px solid #f9c4a8;
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  .btn-cta,
  .step-card,
  .showcase-frame {
    transition: none;
  }
  .btn-cta:hover,
  .step-card:hover,
  .showcase-item:hover .showcase-frame {
    transform: none;
  }
}

/* Responsive */
@media (max-width: 640px) {
  .hero-section {
    padding: 5rem 0 4rem;
  }

  .how-section {
    padding: 4rem 0;
  }

  /* 좁은 화면에서는 화면 폭을 꽉 채우는 바 형태로 */
  .sticky-cta {
    bottom: calc(0.875rem + env(safe-area-inset-bottom, 0px));
  }

  .btn-cta {
    width: 100%;
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }
}

@media (min-width: 640px) {
  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .steps-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
