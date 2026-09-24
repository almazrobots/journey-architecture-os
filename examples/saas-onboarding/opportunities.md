# Opportunities and funding recommendation

> **Fictional example.** Ledgerly and all evidence are invented for illustration. Produced with `experience-opportunity-prioritization`; rows live in [opportunity-register.csv](opportunity-register.csv) and [initiative-register.csv](initiative-register.csv). Arithmetic in [stats.md](stats.md).

Journey `JRN-CUST-SAAS-ONBOARD-001`. Decision: which 2–3 changes to fund in Q1 2027 to raise `MET-0001` from 34%.

## Opportunity statements

There is one opportunity per root cause from the trees in [service-blueprint.md](service-blueprint.md). Three more sit outside the trees: one for a contributing cause that has its own symptom, and two that did not come from a tree. Each is written as: improve [actor outcome] at [node] by addressing [cause]. Solutions appear only as initiatives.

| ID | Node | Improve… | …by addressing (root cause) | Problem status | Cause status |
|---|---|---|---|---|---|
| `OPP-0001` | `NOD-CUST-SAAS-ONBOARD-001-02-02` | the admin's first real invoice posting without rejection | unmatched tax rates silently given the ledger's default code | observed | observed (mechanism trace, 22 of 30) |
| `OPP-0008` | `NOD-CUST-SAAS-ONBOARD-001-02-02` | the admin getting a mapping answer from the person who knows | a seat policy that keeps the accountant out of the product | observed | inferred |
| `OPP-0009` | `NOD-CUST-SAAS-ONBOARD-001-02-02` | the admin knowing who holds an open mapping question and since when | no record of, and no owner for, an open mapping question | observed | hypothesis (RACI check pending) |
| `OPP-0002` | `NOD-CUST-SAAS-ONBOARD-001-03` | the admin's ability to confirm the figures match the books before committing the team | a posting result that is never shown to the admin | observed | inferred |
| `OPP-0003` | `NOD-CUST-SAAS-ONBOARD-001-04` | the team starting while accounting set-up is still being confirmed | every sent invoice posting to the ledger at once | inferred | hypothesis |
| `OPP-0005` | `NOD-CUST-SAAS-ONBOARD-001-02-02` | blocked admins getting expert help regardless of account size | live help allocated by seat count, not blocking risk (contributing cause with its own symptom) | observed | observed (declines recorded under the policy) |
| `OPP-0004` | `NOD-CUST-SAAS-ONBOARD-001-04-01` | teammates' first week with stable permissions | leading candidate: the rules screen is reached only after invites | observed | hypothesis |
| `OPP-0006` | `NOD-CUST-SAAS-ONBOARD-001-04-02` | teammates receiving their invitations | email deliverability (stakeholder claim) | hypothesis | hypothesis, contradicted |
| `OPP-0007` | `NOD-CUST-SAAS-ONBOARD-001-01` | admins who have not started in the first week getting going | unknown | observed (45 of 412 with no login) | unknown |

## Expected value as a range

Expected value is reach × consequence, expressed as points on `MET-0001`. Each range assumes that removing the cause moves an account from the "first sync rejected" outcome rate (26%) to the "accepted" rate (44%). That gap is correlational, so every upper end is optimistic. The lower end also takes the confidence limits of the reach estimate into account.

| Opportunity | Reach | Consequence | Range (low / mid / high) | Lower bound material? |
|---|---|---|---|---|
| `OPP-0001` | 69 to 107 of 412 accounts (silent-default share of rejections, 22/30, Wilson interval) | 8.4 to 29.1 points (gap interval) | **1.4 / 4.2 / 7.6** | Barely: about 1.4 points |
| `OPP-0008` | at most 18 to 56 accounts (admin-edited share, 8/30), of which only the external-accountant share is addressable (unsized) | same gap | **0 / 1.5 / 3.9** | No |
| `OPP-0002` | the 78% of accounts that attempt a sync (321); the relevant part is the 241 whose first synced invoice came after day 7 or never | unmeasured; upper bound uses 8 of 14 admins describing gating and the 24-point gap | **0 / — / 8.0**, overlapping `OPP-0001` | No |
| `OPP-0003` | potentially every stalled account | not measurable at realistic sizes (stats.md §10) | not estimated | No |

A reader who adds these ranges is double-counting. `OPP-0001` and `OPP-0002` act on the same stalled accounts through different routes.

## Assessment

These are ordinal judgments, each with its reason. There is no weighted score: the factors are not on a common scale.

| ID | Evidence strength | Consequence | Feasibility (Q1) | Unmet dependency | Risk | Reversibility / learning |
|---|---|---|---|---|---|---|
| `OPP-0001` | Strong: mechanism traced in records | Largest lower bound, still small | High: matcher rule change | `MET-0016` baseline (2026-12-07); third ledger has no feed | More visible work at connection | Fully reversible |
| `OPP-0008` | Moderate: policy text plus 3 of 4 accountants | Unsized | Medium | Segment size; prototype with 8 accountants; Pricing and Packaging decision | Wider data access | Access can be withdrawn |
| `OPP-0009` | Weak on cause | Makes the wait visible | High once owned | RACI check | Low | Cheap to test |
| `OPP-0002` | Moderate on problem; consequence unmeasured | Lower bound 0 | High | `MET-0012` and `MET-0005` baselines | Short-term ticket rise | Randomized rollout tests the trust link |
| `OPP-0003` | Weak on safety and cause | Large gain or mis-posted invoices | Low | Guardrail baselines; safety not demonstrable at pilot size | Errors in customers' ledgers | Pilot can stop; ledger errors are costly to undo |
| `OPP-0005` | Strong on policy facts | Medium; sessions do not replace the accountant (7 of 11) | Low: capacity fixed at 6 | Effect of `INI-0001` on `MET-0008` | Cost-to-serve (`MET-0010`) | Reversible |
| `OPP-0004` | Moderate on problem, none on cause | Not computable | Unknown | Study | Stricter defaults slow teams | — |
| `OPP-0006` | Contradicted | Low | High | — | Diverts effort | — |
| `OPP-0007` | Size known, cause unknown | Unknown | Research only | — | Repeating the checklist result | High learning value |

