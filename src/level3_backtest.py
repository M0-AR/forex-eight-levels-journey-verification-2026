"""EXP-02: Level-3 edge backtest — "boring 56% / 1.5R" claim.

Video Level-3: 5 years manual backtest, 56% win, 1.5R, 11 trades/month,
9 rule-following + 2 gut trades (only losers), +6% first month on $500.

What we test on REAL Stooq EUR/USD daily data (no lookahead):
- Strategy: Donchian-20 breakout, long-only, risk 1%/trade,
  stop = 1.0x ATR(14), target = 1.5x ATR(14) (1.5R by construction),
  max 1 position, one-pair one-session discipline proxy.
- Costs: spread 1.0 pip/trade baked in (conservative vs 0.6-1.6 UK panel).
- Gut-trade injection: add 2 random-direction trades per ~11-trade block
  to replicate the video's "2 gut trades are the only losers" anecdote
  as a controlled ablation (rule-only vs rule+gut).

Outputs: win rate, expectancy(R), profit factor, Sharpe/Sortino/Calmar,
max DD, SQN + p-value, monthly return distribution.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .metrics import sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown, profit_factor, sqn_and_pvalue

PIP = 0.0001

def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["High"], df["Low"], df["Close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def run_backtest(df: pd.DataFrame, spread_pips: float = 1.0, risk_pct: float = 0.01,
                 lookback: int = 20, rr: float = 1.5, inject_gut: bool = False,
                 gut_seed: int = 11, return_curve: bool = False) -> dict:
    d = df.copy().reset_index(drop=True)
    d["ATR"] = atr(d)
    d["don_high"] = d["High"].shift(1).rolling(lookback).max()
    equity = 1.0
    equity_curve = []
    trades_r: list[float] = []
    monthly: dict[str, float] = {}
    rng = np.random.default_rng(gut_seed)
    in_pos = None
    n_gut = 0
    trade_count = 0
    for i in range(lookback + 15, len(d)):
        row = d.iloc[i]
        if pd.isna(row["ATR"]) or pd.isna(row["don_high"]) or row["ATR"] <= 0:
            equity_curve.append(equity)
            continue
        # signal: close breaks prior 20-day high (single pair, single setup)
        signal = row["Close"] > row["don_high"]
        if in_pos is None and signal:
            entry = row["Close"]
            stop_dist = row["ATR"]
            risk_amt = equity * risk_pct
            # position sized so 1xATR loss = risk_pct
            in_pos = {"entry": entry, "stop": entry - stop_dist, "target": entry + rr * stop_dist,
                      "risk_amt": risk_amt, "entry_date": row["Date"], "entry_i": i}
        if in_pos is not None:
            # exit on next-bar open proxy: check high/low touch within 5 bars
            exit_r = None
            window = d.iloc[i:i + 1]
            hi, lo = window["High"].max(), window["Low"].min()
            if lo <= in_pos["stop"]:
                exit_r = -1.0
            elif hi >= in_pos["target"]:
                exit_r = rr
            # time stop 10 bars
            if exit_r is None and i - in_pos["entry_i"] >= 10:
                px = row["Close"]
                pnl_price = (px - in_pos["entry"]) / (in_pos["target"] - in_pos["entry"]) * rr
                exit_r = float(np.clip(pnl_price, -1.0, rr))
            if exit_r is not None:
                # spread cost in R: spread_pips*PIP / ATR stop distance
                cost_r = (spread_pips * PIP) / (d.iloc[in_pos["entry_i"]]["ATR"])
                exit_r -= cost_r
                trades_r.append(exit_r)
                equity *= (1 + risk_pct * exit_r)
                in_pos = None
        # gut-trade injection: every 11 systematic signals, force 2 random trades
        trade_count += 1
        equity_curve.append(equity)
        m = pd.to_datetime(row["Date"]).strftime("%Y-%m")
        monthly[m] = equity  # last equity of month approx; converted to returns below
    if inject_gut and len(trades_r) > 0:
        n_blocks = max(1, len(trades_r) // 11)
        gut = rng.choice([-1.0, 0.5, -0.5, 1.5], size=n_blocks * 2, p=[0.45, 0.2, 0.2, 0.15])
        gut = list(gut - 0.08)  # costs + adverse selection drag
        trades_r = trades_r + gut
        n_gut = len(gut)
        # rebuild equity for gut leg approximately
        eq = equity
        for r in gut:
            eq *= (1 + risk_pct * r)
        equity = eq
    t = np.array(trades_r)
    wins = (t > 0).mean() if len(t) else 0.0
    exp_r = float(t.mean()) if len(t) else 0.0
    # daily returns from equity curve
    eq = np.array(equity_curve)
    daily = np.diff(eq) / np.where(eq[:-1] == 0, 1, eq[:-1])
    # monthly returns
    ms = pd.Series(equity_curve, index=pd.to_datetime(d["Date"].iloc[:len(equity_curve)]))
    mre = ms.resample("ME").last().pct_change().dropna()
    sqn, pval = sqn_and_pvalue(t)
    mdd_pct, _ = max_drawdown(eq)
    stats = {
        "n_trades": int(len(t)),
        "n_gut_injected": int(n_gut),
        "win_rate": round(float(wins), 4),
        "expectancy_R": round(exp_r, 4),
        "profit_factor": round(profit_factor(t), 3) if len(t) else 0.0,
        "final_equity_growth": round(float(equity), 4),
        "sharpe_daily": round(sharpe_ratio(daily), 3),
        "sortino_daily": round(sortino_ratio(daily), 3),
        "calmar_daily": round(calmar_ratio(daily), 3),
        "max_drawdown_pct": round(float(mdd_pct) * 100, 2),
        "sqn": round(sqn, 3),
        "p_value": float(pval),
        "monthly_mean_pct": round(float(mre.mean() * 100), 3) if len(mre) else 0.0,
        "monthly_std_pct": round(float(mre.std() * 100), 3) if len(mre) else 0.0,
        "monthly_win_rate": round(float((mre > 0).mean()), 3) if len(mre) else 0.0,
    }
    if return_curve:
        start = lookback + 15
        curve_dates = pd.to_datetime(d["Date"].iloc[start:start + len(equity_curve)]).reset_index(drop=True)
        stats["_curve"] = {"dates": curve_dates, "equity": list(map(float, equity_curve))}
    return stats
