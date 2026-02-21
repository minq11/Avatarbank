<template>
  <div class="revenue-page">
    <!-- Hero -->
    <section class="revenue-hero">
      <div class="revenue-container">
        <div class="revenue-hero-content">
          <h1 class="revenue-title">Revenue model for creators</h1>
          <p class="revenue-lead">
            You upload photos. We train your AI avatar. You earn whenever someone generates an image with it.
          </p>
        </div>
      </div>
    </section>

    <!-- Creator flow: model → earnings -->
    <section class="revenue-section">
      <div class="revenue-container">
        <h2 class="section-heading">From model to earnings</h2>
        <p class="flow-intro">Here’s how you get your avatar on the platform and start earning.</p>
        <div class="flow-timeline">
          <div class="flow-step">
            <span class="flow-step-num">1</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">Become a creator</h3>
              <p class="flow-step-desc">Sign up, then request creator status by sending a DM to our official Instagram with your AvatarBank nickname. Once we verify you, your account is upgraded and you get access to the creator dashboard.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">2</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">Submit a training request</h3>
              <p class="flow-step-desc">In <strong>My Avatars</strong>, create a new request: add your avatar name, description, and set your <strong>credit per generation</strong> (how much you earn each time someone generates an image with your avatar). Upload training photos—front (at least 4), side (at least 4), full body (at least 1), and a few extra. If it’s a real-person likeness, we’ll confirm via Instagram DM before training.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">3</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">We train and publish your avatar</h3>
              <p class="flow-step-desc">We review your request, run the AI training, and add your avatar to the marketplace. You’ll get a notification when it’s live. You can then adjust options (e.g. credit per generation) in the avatar detail screen.</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-step-num">4</span>
            <div class="flow-step-body">
              <h3 class="flow-step-title">Earn and cash out</h3>
              <p class="flow-step-desc">Every time a user generates an image with your avatar, the <strong>option credits</strong> they pay go to you (the base 1 credit stays with the platform). Earnings show up in your dashboard. When you’re ready, request a payout: <strong>10 credits = 1 USD</strong>. Payouts are processed by admin approval and sent via PayPal.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- What you earn (summary) -->
    <section class="revenue-section revenue-section-alt">
      <div class="revenue-container">
        <h2 class="section-heading">What you earn</h2>
        <div class="earn-card">
          <p class="earn-desc">
            Each image generation costs the user <strong>1 base credit (platform) + optional credits (yours)</strong>. You set the optional amount per avatar. So if a user pays 1 + 4 credits for one image, you receive 4 credits. Only creators can withdraw; buyers earn credits but cannot cash out.
          </p>
          <ul class="earn-list">
            <li><strong>Your share:</strong> 100% of the optional credits users pay when generating with your avatar.</li>
            <li><strong>Dashboard:</strong> total earnings and per-avatar stats in your creator dashboard.</li>
            <li><strong>Payout:</strong> 10 credits = 1 USD, subject to minimum and admin approval; paid via PayPal.</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Guidelines -->
    <section class="revenue-section">
      <div class="revenue-container">
        <h2 class="section-heading">Guidelines</h2>
        <div class="guidelines-card">
          <p class="guidelines-desc">
            We keep the marketplace <strong>safe for work</strong>—upload photos that are appropriate for all audiences. Adult or explicit content isn’t permitted and may be removed. By contributing, you’re helping keep the platform brand-friendly for everyone.
          </p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="revenue-section revenue-cta-section">
      <div class="revenue-container">
        <div class="cta-block">
          <p class="cta-text">Ready to turn your likeness into an income stream?</p>
          <RouterLink to="/my/avatars" class="cta-btn">
            <svg class="cta-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            Start uploading
          </RouterLink>
          <RouterLink to="/" class="cta-link">Back to home</RouterLink>
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
