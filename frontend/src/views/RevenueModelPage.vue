<template>
  <div class="revenue-page">
    <!-- Hero -->
    <section class="revenue-hero">
      <div class="revenue-container">
        <div class="revenue-hero-content">
          <h1 class="revenue-title">크리에이터 수익 모델</h1>
          <p class="revenue-lead">
            사진을 올리면 AI 아바타를 학습해 드려요. 누군가 그 아바타로 이미지를 생성할 때마다 수익이 쌓입니다.
          </p>
        </div>
      </div>
    </section>

    <!-- Creator flow: model → earnings -->
    <section class="revenue-section">
      <div class="revenue-container">
        <h2 class="section-heading">모델에서 수익까지</h2>
        <p class="flow-intro">아바타를 플랫폼에 올리고 수익을 내기 시작하는 과정이에요.</p>
        <div class="flow-timeline">
          <div class="flow-step">
            <span class="flow-step-num">1</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">크리에이터 되기</h3>
              <p class="flow-step-desc">회원가입 후, 공식 인스타그램으로 AvatarBank 닉네임과 함께 DM을 보내 크리에이터 전환을 요청하세요. 본인 확인이 끝나면 계정이 업그레이드되고 크리에이터 대시보드를 이용할 수 있어요.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">2</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">학습 요청 제출</h3>
              <p class="flow-step-desc"><strong>내 아바타</strong>에서 새 요청을 만드세요: 아바타 이름·설명을 입력하고 <strong>생성당 크레딧</strong>(누군가 이 아바타로 이미지를 생성할 때마다 받는 수익)을 설정합니다. 학습 사진을 올리세요 — 정면(4장 이상), 측면(4장 이상), 전신(1장 이상), 그리고 기타 몇 장. 실존 인물 기반이라면 학습 전 인스타그램 DM으로 본인 확인을 진행해요.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">3</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">아바타 학습·공개</h3>
              <p class="flow-step-desc">요청을 검토하고 AI 학습을 진행한 뒤 아바타를 마켓에 추가해요. 공개되면 알림을 보내드립니다. 이후 아바타 상세 화면에서 옵션(예: 생성당 크레딧)을 조정할 수 있어요.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">4</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">수익 정산·출금</h3>
              <p class="flow-step-desc">사용자가 내 아바타로 이미지를 생성할 때마다, 그들이 낸 <strong>옵션 크레딧</strong>이 나에게 들어와요(기본 1크레딧은 플랫폼 몫). 수익은 대시보드에 표시됩니다. 준비되면 출금을 요청하세요: <strong>10크레딧 = 1 USD</strong>. 출금은 관리자 승인 후 PayPal로 지급돼요.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- What you earn (summary) -->
    <section class="revenue-section revenue-section-alt">
      <div class="revenue-container">
        <h2 class="section-heading">내 수익 구조</h2>
        <div class="earn-card">
          <p class="earn-desc">
            이미지 1회 생성 비용은 <strong>기본 1크레딧(플랫폼) + 옵션 크레딧(내 몫)</strong>이에요. 옵션 금액은 아바타별로 직접 정합니다. 사용자가 이미지 하나에 1+4 크레딧을 내면 내가 4크레딧을 받아요. 출금은 크리에이터만 가능하며, 구매자는 크레딧을 벌 수 있지만 출금은 안 돼요.
          </p>
          <ul class="earn-list">
            <li><strong>내 몫:</strong> 사용자가 내 아바타로 생성할 때 낸 옵션 크레딧의 100%.</li>
            <li><strong>대시보드:</strong> 크리에이터 대시보드에서 총수익과 아바타별 통계 확인.</li>
            <li><strong>출금:</strong> 10크레딧 = 1 USD, 최소 금액·관리자 승인 조건, PayPal 지급.</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Guidelines -->
    <section class="revenue-section">
      <div class="revenue-container">
        <h2 class="section-heading">가이드라인</h2>
        <div class="guidelines-card">
          <p class="guidelines-desc">
            마켓은 <strong>건전한(SFW)</strong> 콘텐츠만 유지해요 — 모든 사용자에게 적합한 사진을 올려주세요. 성인·선정적 콘텐츠는 허용되지 않으며 삭제될 수 있어요. 이런 참여가 모두를 위한 브랜드 친화적 플랫폼을 만듭니다.
          </p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="revenue-section revenue-cta-section">
      <div class="revenue-container">
        <div class="cta-block">
          <p class="cta-text">내 얼굴을 수익원으로 만들 준비됐나요?</p>
          <RouterLink to="/my/avatars" class="cta-btn">
            <svg class="cta-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            사진 올리기 시작
          </RouterLink>
          <RouterLink to="/" class="cta-link">홈으로 돌아가기</RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<style scoped>
