/**
 * 페이지별 제목·설명 관리.
 *
 * SPA 라서 index.html 의 <title> 은 최초 1회만 적용되고, 라우트를 옮겨도
 * 그대로 남는다. 검색엔진 입장에서는 모든 주소가 같은 제목·설명을 가진
 * 문서로 보여서 개별 페이지가 따로 잡히지 않는다. 라우터 이동마다 여기서
 * 덮어쓴다.
 *
 * 한글 키워드가 실제로 문서에 존재해야 한글 검색에 걸린다. 영문 브랜드명만
 * 있으면 "아바타클럽" 으로 검색했을 때 매칭될 문자열이 없다.
 */

const SITE = "아바타클럽";
const ORIGIN = "https://avatarclub.net";

interface PageSeo {
  title: string;
  description: string;
}

/** 라우트 name → 제목·설명. 여기 없는 라우트는 기본값을 쓴다. */
const PAGES: Record<string, PageSeo> = {
  landing: {
    title: `${SITE} — 내 얼굴로 만드는 AI 아바타`,
    description:
      "사진 몇 장으로 내 얼굴을 학습시켜 AI 아바타를 만드세요. 원하는 장면을 한국어로 적으면 이미지가 됩니다. 구독료 없이 크레딧으로 이용하세요.",
  },
  pricing: {
    title: `크레딧 안내 — ${SITE}`,
    description:
      "아바타클럽 크레딧 가격과 이용 방법. 크레딧 1개로 이미지 1장을 만듭니다. 구독료 없이 필요한 만큼만 구매하고, 미사용 크레딧은 환불받을 수 있습니다.",
  },
  "creator-studio": {
    title: `크리에이터 스튜디오 — ${SITE}`,
    description:
      "내 AI 아바타로 이미지를 만들고, 팬에게 리딤 링크를 나눠주세요. 크레딧 잔액과 생성 기록을 한 곳에서 관리합니다.",
  },
  "direct-create": {
    title: `아바타 만들기 — ${SITE}`,
    description:
      "내 얼굴 모델로 원하는 장면을 만드세요. 한국어로 적으면 됩니다 — 배경, 옷, 분위기를 자유롭게 묘사하면 이미지가 나옵니다.",
  },
  "my-avatars": {
    title: `내 아바타 — ${SITE}`,
    description:
      "등록한 내 얼굴 모델을 확인하고 관리합니다. 아바타마다 생성 기록과 미리보기를 볼 수 있습니다.",
  },
  "avatar-create": {
    title: `내 얼굴 모델 만들기 — ${SITE}`,
    description:
      "사진 몇 장만 올리면 내 얼굴을 학습한 AI 아바타가 만들어집니다. 학습이 끝나면 어떤 장면이든 내 얼굴로 생성할 수 있습니다.",
  },
  "my-generations": {
    title: `내 생성물 — ${SITE}`,
    description: "지금까지 만든 이미지를 모아 봅니다.",
  },
  guide: {
    title: `크리에이터 가이드 — ${SITE}`,
    description:
      "아바타 등록부터 이미지 생성, 팬에게 리딤 링크를 나눠주는 방법까지 단계별로 안내합니다.",
  },
  support: {
    title: `고객지원 — ${SITE}`,
    description: "문의하기, 도용·권리침해 신고. 영업일 기준 3일 이내에 답변드립니다.",
  },
  terms: {
    title: `이용약관 — ${SITE}`,
    description: "아바타클럽 이용약관. 크레딧, 결제, 취소 및 환불 규정을 확인하세요.",
  },
  privacy: {
    title: `개인정보처리방침 — ${SITE}`,
    description: "아바타클럽이 수집하는 개인정보와 처리 방침, 보관 기간을 안내합니다.",
  },
  "content-policy": {
    title: `콘텐츠·초상권 정책 — ${SITE}`,
    description:
      "타인의 얼굴 무단 등록 금지, 음란물·범죄적 이미지 금지 등 콘텐츠 정책을 안내합니다.",
  },
  redeem: {
    title: `리딤 링크로 이미지 만들기 — ${SITE}`,
    description: "크리에이터가 나눠준 링크로 이미지를 만들어 보세요. 가입 없이 이용할 수 있습니다.",
  },
};

const FALLBACK: PageSeo = PAGES.landing;

/**
 * <meta> 를 찾아 content 를 갱신한다. 없으면 만든다.
 * name= 과 property= 두 가지를 다 써야 해서 키 이름을 인자로 받는다
 * (description 은 name, OG 는 property).
 */
function setMeta(key: "name" | "property", keyValue: string, content: string) {
  const selector = `meta[${key}="${keyValue}"]`;
  let el = document.head.querySelector<HTMLMetaElement>(selector);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(key, keyValue);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function setLink(rel: string, href: string) {
  let el = document.head.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`);
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", rel);
    document.head.appendChild(el);
  }
  el.setAttribute("href", href);
}

/**
 * 라우트에 맞춰 제목·설명·canonical·OG 를 갱신한다.
 * 라우터의 afterEach 에서 호출한다.
 */
export function applyPageSeo(routeName: string | null | undefined, path: string): void {
  const seo = (routeName && PAGES[routeName]) || FALLBACK;

  document.title = seo.title;
  setMeta("name", "description", seo.description);
  setMeta("property", "og:title", seo.title);
  setMeta("property", "og:description", seo.description);

  // 쿼리스트링은 제외한다 — 같은 문서가 여러 주소로 중복 색인되는 걸 막는다.
  const url = ORIGIN + path.split("?")[0];
  setMeta("property", "og:url", url);
  setLink("canonical", url);
}
