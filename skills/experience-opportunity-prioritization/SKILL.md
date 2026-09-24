---
name: experience-opportunity-prioritization
description: Converts journey evidence, unmet outcomes, friction, and service root causes into solution-independent opportunity statements and prioritizes them using explicit evidence, reach, consequence, strategic relevance, feasibility, dependency, and risk. Use after CJM/EJM or service blueprinting when deciding what to address before generating features or initiatives.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Experience Opportunity Prioritization

## Goal

Move from findings to a defensible change agenda without prematurely locking into solutions.

## Opportunity statement

Prefer:

`Improve [actor outcome] in [context/journey node] by addressing [evidenced unmet need/root cause].`

Avoid:

`Build chatbot`
`Redesign app`
`Automate onboarding`

Those are solutions.

## Workflow

### 1. Extract problems and unmet outcomes
From journey evidence, moments, service failures, and metrics.

### 2. Separate problem from root cause
Record them in separate fields with separate statuses:
- `problem` — what the actor experiences (customer contacts support twice after submitting); qualified by `evidence_status`;
- `root_cause` — why it happens (no one owns the status data after submission); qualified by `root_cause_status`.

A problem is often `observed` while its cause is still `hypothesis`. When the cause is not established, write the leading candidate or `unknown` in `root_cause` and set `root_cause_status` to `hypothesis` or `unknown`; do not upgrade it because the problem is well evidenced.

### 3. Create opportunity statements
Each must include:
- actor;
- context;
- desired outcome;
- evidence IDs and evidence status;
- root cause and its status;
- one primary journey and, where known, the node;
- `moment_ids` of the moments it serves and `metric_ids` of the metrics expected to move.

A root cause that has not been traced through a blueprint or data is `inferred` or `hypothesis`, not `observed`. Another journey affected by the same opportunity reaches it through a relation (for example `enables`), not by a second journey ID.

### 4. Group related opportunities
One opportunity per root cause. Symptoms in several channels, stages, or departments that share a cause become one opportunity with several evidence IDs, not several opportunities that later spawn duplicate initiatives. Two different causes of the same problem are two opportunities.

### 5. Assess decision factors
Use explicit qualitative or ordinal assessment:

- evidence strength;
- affected reach;
- consequence/severity;
- strategic relevance;
- outcome upside;
- feasibility;
- dependencies;
- risk;
- reversibility/learning value.

Do not hide judgment in a mathematically precise score unless the scales are meaningful.

Follow `references/prioritization-method.md` for range estimates of reach and consequence, evidence strength as a separate axis, cost of delay, dependency sequencing, when scoring is acceptable, and the entry criteria for each decision in step 6.

### 6. Classify
Set `decision` to one of:
- `act-now`;
- `investigate` — evidence too weak to commit;
- `sequence` — blocked by a dependency;
- `monitor`;
- `deprioritize` — with the reason recorded.

### 7. Define expected outcome movement
Before proposing a solution.

### 8. Hand off
Use `target-experience-design` or initiative planning.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Rows use the opportunity register columns:

| opportunity_id | journey_id | node_id | moment_ids | metric_ids | actor_outcome | problem | root_cause | root_cause_status | evidence_ids | evidence_status | expected_value | feasibility | dependencies | risk | decision | owner | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Quality gates

- opportunity is solution-independent;
- evidence is traceable;
- prioritization criteria are visible;
- unknown root causes remain unknown, and `root_cause_status` is never stronger than the evidence behind the cause;
- one opportunity per root cause;
- stakeholder power is not disguised as evidence;
- opportunities link to expected outcome movement.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Use `assets/opportunity-register.csv`.
Read `references/prioritization-method.md` before writing opportunity statements, estimating value, or assigning a `decision`.
