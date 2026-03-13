import apiClient from './api';

// Order interface matching backend schema
export interface Order {
  symbol: string;
  trdAcc: string;
  pseAcc?: string;

  id: string;
  updateTime: string;
  status: string;

  qty: number;
  price: number;

  variety: string;
  trade: string;
  order: string;
  product: string;

  exch: string;
  trigPrc: number;

  fillQty: number;
  pendQty: number;

  avgPrc: number;

  exchId: string;
  parentId: string;

  discQty: number;

  amo: boolean;

  validity: string;
  rejectReason?: string;

  brStatus: string;
  brExch: string;
  brSymbol: string;

  day: string;
  client: string;

  platform: string;
  broker: string;

  copyTrace?: string;

  account_id: number;

  last_updated?: string;
}

export interface OrderListResponse {
  orders: Order[];
  total_orders: number;
}

export const orderService = {
  /**
   * Get all orders for all user's enabled broker accounts
   */
  getAll: async (): Promise<OrderListResponse> => {
    const response = await apiClient.get('/accounts/orders');
    return response.data;
  },
};