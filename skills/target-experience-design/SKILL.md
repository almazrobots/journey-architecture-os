---
name: target-experience-design
description: Designs evidence-informed target and transitional journey states using experience principles, desired outcomes, scenarios, service implications, capability gaps, assumptions, and experiments. Use after opportunity prioritization when creating a future-state CJM/EJM, service vision, North Star experience, transition roadmap, or testable target experience.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Target Experience Design

## Goal

Turn prioritized opportunities into a coherent future experience without confusing aspiration with validated reality.

## Workflow

### 1. Confirm current-state evidence
Target state must respond to real outcomes/opportunities or explicit strategic hypotheses.

### 2. Define experience principles
Principles should be:
- specific;
- decision-guiding;
- testable in design critique;
- relevant across touchpoints.

Weak: "delightful."
Stronger: "The actor always knows current status, next action, and accountable owner."

Each principle must name the real trade-off it resolves; see `references/target-design-method.md` (step 2) for the template and test.

### 3. Define target outcomes
For actor, service, employee, business, and guardrails.

### 4. Generate scenarios
Show how target experience works across:
- happy path;
- failure/recovery;
- high-risk edge case;
- relevant segment/context variations.

Follow `references/target-design-method.md` (steps 3–5) for outcomes per layer, the scenario set, service promises, and recovery.

### 5. Design the target journey
Keep:
- target behaviors;
- target expectations;
- service promises;
- channel roles;
- moments that matter;
- recovery design.

### 6. Design service implications
What must change in:
- people/roles;
- process;
- policy;
- data;
- systems;
- AI/automation;
- partners;
- governance.

### 7. Identify capability gaps
Separate experience vision from implementation fantasy. For AI and automation, state decision rights, confidence handling, escalation, and failure disclosure (`references/target-design-method.md`, steps 6–7).

### 8. Create transitional states
If rollout is complex, model intermediate journeys and who experiences what during rollout (`references/target-design-method.md`, step 8).

### 9. Convert assumptions into experiments
Every uncertain high-impact assumption should have a learning plan. Record each change or experiment as an initiative linked to the `OPP-` IDs it addresses and the `MET-` IDs it is expected to move.

Target states are designed, so their claims about actor response are `hypothesis` until tested; claims about the current state keep the status they had in research.

Map assumptions with `references/target-design-method.md` (step 9), then design each test with `references/experiment-design.md`: choice of design and the `evidence_status` it can earn, minimum detectable effect and sample size, clustering, rare-event guardrails, stop rules, pre-registration, and when not to run one.

### 10. Link metrics
Define expected metric movement and guardrails. Write the pre-registered effect and its minimum detectable effect in `expected_effect`, and record results in the evidence and metric-edge registers as `references/experiment-design.md` (step 11) describes.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

1. Experience principles.
2. Target outcomes.
3. Target journey.
4. Failure/recovery scenario.
5. Service implications.
6. Capability gaps.
7. Assumptions/experiments, as initiative register rows:

| initiative_id | opportunity_ids | hypothesis | change | expected_metric_ids | expected_effect | dependencies | owner | status |
|---|---|---|---|---|---|---|---|---|

8. Transitional-state needs. The target journey and each transitional journey get their own `JRN-` ID and name the `current` journey they change in `baseline_journey_id`.
9. Metric expectations.

## Quality gates

- target state is distinct from current state;
- target design is not a feature backlog;
- principles can resolve design trade-offs;
- recovery/failure is designed;
- capability implications are explicit;
- uncertain assumptions are testable.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/target-design-method.md` for principles, scenarios, promises, service implications, capability gaps, transitional states, and assumption mapping.
Read `references/experiment-design.md` for experiment design, sample size, guardrails, stop rules, and recording results.
Use `assets/initiative-register.csv` for initiatives and experiments.
