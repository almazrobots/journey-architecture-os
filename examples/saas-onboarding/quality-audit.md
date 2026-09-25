# Quality audit of this example

> **Fictional example.** This audits the fictional Ledgerly journey system in this directory. Produced with `journey-quality-audit` by the team that built the artifacts, which is itself a limitation (see required validation).

- Artifact audited: registers and views in this directory at journey version 1.4 (`CHG-0006`)
- Journey ID: `JRN-CUST-SAAS-ONBOARD-001`, with `JRN-CUST-SAAS-ONBOARD-002` (target) and `JRN-CUST-SAAS-ONBOARD-003` (transitional)
- Decision the artifact must support: the Q1 2027 funding choice (2–3 changes to raise `MET-0001`)
- Auditor / date: journey team self-audit, 2026-09-24

## Scorecard

Scores (0 missing or misleading, 1 weak, 2 usable, 3 strong) are a diagnostic aid and are not summed. Evidence status labels the finding; `observed` means visible in the artifact or its cited sources.

| Dimension | Score 0–3 | Finding | Evidence status | Evidence IDs | Risk | Remediation | Skill |
|---|---:|---|---|---|---|---|---|
| Scope and boundaries | 3 | Trigger, start, an actor-outcome end, alternate end and exclusions are explicit. The 30-day window sits on `MET-0001`. Stage 2 ends at a logged event (first accepted posting), and accounts that never connect a ledger have their own unknown path | observed | `EVD-2026-0021` | The alternate end (admin gives up) is still only proxied by `MET-0001` | Define an observable abandonment signal | `journey-architecture` |
| Actor centricity | 2 | Stages follow the admin's progress, and the accountant is modeled as an actor. The outcome is a team outcome, yet team members appear only through 6 interviews from successful accounts | observed | `EVD-2026-0019` | Team-side barriers in stalled accounts are invisible | Interview team members from stalled accounts | `journey-research` |
| Evidence | 2 | 22 items across 9 source types. The core baselines were re-run on 2026-09-21 with a pre-specified cut, and the ledger-feed coverage is documented. But four operational and analytics items will be 91–98 days old at the decision against a 60-day rule, so the journey is marked needs-review. Interview recruitment still misses non-starters | observed | `EVD-2026-0021`, `EVD-2026-0022`, `EVD-2026-0003`, `EVD-2026-0009` | The decision may be taken on needs-review evidence if the 2026-10-07 refresh slips | Run the refresh; record in the minutes if it is missed | `journey-research`, `journey-governance` |
| Journey coherence | 2 | Codebook v2 with a chance-corrected agreement (κ 0.72); clusters with provenance; statuses capped at the weakest boundary. Only stage 2 is `observed`; stages 3–5 are `inferred` and stage 1 is `hypothesis` | observed | `EVD-2026-0006` | The pivotal trust boundary rests on one interview cluster | Read the model back to 3–5 admins | `customer-journey-mapping` |
| Variation / nonlinearity | 2 | Accountant vs in-house, tier split, loops and the never-connect path are mapped, each with a split/variant decision. Ledger-vendor variation is still unstratified, even though vendor now decides who gets any change | observed | `EVD-2026-0022` | A vendor effect could sit inside both the silent-default branch and the leading check | Stratify `EVD-2026-0021` by ledger | `journey-research` |
| Experience integrity | 1 | The experience register gives every row a status. Emotion rows exist only where interview or survey evidence supports them (5 `inferred`, 2 `hypothesis`, none `observed`); stages 1 and 4 have none. But 6 of the 9 expectation rows are `hypothesis`, and `MET-0006` does not exist yet | observed | `EVD-2026-0006` | Decisions about trust rest on stated intent until `INI-0002` reports | Expectation probes in the next round; ship `MET-0006` with the randomized rollout | `customer-journey-mapping` |
| Service linkage | 2 | Blueprint steps are rows, each with a status. Two root-cause trees have gate checks and per-path weakest-link statuses, the seat policy is split out as its own root, and conditions are separated. Only one episode is blueprinted, and the specialist journey is unmapped | observed | `EVD-2026-0003`, `EVD-2026-0007` | `OPP-0004` and `OPP-0005` have no delivery model behind them | Blueprint episode 4.1; map `JRN-EMP-ONBOARD-CUSTOMER-001` | `service-blueprinting` |
| Metrics | 2 | 15 metrics with one root; validity separated from causal edges; the definitional edge is labeled; there is a fast and a confirmatory guardrail; monitoring uses p-charts and a sequential boundary; power is published. Seven metrics have no baseline, the root's validity is `inferred`, and guardrail planning numbers are assumptions until 2026-12-07 | observed | `EVD-2026-0021`, `EVD-2026-0022` | The design numbers in stats.md §8 may be wrong until backfill | Recompute §8 on the backfilled baselines before any launch | `journey-metrics` |
| Opportunities | 2 | One opportunity per root cause; range estimates with arithmetic; no `act-now` while dependencies are unmet; trade-offs and reversal conditions written down. The ranges rest on a correlational gap, so the upper ends are optimistic, and two opportunities overlap | observed | `EVD-2026-0021` | Ranges read as forecasts | Present ranges only with the correlational caveat | `experience-opportunity-prioritization` |
| Governance | 2 | Role owners, enumerated triggers, per-journey freshness rules, a change log with approvers including a portfolio-level approval, and an honest `needs-review` state. The cadence has not run once; the RACI check, stop boundary and margin are unagreed | observed | — | Launch preconditions depend on meetings that have not happened | Settle them at the 2026-10-14 review | `journey-governance` |

