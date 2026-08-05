<template>
  <div class="doc-page">
    <div class="doc-container">
      <header class="doc-head">
        <h1>개인정보처리방침</h1>
        <p class="doc-meta">시행일 2026년 8월 5일 · 최종 개정 2026년 8월 5일</p>
        <p class="doc-lead">
          AvatarBank(이하 "서비스")는 이용자의 개인정보를 소중히 다루며, 「개인정보 보호법」 등
          관련 법령을 준수합니다. 본 방침은 서비스가 <strong>실제로 수집하는 항목</strong>과
          그 처리 방식을 있는 그대로 설명합니다.
        </p>
      </header>

      <nav class="doc-toc card">
        <h2>목차</h2>
        <ol>
          <li><a href="#p1">1. 수집하는 개인정보 항목</a></li>
          <li><a href="#p2">2. 얼굴 사진의 처리 (민감할 수 있는 정보)</a></li>
          <li><a href="#p3">3. 개인정보의 이용 목적</a></li>
          <li><a href="#p4">4. 처리위탁과 국외 이전</a></li>
          <li><a href="#p5">5. 보유 및 파기</a></li>
          <li><a href="#p6">6. 이용자의 권리와 행사 방법</a></li>
          <li><a href="#p7">7. 안전성 확보 조치</a></li>
          <li><a href="#p8">8. 쿠키 및 로컬 저장소</a></li>
          <li><a href="#p9">9. 아동의 개인정보</a></li>
          <li><a href="#p10">10. 문의처 및 방침 변경</a></li>
        </ol>
      </nav>

      <section id="p1" class="card">
        <h2>1. 수집하는 개인정보 항목</h2>
        <div class="doc-table-wrap">
          <table class="doc-table">
            <thead>
              <tr>
                <th>구분</th>
                <th>항목</th>
                <th>수집 시점</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>회원 가입</td>
                <td>이메일, 닉네임, 비밀번호(단방향 암호화하여 저장)</td>
                <td>가입 시</td>
              </tr>
              <tr>
                <td>아바타 등록</td>
                <td>
                  얼굴·전신 사진(정면·측면·전신·기타), 아바타 이름·설명,
                  선택 입력한 국적·성별·나이·키·몸무게·특이사항,
                  본인 확인용으로 입력한 경우 인스타그램 아이디
                </td>
                <td>아바타 등록 요청 시</td>
              </tr>
              <tr>
                <td>이미지 생성</td>
                <td>입력한 프롬프트, 생성된 이미지, 생성 일시·상태</td>
                <td>생성 시</td>
              </tr>
              <tr>
                <td>구독·쿼터</td>
                <td>선택한 플랜, 잔여 쿼터, 이용 내역</td>
                <td>플랜 선택 및 이용 시</td>
              </tr>
              <tr>
                <td>리딤 코드</td>
                <td>발급한 코드, 사용 횟수, 코드로 생성된 이미지</td>
                <td>코드 발급·사용 시</td>
              </tr>
              <tr>
                <td>고객 문의</td>
                <td>이름, 회신용 이메일, 문의 분류·제목·내용, 접속 IP</td>
                <td>문의 접수 시</td>
              </tr>
              <tr>
                <td>자동 생성</td>
                <td>최근 로그인 일시, 서비스 이용 기록, 오류 로그</td>
                <td>서비스 이용 중</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="doc-note">
          <strong>비회원 문의:</strong> 로그인하지 않고도 문의를 접수할 수 있으며, 이 경우 회원 정보와
          연결되지 않고 문의 내용만 저장됩니다. 문의 시 수집하는 IP는 스팸·악용 대응 목적으로만 사용합니다.
        </p>
      </section>

      <section id="p2" class="card">
        <h2>2. 얼굴 사진의 처리 (민감할 수 있는 정보)</h2>
        <p class="doc-p">
          서비스의 핵심 기능상 <strong>이용자의 얼굴 사진</strong>을 수집합니다. 이는 다른 정보보다
          민감하게 다뤄야 하므로 별도로 안내합니다.
        </p>
        <ul class="doc-list">
          <li>
            얼굴 사진은 <strong>이용자 본인의 아바타(AI 모델)를 학습시키는 목적으로만</strong> 사용하며,
            광고·마케팅이나 타인의 아바타 학습에 사용하지 않습니다.
          </li>
          <li>
            <strong>본인의 사진만 등록할 수 있습니다.</strong> 관리자는 도용 여부 확인을 위해 제출된
            사진을 열람하며, 심사와 학습에는 2~7일이 소요됩니다.
          </li>
          <li>
            사진은 아마존 웹 서비스(AWS) S3 저장소에 보관되며, 접근 권한이 있는 담당자만 열람할 수 있습니다.
          </li>
          <li>
            아바타 삭제를 요청하면 해당 아바타와 연결된 학습 사진의 이용을 중단하고 파기합니다.
          </li>
        </ul>
      </section>

      <section id="p3" class="card">
        <h2>3. 개인정보의 이용 목적</h2>
        <ul class="doc-list">
          <li>회원 식별 및 로그인 유지, 계정 보안</li>
          <li>아바타 학습·생성 등 서비스 제공, 잔여 쿼터 관리</li>
          <li>아바타 등록 심사(타인 사진 도용 방지)</li>
          <li>안전 필터 적용 등 콘텐츠 정책 준수 확인</li>
          <li>고객 문의 접수 및 회신</li>
          <li>부정 이용·스팸 대응, 장애 대응 및 서비스 개선</li>
        </ul>
      </section>

      <section id="p4" class="card">
        <h2>4. 처리위탁과 국외 이전</h2>
        <p class="doc-p">
          서비스는 아래 사업자에게 개인정보 처리를 위탁하고 있으며, 해당 사업자의 서버가
          <strong>국외에 위치</strong>합니다.
        </p>
        <div class="doc-table-wrap">
          <table class="doc-table">
            <thead>
              <tr>
                <th>수탁자</th>
                <th>위탁 업무</th>
                <th>이전 항목</th>
                <th>보관 국가</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>fal.ai</td>
                <td>AI 이미지 생성 처리</td>
                <td>학습된 아바타 모델, 생성 프롬프트</td>
                <td>미국</td>
              </tr>
              <tr>
                <td>Amazon Web Services (AWS)</td>
                <td>이미지·파일 저장(S3)</td>
                <td>학습용 사진, 생성 이미지</td>
                <td>미국</td>
              </tr>
              <tr>
                <td>Google (Gmail SMTP)</td>
                <td>문의 접수 알림 및 답변 메일 발송</td>
                <td>이름, 이메일, 문의 내용</td>
                <td>미국</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="doc-note">
          이전 일시·방법: 서비스 이용 시점에 네트워크를 통해 암호화 전송됩니다. 이용자는 국외 이전을
          거부할 수 있으나, 이 경우 이미지 생성 등 핵심 기능을 이용할 수 없습니다.
          위 목적 외의 제3자 제공은 하지 않으며, 법령에 따른 요청이 있는 경우에만 예외적으로 제공합니다.
        </p>
      </section>

      <section id="p5" class="card">
        <h2>5. 보유 및 파기</h2>
        <ul class="doc-list">
          <li>
            <strong>회원 정보:</strong> 회원 탈퇴 시 지체 없이 파기합니다. 다만 부정 이용 재발 방지를 위해
            필요한 최소한의 식별 정보는 최대 30일간 보관 후 파기할 수 있습니다.
          </li>
          <li>
            <strong>아바타 학습 사진:</strong> 아바타 삭제 또는 회원 탈퇴 시 파기합니다.
          </li>
          <li>
            <strong>생성 이미지·프롬프트:</strong> 회원 탈퇴 시 파기합니다. 이용자가 공개(공유)한
            생성물은 공유를 해제하면 노출이 중단됩니다.
          </li>
          <li>
            <strong>고객 문의 기록:</strong> 분쟁 대응을 위해 접수일로부터 3년간 보관 후 파기합니다.
          </li>
          <li>
            전자상거래법 등 관련 법령이 별도의 보존 기간을 정한 경우 해당 기간 동안 보관합니다.
          </li>
        </ul>
        <p class="doc-p">
          파기 방법: 전자적 파일은 복구할 수 없는 방식으로 삭제하며, 출력물이 있는 경우 분쇄합니다.
        </p>
      </section>

      <section id="p6" class="card">
        <h2>6. 이용자의 권리와 행사 방법</h2>
        <p class="doc-p">
          이용자는 언제든 본인의 개인정보에 대해 열람, 정정, 삭제, 처리정지를 요구할 수 있습니다.
        </p>
        <ul class="doc-list">
          <li>계정 정보 확인·수정: 로그인 후 <strong>계정 관리</strong> 메뉴</li>
          <li>아바타·생성물 삭제: <strong>내 아바타</strong> / <strong>내 생성물</strong> 메뉴</li>
          <li>
            그 밖의 열람·삭제·처리정지 요청:
            <RouterLink to="/support" class="doc-link">문의하기</RouterLink>에서 분류를 "계정/로그인"으로
            선택해 접수
          </li>
        </ul>
        <p class="doc-p">
          요청은 접수일로부터 10일 이내에 처리하며, 처리 결과를 회신 이메일로 안내합니다.
        </p>
      </section>

      <section id="p7" class="card">
        <h2>7. 안전성 확보 조치</h2>
        <ul class="doc-list">
          <li>비밀번호는 복호화가 불가능한 방식으로 암호화하여 저장합니다.</li>
          <li>인증에는 만료 시간이 있는 토큰을 사용하며, 통신은 HTTPS로 암호화합니다.</li>
          <li>관리자 기능은 지정된 관리자 계정만 접근할 수 있도록 제한합니다.</li>
          <li>공개 엔드포인트에는 요청 빈도 제한을 적용해 자동화된 악용을 차단합니다.</li>
          <li>개인정보 취급 담당자를 최소한으로 지정하고 접근 권한을 관리합니다.</li>
        </ul>
      </section>

      <section id="p8" class="card">
        <h2>8. 쿠키 및 로컬 저장소</h2>
        <p class="doc-p">
          서비스는 로그인 상태 유지를 위해 브라우저의 로컬 저장소에 인증 토큰을 보관합니다.
          광고·행태정보 수집 목적의 제3자 추적 쿠키는 사용하지 않습니다. 브라우저 설정에서
          저장소를 삭제하면 로그아웃되며, 이후에도 서비스 이용에는 제한이 없습니다.
        </p>
      </section>

      <section id="p9" class="card">
        <h2>9. 아동의 개인정보</h2>
        <p class="doc-p">
          서비스는 만 14세 미만 아동의 가입을 받지 않습니다. 또한 미성년자를 대상으로 하거나
          미성년자로 묘사되는 이미지의 생성을 금지하며, 이를 시도하는 계정은 즉시 정지됩니다.
          만 14세 미만 아동의 정보가 수집된 사실을 알게 되면 지체 없이 파기합니다.
        </p>
      </section>

      <section id="p10" class="card">
        <h2>10. 문의처 및 방침 변경</h2>
        <p class="doc-p">
          개인정보 관련 문의·불만은
          <RouterLink to="/support" class="doc-link">고객지원</RouterLink>을 통해 접수해 주세요.
          접수된 문의는 담당자가 확인 후 회신 이메일로 답변드립니다.
        </p>
        <!--
          TODO(나중에할일.md): 사업자 등록 후 상호·대표자·사업자등록번호·통신판매업신고번호·주소와
          개인정보 보호책임자 성명·직위·연락처를 여기에 기재할 것.
        -->
        <p class="doc-p">
          본 방침이 변경되는 경우 시행 7일 전부터 서비스 내 공지하며, 이용자에게 불리한 중대한
          변경은 30일 전에 공지합니다.
        </p>
        <p class="doc-note">
          개인정보 침해에 대한 신고·상담이 필요한 경우 아래 기관에 문의할 수 있습니다.<br />
          개인정보침해신고센터 (privacy.kisa.or.kr / 국번없이 118) ·
          개인정보 분쟁조정위원회 (kopico.go.kr / 1833-6972) ·
          대검찰청 사이버수사과 (1301) · 경찰청 사이버수사국 (182)
        </p>
      </section>

      <footer class="doc-foot">
        <p class="doc-meta">
          관련 문서:
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
