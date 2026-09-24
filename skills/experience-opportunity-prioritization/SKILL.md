---
name: experience-opportunity-prioritization
description: Converts journey evidence, unmet outcomes, friction, and service root causes into solution-independent opportunity statements and prioritizes them using explicit evidence, reach, consequence, strategic relevance, feasibility, dependency, and risk. Use after CJM/EJM or service blueprinting when deciding what to address before generating features or initiatives.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
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

### 2. Separate symptom from cause
Example:
- symptom: customer contacts support twice;
- possible cause: status is unavailable after submission;
- root cause may exist in process/data ownership.

### 3. Create opportunity statements
Each must include:
- actor;
- context;
- desired outcome;
- evidence;
- root cause or uncertainty;
- journey node.

### 4. Group related opportunities
Avoid duplicate initiatives across channels or departments.

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

### 6. Classify
Useful portfolio buckets:
- act now;
- investigate;
- sequence after dependency;
- monitor;
- deprioritize with reason.

### 7. Define expected outcome movement
Before proposing a solution.

### 8. Hand off
Use `target-experience-design` or initiative planning.

## Output contract

| opportunity_id | journey_node | actor_outcome | problem/root_cause | evidence | expected_value | feasibility | dependencies | risk | decision | owner |
|---|---|---|---|---|---|---|---|---|---|---|

## Quality gates

- opportunity is solution-independent;
- evidence is traceable;
- prioritization criteria are visible;
- unknown root causes remain unknown;
- stakeholder power is not disguised as evidence;
- opportunities link to expected outcome movement.

## References

Use `assets/opportunity-register.csv`.
