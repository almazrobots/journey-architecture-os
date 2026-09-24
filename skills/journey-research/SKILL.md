---
name: journey-research
description: Plans, gathers, evaluates, and synthesizes qualitative, behavioral, operational, and contextual evidence for customer or employee journeys. Use before or during CJM/EJM work when assumptions must be validated, evidence sources must be triangulated, gaps identified, research questions created, or findings traced to journey claims.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Journey Research

## Goal

Produce enough trustworthy evidence to model the journey without presenting stakeholder assumptions as actor reality.

## Evidence sources

Use a mix when available:

- interviews;
- contextual observation;
- diary studies;
- usability/service tests;
- surveys;
- behavioral analytics;
- funnel/event data;
- support/contact logs;
- CRM/case histories;
- search/query logs;
- process mining;
- operational timestamps;
- quality/error records;
- employee listening;
- HR/IT service tickets;
- policy/process documentation.

## Evidence states

Every claim must be labeled:

- `observed`;
- `inferred`;
- `hypothesis`;
- `unknown`.

## Workflow

### 1. Define the decision
Research is not "learn about users." State the decision the evidence should inform.

### 2. Build research questions
Organize around:

- trigger/context;
- actor goal/job;
- expectations;
- actions and workarounds;
- touchpoints/channels;
- friction/effort;
- emotional or trust shifts;
- desired outcomes;
- failure/recovery;
- handoffs;
- variations by segment/context.

### 3. Inventory existing evidence
Create an evidence register before commissioning new research.

### 4. Evaluate evidence fitness
For each source record:

- population/sample;
- date;
- method;
- what it can and cannot support;
- likely bias;
- granularity;
- relevance to the current journey.

### 5. Fill high-value gaps
Prioritize gaps that could change:

- journey scope;
- stage model;
- root cause;
- moment-that-matters status;
- opportunity priority;
- target-state decision.

### 6. Synthesize
Group observations into themes without destroying provenance.

For each finding record:

- concise finding;
- evidence IDs;
- affected journey/stage;
- actor/context;
- strength and limitation;
- implication;
- evidence state.

### 7. Triangulate
Prefer convergence across source types.

Examples:

- interview reports confusion;
- analytics show repeated retries;
- support logs show contacts on the same topic.

Do not treat frequency in qualitative data as population prevalence unless the sample supports it.

### 8. Create evidence gaps
Explicitly list unknowns and contradictory evidence.

### 9. Hand off to mapping
Deliver an evidence pack usable by CJM/EJM skills.

## Output contract

1. Research objective.
2. Evidence inventory.
3. Evidence register.
4. Findings table.
5. Contradictions.
6. Unknowns.
7. Research gaps.
8. Recommended journey implications.

## Quality gates

- source and claim are traceable;
- sample limitations are visible;
- behavioral and attitudinal evidence are not conflated;
- internal stakeholder opinions are labeled correctly;
- current evidence is not mixed with old evidence without dates;
- sensitive employee/customer data is minimized.

## References

Read `references/evidence-model.md`.
Use `assets/evidence-register.csv`.
