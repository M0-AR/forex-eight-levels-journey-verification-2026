"""EXP-03: Cost drag — spread + swap + slippage as the aggregate winner.

Video claim: "Across millions of retail trades, the counterparty wins the
aggregate. Always. Because the math of spreads, swap fees, and emotional
decision-making is on their side."

Verification:
- UK 14-broker panel (Apr 2026): typical EUR/USD spread 0.5-1.6 pips.
- Model annual friction for trader profiles (scalper/day/swing) in R and %.
- Cross-check Djouad (2026) MPRA estimate: 200-400% of initial capital/year
  friction before directional P&L for active retail.
"""
from __future__ import annotations

def annual_cost_drag(spread_pips: float, trades_per_year: int, avg_stop_pips: float = 30.0,
                     swap_per_night_pips: float = 0.5, nights_per_trade: float = 1.0,
                     slippage_pips: float = 0.2) -> dict:
    per_trade_pips = spread_pips + slippage_pips + swap_per_night_pips * nights_per_trade
    per_trade_r = per_trade_pips / avg_stop_pips
    annual_r = per_trade_r * trades_per_year
    # % of a 1%-risk account consumed by costs
    annual_pct_at_1pct_risk = annual_r * 1.0
    return {
        "per_trade_pips": round(per_trade_pips, 2),
        "per_trade_R": round(per_trade_r, 4),
        "trades_per_year": trades_per_year,
        "annual_R_drag": round(annual_r, 2),
        "annual_pct_drag_at_1pct_risk": round(annual_pct_at_1pct_risk, 2),
    }

def profiles() -> dict:
    return {
        # spread, trades/yr, stop, swap/night, nights, slippage
        "scalper_500trades": annual_cost_drag(1.0, 500, 10.0, 0.0, 0.0, 0.3),
        "daytrader_250trades": annual_cost_drag(1.0, 250, 30.0, 0.0, 0.0, 0.2),
        "swing_60trades": annual_cost_drag(1.2, 60, 80.0, 0.5, 3.0, 0.2),
        "level3_disciplined_132trades": annual_cost_drag(1.0, 132, 40.0, 0.0, 0.2, 0.2),
    }
