import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import LandingPage from "./views/LandingPage.vue";
import MyGenerationsPage from "./views/MyGenerationsPage.vue";
import MyAvatarsPage from "./views/MyAvatarsPage.vue";
import AvatarCreatePage from "./views/AvatarCreatePage.vue";
import AdminTrainingRequestsPage from "./views/AdminTrainingRequestsPage.vue";
import MyPage from "./views/MyPage.vue";
import CreatorStudioPage from "./views/CreatorStudioPage.vue";
import DirectCreatePage from "./views/DirectCreatePage.vue";
import RedeemPage from "./views/RedeemPage.vue";
import TermsPage from "./views/TermsPage.vue";
import PrivacyPage from "./views/PrivacyPage.vue";
import ContentPolicyPage from "./views/ContentPolicyPage.vue";
import GuidePage from "./views/GuidePage.vue";
import SupportPage from "./views/SupportPage.vue";
import AdminInquiriesPage from "./views/AdminInquiriesPage.vue";
import PaymentSuccessPage from "./views/PaymentSuccessPage.vue";
import PaymentFailPage from "./views/PaymentFailPage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "landing", component: LandingPage },
  // 피벗 전 마켓플레이스 경로들(/market, /avatars, /generate, /gallery)은 제거됐다.
  // 남의 아바타를 골라 생성하거나 공개 갤러리에 전시하는 흐름이 사라졌고,
  // 생성은 /studio/create 하나로 모인다. 기존 링크가 죽지 않게 리다이렉트만 남긴다.
  { path: "/generate", redirect: "/studio/create" },
  { path: "/avatars", redirect: "/studio/create" },
  { path: "/market", redirect: "/" },
  { path: "/gallery", redirect: "/" },
  { path: "/my/generations", name: "my-generations", component: MyGenerationsPage },
  { path: "/my/avatars", name: "my-avatars", component: MyAvatarsPage },
  // 아바타 생성 요청 — 팝업이 아니라 전용 페이지 (홈 CTA 가 여기로 유도한다)
  { path: "/my/avatars/new", name: "avatar-create", component: AvatarCreatePage },
  { path: "/my/page", name: "my-page", component: MyPage },
  { path: "/studio", name: "creator-studio", component: CreatorStudioPage },
  { path: "/studio/create", name: "direct-create", component: DirectCreatePage },
  { path: "/r/:code", name: "redeem", component: RedeemPage },
  // 토스 결제창이 돌아오는 주소 (backend PAYMENT_SUCCESS_URL / PAYMENT_FAIL_URL 와 일치해야 함)
  { path: "/payments/success", name: "payment-success", component: PaymentSuccessPage },
  { path: "/payments/fail", name: "payment-fail", component: PaymentFailPage },
  // 푸터: 정책·안내·지원 페이지
  { path: "/terms", name: "terms", component: TermsPage },
  { path: "/privacy", name: "privacy", component: PrivacyPage },
  { path: "/content-policy", name: "content-policy", component: ContentPolicyPage },
  { path: "/guide", name: "guide", component: GuidePage },
  { path: "/support", name: "support", component: SupportPage },
  {
    path: "/admin/training-requests",
    name: "admin-training-requests",
    component: AdminTrainingRequestsPage,
  },
  {
    path: "/admin/inquiries",
    name: "admin-inquiries",
    component: AdminInquiriesPage,
  },
  // 없는 주소는 빈 화면 대신 홈으로. 반드시 마지막에 와야 한다 (앞의 규칙을 다 훑은 뒤 매칭)
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, __, savedPosition) {
    if (savedPosition) return savedPosition;
    // /support#report, /content-policy#report 같은 앵커 링크 지원
    if (to.hash) return { el: to.hash, behavior: "smooth" };
    return { top: 0 };
  },
});

export default router;


