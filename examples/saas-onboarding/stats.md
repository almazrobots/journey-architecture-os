# Statistics appendix

> **Fictional example.** Ledgerly and all figures are invented. This page shows the arithmetic behind every interval, range, detectable effect and sample size quoted elsewhere, so a reader can check it. Design choices follow the experiment-design method of the target-experience-design skill (`experiment-design.md`): which design earns which evidence status, minimum detectable effect, clustering and design effect, rare-event guardrails, non-inferiority, and sequential stop rules.

## Conventions

- **Proportions.** SE of a difference = √(p₁(1−p₁)/n₁ + p₂(1−p₂)/n₂); 95% interval = estimate ± 1.96 SE.
- **Minimum detectable effect (MDE).** 80% power, two-sided α = 0.05: (1.96 + 0.84) × SE at the baseline rate.
- **Sample size per arm for a difference d:** n = (1.96 + 0.84)² × (p₁(1−p₁) + p₂(1−p₂)) / d².
- **Clustering.** Randomized by account and analyzed by invoice, so the design effect is DE = 1 + (m − 1) × ICC, with m invoices per account. Effective n = invoices ÷ DE.
- **Status each design can earn**, per `experiment-design.md`:
  - randomized comparison: `observed` for the effect it was powered to detect;
  - staged rollout with concurrent controls: `observed` only if assignment was not chosen by the team;
  - before/after, timing or unstratified comparison: `inferred` at most.
- Normal approximations throughout.

## 1. The 2025 checklist experiment (`EVD-2026-0015`)

- n = 388 (194 per arm); control rate about 30%. SE = √(2 × 0.30 × 0.70 / 194) = 0.0465.
- Difference +1 point, 95% interval **−8 to +10 points**. MDE = 2.80 × 0.0465 = **13 points**.
- Timing: accounts signed 2025-04-01 to 2025-08-31; all 30-day windows closed by 2025-09-30; readout 2025-10-15. The test ran entirely before policy v4 took effect (2025-10-01).

## 2. Outcome baseline (`MET-0001`)

- 140 / 412 = 34.0%, re-confirmed on 2026-09-21 (`EVD-2026-0021`). SE = 0.0233; 95% interval **±4.6 points**.

## 3. Can one quarter show the target? (34% → 42%)

- About 82 new accounts a month, so the Q1 2027 cohorts give about 246 accounts.
- A before/after comparison (412 vs 246) has an MDE of about **11 points**; the 95% interval on an 8-point change is ±7.7 points.
- It is also a before/after design, so any change it shows is `inferred` at most: seasonality and cohort mix are not controlled. 42% is a planning target, read as a trend.

## 4. First-sync success (`MET-0003`) and its control chart

- **Before/after:** 61% of 321 vs about 190 expected Q1 attempts gives an MDE of about 12.5 points. A rise of that size would be visible, but attributing it to `INI-0001` is `inferred`: first-sync success may move with ledger vendor mix and with the season (year-end tax-rate changes fall in the same window).
- **Monitoring:** about 64 first attempts a month, or 15 a week. With p = 0.61, 3-sigma p-chart limits are:

| Window | n | ± limits |
|---|---|---|
| weekly | 15 | ±38 points (noise; not used) |
| monthly | 64 | ±18 points |
| rolling 8 weeks | 118 | **±13 points** |

The rolling 8-week p-chart is the monitoring view. Action is triggered by a point outside the control limits, or by 8 consecutive points on one side of the centre line.

## 5. The leading-metric check (`MET-0002` → `MET-0001`, `EVD-2026-0021`)

- Population: the 321 accounts that attempted a sync. 284 of them had a synced invoice by day 30 (median 12 days); the other 37 had none.
- The 7-day cut was pre-specified in analysis plan AP-01 (2026-06-20) and was the only cut examined.
- 55% (44/80) vs 31% (75/241): difference 24 points, 95% interval **12 to 36 points**.
- Stratified by seat band:
  - 3–9 seats: 52% (28/54) vs 29% (49/170);
  - 10+ seats: 62% (16/26) vs 37% (26/71).
- The gap holds within both bands. Ledger vendor is not stratified, so the edge stays `inferred`.
- Consistency: 44 + 75 = 119 attempters met the threshold, and 21 of the 91 accounts that never connected did; 119 + 21 = 140.

## 6. Moment sizing (the `moments-that-matter` rule)

