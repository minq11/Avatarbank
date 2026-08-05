<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>크리에이터 가이드</h1>
        <p class="doc-meta">아바타 등록부터 팬 공유까지</p>
        <p class="doc-lead">
          내 얼굴로 AI 아바타를 만들고, 원하는 장면을 자유롭게 생성하고, 원할 땐 팬에게 리딤 코드를
          나눠주는 것까지 — 한 번에 따라 할 수 있게 정리했어요.
        </p>
      </header>

      <section class="card">
        <h2>전체 흐름</h2>
        <div class="doc-steps">
          <div class="doc-step">
            <span class="doc-step-num">1</span>
            <div class="doc-step-body">
              <h3>아바타 등록</h3>
              <p>정면·측면·전신 사진을 올리면 내 얼굴을 학습한 아바타가 만들어져요.</p>
            </div>
          </div>
          <div class="doc-step">
            <span class="doc-step-num">2</span>
            <div class="doc-step-body">
              <h3>플랜 선택</h3>
              <p>플랜을 고르면 월 생성 쿼터(이미지 장수)를 받아요.</p>
            </div>
          </div>
          <div class="doc-step">
            <span class="doc-step-num">3</span>
            <div class="doc-step-body">
              <h3>직접 만들기</h3>
              <p>프롬프트로 원하는 장면·의상·분위기를 자유롭게 생성해요.</p>
            </div>
          </div>
          <div class="doc-step">
            <span class="doc-step-num">4</span>
            <div class="doc-step-body">
              <h3>팬에게 코드 공유 (선택)</h3>
              <p>리딤 코드를 발급해 링크나 QR로 나눠주면 팬이 함께 만들 수 있어요.</p>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>1. 아바타 등록 — 사진이 결과를 좌우해요</h2>
        <p class="doc-p">
          <RouterLink to="/my/avatars" class="doc-link">내 아바타</RouterLink> 페이지에서 등록을
          요청할 수 있어요. 학습 품질은 사진 품질에 거의 그대로 비례하니 아래를 참고하세요.
        </p>
        <h3>좋은 사진</h3>
        <ul class="doc-list">
          <li>얼굴이 또렷하게 나온 <strong>정면 사진</strong> 여러 장 (표정·각도를 조금씩 다르게)</li>
          <li>좌우 <strong>측면</strong>과 <strong>전신</strong> 사진</li>
          <li>자연광 등 <strong>밝고 고른 조명</strong>, 그림자가 얼굴을 가리지 않는 사진</li>
          <li>배경이 단순하고 인물이 크게 나온 고해상도 사진</li>
        </ul>
        <h3>피해야 할 사진</h3>
        <ul class="doc-list">
          <li>선글라스·마스크·과한 필터로 얼굴이 가려진 사진</li>
          <li>여러 사람이 함께 나와 누가 본인인지 불분명한 사진</li>
          <li>흐릿하거나 심하게 어두운 사진, 저해상도로 확대된 사진</li>
          <li>모두 같은 각도·같은 표정으로만 찍힌 사진 묶음</li>
        </ul>
        <p class="doc-note">
          <strong>등록은 관리자 심사를 거칩니다.</strong> 도용 여부를 확인한 뒤 승인되며
          <strong>영업일 기준 1~7일</strong>이 걸려요. 반드시
          <strong>본인 사진만</strong> 올려 주세요 — 타인 사진 등록이 확인되면 계정이 정지됩니다.
          (<RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink>)
        </p>
      </section>

      <section class="card">
        <h2>2. 플랜과 쿼터</h2>
        <ul class="doc-list">
          <li>
            플랜마다 <strong>월 생성 쿼터</strong>, 등록 가능 아바타 수, 동시 활성 코드 수가 달라요.
          </li>
          <li>
            <strong>이미지가 성공적으로 만들어질 때마다 쿼터가 1 차감</strong>돼요. 생성이 실패하거나
            안전 필터에 걸려 차단되면 차감되지 않아요.
          </li>
          <li>
            <strong>팬이 리딤 코드로 만든 이미지도 내 쿼터에서 차감</strong>돼요. 코드를 배포할 땐
            사용 횟수 설정을 꼭 확인하세요.
          </li>
          <li>남은 쿼터는 다음 기간으로 이월되지 않아요.</li>
        </ul>
        <p class="doc-note">
          현재 <strong>결제는 연동 전</strong>이라 플랜을 고르면 과금 없이 쿼터가 바로 활성화돼요(데모).
        </p>
      </section>

      <section class="card">
        <h2>3. 직접 만들기 — 프롬프트 쓰는 법</h2>
        <p class="doc-p">
          <RouterLink to="/studio" class="doc-link">크리에이터 스튜디오</RouterLink>의
          <strong>직접 만들기</strong>에서 아바타를 고르고 원하는 장면을 문장으로 묘사하면 돼요.
        </p>
        <h3>좋은 프롬프트의 구성</h3>
        <ul class="doc-list">
          <li><strong>장소·배경</strong> — 노을 지는 해변, 도쿄 뒷골목, 흰 스튜디오 배경</li>
          <li><strong>의상</strong> — 리넨 셔츠, 겨울 코트에 목도리, 클래식한 정장</li>
          <li><strong>조명·분위기</strong> — 영화 같은 조명, 부드러운 자연광, 따뜻한 색감</li>
          <li><strong>구도</strong> — 상반신 클로즈업, 전신 샷, 살짝 위에서 내려다본 각도</li>
        </ul>
        <p class="doc-note">
          예시: <em>"노을 지는 해변, 베이지 리넨 셔츠, 바람에 날리는 머리카락, 영화 같은 역광,
          상반신 클로즈업"</em>
        </p>
        <h3>팁</h3>
        <ul class="doc-list">
          <li>한 문장에 다 넣기보다 <strong>쉼표로 요소를 나열</strong>하면 반영이 잘 돼요.</li>
          <li>마음에 드는 프롬프트는 따로 메모해 두면 다시 쓰기 좋아요.</li>
          <li>
            같은 프롬프트라도 결과는 매번 조금씩 달라져요. 여러 번 만들어 보고 고르는 걸 권장해요.
          </li>
          <li>
            모든 생성은 <strong>SFW(전 연령) 필터</strong>를 거쳐요. 선정적 표현은 생성 전에 차단됩니다.
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>4. 리딤 코드로 팬과 함께 만들기</h2>
        <p class="doc-p">
          스튜디오의 <strong>리딤 코드</strong> 섹션에서 아바타를 고르고 코드 개수·사용 횟수를 정해
          발급해요. 발급된 코드는 <strong>링크 복사</strong> 또는 <strong>QR</strong>로 공유할 수 있어요.
        </p>
        <h3>사용 횟수 정하기</h3>
        <ul class="doc-list">
          <li>
            <strong>1회용 코드를 여러 장</strong> — 이벤트 경품, 추첨처럼 1인 1회로 나눠줄 때.
          </li>
          <li>
            <strong>다회용 코드 1장</strong> — 멤버십 채널 등 신뢰할 수 있는 그룹에 하나만 공유할 때.
          </li>
          <li class="doc-callout">
            공개된 곳(공개 SNS 등)에 다회용 코드를 올리면 <strong>내 쿼터가 빠르게 소진</strong>될 수
            있어요. 공개 배포는 1회용 코드를 여러 장 만드는 방식을 권장해요. 문제가 생기면 언제든
            <strong>비활성화</strong>할 수 있어요.
          </li>
        </ul>
        <h3>팬이 보는 화면</h3>
        <p class="doc-p">
          팬은 링크를 열면 <strong>별도 가입 없이</strong> 원하는 장면을 프롬프트로 입력해 이미지를
          만들고 내려받을 수 있어요. 팬의 생성물에도 동일한 SFW 필터가 적용됩니다.
        </p>
      </section>

      <section class="card">
        <h2>5. 자주 묻는 질문</h2>
        <h3>생성이 실패했는데 쿼터가 차감됐나요?</h3>
        <p class="doc-p">아니요. 실패하거나 필터에 차단된 생성은 차감되지 않아요.</p>
        <h3>아바타를 여러 개 만들 수 있나요?</h3>
        <p class="doc-p">
          플랜마다 등록 가능 아바타 수가 정해져 있어요. 모두 본인 얼굴이어야 합니다.
        </p>
        <h3>발급한 코드를 회수할 수 있나요?</h3>
        <p class="doc-p">
          네. 스튜디오의 코드 목록에서 <strong>비활성화</strong>하면 즉시 사용이 중단돼요.
          이미 만들어진 이미지는 되돌릴 수 없어요.
        </p>
        <h3>내 얼굴이 도용된 것 같아요.</h3>
        <p class="doc-p">
          <RouterLink to="/support#report" class="doc-link">신고하기</RouterLink>에서 접수해 주세요.
          확인되면 해당 계정은 정지되고 아바타·코드가 삭제됩니다.
        </p>
      </section>

      <footer class="doc-foot">
        <p class="doc-meta">
          더 궁금한 점은 <RouterLink to="/support" class="doc-link">문의하기</RouterLink>로 알려주세요 ·
          <RouterLink to="/terms" class="doc-link">이용약관</RouterLink> ·
          <RouterLink to="/content-policy" class="doc-link">콘텐츠·초상권 정책</RouterLink>
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