## Decisions

`act-now` requires no unmet dependency and a lower bound that clears materiality. No opportunity meets both today.

| ID | Decision | Reason |
|---|---|---|
| `OPP-0001` | sequence | Best evidence and the only positive lower bound, but it waits on the `MET-0016` baseline (`INI-0004`) and is limited to the two ledgers with a change feed |
| `OPP-0002` | sequence | Waits on the `MET-0012` and `MET-0005` baselines; its lower bound is 0, and the randomized rollout is how it earns one |
| `OPP-0003` | sequence | Waits on guardrails, and even then the pilot can only screen for gross harm |
| `OPP-0008` | investigate | Unsized segment, lower bound 0; the accountant prototype and the new CRM field size it |
| `OPP-0009` | investigate | The RACI check at the 2026-10-14 review decides it |
| `OPP-0005` | investigate | Decide after `INI-0001` shows how much session time mapping still takes |
| `OPP-0004` | investigate | Real problem, unknown cause |
| `OPP-0006` | deprioritize | Contradicted by behavioural data; kept visible |
| `OPP-0007` | investigate | A research task, not a delivery item |

## Recommendation for Q1 2027

Fund three changes, in this order:

1. **`INI-0004` guardrail instrumentation**, now.
   - Starts 2026-10-19; instrumentation live 2026-11-30.
   - Backfilled baselines for `MET-0016`, `MET-0011`, `MET-0012` and `MET-0014` by 2026-12-07, from the 90-day change feed of the two ledgers that have one and from existing product events.
   - 4 weeks of live data by 2026-12-28.
   - Adds the external-accountant field.
2. **`INI-0001` flag unmatched rates** (for `OPP-0001`). Built now; ships in January 2027, **only to the two ledgers with a change feed**, once `MET-0016` has its baseline. The third ledger keeps current behaviour until it offers a feed. `MET-0003` is read on the rolling 8-week p-chart, and any change is `inferred` (before/after, with year-end seasonality in the window). The accountant review link and open-question trail inside `INI-0001` (for `OPP-0008`, `OPP-0009`) proceed only as the 8-accountant prototype until the segment is sized.
3. **`INI-0002` first-invoice verification** (for `OPP-0002`), as a **randomized rollout**: by account, 50/50, January to June 2027, about 170 per arm. It can detect an effect of about 15 points on `MET-0005`; a 10-point effect would need about 390 per arm. Launches after the `MET-0012` and `MET-0005` baselines exist.

**Hold `INI-0003`** (team start before mapping is confirmed). It is a harm-screening pilot, about 49 accounts per arm on the two ledgers with a feed, under a weekly sequential stop rule on `MET-0016`. It can detect a doubling of corrections and nothing smaller. Showing non-inferiority at 5 per 1,000 would need about 790 accounts per arm, roughly 30 months of intake. A clean pilot therefore does not show safety. Any wider rollout would be a risk the journey owner and Accounting Integrations accept on the record, not a demonstrated result.

Research outside the funding decision: phone recruitment of non-starters (`OPP-0007`), a study plus a blueprint of episode 4.1 (`OPP-0004`), the RACI check (`OPP-0009`), and the evidence refresh on 2026-10-07 (the operational baselines pass 60 days before the decision).

## Trade-offs made visible

- **Speed vs safety.** Gating on `INI-0004` pushes launches into January. Shipping without the fast guardrail would leave mis-posted invoices uncounted, and it is the customer who finds and pays for those.
- **Coverage vs measurability.** Customers of the third ledger get nothing this quarter, because no guardrail can be measured for them.
- **Reach vs demonstrability.** `OPP-0003` could reach the most accounts, but its safety cannot be shown at current intake. The recommendation says this plainly rather than calling a small pilot a safety test.
- **Randomization vs everyone getting the feature.** Half of the eligible accounts wait up to six months for verification, so that the trust link can be tested rather than assumed.
- **The 11 per 100 who never start** are untouched for a quarter, because nothing known would tell us what to fund.

## What would change this recommendation

- The external-accountant field shows the segment is large (over 40% of accounts): `OPP-0008` moves to `sequence`, with a lower bound.
- `MET-0003` rises after `INI-0001` but `MET-0002` does not fall: route 1 of the metric tree is wrong at its first edge.
- `INI-0002` shows no difference at its MDE: the trust link behind `MTM-0001` is weaker than assumed. That is not proof of no effect.
- Backfilled `MET-0016` baselines show corrections are already frequent: `INI-0003` is redesigned or dropped.
