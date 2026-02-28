import apiClient from './api';

// Exact backend schema types
export interface ZerodhaAccountData {
  broker_name: 'ZERODHA';
  trading_login_id: string;
  trading_password: string;
  totp_secret_key: string;
  api_key: string;
  api_secret: string;
  nickname?: string;
  is_enabled?: boolean;
}

export interface FivePaisaAccountData {
  broker_name: 'FIVEPAISA';
  trading_login_id: string;
  mpin: string;
  totp_secret_key: string;
  user_id: string;
  login_password: string;
  user_key: string;
  app_source: string;
  api_key?: string;
  api_secret?: string;
  nickname?: string;
  is_enabled?: boolean;
}

export type AccountCreateData = ZerodhaAccountData | FivePaisaAccountData;

export interface ValidationResponse {
  valid: boolean;
  message: string;
  broker: string;
}

export interface Account {
  account_id: number;
  owner_id: number;
  broker_name: string;
  nickname?: string;
  trading_login_id: string;
  is_enabled: boolean;
  is_validated: boolean;
  is_paid: boolean;
  token_generated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountListResponse {
  accounts: Account[];
  total: number;
}

export const accountService = {
  // Validate credentials (doesn't save)
  validate: async (data: AccountCreateData): Promise<ValidationResponse> => {
    const response = await apiClient.post('/accounts/validate', data);
    return response.data;
  },

  // Create account (saves after validation)
  create: async (data: AccountCreateData): Promise<Account> => {
    const response = await apiClient.post('/accounts', data);
    return response.data;
  },

  // Get all user's accounts
  getAll: async (enabledOnly?: boolean): Promise<AccountListResponse> => {
    const params = enabledOnly ? { enabled_only: true } : {};
    const response = await apiClient.get('/accounts', { params });
    return response.data;
  },

  // Get single account
  getById: async (accountId: number): Promise<Account> => {
    const response = await apiClient.get(`/accounts/${accountId}`);
    return response.data;
  },

  // Update account
  update: async (accountId: number, data: Partial<AccountCreateData>): Promise<Account> => {
    const response = await apiClient.put(`/accounts/${accountId}`, data);
    return response.data;
  },

  // Delete account
  delete: async (accountId: number): Promise<void> => {
    await apiClient.delete(`/accounts/${accountId}`);
  },

  // Get manual authorization URL for Zerodha
  getZerodhaLoginUrl: async (accountId: number): Promise<{ login_url: string }> => {
    const response = await apiClient.get(`/accounts/${accountId}/zerodha/login-url`);
    return response.data;
  },
};
