---
name: customer-journey-mapping
description: Creates evidence-backed customer journey maps that model a customer's goals, stages, actions, expectations, touchpoints, channels, friction, workarounds, emotions when evidenced, outcomes, and variations. Use for current-state, day-in-the-life, future-state, or scenario-based CJM work and when translating research into an end-to-end customer experience model.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Customer Journey Mapping

## Goal

Model customer progress and experience across a bounded journey in a form that supports diagnosis and action.

## Before mapping

Prefer to have:

- journey scope and actor;
- evidence register;
- jobs/goals/outcomes;
- clear current vs target state.

If missing, create a hypothesis map and label it as such.

## Map structure

Recommended rows:

1. Stage / episode.
2. Customer goal or job.
3. Customer actions.
4. Expectations.
5. Touchpoints.
6. Channels.
7. Questions / information needs.
8. Experience signals.
9. Frictions / barriers.
10. Workarounds.
11. Desired outcomes.
12. Evidence references.
13. Metrics.
14. Opportunities.

Do not force all rows when they add no value.

## Workflow

### 1. Confirm scope
State actor, trigger, start, end, desired outcome, and exclusions.

### 2. Choose map state
Use one of:

- current state;
- target state;
- transitional state;
- broader day-in-the-life/context map.

Do not blend states.

### 3. Derive stages
Stages should represent meaningful progression, not company departments or channels.

### 4. Populate behavior first
Add what the customer actually does before adding emotional interpretation.

### 5. Add expectations and outcomes
Expectation gaps often explain experience quality better than a generic satisfaction score.

### 6. Add touchpoints/channels
A touchpoint is an interaction; a channel is the medium.

### 7. Add friction and workarounds
Workarounds are valuable evidence of unmet needs or service design failure.

### 8. Add emotion carefully
Only show emotional states that are observed or explicitly hypothetical. Do not draw a decorative emotion curve.

### 9. Capture nonlinearity
Represent:

- branches;
- loops/retries;
- skips;
- handoffs;
- pauses;
- channel switches.

### 10. Attach evidence
Each significant insight should reference evidence IDs.

### 11. Identify candidate moments
Do not automatically label every pain point a moment that matters. Route to `moments-that-matter`.

### 12. Link metrics/opportunities
Use stable stage/node IDs so metrics and opportunities can live outside the visual map.

## Output contract

Produce:

- journey header;
- stage table;
- variations/branches;
- evidence gaps;
- strongest observed frictions;
- candidate moments that matter;
- next research questions;
- recommended next skill.

## Quality gates

- map is written from customer perspective;
- stages describe progress;
- internal process is not masquerading as the journey;
- claims have evidence status;
- channels are not used as stages unless actor progress genuinely follows channel;
- journey ends at an actor outcome, not merely "transaction complete";
- future ideas are not inserted into current state.

## References

Read `references/map-types.md` when choosing map type.
Use `assets/cjm-template.md`.
