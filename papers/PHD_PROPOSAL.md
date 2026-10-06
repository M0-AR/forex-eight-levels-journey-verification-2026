# PhD Proposal (extension of this repo): Why 71% Lose — Structure, Behaviour, and the Rare Edge in Retail FX

## 1. Title
**The retail forex attractor: leverage cliffs, news-tail risk, cost drag, and selective edges — a reproducible mixed-methods study from $200 accounts to $22M mandates.**

## 2. Problem
Regulator panels agree ~71% of retail CFD/FX accounts lose annually (ESMA 74–89%; 49-broker 71.0%; UK 68.4%; KNF 70–79%; AMF 89%/4yr), yet viral narratives frame a deterministic 8-level ascent. The gap between population base rate and anecdotal ascent is unexplained quantitatively. This repo bounds it: naïve public rules are significantly negative (Sharpe −0.66, p=0.001); the 56%/1.5R arithmetic works only conditionally.

## 3. Questions
1. What fraction of the 71% is structural (costs/internalisation) vs behavioural (leverage/overtrading/revenge)?
2. What is the intraday NFP hazard (P(≥50/100-pip 30s shock | first-Friday 8:30 ET))?
3. Which selective filters (session, level-touch, news-avoidance, ATR-regime) survive walk-forward + multiple-testing correction?
4. Does leverage (not frequency) predict ruin when instrumented by audience/social exposure (Forman mechanism)?
5. At what AUM does the strategy become a business (staff, Sharpe gating, drawdown covenants)?

## 4. Design (3 years)
- **Y1 — Measurement:** Dukascopy tick (5 yrs EUR/USD + GBP/USD) around NFP timestamps; reproduce EXP-01b intraday; estimate shock CDF; pre-register 3 rules; walk-forward with White (2000) reality check + Harvey-Liu-Zhu haircuts; report Sharpe/Sortino/Calmar/SQN/p.
- **Y2 — Behaviour:** partner-broker anonymised panel (or TradeJournal-style journaling RCT, n≥500): tag Neutral/Confident/Impulsive/FOMO/Revenge/Anxious; test Neutral≈68% vs Revenge≈18% replication; instrument leverage with social-audience size; disposition-effect decomposition.
- **Y3 — Structure:** interview LPs/B-book desks (Chatham rules); model internalisation >80% as prior for retail negative-sum; family-office gating (Sharpe>1/>2, 15% DD covenant) ethnography; write-up.

## 5. Data & ethics
Public tick (Dukascopy/TrueFX), BIS, regulator panels (no PII). Broker panel only under IRB + data-sharing agreement, k-anonymised. No trading advice; participant debrief includes loss-rate disclosure. Pre-registration on OSF; negative results published.

## 6. Expected contributions
1. First falsification-bounded map of a viral journey onto BIS + regulator + live moments.
2. Intraday NFP shock CDF for EUR/USD (risk-limit input).
3. Walk-forward evidence on which selective filters survive (or don't).
4. Structural-behavioural decomposition of the 71% attractor.
5. Open benchmark (this repo) as community standard for "guru-claim" testing.

## 7. Risks & mitigations
Tick-data gaps → cross-validate Dukascopy vs TrueFX vs broker. Broker access fails → journaling RCT fallback. Non-stationarity (H4 decay) → regime-conditional reporting, no pooled claims.

## 8. Timeline & outputs
Y1: preprint (NFP hazard + walk-forward null); Y2: behaviour paper; Y3: thesis + microstructure chapter; throughout: repo releases v1–v3 with Docker digests.
