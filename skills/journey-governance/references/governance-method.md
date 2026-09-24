# Governance method

Method for keeping governed journeys true over time: compute evidence freshness from dated evidence, move journeys through lifecycle statuses by explicit criteria, turn review triggers into actions, control changes through the change log, and resolve ownership conflicts. Use it in workflow steps 3–8. The result fills `assets/governance-register.csv` and `assets/change-log.csv`.

Grounding: records management principles, under which a record keeps its value as evidence only while its context, date, and authority are known (ISO 15489-1:2016); change control practice that classifies changes by risk and names an approver per class (ITIL 4 change enablement); versioning in which the number signals the kind of change (after Semantic Versioning); decision-role clarity (Rogers & Blenko 2006); journey management with one accountable owner and scheduled review (Stickdorn, Smaply).

## Step 1 — Classify volatility

Freshness windows depend on how fast the experience changes. Classify each governed journey, and any stage that differs from it:

| Volatility | Typical signs | Example |
|---|---|---|
| High | Releases monthly or faster; pricing or eligibility changes often; seasonal demand | Digital sign-up, app-based ordering |
| Medium | Quarterly process or system changes; stable policy | Fault repair, account changes |
| Low | Regulated or contractual process; changes yearly or less | Mortgage completion, statutory leave |

Record the class in `freshness_rule`. When unsure, choose the higher volatility; a window that is too short costs a review, one that is too long costs a wrong decision.

## Step 2 — Compute freshness per evidence row

Windows by source type and volatility (defaults; the journey owner may tighten them):

| Source type | High | Medium | Low |
|---|---|---|---|
| `analytics`, `operational-record`, `support-log` | 60 days | 90 days | 180 days |
| `interview`, `observation`, `diary`, `usability-test`, `survey` | 6 months | 12 months | 24 months |
| `experiment` | Until the tested surface, policy, or population changes | same | same |
| `document` (policy, contract, procedure) | Until superseded; check at every review | same | same |
| `stakeholder-input` | Supports `hypothesis` at most; freshness does not raise it | same | same |

For each evidence row, with `age` = review date − `collected_at` and `W` = its window:

| Freshness | Rule |
|---|---|
| `current` | `age` ≤ `W`, and no material change affecting its node has been logged since `collected_at` |
| `needs-review` | `W` < `age` ≤ 1.5 × `W`; or a material change affecting its node was logged after `collected_at` |
| `stale` | `age` > 1.5 × `W`; or the mechanism the evidence describes has been replaced (the policy, system, or process it observed no longer exists) |
| `unknown` | `collected_at` is empty, or the row is an evidence gap with status `unknown` |

The change log is the link between the two: a change row whose `affected_node_ids` include the evidence row's node, dated after `collected_at`, puts that evidence in `needs-review` at least.

## Step 3 — Roll freshness up to stages and the journey

- **Stage:** the freshness of the freshest evidence row that, on its own, supports the stage's current `evidence_status`. If only stale rows support an `observed` stage, the stage is `stale`, and at the next change its status may have to drop.
- **Journey:** the worst freshness across its stage-level nodes (weakest link). A journey with one stale stage is `stale` even if the others are current; the panel lists which stage.
- **Journey `unknown`:** when any stage has no dated evidence at all.
- Write the result to the portfolio register's `evidence_freshness` and state the rule in one line in `freshness_rule`, with the date the oldest supporting evidence crosses its window.

## Step 4 — Move through lifecycle statuses by criteria

| From → to | Entry criteria (all must hold) | Who changes it | Who approves |
|---|---|---|---|
| (new) → `draft` | Registry row with ID, actor, scope | Anyone proposing the journey | Journey owner, or portfolio lead if no owner yet |
| `draft` → `validated` | Every stage-level node cites evidence; material claims are `observed` or `inferred`; no `stakeholder-input` above `hypothesis`; contradictions recorded | Evidence steward | Journey owner |
| `validated` → `active` | Owner accepted; governance row complete; actor-outcome metric defined with a baseline or a dated plan for one; the journey is used in a planning decision (opportunities with `decision` values) | Journey owner | Domain or portfolio owner |
| `active` or `validated` → `stale` | Journey freshness `stale`; or review overdue by more than half the interval; or a review trigger unaddressed for 30 days | Evidence steward (applies the rule; no discretion) | None needed; journey owner is notified |
| `stale` → `active` / `validated` | Stale evidence refreshed or claims downgraded; review completed; change-log row written | Journey owner | Journey owner; domain owner if a shared boundary changed |
| `validated` or `active` → `draft` | Evidence found invalid for material claims (sample wrong, source withdrawn) | Evidence steward | Journey owner |
| any → `archived` | Superseded, merged, or out of managed scope; change-log row names the successor, if any | Journey owner | Domain or portfolio owner |

