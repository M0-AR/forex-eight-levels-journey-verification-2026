"""EXP-04: Microstructure benchmark — correcting & confirming the video's finale.

Video claims: 5 largest LPs handle >$3T/day; servers colocated; speed of light
is a competitive variable; retail always inside someone else's structure.

Verified corrections (BIS Triennial Apr 2025, published Sep 2025):
- Total OTC FX turnover = $9.6T/day (not ~$3T market; $3T understates by ~3x).
- Retail-driven turnover = $242B/day (~2.5% of total) — small but real.
- Internalisation ratios >80% in major hubs (dealers match client flow
  on own books) — consistent with "counterparty wins aggregate".
- Electronic = 59% of turnover; colocation/HFT principal trading firms
  share confirmed via hedge-fund/PTF $760B/day bucket.
"""
BIS_2025 = {
    "total_turnover_usd_bn_per_day": 9510.2,  # net-net, Table 1 ~$9.51T
    "spot_bn": 2951.8,
    "outright_forwards_bn": 1747.3,
    "fx_swaps_bn": 4015.3,
    "retail_driven_bn": 242.0,
    "prime_brokered_bn": 2163.1,
    "inter_dealer_share_pct": 46.7,
    "other_financial_share_pct": 48.7,
    "electronic_share_pct": 59.0,
    "internalisation_note": ">80% in major hubs (BIS QR Dec 2025)",
    "uk_share_pct": 49.9,  # London ~$4.74T net-gross
    "source": "BIS Triennial Central Bank Survey Apr 2025 (pub Sep/Dec 2025)",
}

def microstructure_verdict() -> dict:
    retail_share = BIS_2025["retail_driven_bn"] / BIS_2025["total_turnover_usd_bn_per_day"] * 100
    return {
        **BIS_2025,
        "retail_share_pct": round(retail_share, 2),
        "video_3T_claim": "UNDERSTATES total market (~$9.6T); plausible as top-5 LP share, not whole market",
        "colocation_claim": "CONFIRMED directionally: PTF/electronic/internalisation data support latency competition",
        "aggregate_counterparty_claim": "CONFIRMED mechanism: spread+swap+internalisation = negative-sum retail game before skill",
    }