Excess failures per 1,000 entrants = share with the bad moment × (outcome rate when good − when bad) × 1,000. These are upper bounds, because the gaps are correlational.

| Moment | Bad share of entrants | Rate good vs bad | Excess per 1,000 |
|---|---|---|---|
| `MTM-0001` first synced invoice later than 7 days, or never among attempters | 241 / 412 = 0.585 | 55% vs 31% | **140** |
| First sync rejected (consequence carried by `MTM-0002`) | 125 / 412 = 0.303 | 44% vs 26% | **57** |
| `MTM-0003` week-1 permission downgrade | unknown until `MET-0014` baseline | unknown | not computable |

## 7. Opportunity ranges (reach × consequence)

The consequence is the rejected-vs-accepted gap: 44% (87/196) vs 26% (32/125), a difference of 18.8 points with a 95% interval of 8.4 to 29.1. Ranges assume that preventing a cause moves an account from the "rejected" rate to the "accepted" rate. Because that gap is correlational, the upper ends are optimistic.

| Opportunity | Reach (accounts in 412) | Arithmetic | Points on `MET-0001` |
|---|---|---|---|
| `OPP-0001` silent default | 22/30 of 125 rejections; Wilson 95% interval 56–86% → 69 to 107 accounts | low 69 × 0.084 = 5.8; mid 92 × 0.188 = 17.2; high 107 × 0.291 = 31.2 accounts | **1.4 / 4.2 / 7.6** |
| `OPP-0008` seat policy | 8/30 of 125 rejections; Wilson 14–44% → 18 to 56 accounts; only the external-accountant share is addressable, and it is unsized | low 0 (segment unsized); mid 33 × 0.188 = 6.3; high 56 × 0.291 = 16.2 accounts | **0 / 1.5 / 3.9** |
| `OPP-0002` posting not visible | 241 later-sync attempters; 8 of 14 admins describe gating (sample, not prevalence) | low 0 (consequence unmeasured); high 241 × 8/14 × 0.239 = 32.9 accounts | **0 / — / 8.0**, overlapping `OPP-0001` |

`OPP-0001` is the only opportunity with a lower bound above zero, and that bound is small (about 1.4 points). None is classified `act-now`, because every change depends on a guardrail baseline that does not yet exist.

## 8. Guardrails: fast signal, confirmatory read, non-inferiority

**Why two guardrail metrics.** Corrections within 60 days (`MET-0011`) cannot be read for 60 days, so they cannot drive a stop rule. Corrections within 14 days (`MET-0016`) are the fast signal the stop rule watches; `MET-0011` is the confirmatory read.

**Baselines.** Two of the three ledgers expose a 90-day change feed (`EVD-2026-0022`). Once instrumentation is live on 2026-11-30, the history is backfilled:

- `MET-0016` gets its baseline from invoices posted 2026-09-01 to 2026-11-16;
- `MET-0011` gets its baseline from invoices posted in September 2026, whose 60-day windows closed by 2026-11-30.

Both are due 2026-12-07. The third ledger has no feed, so neither `INI-0001` nor `INI-0003` is rolled out to its customers until a feed or a proxy exists.

**Planning assumptions**, to be replaced by the baselines:

- `MET-0016` rate p₀ = 20 per 1,000 invoices;
- m = 30 invoices per account in its first 60 days;
- ICC = 0.05, so DE = 1 + 29 × 0.05 = **2.45**.

**`INI-0003` harm-screening pilot:** about 49 accounts per arm (section 10).

- 49 × 30 = 1,470 invoices per arm, effective n = 600; about 29 expected corrections per arm at baseline.
- **Smallest detectable harm** (one-sided α = 0.05, 80% power) = 2.49 × √(2 × 0.02 × 0.98 / 600) = **20 per 1,000**. The pilot can see the rate double, and nothing smaller.
- **Non-inferiority at a margin of 5 per 1,000:** effective n = 2.49² × 2 × 0.02 × 0.98 / 0.005² ≈ 9,700 per arm. That is ≈ 23,800 invoices, or **≈ 790 accounts per arm**. At about 53 eligible accounts a month (82 × 0.65), both arms take about **30 months**.
- **Consequence:** the pilot cannot show safety. It can only screen for gross harm. A wider rollout after a clean pilot is a **recorded risk acceptance** by the journey owner and Accounting Integrations, not a demonstrated safety result. That rollout is staged by ledger with a concurrent control and continued monitoring of `MET-0016`.

