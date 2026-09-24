# Engagement brief: new accounts reaching team use

> **Fictional example.** Ledgerly and all people, numbers and sources are invented for illustration. Produced with `experience-architecture`.

- **Decision to support:** which 2–3 changes to fund in Q1 2027 to raise the share of new accounts reaching first team value within 30 days of signature (`MET-0001`, baseline 34%).
- **Decision owner:** Director of Customer Onboarding, with funding approved at the quarterly product portfolio review (2026-10-14).
- **Primary actor:** customer account admin, `ACT-CUST-SMB-ADMIN-01`.
- **Secondary actors:** team members (`ACT-CUST-SMB-TEAM-01`), external accountants (`ACT-PART-ACCOUNTANT-01`, a partner and not a customer), onboarding specialists (`ACT-EMP-ONBOARD-SPEC-01`, employee journey `JRN-EMP-ONBOARD-CUSTOMER-001`, not mapped here).
- **Context/segment:** small businesses with 3–50 staff on paid plans with 3 or more seats. Single-seat plans are excluded: "team value" does not apply to them.
- **Experience domain:** `DOM-CUSTOMER-RELATIONSHIP-001`; lifecycle `LFC-CUST-SMB-RELATIONSHIP-001`.
- **Journey level:** L2 journey `JRN-CUST-SAAS-ONBOARD-001`, with L3 stages and L4 episodes.
- **State:** current state is mapped as `JRN-CUST-SAAS-ONBOARD-001`; target as `JRN-CUST-SAAS-ONBOARD-002`; transitional as `JRN-CUST-SAAS-ONBOARD-003`.
- **Trigger:** contract signed for a plan with 3 or more seats.
- **Start boundary:** contract signature timestamp. Evaluation and purchase (`JRN-CUST-SAAS-EVALUATE-001`) are out of scope.
- **End boundary:** the team sends its real invoices through Ledgerly as its normal way of working and the admin has stopped checking postings by hand. The 30-day window belongs to the outcome metric (`MET-0001`), not to the journey: an account that gets there on day 45 has still completed the journey. Renewal (`JRN-CUST-SAAS-RENEW-001`) is out of scope.
- **Desired actor outcome:** the team sends its real invoices through Ledgerly and the admin trusts that they land correctly in the books.
- **Business outcome:** 90-day logo retention of new accounts (`MET-0009`, 86%), attached to the lifecycle `LFC-CUST-SMB-RELATIONSHIP-001`. A lagging outcome only; its link to `MET-0001` is correlational (`EVD-2026-0016`).
- **Evidence available at start:** product events, sync error log, help desk tickets, the 2025 checklist experiment (`EVD-2026-0015`), a day-30 survey, and two stakeholder views (`EVD-2026-0013`, `EVD-2026-0014`).
- **Evidence commissioned:** 14 admin interviews, 4 accountant interviews, 6 team member interviews, 11 shadowed set-up sessions (June–August 2026).
- **Known unknowns at start:** why the stall happens; whether the stakeholder explanations hold; whether any existing metric describes team value (none did, so `MET-0001` was defined for this work).
- **Stakeholders:** Customer Onboarding, Accounting Integrations product team, Team and Permissions product team, Onboarding Operations, Customer Success, Sales, Pricing and Packaging, Research Operations, Product Analytics.
- **Delivery constraints:** specialist headcount fixed at 6 through Q1 2027; the connector team has one squad; any change to adviser seat pricing needs Pricing and Packaging sign-off; about 82 new accounts a month, which limits what any experiment can detect ([stats.md](stats.md)).
- **Sensitive-data constraints:** interview notes are stored with first names removed; accountant interviews cover their clients' books, so no client names or figures are kept; support ticket text was read in the help desk tool and only tag counts left it.
- **Target review date:** 2026-09-15 for the evidence and opportunity readout; funding decision 2026-10-14.

## Why this scope

The stall is a single actor goal (get the team working in the service) with one trigger and one measurable end state, so it passes the granularity test in `journey-architecture`. Splitting by channel (email invites, in-product set-up, sessions) would have separated the admin's wait on the accountant from its consequence at team start, which is the core finding. The specialist's work was kept as a separate employee journey because its outcome and owner differ.

## Proposed skill sequence

1. `journey-architecture`: place the journey, fix IDs and boundaries (done 2026-06-20).
2. `journey-research`: inventory existing evidence, then interviews and shadowing (June–August).
3. `customer-journey-mapping`: current-state map from the admin's progress.
4. `service-blueprinting`: episode `NOD-CUST-SAAS-ONBOARD-001-02-02` only, where evidence converged.
5. `moments-that-matter`: test candidates against the counterfactual, choose three.
6. `journey-metrics`: define `MET-0001` and the tree beneath it.
7. `experience-opportunity-prioritization`: solution-independent opportunities, visible trade-offs.
8. `target-experience-design`: principles, target and transitional journeys, experiments.
9. `journey-governance` and `journey-portfolio-management`: owner, cadence, portfolio entry.
10. `journey-quality-audit`: self-audit before the funding review.

## Definition of done

- The funding recommendation names initiatives, the opportunities they address and the metrics expected to move, each by ID.
- Every stage in the current-state map has an evidence status, and at least one stage or episode is honestly `unknown`.
- At least one stakeholder belief was tested against behavioural data and the result is recorded, whichever way it went.
- Every change proposed for funding has a guardrail with a baseline before it ships.
- The journey has an accountable owner (a role), a review cadence and event-based review triggers.
- A self-audit names the weakest dimensions and what would fix them.
