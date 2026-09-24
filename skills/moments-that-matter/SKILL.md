---
name: moments-that-matter
description: Identifies and validates moments that have disproportionate influence on customer or employee outcomes, trust, confidence, retention, effort, recovery, or business value. Use when a journey has many touchpoints and the team needs to distinguish genuinely consequential moments from ordinary pain points or high-volume interactions.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Moments That Matter

## Goal

Find moments where quality has disproportionate consequences and explain why they matter.

## A moment is not automatically important because

- it is painful;
- it is emotional;
- it is high volume;
- a senior stakeholder cares about it;
- it appears in every journey map.

## Candidate dimensions

Evaluate with evidence:

- consequence if failed;
- irreversibility;
- trust impact;
- uncertainty/vulnerability;
- frequency or reach;
- effect on downstream behavior;
- effect on employee ability to serve;
- recovery potential;
- strategic importance;
- regulatory/safety implications.

## Workflow

### 1. Generate candidates
From research, journey map, service blueprint, metrics, complaints, and critical incidents.

### 2. Define the outcome at stake
A moment matters because of an outcome.

### 3. Attach evidence
Cite `EVD-` evidence IDs and `MET-` metric IDs. A moment whose consequence is only asserted by stakeholders stays a candidate.

### 4. Distinguish types
Assign one `moment_type`: `decision`, `trust`, `transition`, `recovery`, `capability`, `relationship`, or `high-risk`.

### 5. Test counterfactual
Ask:
`If this moment went exceptionally well or badly, what downstream outcome would materially change?`

Answer it with data where possible: follow `references/moment-analysis.md` for the outcome-conditioned comparison with stratification, critical incidents, key-driver pitfalls, and structural tests (decision, irreversibility, vulnerability).

### 6. Rank cautiously
Use evidence and explicit rationale, not decorative scores.

### 7. Define design/operational implication
What must be protected, improved, or measured?

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Rows use the moment register columns; `node_id` must exist in the node register.

| moment_id | node_id | moment_type | outcome_at_stake | why_disproportionate | evidence_ids | evidence_status | metric_ids | failure_consequence | owner |
|---|---|---|---|---|---|---|---|---|---|

Follow with rejected candidates and the reason each was rejected.

## Quality gates

- no more moments are selected than the organization can meaningfully manage;
- every moment has a consequence/outcome rationale;
- evidence is distinguishable from stakeholder belief;
- high volume alone is not sufficient.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Use `assets/moment-register.csv` for the moment register.
Read `references/moment-analysis.md` before claiming a moment is disproportionate, assigning its `evidence_status`, or deciding how many to select.
