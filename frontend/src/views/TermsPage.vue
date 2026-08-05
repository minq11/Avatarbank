<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>이용약관</h1>
        <p class="doc-meta">시행일 2026년 8월 5일 · 최종 개정 2026년 8월 5일</p>
        <p class="doc-lead">
          AvatarBank(이하 "서비스")는 이용자가 본인의 얼굴로 AI 아바타를 만들고, 그 아바타로
          이미지를 생성하며, 원할 경우 팬에게 리딤 코드를 배포할 수 있도록 하는 크리에이터
          스튜디오입니다. 본 약관은 서비스 이용에 관한 조건과 절차를 정합니다.
        </p>
      </header>

      <nav class="doc-toc card">
        <h2>목차</h2>
        <ol>
          <li><a href="#a1">제1조 (목적과 정의)</a></li>
          <li><a href="#a2">제2조 (계정)</a></li>
          <li><a href="#a3">제3조 (아바타 등록과 심사)</a></li>
          <li><a href="#a4">제4조 (구독과 생성 쿼터)</a></li>
          <li><a href="#a5">제5조 (리딤 코드)</a></li>
          <li><a href="#a6">제6조 (콘텐츠 정책과 금지행위)</a></li>
          <li><a href="#a7">제7조 (생성물의 권리)</a></li>
          <li><a href="#a8">제8조 (이용 제한과 해지)</a></li>
          <li><a href="#a9">제9조 (면책과 서비스 변경)</a></li>
          <li><a href="#a10">제10조 (분쟁 해결)</a></li>
        </ol>
      </nav>

      <section id="a1" class="card">
        <h2>제1조 (목적과 정의)</h2>
        <ol class="doc-list">
          <li>
            본 약관은 서비스 이용과 관련하여 회사와 이용자 간의 권리·의무를 정하는 것을 목적으로 합니다.
          </li>
          <li>
            <strong>크리에이터</strong>란 본인의 사진으로 아바타를 등록하고 이미지를 생성하는 회원을 말합니다.
          </li>
          <li>
            <strong>아바타</strong>란 크리에이터가 제출한 사진으로 학습된 AI 모델을 말합니다.
          </li>
          <li>
            <strong>리딤 코드</strong>란 크리에이터가 팬에게 배포하는, 해당 아바타로 이미지를 생성할 수 있는
            일회성 또는 다회성 코드를 말합니다.
          </li>
        </ol>
      </section>

      <section id="a2" class="card">
        <h2>제2조 (계정)</h2>
        <ol class="doc-list">
          <li>회원가입은 이메일, 닉네임, 비밀번호로 이루어집니다.</li>
          <li>
            계정은 본인만 사용할 수 있으며, 계정 정보를 타인에게 양도·대여할 수 없습니다.
          </li>
          <li>
            비밀번호 관리 책임은 이용자에게 있으며, 도용이 의심되면 즉시
            <RouterLink to="/support" class="doc-link">문의</RouterLink>해 주셔야 합니다.
          </li>
        </ol>
      </section>

      <section id="a3" class="card">
        <h2>제3조 (아바타 등록과 심사)</h2>
        <ol class="doc-list">
          <li>
            아바타 등록을 위해서는 정면·측면·전신 사진 등 학습용 이미지를 제출해야 합니다.
          </li>
          <li>
            <strong>이용자는 본인의 얼굴만 등록할 수 있습니다.</strong> 타인의 사진을 본인 동의 없이
            제출하는 행위는 금지되며, 이는 제6조의 중대한 위반에 해당합니다.
          </li>
          <li>
            모든 아바타 등록 요청은 관리자가 도용 여부를 확인한 뒤 승인되며, 승인까지
            <strong>영업일 기준 1~7일</strong>이 소요됩니다. 회사는 심사 결과 도용이 의심되거나
            사진 품질이 학습에 부적합한 경우 등록을 반려할 수 있습니다.
          </li>
          <li>
            이용자는 언제든 본인의 아바타 삭제를 요청할 수 있습니다. 삭제 시 해당 아바타에 연결된
            리딤 코드는 더 이상 사용할 수 없습니다.
          </li>
        </ol>
      </section>

      <section id="a4" class="card">
        <h2>제4조 (구독과 생성 쿼터)</h2>
        <ol class="doc-list">
          <li>
            서비스는 플랜별로 <strong>월 생성 쿼터(이미지 장수)</strong>, 등록 가능 아바타 수,
            동시 활성 코드 수를 제공합니다.
          </li>
          <li>
            <strong>이미지 생성이 성공할 때마다 쿼터가 1 차감됩니다.</strong> 생성이 실패한 경우
            쿼터는 차감되지 않습니다.
          </li>
          <li>
            남은 쿼터는 <strong>다음 결제 기간으로 이월되지 않습니다.</strong>
          </li>
          <li>
            플랜을 변경하면 변경 시점의 플랜 쿼터가 적용됩니다.
          </li>
          <li class="doc-callout">
            <strong>현재 결제 시스템은 연동 전입니다.</strong> 따라서 유료 플랜을 선택하더라도 실제
            과금이 발생하지 않으며 쿼터가 즉시 활성화됩니다(데모 운영). 결제가 도입되는 시점에
            요금·환불 조건을 사전 고지하며, 그 전까지 발생한 이용에 대해 소급 과금하지 않습니다.
          </li>
        </ol>
      </section>

      <section id="a5" class="card">
        <h2>제5조 (리딤 코드)</h2>
        <ol class="doc-list">
          <li>
            크리에이터는 본인 아바타에 대해 리딤 코드를 발급하여 팬에게 배포할 수 있습니다.
            코드는 링크 또는 QR 형태로 공유됩니다.
          </li>
          <li>
            <strong>팬이 코드로 이미지를 생성하면 크리에이터의 쿼터에서 차감됩니다.</strong>
            코드 배포 범위와 사용 횟수 설정은 크리에이터의 책임입니다.
          </li>
          <li>
            코드를 받은 팬은 원하는 장면을 직접 프롬프트로 입력해 생성할 수 있습니다.
          </li>
          <li>
            크리에이터는 언제든 발급한 코드를 비활성화할 수 있습니다. 비활성화된 코드는 즉시
            사용할 수 없게 됩니다.
          </li>
          <li>
            코드는 무상 배포를 전제로 하며, 코드 자체를 유상으로 재판매하는 행위는 금지됩니다.
          </li>
        </ol>
      </section>

      <section id="a6" class="card">
        <h2>제6조 (콘텐츠 정책과 금지행위)</h2>
        <p class="doc-p">
          서비스는 <strong>전 연령 이용 가능한(SFW) 이미지만</strong> 생성합니다. 자세한 기준은
          <RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink>을 따릅니다.
        </p>
        <p class="doc-p">다음 행위는 금지되며, 적발 시 제8조에 따라 조치됩니다.</p>
        <ul class="doc-list">
          <li>타인의 얼굴·신체 사진을 동의 없이 아바타로 등록하는 행위</li>
          <li>미성년자를 대상으로 하거나 미성년자로 묘사되는 이미지를 생성하려는 행위</li>
          <li>성적·선정적 이미지 생성 시도 및 안전 필터를 우회하려는 일체의 시도</li>
          <li>타인을 사칭하거나, 생성물을 실제 촬영물인 것처럼 오인하게 하는 행위</li>
          <li>폭력·혐오·불법 행위를 조장하는 이미지 생성</li>
          <li>자동화 스크립트로 코드·쿼터를 대량 소모하거나 서비스에 과부하를 주는 행위</li>
          <li>리버스 엔지니어링, 무단 크롤링, 보안 취약점의 악용</li>
        </ul>
      </section>

      <section id="a7" class="card">
        <h2>제7조 (생성물의 권리)</h2>
        <ol class="doc-list">
          <li>
            크리에이터가 제출한 사진과 그 사진에 대한 권리는 크리에이터에게 있습니다.
          </li>
          <li>
            생성된 이미지는 생성을 요청한 이용자가 개인적·상업적으로 이용할 수 있습니다.
            다만 아바타의 대상이 된 크리에이터의 초상권이 우선하며, 크리에이터가 특정 생성물의
            이용 중단을 요청하면 회사는 이를 우선 검토합니다.
          </li>
          <li>
            회사는 서비스 운영·개선에 필요한 범위에서 생성물을 저장·표시할 수 있으며,
            이용자가 명시적으로 공개(공유)하지 않은 생성물은 갤러리 등에 노출하지 않습니다.
          </li>
        </ol>
      </section>

      <section id="a8" class="card">
        <h2>제8조 (이용 제한과 해지)</h2>
        <ol class="doc-list">
          <li>
            회사는 제6조 위반 시 사전 통지 없이 해당 콘텐츠 삭제, 아바타 비공개, 코드 비활성화,
            계정 정지 등의 조치를 할 수 있습니다.
          </li>
          <li>
            <strong>타인 얼굴 무단 등록이 확인된 경우 계정이 즉시 정지됩니다.</strong>
          </li>
          <li>
            이용자는 언제든 계정 해지를 요청할 수 있으며, 해지 시 개인정보는
            <RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink>에 따라 처리됩니다.
          </li>
          <li>
            조치에 이의가 있는 경우
            <RouterLink to="/support" class="doc-link">문의하기</RouterLink>를 통해 재심을 요청할 수 있습니다.
          </li>
        </ol>
      </section>

      <section id="a9" class="card">
        <h2>제9조 (면책과 서비스 변경)</h2>
        <ol class="doc-list">
          <li>
            AI 생성 결과물의 품질·정확성은 보장되지 않으며, 동일한 프롬프트라도 결과가 달라질 수 있습니다.
          </li>
          <li>
            서비스는 외부 AI 생성 인프라에 의존하므로, 해당 사업자의 장애로 생성이 실패할 수 있습니다.
            이 경우 쿼터는 차감되지 않습니다.
          </li>
          <li>
            회사는 서비스의 내용·플랜 구성을 변경할 수 있으며, 이용자에게 불리한 변경은
            시행 7일 전(중대한 변경은 30일 전)에 공지합니다.
          </li>
          <li>
            천재지변, 회선 장애 등 회사의 통제를 벗어난 사유로 인한 서비스 중단에 대해서는 책임을 지지 않습니다.
          </li>
        </ol>
      </section>

      <section id="a10" class="card">
        <h2>제10조 (분쟁 해결)</h2>
        <ol class="doc-list">
          <li>본 약관은 대한민국 법을 준거법으로 합니다.</li>
          <li>
            서비스 이용과 관련한 분쟁은 우선 협의로 해결하며, 협의가 이루어지지 않는 경우
            민사소송법상 관할 법원에 소를 제기할 수 있습니다.
          </li>
          <li>
            문의는 <RouterLink to="/support" class="doc-link">고객지원</RouterLink>을 통해 접수해 주세요.
          </li>
        </ol>
      </section>

      <footer class="doc-foot">
        <p class="doc-meta">
          관련 문서:
          <RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink> ·
          <RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink> ·
          <RouterLink to="/guide" class="doc-link">크리에이터 가이드</RouterLink>
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<style scoped>
@import "./doc-page.css";
</style>
