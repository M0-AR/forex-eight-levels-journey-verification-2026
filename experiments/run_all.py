"""Run all experiments end-to-end on real public data. Writes results/*.json."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from src.fetch_data import load_or_fetch
from src.leverage_ruin import analytic_nfp_autopsy, nfp_range_test, ruin_monte_carlo
from src.level3_backtest import run_backtest
from src.costs_drag import profiles
from src.microstructure import microstructure_verdict
from src.hidden_patterns import hidden_patterns
from src.metrics import expectancy_r

OUT = Path(__file__).resolve().parents[1] / "results"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    ap.add_argument("--allow-synthetic", action="store_true")
    a = ap.parse_args()
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    df = load_or_fetch("eurusd", allow_synthetic=a.allow_synthetic)
    synthetic = bool("_synthetic" in df.columns)

    exp01a = analytic_nfp_autopsy()
    exp01b = nfp_range_test(df)
    exp01c = ruin_monte_carlo()
    exp02_rule = run_backtest(df, inject_gut=False)
    exp02_gut = run_backtest(df, inject_gut=True)
    exp03 = profiles()
    exp04 = microstructure_verdict()
    exp05 = hidden_patterns(df)
    # Theory check: 56% x 1.5R expectancy
    theory = {
        "video_claim": {"win_rate": 0.56, "rr": 1.5},
        "expectancy_R": round(expectancy_r(0.56, 1.5), 4),
        "per_trade_pct_at_1pct_risk": round(expectancy_r(0.56, 1.5) * 1.0, 4),
        "per_month_11_trades_pct": round(expectancy_r(0.56, 1.5) * 1.0 * 11, 2),
    }
    results = {
        "meta": {
            "data": f"Yahoo EURUSD=X daily rows={len(df)} {df['Date'].iloc[0].date()}..{df['Date'].iloc[-1].date()} synthetic={synthetic}",
            "method": "no lookahead; costs modelled; Welch t-test; Monte Carlo seed=7",
        },
        "EXP01a_nfp_autopsy": exp01a,
        "EXP01b_nfp_range_test": exp01b,
        "EXP01c_ruin_vs_leverage": exp01c,
        "EXP02_rule_only": exp02_rule,
        "EXP02_rule_plus_gut": exp02_gut,
        "EXP02_theory_56_15R": theory,
        "EXP03_cost_drag": exp03,
        "EXP04_microstructure": exp04,
        "EXP05_hidden_patterns": exp05,
    }
    (outdir / "results.json").write_text(json.dumps(results, indent=2))
    # Human-readable summary
    lines = [
        "# Benchmark summary (real Yahoo EURUSD=X daily)",
        f"Data: {results['meta']['data']}",
        f"EXP01a: 0.5 lots on $200 -> ${exp01a['loss_on_100_pips']:.0f} loss on 100 pips ({exp01a['loss_pct_of_account']:.0f}% of account), ruined={exp01a['ruined']}, margin-call at {exp01a['margin_call_pips']} pips, ~{exp01a['approx_leverage']}:1",
        f"EXP01b: NFP-proxy Friday range {exp01b['nfp_mean_range_pips']} vs normal {exp01b['normal_mean_range_pips']} pips (x{exp01b['expansion_ratio']}), p={exp01b['welch_p']:.4g}, max NFP-day {exp01b['nfp_max']} pips",
        f"EXP01c: 60-day ruin {exp01c}",
        f"EXP02 rule-only: {exp02_rule}",
        f"EXP02 +gut: {exp02_gut}",
        f"EXP02 theory 56%/1.5R: {theory}",
        f"EXP03: {exp03}",
        f"EXP04: {exp04}",
        f"EXP05_hidden: {exp05}",
    ]
    (outdir / "SUMMARY.md").write_text("\n\n".join(lines))
    print("\n\n".join(lines))

if __name__ == "__main__":
    main()
