# Moments that matter: Get the team invoicing in the service

> **Fictional example.** Ledgerly and all evidence are invented for illustration. Produced with `moments-that-matter`; rows live in [moment-register.csv](moment-register.csv).

Journey: `JRN-CUST-SAAS-ONBOARD-001` (current state). Outcome the moments are judged against: the team makes Ledgerly its normal way of invoicing, and the admin trusts the numbers (`MET-0001` measures this within 30 days).

## Selection

Six candidates came from the current-state map, the blueprint, support tags and one stakeholder view. Each went through the counterfactual test: *if this went exceptionally well or badly, would the downstream outcome materially change?* Pain, volume or the seniority of whoever raised it did not count on their own.

| Candidate | Node | Counterfactual result | Selected |
|---|---|---|---|
| First real invoice lands, or fails to land, correctly in the books | `NOD-CUST-SAAS-ONBOARD-001-03` | Admins say they gate the team on it (`EVD-2026-0006`, stated intent). Outcome-conditioned comparison with a pre-specified cut (`EVD-2026-0021`): 55% vs 31% meet the threshold, and the gap holds within seat bands | Yes, `MTM-0001` |
| Mapping question handed to the external accountant | `NOD-CUST-SAAS-ONBOARD-001-02-02` | The journey leaves Ledgerly's sight with no owner or date. A guess made here is one of the two traced routes to a rejected first posting (8 of 30, `EVD-2026-0003`) | Yes, `MTM-0002` |
| Approval rules decided after teammates start | `NOD-CUST-SAAS-ONBOARD-001-04-01` | Teammates' first experience is a block they cannot explain; admins tighten rules further | Yes, `MTM-0003` |
| Invitation email | `NOD-CUST-SAAS-ONBOARD-001-04-02` | High volume, but 84% of invites are accepted within 7 days (`EVD-2026-0008`). Improving it would not change the outcome; the stakeholder claim that it fails (`EVD-2026-0013`) is contradicted | No |
| First login and checklist | `NOD-CUST-SAAS-ONBOARD-001-01` | The 2025 checklist moved early activity with no detectable outcome effect (`EVD-2026-0015`), though that test could only see effects of about 13 points or more. The 11% who never start are unexplained | No; revisit after `OPP-0007` |
| Set-up session | `NOD-CUST-SAAS-ONBOARD-001-02-02` | Reachable only by 10+ seat accounts; in 7 of 11 sessions the admin still needed the accountant, so its consequence is carried by `MTM-0002` | No; folded into `MTM-0002` |

Three is the number the owners named here can actively manage alongside current work.

## Register view

| Moment | Journey node | Type | Outcome at stake | Why disproportionate | Evidence (status) | Metrics | Failure consequence | Owner |
|---|---|---|---|---|---|---|---|---|
| `MTM-0001` | `NOD-CUST-SAAS-ONBOARD-001-03` | trust | Admin's willingness to move the team onto Ledgerly | One invoice gates the whole team's start, by the admins' own account | `EVD-2026-0021`, `EVD-2026-0006` (inferred) | `MET-0002`, `MET-0006`, `MET-0001` | Admin keeps checking by hand and delays invites | Director of Customer Onboarding |
| `MTM-0002` | `NOD-CUST-SAAS-ONBOARD-001-02-02` | transition | Continuity of set-up when the decision leaves the account | The decision passes outside the account with no access, context or deadline | `EVD-2026-0005`, `EVD-2026-0007`, `EVD-2026-0011`, `EVD-2026-0017` (inferred) | `MET-0003`, `MET-0015`, `MET-0008` | Set-up pauses for an unmeasured period, or a guess fails at posting | Product Manager, Accounting Integrations |
| `MTM-0003` | `NOD-CUST-SAAS-ONBOARD-001-04-01` | decision | Teammates' first week and the admin's control over what is sent | Late rules reverse permissions mid-work | `EVD-2026-0019`, `EVD-2026-0020` (inferred) | `MET-0014`, `MET-0012` | Teammates revert to the old way or work around approvals | Product Manager, Team and Permissions |

## Why all three are `inferred`

In each case the event itself is observed. What makes a moment a moment is its disproportionate consequence, and for none of the three is that consequence measured:

- `MTM-0001` splits into two claims:
  - *Outcome differs when it goes badly.* The comparison is stratified by seat band but not by ledger vendor, and it has not been run for reference nodes. Adding both could make this claim `observed`.
  - *Improving it would move the outcome.* A before/after reading after launch would be a timing test, `inferred` at most. The randomized rollout of `INI-0002` is the only planned test that can make it `observed`, and only for an effect of about 15 points or more on `MET-0005` ([stats.md](stats.md)).
- `MTM-0002`: the length of the pause is unmeasured until `MET-0015` exists.
- `MTM-0003`: the six team members interviewed all came from accounts that met the threshold. Once `MET-0014` has a baseline and is linked to account outcomes, its excess failures per 1,000 entrants will be computed and compared with the other moments. It is dropped if its consequence is small beside them, not on prevalence alone.

## Consequence at population level

Excess failures per 1,000 entrants = share with the bad moment × (outcome rate when good − when bad) × 1,000. These are upper bounds, because the gaps are correlational (arithmetic in [stats.md](stats.md)).

| Moment | Excess per 1,000 entrants | Evidence status beside the rank |
|---|---|---|
| `MTM-0001` | about 140 | inferred |
| `MTM-0002` (via rejected first syncs) | about 57 | inferred |
| `MTM-0003` | not computable yet | inferred |

## What each moment requires

| Moment | Protect | Improve | Measure |
|---|---|---|---|
| `MTM-0001` | Accuracy of what posts (`MET-0016`, `MET-0011`) | Admin can see that the first posting matches the ledger | `MET-0006`, `MET-0002` |
| `MTM-0002` | The customer's control over who sees their books | The question reaches the person who can answer it, with context, and its age is visible | `MET-0015`, `MET-0003` |
| `MTM-0003` | Approval control for admins who need it (`MET-0012`) | Rules settled before a teammate's first action | `MET-0014` |

## Relation to the target state

The target journey `JRN-CUST-SAAS-ONBOARD-002` keeps all three moments. If `INI-0003` shows no gross harm and the journey owner accepts the remaining risk, `MTM-0001` stops gating team start. See [target-state-journey.md](target-state-journey.md).
