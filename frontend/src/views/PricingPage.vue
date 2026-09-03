<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>크레딧 안내</h1>
        <p class="doc-lead">
          AvatarClub은 <strong>크레딧</strong>으로 이용하는 AI 이미지 생성 서비스입니다.
          구독료 없이 필요한 만큼만 구매해 사용합니다.
        </p>
      </header>

      <!--
        판매 상품 목록. PG 심사에서 "판매중인 상품"을 확인하는 페이지이므로
        로그인 없이 접근 가능해야 한다 (GET /credits/packs 는 인증 불필요).
      -->
      <section class="card">
        <h2>판매 상품</h2>

        <div v-if="loading" class="pricing-state">불러오는 중…</div>

        <div v-else-if="packs.length" class="pricing-grid">
          <div v-for="p in packs" :key="p.id" class="pricing-card">
            <h3 class="pricing-name">{{ p.name }}</h3>
            <p class="pricing-price">{{ p.price_krw.toLocaleString() }}<span>원</span></p>
            <ul class="pricing-facts">
              <li>이미지 {{ p.credits.toLocaleString() }}장 생성</li>
              <li>장당 {{ Math.round(p.price_krw / p.credits).toLocaleString() }}원</li>
            </ul>
            <RouterLink to="/studio" class="pricing-cta">구매하기</RouterLink>
          </div>
        </div>

        <p v-else class="pricing-state">
          상품 정보를 불러오지 못했어요. 잠시 후 새로고침해 주세요.
        </p>

        <p class="doc-note">
          표시 금액은 부가세 포함가입니다. 구매하기를 누르면 로그인 후
          크리에이터 스튜디오에서 결제창이 열립니다.
        </p>
      </section>

      <!--
        재화의 공급 시기. 디지털 이용권이라 배송이 없고 결제 즉시 지급된다.
        전자상거래법상 "재화 공급 시기" 고지에 해당하는 항목이라 명시해 둔다.
      -->
      <section class="card">
        <h2>이용권 지급 시기</h2>
        <p class="doc-p">
          <strong>결제가 완료되면 즉시(수 초 이내) 계정에 크레딧이 지급됩니다.</strong>
          온라인으로 제공되는 디지털 이용권이므로 <strong>별도의 배송 절차가 없으며</strong>,
          배송비도 발생하지 않습니다.
        </p>
        <p class="doc-p">
          결제는 완료됐으나 크레딧이 반영되지 않은 경우
          <RouterLink to="/support" class="doc-link">고객지원</RouterLink>으로 문의해 주시면
          확인 후 처리해 드립니다.
        </p>
      </section>

      <section class="card">
        <h2>사용 방법</h2>
        <ol class="doc-list">
          <li><strong>크레딧 1개로 이미지 1장</strong>을 생성합니다.</li>
          <li>
            생성이 실패하거나 안전 필터에 걸린 경우
            <strong>차감된 크레딧은 자동으로 돌려드립니다.</strong>
          </li>
          <li>
            크레딧은 계정에 귀속되며 타인에게 양도하거나 현금으로 교환할 수 없습니다.
          </li>
          <li>유효기간은 <strong>마지막 구매일로부터 5년</strong>입니다.</li>
        </ol>
      </section>

      <section class="card">
        <h2>취소 및 환불</h2>
        <ol class="doc-list">
          <li>
            <strong>청약철회</strong> — 구매일로부터 <strong>7일 이내</strong>, 사용하지 않은
            잔여 크레딧에 대해 전액 환불을 요청할 수 있습니다.
          </li>
          <li>
            7일이 지난 뒤에도 <strong>미사용 잔여 크레딧</strong>은 고객지원을 통해 환불을
            요청할 수 있습니다. <strong>이미 사용한 크레딧은 환불 대상이 아닙니다.</strong>
          </li>
          <li>환불은 <strong>원결제 수단</strong>으로 처리됩니다.</li>
          <li>
            회사의 귀책사유로 서비스를 이용하지 못한 경우 해당 크레딧은 전액 환원되며,
            환불을 요청할 수 있습니다.
          </li>
          <li>
            회원가입 시 무상 지급되는 크레딧은 현금 환불 및 양도의 대상이 아닙니다.
          </li>
        </ol>
        <p class="doc-note">
          자세한 내용은 <RouterLink to="/terms" class="doc-link">이용약관 제4조</RouterLink>를
          확인해 주세요. 환불 문의는
          <RouterLink to="/support" class="doc-link">고객지원</RouterLink>으로 접수해 주시면
          영업일 기준 3일 이내에 답변드립니다.
        </p>
      </section>

      <footer class="doc-foot">
        <p class="doc-meta">
          관련 문서:
          <RouterLink to="/terms" class="doc-link">이용약관</RouterLink> ·
          <RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink> ·
          <RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink>
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { creditsApi, type CreditPack } from "@/services/api";

const packs = ref<CreditPack[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    packs.value = await creditsApi.getPacks();
  } catch {
    // 목록을 못 불러와도 페이지의 나머지(지급 시기·환불 규정)는 보여야 하므로
    // 오류를 던지지 않고 빈 상태로 둔다.
    packs.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
@import "./doc-page.css";

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.85rem;
  margin-top: 0.9rem;
}

.pricing-card {
  border: 1px solid #e8e8ec;
  border-radius: 12px;
  padding: 1.1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #fff;
}

.pricing-name {
  margin: 0;
  font-size: 1rem;
  color: #52525b;
}

.pricing-price {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #18181b;
}

.pricing-price span {
  font-size: 0.95rem;
  font-weight: 500;
  margin-left: 0.1rem;
}

.pricing-facts {
  margin: 0;
  padding-left: 1.05rem;
  color: #52525b;
  font-size: 0.85rem;
  line-height: 1.7;
  flex: 1;
}

.pricing-cta {
  display: block;
  text-align: center;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  background: #e24e12;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
}

.pricing-cta:hover {
  background: #c94310;
}

.pricing-state {
  margin: 0.9rem 0 0;
  color: #71717a;
  font-size: 0.9rem;
}
</style>
