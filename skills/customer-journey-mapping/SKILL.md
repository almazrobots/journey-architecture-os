---
name: customer-journey-mapping
description: Creates evidence-backed customer journey maps that model a customer's goals, stages, actions, expectations, touchpoints, channels, friction, workarounds, emotions when evidenced, outcomes, and variations. Use for current-state, transitional, day-in-the-life, or scenario-based CJM work and when translating research into an end-to-end customer experience model; for designing a future-state experience, prefer target-experience-design.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
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

### 2. Choose state and map type
Set `state` to exactly one of `current`, `target`, or `transitional`; each is a separate journey with its own ID, and a target or transitional map names the current journey it changes in `baseline_journey_id`. Do not blend states.

Separately choose the map type: a journey map bounded by the organization's service, or a day-in-the-life/context map when the service is a small part of the customer's wider effort. A context map still has one state. A map built without adequate evidence is a hypothesis map: a research instrument, not a finding.

### 3. Derive stages
Derive stages from evidence, not from the org chart:

1. Walk each customer's notes in time order and mark boundary signals: goal change, commitment point (costly to reverse), waiting or handoff the customer experiences as a distinct period, knowledge threshold, sub-outcome reached or lost.
2. Not a boundary on its own: channel change, department or system change, a calendar interval the customer does not organize around. Record these as attributes of a stage.
3. Keep a boundary when two customers, or one customer plus a non-interview source, show it.
4. Keep a span between boundaries as a stage only if it passes all four tests: the customer would recognize it; it has its own goal; it ends on an exit condition visible from the customer's side; renaming it after the team or channel serving it would lose meaning.
5. Loops and retries stay inside a stage. Aim for 3–7 stages in an L2 journey; fewer suggests an episode, more suggests steps.
6. A stage (L3) is `observed` only when its goal and boundaries are supported by at least two clusters, or by one cluster that draws on at least two independent source types; a stage resting on one cluster from a single source type is at most `inferred`; a stage with no observed evidence is `hypothesis`. A stage is never stronger than its weakest defining finding. Episodes (L4) use a lighter rule: an episode is `observed` when at least one observed finding directly shows its actions, start, and end; otherwise it takes the status of its best supporting finding.

If the `journey-research` skill is installed, its synthesis-to-stages method gives the full procedure with coding and a worked example.

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
Each significant insight should reference `EVD-` evidence IDs.
Record each node's actions, touchpoints, channels, expectations, thoughts, pains, workarounds, emotions, and questions as rows of `assets/experience-register.csv`, each with its evidence and status.

### 11. Identify candidate moments
Do not automatically label every pain point a moment that matters. Route to `moments-that-matter`.

### 12. Link metrics/opportunities
Give each stage a `NOD-` ID so metrics and opportunities can live outside the visual map in their registers.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Produce:

- journey header;
- stage table with `node_id`, `evidence_status`, and `evidence_ids` on every row;
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

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/map-types.md` when choosing map type.
Use `assets/cjm-template.md`.
Use `assets/experience-register.csv` for the per-node experience rows behind the map.
