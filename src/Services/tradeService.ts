import api from './api';

export interface TradeOrderRequest {
  symbol: string;
  exchange: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  order_type: 'MARKET' | 'LIMIT' | 'SL' | 'SL_M';
  price?: number;
  trigger_price?: number;
  product?: string;
  variety?: string;
  validity?: string;
  account_ids?: number[];
  disclosed_quantity?: number;
  tag?: string;
  Target?: number;
  Stoploss?: number;
  trailing_stoploss?: number;
  amo?: boolean;
  groupAcc?: boolean;
  multiplier?: boolean;
  split?: string;
  splitQty?: number;
}

export interface TradeExecution {
  execution_id: number;
  account_id: number;
  broker: string;
  order_id: string;
  status: string;
  executed_price?: number;
  error_reason?: string;
}

export interface TradeResponse {
  trade_id: number;
  symbol: string;
  side: string;
  details: TradeExecution[];
}
const tradeService = {
  placeTrade: async (order: TradeOrderRequest): Promise<TradeResponse> => {
    const response = await api.post('/trades', order);
    return response.data;
  },

  getTrades: async () => {
    const response = await api.get('/trades');
    return response.data;
  }
};

export default tradeService;