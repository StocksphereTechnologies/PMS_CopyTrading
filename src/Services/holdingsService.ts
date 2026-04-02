import apiClient from "./api";

export interface Holding {
  pseAcc: string;
  trdAcc: string;
  exchange: string;
  symbol: string;

  totqty: number;
  ltp: number;
  currval: number;

  quantity: number;
  t1qty: number;

  pnl: number;

  product: string;

  nsesymbol: string;
  bsesymbol: string;
  isin: string;

  insttoken: string;

  collateralQty: number;
  collateralType: string;
  haircut: number;

  avgPrice: number;

  day: string;
  platform: string;
  broker: string;
}

export interface HoldingListResponse {
  holdings: Holding[];
  total: number;
}

export const holdingsService = {
  getAll: async (): Promise<HoldingListResponse> => {
    const response = await apiClient.get("/holdings");
    return response.data;
  },
};