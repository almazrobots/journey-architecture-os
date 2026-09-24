# Governance: Get the team invoicing in the service

> **Fictional example.** Ledgerly, its roles and dates are invented for illustration. Produced with `journey-governance`. The machine-readable records are [governance-register.csv](governance-register.csv) and [change-log.csv](change-log.csv); this page is the charter around them. Owners are roles, not people.

## Managed scope

| Journey | State | Status | Owner | Review interval | Last reviewed | Next review |
|---|---|---|---|---|---|---|
| `JRN-CUST-SAAS-ONBOARD-001` | current | validated, v1.4 | Director of Customer Onboarding | 90 days | 2026-09-24 | 2026-10-14 (funding decision) |
| `JRN-CUST-SAAS-ONBOARD-002` | target | draft, v0.5 | Director of Customer Onboarding | 30 days | 2026-09-24 | 2026-10-22 |
| `JRN-CUST-SAAS-ONBOARD-003` | transitional | draft, v0.3 | Director of Customer Onboarding | 30 days | 2026-09-24 | 2026-10-22 |

The target and transitional journeys name the current journey in `baseline_journey_id` ([journey-registry.csv](journey-registry.csv)). Neighbouring journeys are linked in [relation-register.csv](relation-register.csv). `JRN-CUST-SAAS-EVALUATE-001` precedes this journey and is stale, so what sales promises about set-up is unknown here. `JRN-EMP-ONBOARD-CUSTOMER-001` enables it and has not been mapped.

## Roles

| Role | Held by | Accountable for |
|---|---|---|
| Journey owner | Director of Customer Onboarding | End-to-end outcome (`MET-0001`), roll-out decisions, approving changes |
| Portfolio owner | Chief Customer Officer | Boundaries with neighbouring journeys; funding priorities |
| Evidence steward | Research Operations Lead | Evidence register, freshness, sample notes |
| Metric owners | Named per metric in [metric-register.csv](metric-register.csv) | Definitions, instrumentation, acting on the number |
| Capability owners | PM Accounting Integrations (connector, mapping, posting); PM Team and Permissions (roles, approvals); Onboarding Operations Lead (sessions); Pricing and Packaging Lead (seat and tier policy) | Their part of delivery, not the whole journey |
| Governance forum | Monthly onboarding operations review; quarterly product portfolio review | Cross-functional decisions when ownership conflicts |

### Open RACI check

The root-cause tree lists "no owner for an open mapping question" as a `hypothesis` (`OPP-0009`). The check is scheduled for the 2026-10-14 review:

| Activity | Accounting Integrations | Onboarding Operations | Help desk | Journey owner |
|---|---|---|---|---|
| Keep the connector and matcher correct | A/R | I | I | I |
| Run set-up sessions | C | A/R | I | I |
| Answer tickets about failed syncs | C | I | A/R | I |
| Track a mapping question while it is with the accountant | ? | ? | ? | ? |

If any role can show that it already tracks open questions, the hypothesis is falsified and `OPP-0009` is closed.

## Lifecycle and freshness

- Lifecycle states: draft → validated → active → stale → archived. The current journey is `validated`. It becomes `active` once `INI-0001` ships and its metrics are reviewed monthly.
- Freshness rules (in [governance-register.csv](governance-register.csv)):
  - analytics and operational records are refreshed monthly and go stale after 60 days;
  - interviews and observation need review after 6 months (2027-02-12) and go stale after 9;
  - stakeholder input is never promoted above hypothesis;
  - an experiment goes stale once the surface or policy it tested has changed. `EVD-2026-0015` is therefore already stale for decisions about today's product, because it predates policy v4.
- Current assessment: **`needs-review`** (see [portfolio-register.csv](portfolio-register.csv)). By the 2026-10-14 decision, several operational and analytics items will be 91 to 98 days old against a 60-day rule: `EVD-2026-0003`, `EVD-2026-0004`, `EVD-2026-0008`, `EVD-2026-0009`. The outcome baseline and the leading check were re-run on 2026-09-21 (`EVD-2026-0021`) and are current. A refresh that adds the Jun–Aug 2026 cohorts is due on 2026-10-07. If it slips, the decision is taken on needs-review evidence, and the minutes say so.

## Review cadence and triggers

| Cadence | Forum | Covers |
|---|---|---|
| Weekly | Accounting Integrations | Sequential look at the fast guardrail `MET-0016` while a change or pilot is live |
| Monthly | Onboarding operations review | `MET-0003` on a rolling 8-week p-chart (act on a control-limit breach; weekly counts of about 15 are noise); `MET-0004` as a flow metric; `MET-0001` trend; `MET-0002`, `MET-0006`; guardrails `MET-0011`, `MET-0012`, `MET-0010` |
| Quarterly | Product portfolio review | Moments, opportunities, funding, boundaries |
| Every 90 days or on a trigger | Journey owner | Full journey review |

Event triggers, as recorded in the register:

| Trigger | Example for this journey |
|---|---|
| `major-service-change` | Connector release that changes matching or posting |
| `policy-change` | Change to the adviser seat rule or session tiers |
| `metric-shift` | `MET-0003` outside its p-chart limits; `MET-0016` crosses its sequential boundary; `MET-0012` breaches its threshold |
| `incident` | Mis-posted invoices reported by customers |
| `organizational-change` | Onboarding team or ownership reorganisation |
| `new-research` | Evidence that contradicts a stage or a moment, e.g. a `MET-0014` baseline under 5% |

## Change control

Every material change needs a reason, evidence IDs, the affected nodes, a version bump and an approver, and is recorded in [change-log.csv](change-log.csv) (`CHG-0001` to `CHG-0006` so far). The journey owner approves changes inside the journey. The portfolio owner approves changes that move a boundary or touch another journey.

| Change | Date | Version | What changed | Approved by |
|---|---|---|---|---|
| `CHG-0001` | 2026-08-05 | 1.0 | First validated map | Director of Customer Onboarding |
| `CHG-0002` | 2026-08-28 | 1.1 | Import episode added as unknown; survey read as a completer view | Director of Customer Onboarding |
| `CHG-0003` | 2026-09-15 | 1.2 | Stage 4 split into episodes; spam-filter claim rejected | Director of Customer Onboarding |
| `CHG-0004` | 2026-09-22 | 1.3 | Stage statuses re-derived; end boundary restated as an actor outcome; moments set to inferred; mapping opportunity split by root cause | Director of Customer Onboarding |
| `CHG-0005` | 2026-09-22 | target 0.4 | Target stage 5 aligned; pilot recast as a safety pilot | Director of Customer Onboarding |
| `CHG-0006` | 2026-09-24 | 1.4 | Stage 2 exit set at the first accepted posting; never-connectors routed to an unknown path; leading check re-cut; fast guardrail added; opportunity decisions reclassified | Chief Customer Officer (portfolio forum) |

## Open governance issues

1. The owner of an open mapping question (RACI check, 2026-10-14).
2. The sequential boundary and non-inferiority margin for `MET-0016` and `MET-0011`, to be agreed before `INI-0001` ships. Whether to accept the residual risk after `INI-0003` is a separate, recorded decision.
3. `JRN-EMP-ONBOARD-CUSTOMER-001` has no stages or metrics, although specialist capacity constrains `OPP-0005`.
4. `JRN-CUST-SAAS-EVALUATE-001` is stale; what customers are told about set-up before signing is unknown.
5. The third ledger has no change feed (`EVD-2026-0022`), so no guardrail exists for its customers, who get no change this quarter.
