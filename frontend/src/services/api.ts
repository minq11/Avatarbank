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

  changePassword: async (data: { current_password: string; new_password: string }): Promise<User> => {
    const response = await api.put<User>("/auth/me/password", data);
    return response.data;
  },

  changeNickname: async (data: { nickname: string }): Promise<User> => {
    const response = await api.put<User>("/auth/me/nickname", data);
    return response.data;
  },
};

// Avatars API (public + my)
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
  up_count?: number;
  down_count?: number;
  comment_count?: number;
}

export interface AvatarListParams {
  q?: string;
  nationality?: string;
  gender?: string;
  sort?: "recommend" | "name" | "comments" | "newest";
}

export interface AvatarFilterOptions {
  nationalities: string[];
  genders: string[];
}

/** 마켓 모달용: creator_nickname, instagram_id 포함 */
export interface AvatarDetailItem extends AvatarItem {
  creator_nickname: string;
  instagram_id: string | null;
}

export interface AvatarRatingItem {
  up_count: number;
  down_count: number;
  my_vote: "up" | "down" | null;
}

export interface AvatarCommentItem {
  id: number;
  creator_nickname: string;
  content: string;
  created_at: string;
}

export interface UpdateAvatarData {
  title?: string;
  credit_per_generation?: number;
  description?: string;
  preview_image?: File;
}

