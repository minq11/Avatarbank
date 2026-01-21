<template>
  <div class="landing-page">
    <!-- 히어로 섹션 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">인플루언서 아바타로 나만의 이미지를 생성하세요</h1>
        <p class="hero-subtitle">이미지 1장마다 인플루언서와 수익을 나누는 AI 아바타 마켓플레이스</p>
        <div class="hero-actions">
          <RouterLink to="/market" class="btn btn-primary btn-large">지금 생성해보기</RouterLink>
          <RouterLink to="/influencer/dashboard" class="btn btn-secondary btn-large">
            인플루언서로 참여하기
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 샘플 갤러리 섹션 -->
    <section class="sample-gallery-section">
      <div class="container">
        <h2 class="section-title">인기 아바타</h2>
        <div class="avatar-grid">
          <div v-for="i in 6" :key="i" class="avatar-card">
            <div class="avatar-image-placeholder">
              <span>Avatar {{ i }}</span>
            </div>
            <div class="avatar-info">
              <h3>Influencer {{ i }}</h3>
              <p>1 Credit + 옵션</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 인플루언서 섹션 -->
    <section class="influencer-section">
      <div class="container">
        <div class="influencer-content">
          <div class="influencer-text">
            <h2>사진만 올리면, AI 아바타가 수익을 만듭니다</h2>
            <p>인스타그램 계정만 있으면 누구나 인플루언서로 참여할 수 있습니다. 아바타가 사용될 때마다 자동으로 크레딧을 획득하고, USD로 환전할 수 있습니다.</p>
            <RouterLink to="/influencer/dashboard" class="btn btn-link">수익 구조 보기 →</RouterLink>
          </div>
          <div class="influencer-stats">
            <div class="stat-card">
              <div class="stat-value">5 Credit</div>
              <div class="stat-label">평균 생성당 수익</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">10 Credit</div>
              <div class="stat-label">= 1 USD 환전</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 어떻게 동작하나요? 섹션 -->
    <section class="how-it-works-section">
      <div class="container">
        <h2 class="section-title">어떻게 동작하나요?</h2>
        <div class="steps-grid">
          <div class="step-card">
            <div class="step-number">1</div>
            <h3>Buyer</h3>
            <div class="step-steps">
              <div class="step-item">아바타 선택</div>
              <div class="step-item">프롬프트 입력</div>
              <div class="step-item">이미지 다운로드</div>
            </div>
          </div>
          <div class="step-card">
            <div class="step-number">2</div>
            <h3>Influencer</h3>
            <div class="step-steps">
              <div class="step-item">인증</div>
              <div class="step-item">사진 업로드</div>
              <div class="step-item">자동 수익</div>
            </div>
          </div>
          <div class="step-card">
            <div class="step-number">3</div>
            <h3>Platform</h3>
            <div class="step-steps">
              <div class="step-item">AI 학습</div>
              <div class="step-item">이미지 생성</div>
              <div class="step-item">수익 분배</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<style scoped>
.landing-page {
  width: 100%;
}

/* 히어로 섹션 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6rem 2rem;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-large {
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 600;
}

.btn-primary {
  background: #111827;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #1f2937;
}

.btn-secondary {
  background: white;
  color: #111827;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.95);
}

.btn-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-top: 1rem;
  display: inline-block;
}

.btn-link:hover {
  text-decoration: underline;
}

/* 컨테이너 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 샘플 갤러리 섹션 */
.sample-gallery-section {
  padding: 4rem 0;
  background: #f9fafb;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 2rem;
  color: #111827;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.avatar-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.avatar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.avatar-image-placeholder {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-weight: 600;
}

.avatar-info {
  padding: 1rem;
}

.avatar-info h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #111827;
}

.avatar-info p {
  font-size: 0.875rem;
  color: #6b7280;
}

/* 인플루언서 섹션 */
.influencer-section {
  padding: 4rem 0;
  background: white;
}

.influencer-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.influencer-text h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #111827;
}

.influencer-text p {
  font-size: 1.125rem;
  color: #6b7280;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.influencer-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

/* 어떻게 동작하나요? 섹션 */
.how-it-works-section {
  padding: 4rem 0;
  background: #f9fafb;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.step-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto 1rem;
}

.step-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #111827;
}

.step-steps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.step-item {
  padding: 0.5rem;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #374151;
}

/* 반응형 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .influencer-content {
    grid-template-columns: 1fr;
  }

  .influencer-stats {
    flex-direction: column;
  }

  .steps-grid {
    grid-template-columns: 1fr;
  }
}
</style>


