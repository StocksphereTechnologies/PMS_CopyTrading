import apiClient from './api'

export interface AccountSummary {
  pseudoAcc: string
  tradingAcc: string

  m2m: number
  pnl: number
  atPnl: number

  totalPos: number
  openPos: number
  closedPos: number

  marginTotal: number
  marginUtilized: number
  marginAvailable: number

  orderTotal: number
  orderOpen: number
  orderTPend: number
  orderComplete: number
  orderRejected: number
  orderCancelled: number
}

export interface SymbolSummary {
  exchange: string
  symbol: string

  buyQty: number
  sellQty: number
  netQty: number

  m2m: number
  pnl: number
  atPnl: number

  buyVal: number
  sellVal: number
  netVal: number

  buyAvg: number
  sellAvg: number
}

export interface PositionsAnalytics {
  m2m: number
  pnl: number
  atPnl: number

  total: number
  open: number
  closed: number
}

export interface OrdersAnalytics {
  total: number
  open: number
  complete: number
  trigPend: number
  cancelled: number
  rejected: number
}

export interface MarginAnalytics {
  total: number
  utilized: number
  available: number
}

export interface SummaryResponse {

  account_summary: AccountSummary[]

  symbol_summary: SymbolSummary[]

  positions_analytics: PositionsAnalytics

  orders_analytics: OrdersAnalytics

  margin_analytics: MarginAnalytics

  last_updated: string
}

/* ===============================
   Service
================================ */

export const summaryService = {

  getSummary: async (): Promise<SummaryResponse> => {

    const response = await apiClient.get('/summary')

    return response.data
  }

}