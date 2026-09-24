---
name: journey-research
description: Plans, gathers, evaluates, and synthesizes qualitative, behavioral, operational, and contextual evidence for customer or employee journeys. Use before or during CJM/EJM work when assumptions must be validated, evidence sources must be triangulated, gaps identified, research questions created, or findings traced to journey claims.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
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

Give every claim an `evidence_status` (definitions in `references/conventions.md`). Research-specific rules:

- the status belongs to the claim, not the source: one analytics export can support an `observed` drop-off and only an `inferred` reason for it;
- `stakeholder-input` evidence is registered as `hypothesis` or `unknown`, never `observed` or `inferred`;
- register each material open question as an evidence row with status `unknown` whose `finding` states the question, so gaps are citable.

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
Before any new fieldwork, apply `references/research-ethics.md` (consent, minimization, retention, AI tools on transcripts).
Prioritize gaps that could change:

- journey scope;
- stage model;
- root cause;
- moment-that-matters status;
- opportunity priority;
- target-state decision.

### 6. Synthesize
Group observations into themes without destroying provenance. Follow `references/synthesis-to-stages.md` to unitize, code, cluster, and derive stages.

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

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

1. Research objective.
2. Evidence inventory.
3. Evidence register.
4. Findings table:

| finding | evidence_ids | journey_id | node_id | actor_context | evidence_status | limitations | implication |
|---|---|---|---|---|---|---|---|

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

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/evidence-model.md`.
Read `references/synthesis-to-stages.md` when turning raw evidence into findings and a stage model.
Read `references/research-ethics.md` before collecting or handling participant data.
Use `assets/evidence-register.csv`.