export const avatarsApi = {
  getList: async (params?: AvatarListParams): Promise<AvatarItem[]> => {
    const response = await api.get<AvatarItem[]>("/avatars", { params });
    return response.data;
  },
  getFilterOptions: async (): Promise<AvatarFilterOptions> => {
    const response = await api.get<AvatarFilterOptions>("/avatars/filter-options");
    return response.data;
  },
  getById: async (id: number): Promise<AvatarDetailItem> => {
    const response = await api.get<AvatarDetailItem>(`/avatars/${id}`);
    return response.data;
  },
  getRating: async (avatarId: number): Promise<AvatarRatingItem> => {
    const response = await api.get<AvatarRatingItem>(`/avatars/${avatarId}/rating`);
    return response.data;
  },
  setRating: async (avatarId: number, type: "up" | "down"): Promise<AvatarRatingItem> => {
    const response = await api.put<AvatarRatingItem>(`/avatars/${avatarId}/rating`, { type });
    return response.data;
  },
  getComments: async (avatarId: number): Promise<AvatarCommentItem[]> => {
    const response = await api.get<AvatarCommentItem[]>(`/avatars/${avatarId}/comments`);
    return response.data;
  },
  createComment: async (avatarId: number, content: string): Promise<AvatarCommentItem> => {
    const response = await api.post<AvatarCommentItem>(`/avatars/${avatarId}/comments`, { content });
    return response.data;
  },
  getMyAvatars: async (): Promise<AvatarItem[]> => {
    const response = await api.get<AvatarItem[]>("/my/avatars");
    return response.data;
  },
  updateAvatar: async (
    id: number,
    data: UpdateAvatarData,
    onUploadProgress?: (percent: number) => void
  ): Promise<AvatarItem> => {
    const formData = new FormData();
    if (data.title) formData.append("title", data.title);
    if (data.credit_per_generation !== undefined) {
      formData.append("credit_per_generation", data.credit_per_generation.toString());
    }
    if (data.description) formData.append("description", data.description);
    if (data.preview_image) formData.append("preview_image", data.preview_image);

    const config =
      onUploadProgress ?
        {
          onUploadProgress: (ev: { loaded: number; total?: number }) => {
            if (ev.total != null && ev.total > 0) {
              onUploadProgress(Math.round((ev.loaded / ev.total) * 100));
            }
          },
        }
      : {};
    const response = await api.put<AvatarItem>(`/my/avatars/${id}`, formData, config);
    return response.data;
  },

  /** 아바타 삭제 (논리 삭제 + LoRA 실제 삭제) */
  deleteAvatar: async (id: number): Promise<void> => {
    await api.delete(`/my/avatars/${id}`);
  },

  /** LoRA(.safetensors) 파일 직접 업로드로 새 아바타 등록 */
  uploadLoRA: async (
    formData: FormData,
    onUploadProgress?: (percent: number) => void
  ): Promise<AvatarItem> => {
    const config = onUploadProgress
      ? {
          onUploadProgress: (ev: { loaded: number; total?: number }) => {
            if (ev.total != null && ev.total > 0) {
              onUploadProgress(Math.round((ev.loaded / ev.total) * 100));
            }
          },
        }
      : {};
    const response = await api.post<AvatarItem>("/my/avatars/upload-lora", formData, config);
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
  is_shared?: boolean;
  created_at: string;
}

export interface GalleryItem {
  id: number;
  image_url: string;
  prompt: string;
  created_at: string;
  creator_nickname: string;
}

export interface GenerationCreatePayload {
  avatar_id: number;
  prompt: string;
  option_credits: number;
  idempotency_key: string;
}

export const generationsApi = {
  getMyGenerations: async (): Promise<GenerationItem[]> => {
    const response = await api.get<GenerationItem[]>("/my/generations");
    return response.data;
  },
  getById: async (id: number): Promise<GenerationItem> => {
    const response = await api.get<GenerationItem>(`/generations/${id}`);
    return response.data;
  },
  create: async (data: GenerationCreatePayload): Promise<GenerationItem> => {
    const response = await api.post<GenerationItem>("/generations", data);
    return response.data;
  },
  toggleShare: async (id: number): Promise<GenerationItem> => {
    const response = await api.put<GenerationItem>(`/my/generations/${id}/share`);
    return response.data;
  },
};

export const galleryApi = {
  /** 공유된 생성물 목록. avatarId 지정 시 해당 아바타로 생성된 것만. limit/offset 있으면 페이지네이션(생략 시 전체). */
  getGenerations: async (
    avatarId?: number,
    limit?: number,
    offset?: number
  ): Promise<GalleryItem[]> => {
    const params: Record<string, number> = {};
    if (avatarId != null) params.avatar_id = avatarId;
    if (limit != null) params.limit = limit;
    if (offset != null) params.offset = offset;
    const response = await api.get<GalleryItem[]>("/gallery/generations", { params });
    return response.data;
  },
};

// Training Requests API
export interface TrainingRequestItem {
  id: number;
  avatar_name: string;
  status: "requested" | "approved_training" | "rejected" | "cancelled";
  created_at: string;
  updated_at: string;
}

/** 관리자용 목록: 요청자 정보 포함 */
export interface AdminTrainingRequestItem {
  id: number;
  avatar_name: string;
  status: "requested" | "approved_training" | "rejected" | "cancelled";
  created_at: string;
  updated_at: string;
  user_id: number;
  user_email: string;
  user_nickname: string;
}

export interface TrainingRequestDetailItem {
  id: number;
  avatar_name: string;
  negative_prompt: string | null;
  credit_per_generation: number;
  national: string | null;
  gender: string | null;
  description: string | null;
  is_real_person: boolean;
  instagram_id: string | null;
  preview_image_url: string | null;
  front_photos_urls: string[] | null;
  side_photos_urls: string[] | null;
  fullbody_photos_urls: string[] | null;
  other_photos_urls: string[] | null;
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

  getRequestDetail: async (id: number): Promise<TrainingRequestDetailItem> => {
    const response = await api.get<TrainingRequestDetailItem>(`/my/training-requests/${id}`);
    return response.data;
  },

  cancelRequest: async (id: number): Promise<TrainingRequestItem> => {
    const response = await api.patch<TrainingRequestItem>(`/my/training-requests/${id}/cancel`);
    return response.data;
  },

  /** 학습 요청 삭제 (논리 삭제 + 이미지 실제 삭제) */
  deleteRequest: async (id: number): Promise<void> => {
    await api.delete(`/my/training-requests/${id}`);
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

  // Admin APIs
  getAllRequestsAdmin: async (): Promise<AdminTrainingRequestItem[]> => {
    const response = await api.get<AdminTrainingRequestItem[]>("/admin/training-requests");
    return response.data;
  },

  getRequestDetailAdmin: async (id: number): Promise<TrainingRequestDetailItem> => {
    const response = await api.get<TrainingRequestDetailItem>(`/admin/training-requests/${id}`);
    return response.data;
  },

  downloadPhotosZipAdmin: async (id: number): Promise<Blob> => {
    const response = await api.get(`/admin/training-requests/${id}/photos.zip`, {
      responseType: "blob",
    });
    return response.data as Blob;
  },

  /** 관리자: LoRA(.safetensors) 업로드 → S3 업로드 후 Avatar 생성/갱신 */
  getLoraDownloadUrlAdmin: async (requestId: number): Promise<{ url: string }> => {
    const response = await api.get<{ url: string }>(
      `/admin/training-requests/${requestId}/lora`
    );
    return response.data;
  },

  uploadLoRAAdmin: async (
    requestId: number,
    file: File,
    onUploadProgress?: (percent: number) => void
  ): Promise<AvatarItem> => {
    const formData = new FormData();
    formData.append("lora_file", file);
    const response = await api.post<AvatarItem>(
      `/admin/training-requests/${requestId}/upload-lora`,
      formData,
      {
        onUploadProgress: (ev) => {
          if (ev.total != null && ev.total > 0 && onUploadProgress) {
            onUploadProgress(Math.round((ev.loaded / ev.total) * 100));
          }
        },
      }
    );
    return response.data;
  },
};

