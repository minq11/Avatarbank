<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>콘텐츠·초상권 정책</h1>
        <p class="doc-meta">시행일 2026년 8월 5일</p>
        <p class="doc-lead">
          AvatarClub은 두 가지 원칙 위에서 운영됩니다.
          <strong>하나, 내 얼굴만 등록한다.</strong>
          <strong>둘, 전 연령이 볼 수 있는 이미지만 만든다.</strong>
          이 문서는 그 원칙이 실제로 어떻게 지켜지는지 설명합니다.
        </p>
      </header>

      <section class="card">
        <h2>1. SFW 전용 — 성적·선정적 이미지는 생성되지 않습니다</h2>
        <p class="doc-p">
          서비스는 <strong>전 연령 이용 가능한(SFW, Safe For Work) 이미지만</strong> 생성합니다.
          이는 설정으로 끌 수 있는 옵션이 아니라 서비스 전체에 강제되는 기본값입니다.
        </p>
        <h3>이중 안전장치</h3>
        <ul class="doc-list">
          <li>
            <strong>생성 전 — 프롬프트 사전 필터.</strong> 입력한 프롬프트는 이미지 생성 요청이
            전송되기 <em>전에</em> 검사됩니다. 성적·노출 관련 표현이 감지되면 요청 자체가 차단되며,
            문자를 변형해 우회하려는 시도(예: 문자 사이에 기호를 넣거나 숫자로 바꾸는 방식)도
            정규화 후 검사합니다.
          </li>
          <li>
            <strong>생성 후 — 결과 이미지 안전 검사.</strong> 이미지 생성 단계에서도 안전 검사기가
            항상 켜진 상태로 동작하여, 부적절한 결과물이 만들어지면 전달되지 않습니다.
          </li>
        </ul>
        <p class="doc-note">
          필터에 차단된 경우 <strong>크레딧은 차감되지 않습니다.</strong> 다만 필터를 반복적으로
          우회하려는 시도가 확인되면 계정 이용이 제한됩니다.
        </p>
        <h3>차단되는 콘텐츠</h3>
        <ul class="doc-list">
          <li>성적·선정적 묘사, 노출을 의도한 표현</li>
          <li>미성년자를 대상으로 하거나 미성년자로 묘사되는 이미지 (예외 없이 차단)</li>
          <li>폭력·유혈·혐오 표현, 특정 집단에 대한 차별을 조장하는 이미지</li>
          <li>불법 행위를 묘사하거나 조장하는 이미지</li>
        </ul>
        <p class="doc-note">
          자동 필터는 완벽하지 않습니다. 걸러지지 않은 부적절한 결과물을 발견하시면
          <RouterLink to="/support#report" class="doc-link">신고</RouterLink>해 주세요.
          신고는 필터 개선에 반영됩니다.
        </p>
      </section>

      <section class="card">
        <h2>2. 초상권 — 본인의 얼굴만 등록할 수 있습니다</h2>
        <p class="doc-p">
          아바타는 <strong>등록하는 본인의 얼굴</strong>로만 만들 수 있습니다. 연예인, 지인,
          인터넷에서 구한 사진 등 <strong>타인의 얼굴을 동의 없이 등록하는 것은 금지</strong>됩니다.
        </p>
        <h3>등록 심사</h3>
        <ul class="doc-list">
          <li>
            모든 아바타 등록·학습은 관리자가 <strong>도용 여부를 직접 확인</strong>한 뒤 진행됩니다.
            승인 및 학습까지 <strong>2~7일</strong>이 소요됩니다.
          </li>
          <li>
            도용이 의심되면 등록이 반려됩니다. 본인임을 확인할 수 있는 추가 자료(예: 지정된 문구를
            든 사진, 공개 계정 확인)를 요청할 수 있습니다.
          </li>
          <li>
            <strong>도용이 확인되면 계정이 즉시 정지</strong>되고, 해당 아바타와 그 아바타로 생성된
            이미지, 발급된 리딤 링크가 모두 삭제·비활성화됩니다.
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>3. 팬이 만드는 이미지에도 같은 기준이 적용됩니다</h2>
        <p class="doc-p">
          크리에이터가 발급한 리딤 링크로 팬이 이미지를 만들 때에도 위 1항의 안전장치가 동일하게
          작동합니다. 팬이 자유롭게 프롬프트를 입력하더라도 SFW 기준을 벗어난 생성은 불가능합니다.
        </p>
        <ul class="doc-list">
          <li>
            팬이 입력한 프롬프트도 크리에이터 본인의 생성과 동일한 필터를 거칩니다.
            발급한 링크가 원치 않게 쓰이고 있다면 언제든 비활성화할 수 있습니다.
          </li>
          <li>
            크리에이터는 언제든 발급한 링크를 <strong>비활성화</strong>할 수 있으며, 즉시 사용이 중단됩니다.
          </li>
          <li>
            팬의 생성으로 소모되는 크레딧은 크리에이터의 것입니다. 링크를 공개된 장소에 배포할 때는
            사용 횟수 설정을 함께 확인해 주세요.
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>4. 생성물을 사용할 때의 책임</h2>
        <ul class="doc-list">
          <li>
            생성된 이미지는 <strong>AI로 만들어진 것</strong>입니다. 실제 촬영물인 것처럼 오인하게
            하거나, 타인을 사칭하는 데 사용해서는 안 됩니다.
          </li>
          <li>
            생성물을 외부에 공개할 때는 AI 생성물임을 밝히는 것을 권장합니다.
          </li>
          <li>
            아바타의 대상이 된 크리에이터의 초상권이 우선합니다. 크리에이터가 특정 생성물의 이용
            중단을 요청하면 회사는 이를 우선 검토합니다.
          </li>
        </ul>
      </section>

      <section id="report" class="card">
        <h2>5. 신고 절차</h2>
        <p class="doc-p">아래 경우에 해당하면 신고해 주세요.</p>
        <ul class="doc-list">
          <li>내 얼굴이 동의 없이 아바타로 등록된 것 같을 때</li>
          <li>안전 필터를 통과했지만 부적절한 이미지가 생성됐을 때</li>
          <li>생성물이 나를 사칭하거나 명예를 훼손하는 방식으로 사용될 때</li>
          <li>그 밖에 본 정책이나 <RouterLink to="/terms" class="doc-link">이용약관</RouterLink> 위반이 의심될 때</li>
        </ul>

        <div class="doc-steps" style="margin-top: 1.25rem">
          <div class="doc-step">
            <span class="doc-step-num">1</span>
            <div class="doc-step-body">
              <h3>신고 접수</h3>
              <p>
                <RouterLink to="/support#report" class="doc-link">문의하기</RouterLink>에서 분류를
                <strong>"신고 (도용·권리침해)"</strong>로 선택하고, 문제가 되는 아바타명·링크·이미지
                링크와 상황을 적어 주세요. 회신받을 이메일은 정확히 입력해 주세요.
              </p>
            </div>
          </div>
          <div class="doc-step">
            <span class="doc-step-num">2</span>
            <div class="doc-step-body">
              <h3>검토</h3>
              <p>
                관리자가 접수 내용을 확인합니다. 긴급하다고 판단되면 검토 중이라도 해당 아바타·링크를
                먼저 비활성화할 수 있습니다.
              </p>
            </div>
          </div>
          <div class="doc-step">
            <span class="doc-step-num">3</span>
            <div class="doc-step-body">
              <h3>조치 및 회신</h3>
              <p>
                위반이 확인되면 콘텐츠 삭제, 아바타 비공개, 링크 비활성화, 계정 정지 등의 조치를
                취하고 결과를 회신 이메일로 안내합니다.
              </p>
            </div>
          </div>
        </div>

        <p class="doc-note">
          허위 신고를 반복하는 경우 이용이 제한될 수 있습니다. 조치 결과에 이의가 있으면 같은
          경로로 재심을 요청할 수 있습니다.
        </p>
      </section>

      <footer class="doc-foot">
        <p class="doc-meta">
          관련 문서:
          <RouterLink to="/terms" class="doc-link">이용약관</RouterLink> ·
          <RouterLink to="/privacy" class="doc-link">개인정보처리방침</RouterLink> ·
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
