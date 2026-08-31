/**
 * 사업자 정보 — 전자상거래법상 표시 의무 항목.
 *
 * 여기 한 곳만 채우면 푸터(App.vue)와 개인정보처리방침(PrivacyPage.vue)에
 * 동시에 반영된다. 같은 값을 여러 파일에 흩어두면 사업장을 옮기거나
 * 연락처가 바뀔 때 한 곳을 빠뜨리게 되므로 단일 출처로 둔다.
 *
 * ── 중요 ──
 * 빈 문자열("")인 항목은 화면에 아예 렌더링되지 않는다.
 * 따라서 값을 채우기 전까지 "상호명 미정" 같은 자리표시자가 사용자에게
 * 노출되는 일은 없다. 거짓 사업자 정보를 띄우는 것보다 안 띄우는 편이 낫다.
 *
 * 통신판매업신고번호는 정부24 신고가 끝나야 나온다. 그전까지는 비워둔다.
 */
export const business = {
  /** 상호명 (사업자등록증상 명칭) */
  companyName: "",
  /** 대표자명 */
  ceoName: "",
  /** 사업자등록번호 (예: 123-45-67890) */
  registrationNumber: "",
  /** 통신판매업신고번호 (예: 제2026-서울강남-01234호) */
  mailOrderNumber: "",
  /** 사업장 주소 */
  address: "",
  /** 고객센터 전화번호 — 전자상거래법상 표시 의무 */
  phone: "",
  /** 고객 문의 이메일 */
  email: "gooddonutsyh@gmail.com",

  /**
   * 개인정보 보호책임자 — 개인정보보호법상 성명과 연락처 기재 의무가 있다.
   * 1인 사업자면 대표자가 겸임하는 것이 일반적이다.
   */
  privacyOfficer: {
    name: "",
    title: "",
    email: "",
  },
} as const;

/**
 * 사업자 정보 블록을 렌더링할지 여부.
 * 상호명과 사업자등록번호가 모두 있을 때만 의미 있는 표시가 된다.
 */
export const hasBusinessInfo = Boolean(
  business.companyName && business.registrationNumber
);

/**
 * 개인정보 보호책임자 블록을 렌더링할지 여부.
 */
export const hasPrivacyOfficer = Boolean(business.privacyOfficer.name);
