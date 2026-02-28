import apiClient from './api';

// Position interface matching backend schema
export interface Position {
  id: string;
  symbol: string;
  m2m: number;
  pnl: number;
  atpnl: number;
  realpl: number;
  unrealpl: number;
  netqty: number;
  ltp: number;
  buyqty: number;
  sellqty: number;
  buyval: number;
  sellval: number;
  netval: number;
  bavg: number;
  savg: number;
  state: string;
  direction: string;
  type: string;
  category: string;
  broker: string;
  overqty: number;
  multiplier: number;
  exch: string;
  brexch: string;
  brsymbol: string;
  day: string;
  platform: string;
  accid: string;
  account_id: number;
  last_updated: string;
}

export interface PositionListResponse {
  positions: Position[];
  total_positions: number;
  active_positions: number;
}

export const positionService = {
  /**
   * Get consolidated positions for all user's enabled accounts
   * @param openOnly If true, return only positions with net quantity != 0
   */
  getAll: async (openOnly: boolean = true): Promise<PositionListResponse> => {
    const response = await apiClient.get('/positions', {
      params: { open_only: openOnly }
    });
    return response.data;
  },
};