## Critical blockers

None blocks funding `INI-0004` now. For the other launches:

1. `INI-0001` cannot ship before the `MET-0016` baseline (2026-12-07), and cannot ship at all to the third ledger.
2. `INI-0002` cannot launch before the `MET-0012` and `MET-0005` baselines.
3. `INI-0003` cannot demonstrate safety at any size reachable within a year. Rolling it out would be a risk acceptance, and the artifact says so.

## Strong elements

- Every arrow in the README chain diagram is a register link, checked by script.
- Designs are matched to the status they can earn: randomized for the `MTM-0001` causal claim, before/after labeled `inferred`, pilot labeled harm-screening.
- Guardrails are split into a fast signal, which can stop a change, and a slow confirmatory read, which cannot.
- Several claims were downgraded rather than defended: stages, moments, and decisions moved from `act-now` to `sequence` or `investigate` (`CHG-0004`, `CHG-0006`).

## Remaining weaknesses, ranked

1. **All evidence is fictional.** Internal consistency is checked; realism is not.
2. **No causal evidence yet.** Every `drives` edge is `inferred` or `hypothesis`; the first causal test ends in mid-2027 and can only see effects of about 15 points or more.
3. **Safety of principle 4 cannot be shown at current intake.**
4. **Experience layer.** Expectations are thin, and `MET-0006` is missing.
5. **Stage model.** One `observed` stage out of five.
6. **Vendor stratification is missing**, although vendor decides rollout.
7. **Freshness.** The decision may use evidence older than the journey's own 60-day rule.

## Remediation sequence

1. Fund and ship `INI-0004`; run the 2026-10-07 refresh; agree the boundary and margin; hold the RACI check.
2. Stratify the leading check and the silent-default trace by ledger.
3. Read the stage model back to admins; research the `MET-0001` threshold and the non-starters.
4. Blueprint episode 4.1; map the specialist journey.
5. Re-audit at v1.5 by someone who did not build it.

## Required validation

- An independent reviewer for this audit; Scope (3) is the score most likely to be generous.
- A second analyst to re-run `EVD-2026-0021` and recompute [stats.md](stats.md) §8 on the backfilled guardrail baselines.
