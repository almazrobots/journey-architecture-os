# Example — Employee access onboarding

> Fictional example. Figures and evidence IDs are illustrative.

## Journey header

- Journey ID: `JRN-EMP-ACCESS-ONBOARD-001`
- Parent: `LFC-EMP-EMPLOYMENT-001` (join and work in the organization)
- Actor: `ACT-EMP-KNOWLEDGE-WORKER-01` — newly hired knowledge worker, hybrid, no prior accounts
- Name: Become able to work with the required systems
- State: `current`
- Status: `draft` — stage 01 is still a workshop hypothesis, stage 04 is unknown, and the ownership claim in stage 03 is unverified
- Trigger: employment contract signed
- Start boundary: start date confirmed
- End boundary: first role-critical task completed without borrowed access
- Desired outcome: can perform core role tasks using required systems

## Evidence used

| evidence_id | source_type | finding | evidence_status | limitations |
|---|---|---|---|---|
| `EVD-2024-0101` | `operational-record` | 212 of 540 service-desk tickets raised by new hires in their first 10 working days concern missing application permissions | `observed` | One quarter, one region; ticket category assigned by agents |
| `EVD-2024-0102` | `stakeholder-input` | IT believes managers submit role profiles late | `hypothesis` | Workshop statement; no timestamps checked |
| `EVD-2024-0103` | `interview` | 5 of 8 new hires describe borrowing a colleague's session or screen to complete first tasks | `observed` | Small sample; engineering and finance only |

## Stage table

| Node ID | Stage | Employee goal | Employee action | Service dependency | Friction | Evidence status | Evidence IDs |
|---|---|---|---|---|---|---|---|
| `NOD-EMP-ACCESS-ONBOARD-001-01` | Know what is needed | Understand which tools and access the role needs | Reads onboarding pack, asks manager | HR record + manager role profile | Requirements differ by team and are not written down | `hypothesis` | |
| `NOD-EMP-ACCESS-ONBOARD-001-02` | Request access | Get accounts before they are needed | Follows links, authenticates, raises requests | IAM + ITSM | Several separate requests for one role | `inferred` | `EVD-2024-0101` |
| `NOD-EMP-ACCESS-ONBOARD-001-03` | Resolve gaps | Fix missing permissions | Asks manager and service desk, borrows access | Manager approval + service desk | Missing permissions surface on first use; workaround is a borrowed session. That nobody owns the end-to-end request is a `hypothesis` to check in `service-blueprinting` | `observed` | `EVD-2024-0101;EVD-2024-0103` |
| `NOD-EMP-ACCESS-ONBOARD-001-04` | Become productive | Use tools for real work | Performs first role tasks | Applications + knowledge base + team | Access exists but context on how the team uses the tools is missing | `unknown` | |

Evidence status: `observed` (cited source or measurement) · `inferred` (reasoned from observed evidence) · `hypothesis` (plausible, not validated; includes all stakeholder input) · `unknown` (material, no adequate evidence). Stage 02 is `inferred`: ticket volume shows gaps exist but not that separate requests cause them. Stage 03 is `observed` for the permission gaps and the borrowed-session workaround, which two independent source types show (service-desk records and interviews); the claim that nobody owns the end-to-end request is not yet evidenced and stays a `hypothesis`. The late-profile claim (`EVD-2024-0102`) is kept out of the table until timestamps are checked.

## Blueprint implication

Backstage layers to verify with `service-blueprinting` (all `hypothesis` until observed in records):

- HR creates the employee record;
- manager supplies the role/access profile;
- IAM provisions baseline permissions;
- application owners approve exceptions;
- service desk resolves failures.

## Metric candidates

| metric_id | journey_or_node_id | layer | name | direction |
|---|---|---|---|---|
| `MET-0601` | `JRN-EMP-ACCESS-ONBOARD-001` | `actor-outcome` | Days from start date to first role-critical task completed | `decrease` |
| `MET-0602` | `NOD-EMP-ACCESS-ONBOARD-001-02` | `operational` | Share of baseline access ready on start date | `increase` |
| `MET-0603` | `NOD-EMP-ACCESS-ONBOARD-001-03` | `behavior` | Access-related tickets per new hire in first 10 working days | `decrease` |
| `MET-0604` | `JRN-EMP-ACCESS-ONBOARD-001` | `guardrail` | Access granted beyond role profile (least-privilege exceptions) | `maintain` |

## Next step

Before prioritizing, observe stage 01 (how requirements are actually communicated) and test the late-profile hypothesis against request timestamps. Route to `journey-research`.
