---
name: moments-that-matter
description: Identifies and validates moments that have disproportionate influence on customer or employee outcomes, trust, confidence, retention, effort, recovery, or business value. Use when a journey has many touchpoints and the team needs to distinguish genuinely consequential moments from ordinary pain points or high-volume interactions.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
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
Use evidence IDs and metric signals.

### 4. Distinguish types
Useful labels:
- decision moment;
- trust moment;
- transition moment;
- recovery moment;
- capability moment;
- relationship moment;
- high-risk moment.

### 5. Test counterfactual
Ask:
`If this moment went exceptionally well or badly, what downstream outcome would materially change?`

### 6. Rank cautiously
Use evidence and explicit rationale, not decorative scores.

### 7. Define design/operational implication
What must be protected, improved, or measured?

## Output contract

| moment | journey_node | outcome_at_stake | why_disproportionate | evidence | metric | failure_consequence | owner |
|---|---|---|---|---|---|---|---|

## Quality gates

- no more moments are selected than the organization can meaningfully manage;
- every moment has a consequence/outcome rationale;
- evidence is distinguishable from stakeholder belief;
- high volume alone is not sufficient.
