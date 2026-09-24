---
name: journey-metrics
description: Designs measurement trees for journeys and stages by linking actor outcomes, experience measures, behavior, operational drivers, employee/service signals, business outcomes, and guardrails. Use when a CJM/EJM needs KPIs, baselines, targets, instrumentation, health monitoring, or a causal measurement model rather than a list of disconnected metrics.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
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
Do not start with available dashboard metrics.

### 2. Build a metric tree
For each important outcome ask:
- what indicates success?
- what behavior precedes it?
- what operational conditions drive that behavior?
- what guardrail could be harmed?

### 3. Attach to journey nodes
Use stable IDs.

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

### 5. Separate diagnostic from outcome metrics
A faster internal process is not automatically a better experience.

### 6. Add qualitative sensing
Not every important experience dimension can be reduced to telemetry.

### 7. Define journey health
Create a small set of portfolio-level health indicators rather than averaging every stage metric into one opaque score.

## Output contract

| metric_id | journey_node | layer | metric | definition | source | cadence | owner | baseline | target | guardrail |
|---|---|---|---|---|---|---|---|---|---|---|

Include a causal narrative.

## Quality gates

- metrics map to explicit outcomes;
- available data does not dictate the model;
- leading and lagging signals are distinguished;
- operational metrics connect to experience effects;
- targets include units/populations/time windows;
- guardrails exist for high-risk changes.

## References

Use `assets/metric-tree-template.md`.