Target journeys: when a target is delivered, the delivered experience is researched before anyone calls it current. Only then may the target row's `state` become `current` (its `baseline_journey_id` is cleared), and the old current journey is archived with a change-log row naming its successor.

## Step 5 — Turn review triggers into actions

| `review_trigger` | Detection | Action within | Minimum action |
|---|---|---|---|
| `major-service-change` | Release or process change touching a node | 30 days | Mark affected evidence `needs-review`; check stage model and moments; log changes |
| `policy-change` | New or changed policy, eligibility, or pricing rule | 30 days | Check `document` evidence and root causes that cite the old policy |
| `channel-launch` | New channel or touchpoint | 60 days | Research the new path; add variants or branches |
| `metric-shift` | A journey metric crosses its watch threshold, or a metric definition changes | 14 days | Check whether the model explains the shift; open a research question if not |
| `incident` | Service incident, complaint spike, or regulator contact affecting actors in the journey | 7 days | Review moments of type `high-risk` and `recovery`; record findings as evidence |
| `organizational-change` | Reorganization affecting owner, steward, or capability owners | 30 days | Reconfirm roles in the governance register |
| `new-research` | Evidence added for the journey | At next review | Re-run freshness; update statuses; log material changes |

A trigger fires a targeted review of the affected nodes, not a full remap.

## Step 6 — Control changes

Classify every edit before making it:

| Class | Examples | Version | Change-log row | Approver |
|---|---|---|---|---|
| Non-material | Wording that keeps the meaning; layout; typo | No change | No | — |
| Material | Add, remove, split, or merge a node; change a claim's `evidence_status`; change a moment or its metric | Minor (1.3 → 1.4) | Yes | Journey owner (domain or portfolio owner while the journey has no owner) |
| Structural | Move a start or end boundary; change the desired outcome, actor, or trigger; split or merge journeys | Major (1.4 → 2.0) | Yes | Journey owner; domain or portfolio owner, after the other journey's owner agrees, when the boundary is shared with another journey or journeys are split or merged |

Procedure:

1. State the change and its reason; cite evidence IDs, or write "not evidence-driven" and why.
2. List `affected_node_ids`. For structural changes, list the other journeys affected.
3. Apply the change to the registers, not only to the picture.
4. Write the change-log row with the new version and `approved_by`; update `version` in the journey registry.
5. Re-run freshness for affected nodes (Step 2); evidence about the old version goes to `needs-review` or `stale`.
6. Reissue views (maps, blueprints) generated from the registers.

A change without an approver is not a governed change; it is reverted or completed.

## Step 7 — Resolve ownership conflicts

| Conflict | Signal | Resolution path |
|---|---|---|
| No owner | Journey row with empty `owner`; nobody accepts | Portfolio lead proposes a role with authority over the largest share of the actor's outcome; domain owner decides within one review cycle |
| Two claimants | Two teams each maintain a map of the same journey | Resolve as a duplicate first (one row); then the domain owner assigns one owner and names the other as capability owner |
| Owner without authority | The bottleneck sits in a capability the owner cannot change | Owner escalates the specific opportunity, not ownership, to the governance forum; capability owner is named in the opportunity's dependencies |
| Shared boundary dispute | Two journeys claim or disown the same stage | Owners of both journeys propose; domain owner decides; structural change in the change log for both |

Escalation: journey owner and counterpart try first (two weeks); then domain owner (next review); then the governance forum, which must record a decision with one named decider. Unresolved conflicts appear on the portfolio health panel until closed.

## Failure modes

- One freshness date for the whole journey, taken from the latest workshop.
- Status set by opinion ("it feels current") rather than the rule.
- Changes made in the picture, not the registers, so the model and the view drift apart.
- Stakeholder input refreshed and treated as newer evidence.
- Committees named as owners.
- Triggers listed but never detected, because nobody watches for them.

## Worked example

Journey `JRN-CUST-TELCO-FAULT-001`, "Get a broken connection fixed"; medium volatility; review date 2026-09-24. Stage-level nodes: 01 Notice the connection is down; 02 Report the fault; 03 Wait for a fix or an engineer; 04 Confirm it works again.

Evidence rows and freshness:

| evidence_id | source_type | collected_at | node | window | age | freshness |
|---|---|---|---|---|---|---|
| EVD-2024-0751 | interview | 2024-03-12 | stages 01–04 | 12 months | 30 months | stale |
| EVD-2025-0752 | support-log | 2025-01-20 | NOD-CUST-TELCO-FAULT-001-02 | 90 days | 20 months | stale |
| EVD-2026-0753 | operational-record | 2026-08-31 | NOD-CUST-TELCO-FAULT-001-03 | 90 days | 24 days | current (collected after CHG-0701) |
| EVD-2026-0754 | operational-record (incident review) | 2026-09-10 | NOD-CUST-TELCO-FAULT-001-03 | 90 days | 14 days | current |

