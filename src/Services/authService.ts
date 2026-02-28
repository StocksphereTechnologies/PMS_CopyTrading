import apiClient from './api';

export interface SignupData {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  city?: string;
  state?: string;
  country?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  user_id: number;
  email: string;
  full_name: string;
  phone_number?: string;
  city?: string;
  state?: string;
  country?: string;
  is_active: boolean;
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  user_id: number;
  email: string;
  full_name: string;
  phone_number?: string;
  city?: string;
  state?: string;
  country?: string;
  is_active: boolean;
}

export const authService = {
  signup: async (data: SignupData): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/signup', data);
    return response.data;
  },

  login: async (data: LoginData): Promise<{ access_token: string; token_type: string }> => {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};
