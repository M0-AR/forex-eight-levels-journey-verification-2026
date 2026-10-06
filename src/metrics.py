"""Risk-adjusted performance metrics. Formulas follow standard definitions
(Sharpe 1966; Investopedia; freqtrade backtesting docs for drawdown/SQN).

All functions operate on per-trade R multiples or daily returns with
no lookahead. Annualization assumes 252 trading days for daily series.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

def sharpe_ratio(returns: pd.Series | np.ndarray, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2 or np.std(r, ddof=1) == 0:
        return 0.0
    excess = r - risk_free / periods_per_year
    return float(np.mean(excess) / np.std(excess, ddof=1) * np.sqrt(periods_per_year))

def sortino_ratio(returns, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    downside = r[r < 0]
    if len(downside) < 2 or np.std(downside, ddof=1) == 0:
        return 0.0
    excess = np.mean(r) - risk_free / periods_per_year
    return float(excess / np.std(downside, ddof=1) * np.sqrt(periods_per_year))

def max_drawdown(equity: pd.Series | np.ndarray) -> tuple[float, float]:
    e = np.asarray(equity, dtype=float)
    peak = np.maximum.accumulate(e)
    dd = (e - peak) / np.where(peak == 0, 1, peak)
    return float(np.min(dd)), float(np.min(e - peak))

def calmar_ratio(returns, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    equity = (1 + r).cumprod()
    mdd, _ = max_drawdown(equity)
    if mdd == 0:
        return 0.0
    cagr = float(equity[-1] ** (periods_per_year / len(r)) - 1) if equity[-1] > 0 else -1.0
    return float(cagr / abs(mdd))

def expectancy_r(win_rate: float, avg_win_r: float, avg_loss_r: float = 1.0) -> float:
    """Expected R per trade: p*W - (1-p)*L."""
    return float(win_rate * avg_win_r - (1 - win_rate) * avg_loss_r)

def profit_factor(trade_returns_r: np.ndarray) -> float:
    t = np.asarray(trade_returns_r, dtype=float)
    wins = t[t > 0].sum()
    losses = abs(t[t < 0].sum())
    if losses == 0:
        return float("inf") if wins > 0 else 0.0
    return float(wins / losses)

def sqn_and_pvalue(trade_returns_r: np.ndarray) -> tuple[float, float]:
    """System Quality Number + two-sided t-test p-value (freqtrade convention).
    SQN = sqrt(N) * mean / std. p-value is optimistic (assumes i.i.d.).
    """
    from scipy import stats
    t = np.asarray(trade_returns_r, dtype=float)
    t = t[~np.isnan(t)]
    if len(t) < 3 or np.std(t, ddof=1) == 0:
        return 0.0, 1.0
    sqn = float(np.sqrt(len(t)) * np.mean(t) / np.std(t, ddof=1))
    _, p = stats.ttest_1samp(t, 0.0)
    return sqn, float(p)
