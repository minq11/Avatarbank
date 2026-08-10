/**
 * Authentication State Management Store (Pinia)
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi, type User } from "../services/api";

export const useAuthStore = defineStore("auth", () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(localStorage.getItem("access_token"));
  const refreshToken = ref<string | null>(localStorage.getItem("refresh_token"));
  const isInitialized = ref(false);

  // 전역 인증 모달 상태 — 어느 페이지에서든 openAuthModal() 로 띄운다 (App.vue 가 렌더링).
  // postAuthRedirect: 로그인/가입 성공 후 이동할 경로 (홈 CTA → 가입 → 생성 페이지 흐름용)
  const authModalOpen = ref(false);
  const authModalMode = ref<"login" | "register">("login");
  const postAuthRedirect = ref<string | null>(null);

  const openAuthModal = (mode: "login" | "register" = "login", redirect?: string) => {
    authModalMode.value = mode;
    postAuthRedirect.value = redirect ?? null;
    authModalOpen.value = true;
  };

  const closeAuthModal = () => {
    authModalOpen.value = false;
  };

  /** 성공 시 1회성으로 리다이렉트 경로를 꺼내 간다 (없으면 null) */
  const consumePostAuthRedirect = (): string | null => {
    const r = postAuthRedirect.value;
    postAuthRedirect.value = null;
    return r;
  };

  // Getters
  const isLoggedIn = computed(() => !!user.value && !!accessToken.value);
  const userRole = computed(() => user.value?.role || null);
  const creditBalance = computed(() => user.value?.credit_balance || 0);

  // Actions
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access;
    refreshToken.value = refresh;
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  };

  const setUser = (userData: User) => {
    user.value = userData;
  };

  const clearAuth = () => {
    user.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password });
      setTokens(response.access_token, response.refresh_token);
      setUser(response.user);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      };
    }
  };

  const register = async (
    email: string,
    nickname: string,
    password: string,
    role: "buyer" | "influencer" = "buyer",
    locale: "en" | "ko" | "ja" = "en"
  ) => {
    try {
      await authApi.register({ email, nickname, password, role, locale });
      // Auto login after registration
      return await login(email, password);
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Registration failed",
      };
    }
  };

  /** 구글 로그인/가입 — GIS credential 로 백엔드 인증 후 토큰 저장 */
  const loginWithGoogle = async (credential: string) => {
    try {
      const response = await authApi.googleLogin(credential);
      setTokens(response.access_token, response.refresh_token);
      setUser(response.user);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "구글 로그인에 실패했어요.",
      };
    }
  };

  const logout = () => {
    clearAuth();
  };

  const fetchUser = async () => {
    if (!accessToken.value) {
      return;
    }

    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error: any) {
      const status = error?.response?.status;
      // Only logout on authentication failure (401)
      if (status === 401) {
        clearAuth();
      }
    }
  };

  // Initialize: Fetch user info if token exists
  const initialize = async () => {
    if (accessToken.value) {
      await fetchUser();
    }
    isInitialized.value = true;
  };

  // Check if user is Buyer
  const isBuyer = computed(() => userRole.value === "buyer");
  const isSeller = computed(() => userRole.value === "influencer");
  // 관리자 여부: ADMIN_EMAIL_WHITELIST 기반 (프론트 단 간단 판별)
  const isAdmin = computed(() => {
    const email = user.value?.email?.toLowerCase() || "";
    // 필요 시 여러 개로 확장 가능
    const adminWhitelist = ["minku0128@naver.com"];
    return adminWhitelist.includes(email);
  });

  return {
    // State
    user,
    accessToken,
    refreshToken,
    // Getters
    isLoggedIn,
    userRole,
    creditBalance,
    isBuyer,
    isSeller,
    isAdmin,
    isInitialized,
    // Auth modal (전역)
    authModalOpen,
    authModalMode,
    openAuthModal,
    closeAuthModal,
    consumePostAuthRedirect,
    // Actions
    login,
    register,
    loginWithGoogle,
    logout,
    fetchUser,
    initialize,
    setUser,
  };
});
