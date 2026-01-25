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
    isInitialized,
    // Actions
    login,
    register,
    logout,
    fetchUser,
    initialize,
    setUser,
  };
});
