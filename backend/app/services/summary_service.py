import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.services.position_service import PositionService
from app.services.order_service import OrderService
from app.services.margin_service import MarginService

logger = logging.getLogger(__name__)


class SummaryService:

    @staticmethod
    async def get_summary_for_user(db: AsyncSession, user_id: int) -> Dict[str, Any]:

        positions = await PositionService.get_positions_for_user(db, user_id, open_only=False)
        orders = await OrderService.get_orders_for_user(db, user_id)
        margins = await MarginService.get_margins_for_user(db, user_id)
        positions_analytics = SummaryService._positions_analytics(positions)
        positions_day_analytics = SummaryService._positions_day_analytics(positions)
        orders_analytics = SummaryService._orders_analytics(orders)
        margin_analytics = SummaryService._margin_analytics(margins)
        symbol_summary = SummaryService._symbol_summary(positions)
        account_summary = SummaryService._account_summary(positions, orders, margins)

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

        m2m = sum(p.m2m for p in positions)
        pnl = sum(p.pnl for p in positions)
        atpnl = sum(p.atpnl for p in positions)

        total = len(positions)
        open_pos = len([p for p in positions if p.netqty != 0])
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
    
        day_positions = [p for p in positions if p.product == "DAY"]
    
        m2m = sum(p.m2m for p in day_positions)
        pnl = sum(p.pnl for p in day_positions)
        atpnl = sum(p.atpnl for p in day_positions)
    
        total = len(day_positions)
        open_pos = len([p for p in day_positions if p.netqty != 0])
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

            if not m.get("equity"):
                continue

            total += m["equity"]["net"]
            available += m["equity"]["available"]["cash"]
            utilized += m["equity"]["utilised"]["debits"]

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
                "exchange": p.exch,
                "symbol": p.symbol,

                "buyQty": p.buyqty,
                "sellQty": p.sellqty,
                "netQty": p.netqty,

                "m2m": p.m2m,
                "pnl": p.pnl,
                "atPnl": p.atpnl,

                "buyVal": p.buyval,
                "sellVal": p.sellval,
                "netVal": p.netval,

                "buyAvg": p.bavg,
                "sellAvg": p.savg
            })

        return summary
    
    @staticmethod
    def _account_summary(positions, orders, margins):
        print("ORDERS SAMPLE:", orders[:2])
    
        summary = []

        def status_match(order, words):
            return any(w in order.get("status", "").upper() for w in words)
    
        for m in margins:

            account_id = m.get("account_id")

            if not account_id:
                logger.warning(f"Margin object missing account_id: {m}")
                continue
            
            acc_positions = [p for p in positions if p.account_id == account_id]
            acc_orders = [o for o in orders if o.get("account_id") == account_id]
            
            print("ACC ORDERS:", account_id, len(acc_orders))
            print("REJECTED:", len([o for o in acc_orders if status_match(o, ["REJECT"])]))
            
            # ---- DAY POSITIONS ----
            day_positions = [p for p in acc_positions if p.product == "DAY"]

            day_total = len(day_positions)
            day_open = len([p for p in day_positions if p.netqty != 0])
            day_closed = day_total - day_open

            day_m2m = sum(p.m2m for p in day_positions)
            day_pnl = sum(p.pnl for p in day_positions)
            day_atpnl = sum(p.atpnl for p in day_positions)

            summary.append({
            
                "pseudoAcc": m["nickname"],
                "tradingAcc": m["trading_login_id"],

                # ----- POSITION NET -----
                "m2m": sum(p.m2m for p in acc_positions),
                "pnl": sum(p.pnl for p in acc_positions),
                "atPnl": sum(p.atpnl for p in acc_positions),

                "totalPos": len(acc_positions),
                "openPos": len([p for p in acc_positions if p.netqty != 0]),
                "closedPos": len(acc_positions) - len([p for p in acc_positions if p.netqty != 0]),

                # ----- MARGINS -----
                "marginTotal": m["equity"]["net"],
                "marginUtilized": m["equity"]["utilised"]["debits"],
                "marginAvailable": m["equity"]["available"]["cash"],

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