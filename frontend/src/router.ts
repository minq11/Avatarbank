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
import RevenueModelPage from "./views/RevenueModelPage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "landing", component: LandingPage },
  { path: "/revenue-model", name: "revenue-model", component: RevenueModelPage },
  { path: "/market", name: "market", component: MarketPage },
  { path: "/gallery", name: "gallery", component: GalleryPage },
  { path: "/generate", redirect: "/avatars" },
  { path: "/avatars", name: "generation", component: GenerationPage },
  { path: "/avatars/:id", name: "avatar-detail", component: GenerationPage },
  { path: "/my/generations", name: "my-generations", component: MyGenerationsPage },
  { path: "/my/avatars", name: "my-avatars", component: MyAvatarsPage },
  { path: "/my/page", name: "my-page", component: MyPage },
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_, __, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0 };
  },
});

export default router;


