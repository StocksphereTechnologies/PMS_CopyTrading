import apiClient from './api';

// Margin data interfaces matching backend schemas
export interface MarginAvailable {
  cash: number;
  opening_balance: number;
  live_balance: number;
  collateral: number;
  adhoc_margin: number;
  intraday_payin: number;
}

export interface MarginUtilised {
  debits: number;
  exposure: number;
  m2m_realised: number;
  m2m_unrealised: number;
  option_premium: number;
  payout: number;
  span: number;
  holding_sales: number;
  turnover: number;
  liquid_collateral: number;
  stock_collateral: number;
  delivery: number;
}

export interface SegmentMargin {
  enabled: boolean;
  net: number;
  available: MarginAvailable;
  utilised: MarginUtilised;
}

export interface AccountMargin {
  account_id: number;
  broker_name: string;
  nickname?: string;
  trading_login_id: string;
  equity: SegmentMargin;
  commodity?: SegmentMargin;
  last_updated: string;
}

export interface MarginListResponse {
  margins: AccountMargin[];
  total_accounts: number;
}

export const marginService = {
  /**
   * Get margin data for all user's enabled accounts
   */
  getAll: async (): Promise<MarginListResponse> => {
    const response = await apiClient.get('/accounts/margins');
    return response.data;
  },
};
