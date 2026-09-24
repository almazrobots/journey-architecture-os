---
name: journey-quality-audit
description: Audits customer journeys, employee journeys, service blueprints, and journey-management programs for scope, actor centricity, evidence quality, coherence, nonlinearity, service linkage, metrics, opportunity actionability, governance, and visual/model integrity. Use to review an existing CJM/EJM, detect AI-generated or workshop-only artifacts, or define a remediation plan.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Journey Quality Audit

## Goal

Determine whether a journey artifact is trustworthy and actionable, then identify the smallest set of improvements that materially increases its value.

## Audit dimensions

Score each dimension only as a diagnostic aid:

- 0 = missing or misleading;
- 1 = weak;
- 2 = usable;
- 3 = strong.

Do not collapse the audit into one score without commentary.

### A. Scope and boundaries
Actor, trigger, start/end, state, exclusions.

### B. Actor centricity
Goals/progress rather than internal process.

### C. Evidence
Traceability, recency, limitations, observed vs hypothesis.

### D. Journey coherence
Stages represent meaningful progression.

### E. Variation/nonlinearity
Branches, loops, alternate contexts.

### F. Experience integrity
Expectations, effort, emotion, trust, workarounds are not invented.

### G. Service linkage
Root causes and delivery mechanics are visible when needed.

### H. Metrics
Outcome and diagnostic measures are linked to journey nodes.

### I. Opportunities
Solution-independent, evidenced, outcome-linked.

### J. Governance
Owner, version, freshness, review cadence, change history.

### K. Visual/model integrity
The visual matches the registers (IDs shown, no nodes missing or invented), current and target are not drawn as one path, uncertainty is visually distinguished, and encodings do not imply data that does not exist.

## AI-slop detection

Red flags:

- every journey has the same 5–7 generic stages;
- generic persona with no research;
- emotion curve with no evidence;
- vague phrases like "seamless experience";
- identical pain points across stages;
- opportunities are features;
- no unknowns;
- no contradictory evidence;
- no operational root causes;
- no IDs or version;
- perfect formatting but no provenance.

## Workflow

### 1. Identify artifact purpose
Judge against intended decision, not aesthetics.

### 2. Audit dimensions
Provide score + evidence + remediation.

Score with the anchored 0–3 criteria, generic-content tests, and two-auditor procedure in `references/audit-rubric.md`; blockers override scores.

### 3. Identify critical blockers
Examples:
- wrong scope;
- no actor evidence;
- current/target mix;
- map is actually process flow.

### 4. Prioritize remediation
Fix structural/evidence problems before visual polish.

### 5. Recommend routing
For every remediation, name the repair skill by its exact name in the `skill` column: `journey-architecture`, `journey-research`, `jobs-and-outcomes`, `customer-journey-mapping`, `employee-journey-mapping`, `service-blueprinting`, `moments-that-matter`, `journey-metrics`, `experience-opportunity-prioritization`, `target-experience-design`, `journey-governance`, or `journey-portfolio-management`.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

| dimension | score_0_3 | finding | evidence_status | evidence_ids | risk | remediation | skill |
|---|---:|---|---|---|---|---|---|

Label each finding `observed` (visible in the artifact or its sources), `inferred`, `hypothesis`, or `unknown` (not assessable from the material provided).

Then provide:
- critical blockers;
- strong elements;
- remediation sequence;
- validation needs.

## Quality gates

- critique is tied to purpose;
- visual taste is not confused with methodological quality;
- missing evidence is not penalized as harshly when clearly labeled unknown;
- recommendations are specific and executable.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Use `assets/audit-scorecard.md`.
Read `references/audit-rubric.md` before scoring any dimension or declaring a blocker.