.revenue-page {
  min-height: 100vh;
  background: #f9fafb;
}

.revenue-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

@media (min-width: 768px) {
  .revenue-container {
    padding: 0 2rem;
  }
}

/* Hero */
.revenue-hero {
  padding: 4rem 0 3rem;
  background: linear-gradient(180deg, #fff 0%, #f9fafb 100%);
  border-bottom: 1px solid #e5e7eb;
}

.revenue-hero-content {
  text-align: center;
}

.revenue-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1rem;
}

.revenue-lead {
  font-size: 1.125rem;
  color: #4b5563;
  line-height: 1.6;
  max-width: 36rem;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .revenue-hero {
    padding: 5rem 0 4rem;
  }
  .revenue-title {
    font-size: 2.5rem;
  }
  .revenue-lead {
    font-size: 1.25rem;
  }
}

/* Section */
.revenue-section {
  padding: 3rem 0;
}

.revenue-section-alt {
  background: #fff;
}

.section-heading {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .section-heading {
    font-size: 1.75rem;
    margin-bottom: 2rem;
  }
}

/* Flow timeline */
.flow-intro {
  font-size: 1rem;
  color: #4b5563;
  margin-bottom: 2rem;
  max-width: 36rem;
}

.flow-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.flow-step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.25rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.flow-step:last-child {
  border-bottom: none;
}

.flow-step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  min-width: 2.25rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #9333ea, #4f46e5);
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
}

.flow-step-body {
  min-width: 0;
}

.flow-step-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.flow-step-desc {
  font-size: 0.9375rem;
  color: #4b5563;
  line-height: 1.65;
  margin: 0;
}

.flow-step-desc strong {
  color: #374151;
}

/* Earn card */
.earn-card {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.revenue-section-alt .earn-card {
  background: #f9fafb;
  border-color: #e5e7eb;
}

.earn-desc {
  font-size: 1rem;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.earn-desc strong {
  color: #111827;
}

.earn-list {
  margin: 0;
  padding-left: 1.25rem;
  color: #4b5563;
  font-size: 0.9375rem;
  line-height: 1.7;
}

.earn-list li {
  margin-bottom: 0.5rem;
}

.earn-list li:last-child {
  margin-bottom: 0;
}

/* Guidelines */
.guidelines-card {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.guidelines-desc {
  font-size: 0.9375rem;
  color: #4b5563;
  line-height: 1.65;
  margin: 0;
}

.guidelines-desc strong {
  color: #374151;
}

/* CTA */
.revenue-cta-section {
  padding: 3rem 0 5rem;
  text-align: center;
}

.cta-block {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  border: 1px solid #e5e7eb;
}

.cta-text {
  font-size: 1.125rem;
  color: #374151;
  margin-bottom: 1.25rem;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(to right, #9333ea, #4f46e5);
  border-radius: 0.75rem;
  text-decoration: none;
  transition: box-shadow 0.2s;
}

.cta-btn:hover {
  box-shadow: 0 10px 25px -5px rgba(147, 51, 234, 0.3);
}

.cta-btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.cta-link {
  display: inline-block;
  margin-top: 1rem;
  font-size: 0.9375rem;
  color: #6b7280;
  text-decoration: none;
}

.cta-link:hover {
  color: #111827;
}
</style>
