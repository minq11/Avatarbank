/**
 * API 서비스
 * axios 인스턴스 및 API 호출 함수들
 */

import axios, { AxiosInstance, AxiosError } from "axios";

// API 기본 URL
// 개발 환경: Vite proxy 사용 (/api)
// 프로덕션: 환경 변수 또는 기본값
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "/api" : "http://localhost:8000");

// axios 인스턴스 생성
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 인터셉터: Access Token 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 토큰 갱신 시도
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // 401 에러이고 아직 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem("access_token", access_token);

          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh Token도 만료된 경우 토큰 정리만 수행
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API 응답 타입
export interface ApiError {
  detail: string;
}

// 인증 API
export interface RegisterRequest {
  email: string;
  password: string;
  role?: "buyer" | "influencer";
  locale?: "en" | "ko" | "ja";
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  role: string;
  locale: string;
  credit_balance: number;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

// 인증 API 함수들
export const authApi = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>("/auth/register", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>("/auth/login", data);
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const response = await api.post<RefreshTokenResponse>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>("/auth/me");
    return response.data;
  },

  upgradeToSeller: async (): Promise<User> => {
    const response = await api.post<User>("/auth/upgrade-to-seller");
    return response.data;
  },
};
