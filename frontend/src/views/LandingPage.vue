<template>
  <div class="landing-page">
    <!-- 히어로 섹션 -->
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-content">
          <!-- Badge -->
          <div class="hero-badge">
            <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0L9.937 15.5Z"/>
            </svg>
            <span>AI-Powered Avatar Marketplace</span>
          </div>

          <!-- Headline -->
          <h1 class="hero-title">
            Create your own images with influencer avatars
          </h1>

          <!-- Subheadline -->
          <p class="hero-subtitle">
            An AI avatar marketplace where revenue is shared per image
          </p>

          <!-- Prompt Input -->
          <div class="prompt-input-wrapper">
            <div class="prompt-input-container">
              <input
                v-model="prompt"
                type="text"
                placeholder="Describe the image you want to create..."
                class="prompt-input"
              />
              <button class="generate-btn">
                <svg class="generate-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0L9.937 15.5Z"/>
                </svg>
                Generate
              </button>
            </div>
          </div>

          <!-- CTAs -->
          <div class="hero-actions">
            <RouterLink to="/influencer/dashboard" class="btn-secondary">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
                <polyline points="16 7 22 7 22 13"/>
              </svg>
              Become an influencer
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- 갤러리 섹션 -->
    <section class="gallery-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Explore AI-Generated Avatars</h2>
          <p class="section-description">
            Browse thousands of unique images created with our influencer avatars
          </p>
        </div>

        <div class="gallery-grid">
          <div
            v-for="(avatar, index) in galleryAvatars"
            :key="index"
            class="gallery-card"
            @click="() => $router.push(`/market`)"
          >
            <div class="gallery-image-wrapper">
              <div class="gallery-image-placeholder">
                <span>Avatar {{ index + 1 }}</span>
              </div>
              <div class="gallery-overlay"></div>
              
              <!-- Instagram Badge -->
              <div class="instagram-badge">
                <img :src="instagramLogo" alt="Instagram" class="instagram-icon" />
                <span>{{ avatar.instagram }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- View More -->
        <div class="view-more">
          <RouterLink to="/market" class="btn-view-all">
            View all avatars
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 인플루언서 섹션 -->
    <section class="influencer-section">
      <div class="container">
        <div class="influencer-grid">
          <!-- Left Content -->
          <div class="influencer-content">
            <h2 class="influencer-title">
              Upload photos, earn with your AI avatar
            </h2>
            
            <p class="influencer-description">
              Share your photos to create an AI avatar and earn revenue every time someone generates an image with it. Turn your influence into a sustainable income stream.
            </p>

            <div class="influencer-actions">
              <RouterLink to="/influencer/dashboard" class="btn-primary-influencer">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
                Start uploading
              </RouterLink>
              <a href="#revenue" class="btn-link-influencer">
                View revenue model
                <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </a>
            </div>
          </div>

          <!-- Right Visual -->
          <div class="influencer-visual">
            <div class="visual-grid">
              <div class="visual-column">
                <div class="visual-item aspect-portrait">
                  <div class="visual-placeholder">Photo 1</div>
                </div>
                <div class="visual-item aspect-square">
                  <div class="visual-placeholder">Photo 2</div>
                </div>
              </div>
              <div class="visual-column offset-top">
                <div class="visual-item aspect-square">
                  <div class="visual-placeholder">Photo 3</div>
                </div>
                <div class="visual-item aspect-portrait">
                  <div class="visual-placeholder">Photo 4</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import instagramLogo from "@/assets/icons/Instagram_logo_2016.svg?url";

const prompt = ref("");

const galleryAvatars = [
  { instagram: "@model_anna" },
  { instagram: "@fashion_kim" },
  { instagram: "@pro_david" },
  { instagram: "@creative_sofia" },
  { instagram: "@lifestyle_james" },
  { instagram: "@urban_alex" },
  { instagram: "@elegant_maria" },
  { instagram: "@minimal_chris" },
];
</script>

<style scoped>
.landing-page {
  width: 100%;
}

/* 히어로 섹션 */
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
  line-height: 1.1;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #4b5563;
  margin-bottom: 3rem;
  max-width: 32rem;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.625;
}

.prompt-input-wrapper {
  max-width: 48rem;
  margin: 0 auto 2rem;
}

.prompt-input-container {
  position: relative;
}

.prompt-input {
  width: 100%;
  padding: 1.25rem 1.5rem;
  padding-right: 10rem;
  font-size: 1rem;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.prompt-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

.generate-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #4f46e5, #6366f1);
  border-radius: 0.75rem;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.generate-btn:hover {
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.generate-icon {
  width: 1rem;
  height: 1rem;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.btn-secondary {
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

.btn-secondary:hover {
  border-color: #d1d5db;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 갤러리 섹션 */
.gallery-section {
  padding: 6rem 0;
  background: #f9fafb;
}

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
  max-width: 32rem;
  margin: 0 auto;
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

.btn-primary-influencer {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
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

.btn-primary-influencer:hover {
  box-shadow: 0 20px 25px -5px rgba(147, 51, 234, 0.3);
}

/* 인플루언서 섹션 */
.influencer-section {
  padding: 6rem 0;
  background: white;
}

.influencer-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 4rem;
  align-items: center;
}

@media (min-width: 1024px) {
  .influencer-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.influencer-content {
  max-width: 100%;
}

.influencer-title {
  font-size: 2.25rem;
  line-height: 1.1;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #111827;
  margin-bottom: 1.5rem;
}

.influencer-description {
  font-size: 1.125rem;
  color: #4b5563;
  line-height: 1.625;
  margin-bottom: 2rem;
}

.influencer-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-primary-influencer {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(to right, #9333ea, #4f46e5);
  border-radius: 0.75rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary-influencer:hover {
  box-shadow: 0 20px 25px -5px rgba(147, 51, 234, 0.3);
}

.btn-link-influencer {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: color 0.2s;
}

.btn-link-influencer:hover {
  color: #111827;
}

.arrow-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.2s;
}

.btn-link-influencer:hover .arrow-icon {
  transform: translateX(0.25rem);
}

.influencer-visual {
  position: relative;
}

.visual-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.visual-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.visual-column.offset-top {
  padding-top: 2rem;
}

.visual-item {
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.aspect-portrait {
  aspect-ratio: 3 / 4;
}

.aspect-square {
  aspect-ratio: 1;
}

.visual-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-weight: 600;
}

/* 반응형 */
@media (min-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-actions {
    flex-direction: row;
    justify-content: center;
  }

  .influencer-actions {
    flex-direction: row;
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

  .influencer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
  }

  .influencer-title {
    font-size: 3rem;
  }
}

@media (min-width: 768px) {
  .gallery-section {
    padding: 6rem 0;
  }

  .influencer-section {
    padding: 6rem 0;
  }
}
</style>
