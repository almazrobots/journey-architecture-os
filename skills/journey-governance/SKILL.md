---
name: journey-governance
description: Establishes operational governance for journey artifacts and outcomes, including ownership, lifecycle status, versioning, evidence freshness, review cadence, change control, metric stewardship, contributor roles, and links to initiatives. Use when journey maps must remain current, become enterprise assets, support recurring decisions, or avoid becoming abandoned workshop deliverables.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Journey Governance

## Goal

Make journeys durable decision assets rather than static deliverables.

## Governance objects

Governance lives in two registers, not in documents:

- **Governance register** — one row per managed journey: `journey_id, owner, evidence_steward, metric_owners, review_interval_days, last_reviewed_at, next_review_due, review_triggers, freshness_rule`. Name, actor, state, status, and version stay in the journey registry; linked opportunities and initiatives stay in the portfolio register. Do not copy them.
- **Change log** — one row per material change: `change_id` (`CHG-{NNNN}`), `journey_id, changed_at, version, change, reason, evidence_ids, affected_node_ids, approved_by`.

Owners are role names, not people. `metric_owners` and `review_triggers` are `;`-separated lists; `next_review_due` is on or after `last_reviewed_at`.

## Roles

### Journey owner
Accountable for end-to-end outcome and journey health.

### Domain/portfolio owner
Resolves cross-journey priorities and boundaries.

### Evidence steward
Maintains research traceability/freshness.

### Metric owner
Maintains metric definitions and instrumentation.

### Capability/touchpoint owners
Own parts of delivery, not the whole journey.

### Governance forum
Makes cross-functional decisions when ownership conflicts.

## Workflow

### 1. Define managed scope
Not every map deserves enterprise governance. Select strategic or reusable journeys.

### 2. Assign accountable owner
Avoid committees as sole owner.

### 3. Set lifecycle states
Use `status`:
- `draft` — hypothesis-level, not yet evidenced;
- `validated` — material claims are `observed` or `inferred`;
- `active` — owned, measured, and used in planning;
- `stale` — evidence or review is overdue;
- `archived` — retired; the ID is never reused.

Move between statuses only by the entry criteria and approvers in the transition table of `references/governance-method.md`.

### 4. Set evidence freshness
Record `evidence_freshness` as `current`, `needs-review`, `stale`, or `unknown`. Freshness depends on volatility.

Examples:
- stable regulated process: longer interval;
- rapidly changing digital onboarding: shorter interval.

Compute it per evidence row from `collected_at`, source type, and volatility, then roll up by weakest stage, as in `references/governance-method.md` Steps 1–3; the same guide covers trigger actions, change classes, and ownership escalation for steps 5–6.

### 5. Set review triggers
Review is time-based (`review_interval_days`) and event-based. `review_triggers` takes values from: `major-service-change`, `policy-change`, `channel-launch`, `metric-shift`, `incident`, `organizational-change`, `new-research`. State the `freshness_rule` in one line, for example "stale when the newest observed evidence for any stage is older than 12 months".

### 6. Define change control
Every material change is a change-log row with:
- reason;
- evidence IDs, or an explicit note that the change is not evidence-driven;
- affected node IDs;
- version update;
- a named approver role in `approved_by` for each change. The approver is the journey owner unless the change moves a boundary shared with another journey, in which case the domain or portfolio owner approves.

A change is material when it adds, removes, splits, or merges a node, moves a boundary, changes the desired outcome, or changes a claim's `evidence_status`.

### 7. Link initiatives
No strategic journey should have an opportunity backlog disconnected from delivery planning.

### 8. Define operating cadence
Journey review should enter existing planning/review forums where possible.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Create:
- governance register rows for every managed journey;
- change-log rows for every material change, each with an approver;
- RACI-like role model;
- journey lifecycle (`status` transitions and who may make them);
- review cadence and freshness rules;
- governance forum and escalation path for ownership conflicts.

## Quality gates

- one accountable owner exists;
- ownership is not confused with touchpoint control;
- review triggers are explicit;
- stale journeys can be detected;
- every change-log row has reason, evidence or an explicit no-evidence note, affected nodes, and an approver;
- changes preserve evidence provenance;
- journey links to metrics and initiatives.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Use `assets/governance-register.csv` for owners, review cadence, and triggers.
Use `assets/change-log.csv` to record every material change.
Read `references/governance-method.md` before setting freshness rules, changing a journey's status, or approving a change.
