import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.services.position_service import PositionService
from app.services.order_service import OrderService
from app.services.margin_service import MarginService
from app.services.holdings_service import HoldingsService

logger = logging.getLogger(__name__)


class SummaryService:

    @staticmethod
    async def get_summary_for_user(db: AsyncSession, user_id: int) -> Dict[str, Any]:

        positions = await PositionService.get_positions_for_user(db, user_id, open_only=False)
        orders = await OrderService.get_orders_for_user(db, user_id)
        margins = await MarginService.get_margins_for_user(db, user_id)
        holdings = await HoldingsService.get_holdings_for_user(db, user_id)

        positions_analytics = SummaryService._positions_analytics(positions)
        positions_day_analytics = SummaryService._positions_day_analytics(positions)
        orders_analytics = SummaryService._orders_analytics(orders)
        margin_analytics = SummaryService._margin_analytics(margins)
        symbol_summary = SummaryService._symbol_summary(positions)

        account_summary = SummaryService._account_summary(positions, orders, margins, holdings)

        return {
            "account_summary": account_summary,
            "symbol_summary": symbol_summary,
            "positions_analytics": positions_analytics,
            "positions_day_analytics": positions_day_analytics,
            "orders_analytics": orders_analytics,
            "margin_analytics": margin_analytics,
            "last_updated": datetime.now(timezone.utc)
        }
    
    @staticmethod
    def _positions_analytics(positions):

        m2m = sum(getattr(p, "m2m", 0) for p in positions)
        pnl = sum(getattr(p, "pnl", 0) for p in positions)
        atpnl = sum(getattr(p, "atpnl", 0) for p in positions)

        total = len(positions)
        open_pos = len([p for p in positions if getattr(p, "netqty", 0) != 0])
        closed_pos = total - open_pos

        return {
            "m2m": m2m,
            "pnl": pnl,
            "atPnl": atpnl,
            "total": total,
            "open": open_pos,
            "closed": closed_pos
        }
    
    @staticmethod
    def _positions_day_analytics(positions):
    
        day_positions = [
            p for p in positions 
            if getattr(p, "day", getattr(p, "product", "")).upper() == "DAY"
        ]
    
        m2m = sum(getattr(p, "m2m", 0) for p in day_positions)
        pnl = sum(getattr(p, "pnl", 0) for p in day_positions)
        atpnl = sum(getattr(p, "atpnl", 0) for p in day_positions)

        total = len(day_positions)
        open_pos = len([p for p in day_positions if getattr(p, "netqty", 0) != 0])
        closed_pos = total - open_pos
    
        return {
            "m2m": m2m,
            "pnl": pnl,
            "atPnl": atpnl,
            "total": total,
            "open": open_pos,
            "closed": closed_pos
        }
    
    @staticmethod
    def _orders_analytics(orders):

        def status_match(order, words):
            status = order.get("status", "").upper()
            return any(w in status for w in words)

        return {
            "total": len(orders),
            "open": len([o for o in orders if status_match(o, ["OPEN"])]),
            "complete": len([o for o in orders if status_match(o, ["COMPLETE", "EXECUTED"])]),
            "trigPend": len([o for o in orders if status_match(o, ["TRIGGER"])]),
            "cancelled": len([o for o in orders if status_match(o, ["CANCEL"])]),
            "rejected": len([o for o in orders if status_match(o, ["REJECT"])])
        }
    @staticmethod
    def _margin_analytics(margins):
    
        total = 0
        utilized = 0
        available = 0
    
        for m in margins:
        
            equity = m.get("equity", {})
    
            total += equity.get("net", 0)
            available += equity.get("available", {}).get("cash", 0)
            utilized += equity.get("utilised", {}).get("debits", 0)
    
        return {
            "total": total,
            "utilized": utilized,
            "available": available
        }
    
    @staticmethod
    def _symbol_summary(positions):

        summary = []

        for p in positions:

            summary.append({
                "exchange": getattr(p, "exch", ""),
                "symbol": getattr(p, "symbol", ""),
                
                "buyQty": getattr(p, "buyqty", 0),
                "sellQty": getattr(p, "sellqty", 0),
                "netQty": getattr(p, "netqty", 0),
                
                "m2m": getattr(p, "m2m", 0),
                "pnl": getattr(p, "pnl", 0),
                "atPnl": getattr(p, "atpnl", 0),
                
                "buyVal": getattr(p, "buyval", 0),
                "sellVal": getattr(p, "sellval", 0),
                "netVal": getattr(p, "netval", 0),
                
                "buyAvg": getattr(p, "bavg", 0),
                "sellAvg": getattr(p, "savg", 0)
                })

        return summary
    
    @staticmethod
    def _account_summary(positions, orders, margins, holdings):
        print("ORDERS SAMPLE:", orders[:2])
    
        summary = []

        def status_match(order, words):
            return any(w in order.get("status", "").upper() for w in words)
    
        for m in margins:
            account_id = m.get("account_id")

            if not account_id:
                logger.warning(f"Margin object missing account_id: {m}")
                continue
            
            equity = m.get("equity", {})
            
            acc_positions = [p for p in positions if getattr(p, "account_id", None) == account_id]
            acc_orders = [o for o in orders if o.get("account_id") == account_id]
            acc_holdings = [h for h in holdings if h.get("account_id") == account_id]

            holding_count = len(acc_holdings)
            holding_pnl = sum(float(h.get("pnl", 0)) for h in acc_holdings)
            holding_curr_val = sum(float(h.get("currval", 0)) for h in acc_holdings)
            holding_total_qty = sum(float(h.get("totqty", 0)) for h in acc_holdings)
            holding_qty = sum(float(h.get("quantity", 0)) for h in acc_holdings)
            holding_t1_qty = sum(float(h.get("t1qty", 0)) for h in acc_holdings)

            print("HOLDINGS SAMPLE:", holdings[:2])
            print("CURRENT ACCOUNT ID:", account_id)
            print("ACC HOLDINGS:", acc_holdings)
            print("ACC ORDERS:", account_id, len(acc_orders))
            print("REJECTED:", len([o for o in acc_orders if status_match(o, ["REJECT"])]))
            
            # ---- DAY POSITIONS ----
            day_positions = [
                p for p in acc_positions 
                if getattr(p, "day", getattr(p, "product", "")).upper() == "DAY"
            ]

            day_total = len(day_positions)
            day_open = len([p for p in day_positions if getattr(p, "netqty", 0) != 0])
            day_closed = day_total - day_open

            day_m2m = sum(getattr(p, "m2m", 0) for p in day_positions)
            day_pnl = sum(getattr(p, "pnl", 0) for p in day_positions)
            day_atpnl = sum(getattr(p, "atpnl", 0) for p in day_positions)

            open_positions = [p for p in acc_positions if getattr(p, "netqty", 0) != 0]

            summary.append({
            
                "pseudoAcc": m.get("nickname", ""),
                "tradingAcc": m.get("trading_login_id", ""),

                # ----- POSITION NET -----
                "m2m": sum(getattr(p, "m2m", 0) for p in acc_positions),
                "pnl": sum(getattr(p, "pnl", 0) for p in acc_positions),
                "atPnl": sum(getattr(p, "atpnl", 0) for p in acc_positions),

                "totalPos": len(acc_positions),
                "openPos": len(open_positions),
                "closedPos": len(acc_positions) - len(open_positions),

                # ----- HOLDINGS -----
                "holdingCount": holding_count,
                "holdingPnl": holding_pnl,
                "currVal": holding_curr_val,
                "holdingTotalQty": holding_total_qty,
                "holdingQty": holding_qty,
                "holdingT1Qty": holding_t1_qty,

                # ----- MARGINS -----
                
                "marginTotal": equity.get("net", 0),
                "marginUtilized": equity.get("utilised", {}).get("debits", 0),
                "marginAvailable": equity.get("available", {}).get("cash", 0),

                # ----- ORDERS -----
                "orderTotal": len(acc_orders),
                "orderOpen": len([o for o in acc_orders if status_match(o, ["OPEN"])]),
                "orderTPend": len([o for o in acc_orders if status_match(o, ["TRIGGER"])]),
                "orderComplete": len([o for o in acc_orders if status_match(o, ["COMPLETE", "EXECUTED"])]),
                "orderRejected": len([o for o in acc_orders if status_match(o, ["REJECT"])]),
                "orderCancelled": len([o for o in acc_orders if status_match(o, ["CANCEL"])]),

                # ----- POSITION DAY -----
                "dayM2M": day_m2m,
                "dayPnL": day_pnl,
                "dayATPnl": day_atpnl,

                "dayTotal": day_total,
                "dayOpen": day_open,
                "dayClosed": day_closed
            })

        return summary