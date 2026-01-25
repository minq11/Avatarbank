/**
 * API Service
 * axios instance and API call functions
 */

import axios, { AxiosInstance, AxiosError } from "axios";

// API base URL
// Development: Use Vite proxy (/api)
// Production: Environment variable or default value
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "/api" : "http://localhost:8000");

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Automatically add Access Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    // FormData를 전송할 때는 Content-Type을 제거 (브라우저가 자동으로 설정)
    if (config.data instanceof FormData) {
      delete config.headers["Content-Type"];
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Try token refresh on 401 error
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // 401 error and not yet retried
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

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If Refresh Token is also expired, only clear tokens
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API response types
export interface ApiError {
  detail: string;
}

// Authentication API
export interface RegisterRequest {
  email: string;
  nickname: string;
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
  nickname: string;
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

// Authentication API functions
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
};

// Generations API
export interface GenerationItem {
  id: number;
  avatar_id: number | null;
  buyer_id: number;
  credits_used: number;
  prompt: string;
  request_id: string | null;
  image_url: string | null;
  seed: string | null;
  status: string;
  fail_reason: string | null;
  nsfw_flag: boolean | null;
  created_at: string;
}

export const generationsApi = {
  getMyGenerations: async (): Promise<GenerationItem[]> => {
    const response = await api.get<GenerationItem[]>("/my/generations");
    return response.data;
  },
};

// Training Requests API
export interface TrainingRequestItem {
  id: number;
  avatar_name: string;
  status: "requested" | "approved_training" | "rejected";
  created_at: string;
  updated_at: string;
}

export interface CreateTrainingRequestData {
  avatar_name: string;
  negative_prompt: string;
  credit_per_generation: number;
  national: string;
  gender: string;
  description: string;
  is_real_person: boolean;
  instagram_id?: string;
  preview_image: File;
  front_photos: File[];
  side_photos: File[];
  fullbody_photos: File[];
  other_photos: File[];
}

export const trainingRequestsApi = {
  getMyRequests: async (): Promise<TrainingRequestItem[]> => {
    const response = await api.get<TrainingRequestItem[]>("/my/training-requests");
    return response.data;
  },

  createRequest: async (data: CreateTrainingRequestData): Promise<TrainingRequestItem> => {
    const formData = new FormData();
    formData.append("avatar_name", data.avatar_name);
    formData.append("negative_prompt", data.negative_prompt);
    formData.append("credit_per_generation", data.credit_per_generation.toString());
    formData.append("national", data.national);
    formData.append("gender", data.gender);
    formData.append("description", data.description);
    // is_real_person은 boolean이어야 함 (null이면 false로 변환)
    const isRealPerson = data.is_real_person === true;
    formData.append("is_real_person", String(isRealPerson));
    if (isRealPerson && data.instagram_id) {
      formData.append("instagram_id", data.instagram_id);
    }
    // preview_image는 필수
    formData.append("preview_image", data.preview_image);
    
    data.front_photos.forEach((file, index) => {
      formData.append(`front_photos`, file);
    });
    data.side_photos.forEach((file, index) => {
      formData.append(`side_photos`, file);
    });
    data.fullbody_photos.forEach((file, index) => {
      formData.append(`fullbody_photos`, file);
    });
    data.other_photos.forEach((file, index) => {
      formData.append(`other_photos`, file);
    });

    const response = await api.post<TrainingRequestItem>("/my/training-requests", formData);
    return response.data;
  },
};

// Avatars API
export interface AvatarItem {
  id: number;
  title: string;
  description: string | null;
  nationality: string | null;
  gender: string | null;
  preview_image_url: string | null;
  credit_per_generation: number | null;
  negative_prompt: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateAvatarData {
  title?: string;
  credit_per_generation?: number;
  description?: string;
  preview_image?: File;
}

export const avatarsApi = {
  getMyAvatars: async (): Promise<AvatarItem[]> => {
    const response = await api.get<AvatarItem[]>("/my/avatars");
    return response.data;
  },

  updateAvatar: async (id: number, data: UpdateAvatarData): Promise<AvatarItem> => {
    const formData = new FormData();
    if (data.title) formData.append("title", data.title);
    if (data.credit_per_generation !== undefined) {
      formData.append("credit_per_generation", data.credit_per_generation.toString());
    }
    if (data.description) formData.append("description", data.description);
    if (data.preview_image) formData.append("preview_image", data.preview_image);

    const response = await api.put<AvatarItem>(`/my/avatars/${id}`, formData);
    return response.data;
  },
};
