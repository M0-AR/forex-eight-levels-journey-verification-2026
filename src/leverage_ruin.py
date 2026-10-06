"""EXP-01: Level-1 NFP liquidation autopsy + leverage ruin math.

Video claims:
  (a) 0.5 lots on $200 liquidated by ~100-pip NFP spike before coffee.
  (b) Leverage is the amplifier that destroys beginners.

Verification:
  1. Analytic pip math (no data needed, auditable).
  2. Live-data NFP proxy: first-Friday-of-month daily range vs normal days
     on real Stooq EUR/USD daily data (intraday 30s spike not visible on
     daily bars, so this is a LOWER BOUND — true intraday shock is larger).
  3. Monte-Carlo ruin simulator across leverages.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats

PIP = 0.0001

def analytic_nfp_autopsy(balance=200.0, lots=0.5, adverse_pips=100.0) -> dict:
    # Standard FX: 1.0 lot EUR/USD pip ~= $10 (at ~1.10, $10/pip exact enough for autopsy)
    pip_value_per_lot = 10.0
    pip_value = lots * pip_value_per_lot
    loss = pip_value * adverse_pips
    notional = lots * 100_000  # EUR
    leverage = notional * 1.10 / balance  # approx USD notional / equity
    return {
        "balance": balance, "lots": lots,
        "pip_value_usd": pip_value,
        "loss_on_100_pips": loss,
        "loss_pct_of_account": loss / balance * 100,
        "approx_leverage": round(leverage, 1),
        "ruined": loss >= balance,
        "margin_call_pips": round(balance / pip_value, 1),
    }

def is_first_friday(d: pd.Timestamp) -> bool:
    return d.weekday() == 4 and 1 <= d.day <= 7

def nfp_range_test(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["range_pips"] = (d["High"] - d["Low"]) / PIP
    d["atr_proxy_note"] = "daily range in pips"
    d["is_nfp_friday"] = d["Date"].apply(is_first_friday)
    nfp = d.loc[d["is_nfp_friday"], "range_pips"].dropna()
    normal = d.loc[~d["is_nfp_friday"], "range_pips"].dropna()
    t, p = stats.ttest_ind(nfp, normal, equal_var=False)
    return {
        "n_days": int(len(d)),
        "n_nfp_fridays": int(len(nfp)),
        "nfp_mean_range_pips": round(float(nfp.mean()), 1),
        "normal_mean_range_pips": round(float(normal.mean()), 1),
        "expansion_ratio": round(float(nfp.mean() / normal.mean()), 3),
        "nfp_median": round(float(nfp.median()), 1),
        "normal_median": round(float(normal.median()), 1),
        "welch_t": round(float(t), 3),
        "welch_p": float(p),
        "nfp_max": round(float(nfp.max()), 1),
        "note": "Daily bars understate 30-second NFP spike; intraday shock >= this.",
    }

def ruin_monte_carlo(leverage_list=(5, 10, 30, 100, 250), n_paths=20000, n_days=60,
                     daily_vol=0.006, seed=7) -> dict:
    """GBM with zero edge; ruin = equity <= 0. Shows leverage as amplifier."""
    rng = np.random.default_rng(seed)
    out = {}
    for lev in leverage_list:
        rets = rng.normal(0, daily_vol, size=(n_paths, n_days))
        # Levered equity path starting at 1.0
        eq = (1 + rets * lev).cumprod(axis=1)
        # ruin if it ever touches <=0 (margin call proxy: -100%/lev day kills)
        ruined = (eq <= 0.05).any(axis=1).mean()
        # median terminal
        med = float(np.median(eq[:, -1].clip(min=0)))
        out[str(lev)] = {"ruin_prob_60d": round(float(ruined), 4), "median_terminal": round(med, 3)}
    return out
