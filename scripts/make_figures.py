"""Generate all README/preview figures + animated demo from REAL outputs.

Reads: results/results.json + data/yahoo_EURUSD-X_d.csv
Writes: assets/*.png + assets/demo.gif
Style: clean, large fonts, colorblind-safe, no external assets.
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads((ROOT / "results" / "results.json").read_text())
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

plt.rcParams.update({"figure.dpi": 150, "font.size": 11, "axes.grid": True,
                     "grid.alpha": 0.3, "figure.autolayout": True})
BLUE, RED, GREEN, ORANGE, GREY = "#2563eb", "#dc2626", "#16a34a", "#ea580c", "#64748b"

def fig_price_overview():
    df = pd.read_csv(ROOT / "data" / "yahoo_EURUSD-X_d.csv", parse_dates=["Date"])
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(df["Date"], df["Close"], color=BLUE, lw=1)
    ax.set_title(f"EUR/USD daily close — live public data (n={len(df):,}, "
                 f"{df['Date'].iloc[0].date()} → {df['Date'].iloc[-1].date()})")
    ax.set_ylabel("EUR/USD")
    fig.savefig(ASSETS / "fig_price_overview.png", bbox_inches="tight")
    plt.close(fig)

def fig_nfp():
    b = RESULTS["EXP01b_nfp_range_test"]
    h = RESULTS["EXP05_hidden_patterns"]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    x = ["Normal days", "First-Friday\n(NFP proxy)"]
    y = [b["normal_mean_range_pips"], b["nfp_mean_range_pips"]]
    bars = ax.bar(x, y, color=[GREY, RED])
    ax.bar_label(bars, fmt="%.1f pips")
    ax.set_title(f"News risk is measurable: NFP days ×{b['expansion_ratio']} range "
                 f"(p={b['welch_p']:.3g}); |return| ×{h['H1_expansion_ratio']} (p={h['H1_welch_p']:.2g})")
    ax.set_ylabel("Mean daily range (pips)")
    fig.savefig(ASSETS / "fig_nfp.png", bbox_inches="tight")
    plt.close(fig)

def fig_ruin():
    r = RESULTS["EXP01c_ruin_vs_leverage"]
    levs = [5, 10, 30, 100, 250]
    probs = [r[str(l)]["ruin_prob_60d"] * 100 for l in levs]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.bar([str(l) + ":1" for l in levs], probs, color=[GREEN, GREEN, ORANGE, RED, RED])
    ax.bar_label(bars, fmt="%.1f%%")
    ax.set_ylim(0, 115)
    ax.set_title("Leverage is the amplifier: 60-day ruin probability (zero edge, 20k paths)")
    ax.set_ylabel("Ruin %")
    ax.axvline(1.5, color=GREY, ls="--", lw=1)
    ax.text(1.55, 100, "ESMA cap 30:1", fontsize=9, color=GREY)
    fig.savefig(ASSETS / "fig_ruin.png", bbox_inches="tight")
    plt.close(fig)

def fig_equity():
    import sys
    sys.path.insert(0, str(ROOT))
    from src.fetch_data import load_or_fetch
    from src.level3_backtest import run_backtest
    df = load_or_fetch()
    rule = run_backtest(df, return_curve=True)
    gut = run_backtest(df, inject_gut=True, return_curve=True)
    dates = rule["_curve"]["dates"]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(dates, rule["_curve"]["equity"], color=BLUE, lw=1.4, label="Rule-only (measured)")
    ax.plot(dates, gut["_curve"]["equity"][:len(dates)], color=RED, lw=1.2, alpha=0.85, label="Rule + gut trades (measured)")
    # Theory path: 56% x 1.5R at 11 trades/mo over same span
    n_months = max(1, int((dates.iloc[-1] - dates.iloc[0]).days / 30))
    theory_monthly = 1 + 0.044
    ax.plot(dates, [theory_monthly ** (i / (len(dates) / n_months)) for i in range(len(dates))],
            color=GREEN, ls="--", lw=1.2, label="Theory 56%×1.5R (+4.4%/mo, illustrative)")
    ax.set_title(f"Edge test: naïve breakout loses (exp {rule['expectancy_R']}R, Sharpe {rule['sharpe_daily']}) — "
                 f"gut trades worsen {rule['final_equity_growth']}→{gut['final_equity_growth']}×")
    ax.set_ylabel("Growth of 1.0")
    ax.legend(fontsize=9)
    fig.savefig(ASSETS / "fig_equity.png", bbox_inches="tight")
    plt.close(fig)
    return dates, rule["_curve"]["equity"]

def fig_costs():
    c = RESULTS["EXP03_cost_drag"]
    labels = {"scalper_500trades": "Scalper\n500/yr", "daytrader_250trades": "Day trader\n250/yr",
              "level3_disciplined_132trades": "Disciplined\n132/yr", "swing_60trades": "Swing\n60/yr"}
    keys = list(labels)
    vals = [c[k]["annual_R_drag"] for k in keys]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.bar([labels[k] for k in keys], vals, color=[RED, ORANGE, BLUE, GREEN])
    ax.bar_label(bars, fmt="%.1fR")
    ax.set_title("Cost drag alone (spread+swap+slippage): what your edge must beat every year")
    ax.set_ylabel("Annual drag (R)")
    fig.savefig(ASSETS / "fig_costs.png", bbox_inches="tight")
    plt.close(fig)

def demo_gif(dates, equity):
    equity = np.array(equity)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.set_xlim(dates.iloc[0], dates.iloc[-1])
    ax.set_ylim(float(equity.min()) * 0.95, max(1.05, float(equity.max()) * 1.05))
    ax.set_title("Demo: rule-only equity on live EUR/USD (1%/trade, 1-pip costs)")
    ax.set_ylabel("Growth of 1.0")
    (line,) = ax.plot([], [], color=BLUE, lw=1.6)
    txt = ax.text(0.02, 0.92, "", transform=ax.transAxes, fontsize=11)
    idx = np.linspace(0, len(dates) - 1, 60).astype(int)
    def update(f):
        j = idx[f]
        line.set_data(dates.iloc[:j + 1], equity[:j + 1])
        txt.set_text(f"{dates.iloc[j].date()}  equity {equity[j]:.3f}×")
        return line, txt
    ani = animation.FuncAnimation(fig, update, frames=len(idx), blit=True)
    ani.save(ASSETS / "demo.gif", writer=animation.PillowWriter(fps=12))
    plt.close(fig)

if __name__ == "__main__":
    fig_price_overview()
    fig_nfp()
    fig_ruin()
    dates, equity = fig_equity()
    fig_costs()
    demo_gif(dates, equity)
    print("wrote:", sorted(p.name for p in ASSETS.glob("*")))