**How the pilot is read** (step 5 of `experiment-design.md`):

- The guardrail passes only if the upper 95% bound of (treatment − control) for `MET-0016` falls below the 5 per 1,000 margin. At this size it cannot. "No significant increase" from this pilot is **not** evidence of safety, and it will not be reported as such.
- If a small arm shows few corrections, the exact Poisson upper bounds are reported, for example 7.75 expected events for 3 observed. Zero events in 1,470 invoices would still allow a rate up to about 2 per 1,000 (rule of three).
- Because the pilot cannot be made large enough, the harm path is also reduced by design. Postings stay held until a named person confirms the mapping, and every held posting released after confirmation is traced for a mismatch. That trace can earn `observed` for the mechanism ("no posting leaves on a guessed pair"), though not for the rate.

**Sequential stop rule.** Per step 7 of `experiment-design.md`, the fast signal can stop the pilot but never declare success. Weekly looks over 8 weeks use an O'Brien–Fleming-type boundary (Lan–DeMets spending) with c = 2.07 for 8 looks (one-sided α = 0.025). The boundary on the z statistic for excess corrections (treatment minus control, cluster-adjusted) is:

| Week | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| z boundary | 5.86 | 4.14 | 3.38 | 2.93 | 2.62 | 2.39 | 2.22 | 2.07 |

Crossing the boundary switches sending-before-confirmation off for new accounts within one business day. `MET-0011` is read at 60 days as confirmation. The same fast signal, against its backfilled baseline on the rolling p-chart, is the stop rule for `INI-0001`.

## 9. `INI-0002` randomized rollout (the test that could promote `MTM-0001`)

- Eligible: accounts with a first synced invoice, about 284 / 5 = 57 a month. Randomized by account, 50/50, January to June 2027: about **170 per arm**.
- `MET-0005` (invite within 14 days) has no baseline. Planning value 45%, below the 30-day rate of 58%.
- MDE = 2.80 × √(2 × 0.45 × 0.55 / 170) = **15 points**.
- A 10-point effect needs 7.84 × (0.45 × 0.55 + 0.55 × 0.45) / 0.10² ≈ **390 per arm**, about 14 months of eligible accounts.
- Consequence: a positive result at 15 points or more would make the causal part of `MTM-0001` `observed`. A smaller true effect will most likely read as "not detected", which must not be reported as "no effect".

## 10. `INI-0003` outcome power

- About 82 × 8 / 4.35 = 151 new accounts in 8 weeks. Assuming about 65% are under 10 seats (a planning assumption; the seat distribution is not in the evidence register), that is about 98 accounts, or **about 49 per arm**.
- MDE on `MET-0001` = 2.80 × √(2 × 0.34 × 0.66 / 49) = **27 points**. Detecting 5 points needs about 1,450 per arm.

## 11. Co-variation claims (correlation, not effect)

| Claim | Arithmetic | 95% interval | Status |
|---|---|---|---|
| Median 23 vs 9 days to first synced invoice, first sync failed vs succeeded (`EVD-2026-0002`) | a difference in medians between self-selected groups | not computed | `inferred`: not "a failure adds 14 days" |
| 90-day retention 96% (197/205) vs 81% (323/399) (`EVD-2026-0016`) | 15 points; SE 0.0239 | ±4.7 | `inferred`: confounded by size |
| Invites within 30 days: 81% (65/80) early sync, 58% (139/241) later, 38% (35/91) never connected (`EVD-2026-0021`) | 65 + 139 + 35 = 239 = the 58% of 412 in `EVD-2026-0008` | — | `observed` as description; the causal reading is `inferred` |

## 12. Counts quoted in the views

| Figure | Arithmetic |
|---|---|
| First-sync rejections, about 30 per 100 new accounts | 125 / 321 = 39% of attempts; 125 / 412 = 30 per 100 |
| No invite within 30 days, 42 per 100 | 1 − 239 / 412 |
| Admin login within 7 days | 367 / 412 = 89% |
| Declined session requests | 58 / 187 = 31% |
| Codebook agreement | Cohen's κ = (0.81 − 0.32) / (1 − 0.32) = 0.72 on 146 double-coded notes, with 0.32 chance agreement from the code marginals |
