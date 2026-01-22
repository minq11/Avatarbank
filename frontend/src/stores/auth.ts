/**
 * 인증 상태 관리 Store (Pinia)
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi, type User } from "../services/api";

export const useAuthStore = defineStore("auth", () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(localStorage.getItem("access_token"));
  const refreshToken = ref<string | null>(localStorage.getItem("refresh_token"));

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
    password: string,
    role: "buyer" | "influencer" = "buyer",
    locale: "en" | "ko" | "ja" = "en"
  ) => {
    try {
      await authApi.register({ email, password, role, locale });
      // 회원가입 후 자동 로그인
      return await login(email, password);
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Registration failed",
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
    } catch (error) {
      // 토큰이 유효하지 않으면 로그아웃
      clearAuth();
    }
  };

  // 초기화: 저장된 토큰이 있으면 사용자 정보 가져오기
  const initialize = async () => {
    if (accessToken.value) {
      await fetchUser();
    }
  };

  return {
    // State
    user,
    accessToken,
    refreshToken,
    // Getters
    isLoggedIn,
    userRole,
    creditBalance,
    // Actions
    login,
    register,
    logout,
    fetchUser,
    initialize,
    setUser,
  };
});
