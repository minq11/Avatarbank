import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import LandingPage from "./views/LandingPage.vue";
import MarketPage from "./views/MarketPage.vue";
import GenerationPage from "./views/GenerationPage.vue";
import MyGenerationsPage from "./views/MyGenerationsPage.vue";
import MyAvatarsPage from "./views/MyAvatarsPage.vue";
import InfluencerDashboardPage from "./views/InfluencerDashboardPage.vue";
import AdminTrainingRequestsPage from "./views/AdminTrainingRequestsPage.vue";
import GalleryPage from "./views/GalleryPage.vue";
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
  { path: "/market", name: "market", component: MarketPage },
  { path: "/gallery", name: "gallery", component: GalleryPage },
  { path: "/generate", redirect: "/avatars" },
  { path: "/avatars", name: "generation", component: GenerationPage },
  { path: "/avatars/:id", name: "avatar-detail", component: GenerationPage },
  { path: "/my/generations", name: "my-generations", component: MyGenerationsPage },
  { path: "/my/avatars", name: "my-avatars", component: MyAvatarsPage },
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
    path: "/influencer/dashboard",
    name: "influencer-dashboard",
    component: InfluencerDashboardPage,
  },
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


