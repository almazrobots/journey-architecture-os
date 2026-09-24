---
name: journey-metrics
description: Designs measurement trees for journeys and stages by linking actor outcomes, experience measures, behavior, operational drivers, employee/service signals, business outcomes, and guardrails. Use when a CJM/EJM needs KPIs, baselines, targets, instrumentation, health monitoring, or a causal measurement model rather than a list of disconnected metrics.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Journey Metrics

## Goal

Measure whether the actor achieves the desired outcome, why the journey performs as it does, and whether improvements create sustainable business value.

## Metric layers

Use a balanced set where relevant:

### Actor outcome
Did the actor achieve the result?

### Experience
Effort, confidence, clarity, trust, satisfaction, perceived control, emotion.

### Behavior
Completion, abandonment, retry, channel switching, recontact, adoption, retention.

### Operational driver
Wait time, cycle time, first-contact resolution, error, handoff, queue, defect, SLA.

### Employee/service signal
Capability, workload, tool friction, decision latency, escalation, rework.

### Business outcome
Revenue, conversion, retention, cost-to-serve, productivity, risk, quality.

### Guardrail
Privacy, safety, fairness, accessibility, complaint rate, quality degradation.

## Workflow

### 1. Start with desired outcome
Do not start with available dashboard metrics. Each journey gets exactly one `actor-outcome` metric attached to the `JRN` itself: the root of its tree.

### 2. Build a metric tree
Follow `references/metric-tree-method.md` for tree construction, metric cards, baselines, and guardrails.
For each important outcome ask:
- what indicates success?
- what behavior precedes it?
- what operational conditions drive that behavior?
- what guardrail could be harmed?

Record every causal link as a row in the metric-edge register: `from_metric_id` `drives` `to_metric_id`, or a guardrail that `protects` a metric. Every metric reaches the root through `drives` edges, except `business` metrics (the root drives them) and guardrails (they protect a metric). The edge carries its own `evidence_status`; correlation alone supports `inferred` at most.

Keep the tree to 15 metrics or fewer per journey. A metric nobody will act on is noise.

### 3. Attach to journey nodes
Attach each metric through `journey_or_node_id` to a `NOD` or the `JRN`; business outcomes that span journeys may attach to an `LFC` or `DOM`.

### 4. Define every metric
Specify:
- formula/definition;
- unit;
- source;
- population;
- cadence;
- owner;
- direction;
- baseline;
- target;
- caveats.

### 5. Separate leading from lagging, diagnostic from outcome
A faster internal process is not automatically a better experience. Call a metric "leading" only when its predictive link to the outcome has been checked in data (lagged correlation, cohort comparison, or experiment) and the edge is at least `inferred`; until then it is a candidate driver with a `hypothesis` edge.

### 6. Add qualitative sensing
Not every important experience dimension can be reduced to telemetry.

### 7. Define journey health
Create a small set of portfolio-level health indicators rather than averaging every stage metric into one opaque score.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

1. Metric register rows. `layer` is one of `actor-outcome`, `experience`, `behavior`, `operational`, `employee-service`, `business`, `guardrail`; `direction` is `increase`, `decrease`, or `maintain`.

| metric_id | journey_or_node_id | layer | name | definition | unit | source | population | cadence | owner | direction | baseline | target | evidence_ids | evidence_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

On a metric row, `evidence_status` qualifies measure validity: is it observed that this metric measures what its `name` claims, for its `population`? `evidence_ids` cites that evidence. A metric with no baseline yet can still be valid: write "not yet measured" in `baseline`, not in `evidence_status`.

2. Metric-edge rows: `from_metric_id, relation, to_metric_id, evidence_ids, evidence_status, note`, where `relation` is `drives` or `protects` and `evidence_status` qualifies the causal claim.

3. A causal narrative: one sentence per `drives` edge, citing its evidence IDs.

## Quality gates

- metrics map to explicit outcomes;
- available data does not dictate the model;
- leading and lagging signals are distinguished;
- operational metrics connect to experience effects;
- targets include units/populations/time windows;
- guardrails exist for high-risk changes, and a guardrail without a baseline and an owner blocks shipping the change it protects;
- exactly one `actor-outcome` root per journey, 15 metrics or fewer;
- no metric is called leading without a checked predictive link;
- `drives` edges contain no cycle.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/metric-tree-method.md` before defining metrics or targets.
Use `assets/metric-tree-template.md`.
Use `assets/metric-register.csv` for the metric register.
Use `assets/metric-edge-register.csv` for the drives and protects edges of the metric tree.
