---
name: journey-quality-audit
description: Audits customer journeys, employee journeys, service blueprints, and journey-management programs for scope, actor centricity, evidence quality, coherence, nonlinearity, service linkage, metrics, opportunity actionability, governance, and visual/model integrity. Use to review an existing CJM/EJM, detect AI-generated or workshop-only artifacts, or define a remediation plan.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
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

### 3. Identify critical blockers
Examples:
- wrong scope;
- no actor evidence;
- current/target mix;
- map is actually process flow.

### 4. Prioritize remediation
Fix structural/evidence problems before visual polish.

### 5. Recommend routing
Point to the exact skill needed for repair.

## Output contract

| dimension | score_0_3 | evidence | risk | remediation | skill |
|---|---:|---|---|---|---|

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

Use `assets/audit-scorecard.md`.