Stage roll-up: stages 01, 02, and 04 are supported only by stale rows, so the journey is `stale`. Status moves `active` → `stale` by the evidence steward's rule; no discretion.

Events:

- 2026-07-01, a new appointment-booking system replaced the old one at stage 03. Logged as `CHG-0701`; every evidence row about stage 03 collected before that date goes to `needs-review`, and EVD-2025-0752's description of the old booking flow becomes `stale` because the mechanism no longer exists.
- 2026-09-08, an incident: households with telecare alarms were without service for more than 48 hours. `incident` trigger, 7-day action: moment `MTM-0741` (stage 03, `high-risk`) reviewed with EVD-2026-0754; `CHG-0702` records the moment's evidence status moving from `hypothesis` to `observed`.
- Ownership: network operations and customer service each claimed the other owned the journey. Domain owner decided on 2026-09-20: Head of Repair Experience owns the journey; network operations owns the repair capability.

Change-log rows:

| change_id | journey_id | changed_at | version | change | reason | evidence_ids | affected_node_ids | approved_by |
|---|---|---|---|---|---|---|---|---|
| CHG-0701 | JRN-CUST-TELCO-FAULT-001 | 2026-07-15 | 1.3 | Stage 03 episodes rewritten for the new appointment-booking flow; old flow evidence marked stale | New booking system live 2026-07-01 | EVD-2026-0753 | NOD-CUST-TELCO-FAULT-001-03 | Home connectivity domain owner |
| CHG-0702 | JRN-CUST-TELCO-FAULT-001 | 2026-09-15 | 1.4 | MTM-0741 evidence status hypothesis → observed; failure consequence restated | Incident review of 2026-09-08 outage | EVD-2026-0754 | NOD-CUST-TELCO-FAULT-001-03 | Home connectivity domain owner |
| CHG-0703 | JRN-CUST-TELCO-FAULT-001 | 2026-09-22 | 2.0 | End boundary moved from "engineer visit closed" to "customer confirms service works"; stage 04 now ends there | Old end was an organizational milestone; actor outcome required | not evidence-driven: boundary correction from quality audit | NOD-CUST-TELCO-FAULT-001-04 | Head of Repair Experience |

The journey had no owner until 2026-09-20, so the domain owner approved CHG-0701 and CHG-0702; the new owner approved CHG-0703, which moves a boundary no other journey shares.

Governance register row after the decisions:

| journey_id | owner | evidence_steward | metric_owners | review_interval_days | last_reviewed_at | next_review_due | review_triggers | freshness_rule |
|---|---|---|---|---|---|---|---|---|
| JRN-CUST-TELCO-FAULT-001 | Head of Repair Experience | Research operations lead | Head of Repair Experience;Field operations analytics lead | 90 | 2026-09-24 | 2026-12-23 | major-service-change;policy-change;metric-shift;incident;organizational-change;new-research | Medium volatility: operational data stale after 135 days, interviews after 18 months; stages 01, 02, 04 stale now; refresh interviews by 2026-11-30 |

The journey stays `stale` until interviews refresh stages 01, 02, and 04; then the owner moves it to `active` with a change-log row.

## Quality checks

- Every governed journey has a volatility class and a one-line `freshness_rule`.
- Freshness is computed per evidence row, rolled up by weakest stage, and dated.
- Status changes follow the transition table and name who changed and who approved.
- Each review trigger has a detection route, a deadline, and a minimum action.
- Every material or structural change has a change-log row with version, evidence or a no-evidence note, affected nodes, and approver.
- Ownership conflicts have a decider and a date.

## Sources

- ISO 15489-1:2016, *Information and documentation — Records management — Part 1: Concepts and principles*: https://www.iso.org/standard/62542.html
- PeopleCert / Axelos, ITIL 4 Practitioner: Change Enablement: https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil-4-practitioner-change-enablement-3794
- Tom Preston-Werner, Semantic Versioning 2.0.0: https://semver.org/
- Paul Rogers & Marcia W. Blenko, "Who Has the D? How Clear Decision Roles Enhance Organizational Performance", *Harvard Business Review* (January 2006): https://hbr.org/2006/01/who-has-the-d-how-clear-decision-roles-enhance-organizational-performance
- Marc Stickdorn, Smaply, "What Is Customer Journey Management? A Complete Guide" (2026): https://www.smaply.com/blog/customer-journey-management
