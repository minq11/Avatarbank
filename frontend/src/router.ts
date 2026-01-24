import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import LandingPage from "./views/LandingPage.vue";
import MarketPage from "./views/MarketPage.vue";
import GenerationPage from "./views/GenerationPage.vue";
import MyGenerationsPage from "./views/MyGenerationsPage.vue";
import InfluencerDashboardPage from "./views/InfluencerDashboardPage.vue";
import PromptGenerationPage from "./views/PromptGenerationPage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "landing", component: LandingPage },
  { path: "/market", name: "market", component: MarketPage },
  { path: "/generate", name: "prompt-generate", component: PromptGenerationPage },
  { path: "/avatars/:id", name: "avatar-detail", component: GenerationPage },
  { path: "/my/generations", name: "my-generations", component: MyGenerationsPage },
  {
    path: "/influencer/dashboard",
    name: "influencer-dashboard",
    component: InfluencerDashboardPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;


