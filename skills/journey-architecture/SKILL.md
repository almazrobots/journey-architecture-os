---
name: journey-architecture
description: Defines and maintains a hierarchy of experience domains, lifecycles, journeys, episodes, and interactions with explicit actors, boundaries, stable IDs, states, and relationships. Use when scoping CJM/EJM work, decomposing an end-to-end experience, building a journey taxonomy or atlas, or deciding what should be one journey versus multiple linked journeys.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Journey Architecture

## Goal

Create the structural backbone that prevents journey work from becoming a collection of unrelated maps.

## Use this skill when

- the requested journey is too broad or ambiguous;
- multiple actors, channels, products, or business units overlap;
- a team needs a journey taxonomy, hierarchy, atlas, or repository;
- you must decide the correct level of detail before mapping;
- CJM and EJM need to connect to the same service system.

## Required inputs

Use what is available. If information is missing, mark assumptions rather than inventing certainty.

- decision or business question;
- actor(s);
- trigger and intended outcome;
- known start/end boundaries;
- relevant products/services/channels;
- existing journey maps or lifecycle models;
- organizational scope.

## Non-negotiable rules

1. Start from actor progress, not department ownership.
2. Separate lifecycle, journey, episode, and interaction levels.
3. Give reusable journeys stable IDs.
4. Preserve nonlinearity: branches, loops, skips, retries, and channel switching are allowed.
5. A journey name should describe actor progress, not an internal process.
6. Do not merge multiple materially different actors into one map without a clear reason.
7. Record current, target, and transitional states separately.

## Workflow

### 1. Frame the decision
Write one sentence:

`We need this journey architecture to decide ______.`

If no decision can be identified, create a discovery-oriented architecture and label it provisional.

### 2. Identify actors
For each actor capture:

- role/context;
- goal;
- relevant segment only if behavior/outcomes differ;
- relationship to other actors.

Avoid demographic segmentation unless it explains meaningful differences.

### 3. Identify the experience domain
Define the broad domain without trying to map every interaction.

Examples:

- manage a customer relationship;
- work and grow in the organization;
- receive healthcare;
- operate as a marketplace seller.

### 4. Decompose hierarchy
Use a flexible five-level model:

- L0 experience domain / portfolio;
- L1 lifecycle;
- L2 journey;
- L3 episode;
- L4 interaction/touchpoint.

Not every program needs all five levels.

### 5. Set boundaries
For every L2 journey define:

- trigger;
- start condition;
- desired end state;
- failure/alternate end states;
- important preconditions;
- out-of-scope boundaries.

### 6. Map relationships
Capture:

- `parent_of`;
- `precedes`;
- `can_follow`;
- `branches_to`;
- `depends_on`;
- `shares_touchpoint_with`;
- `shares_capability_with`;
- `employee_enables_customer_journey`.

### 7. Assign stable IDs
IDs must survive renaming and reorganization.

Use the patterns in `references/ontology.md`.

### 8. Check granularity
Split a journey when:

- actor goal materially changes;
- ownership and metrics become incoherent;
- the journey has multiple distinct triggers/outcomes;
- research questions differ;
- the map becomes impossible to reason about.

Combine journeys when they are merely channel variants of the same actor goal.

### 9. Produce the architecture
Return:

1. scope statement;
2. actor inventory;
3. hierarchy table;
4. relationship map;
5. boundary notes;
6. unknowns and hypotheses;
7. recommended next skill.

## Output contract

At minimum:

| journey_id | level | parent_id | actor | journey | trigger | desired_outcome | state | owner |
|---|---|---|---|---|---|---|---|---|

Also include a Mermaid graph when relationships are complex.

## Quality gates

Before finalizing, verify:

- each L2 journey has one coherent actor goal;
- internal process names have been translated into actor language;
- parent-child hierarchy is non-overlapping enough to navigate;
- important alternate paths are not hidden;
- IDs are stable;
- unknowns are explicit.

## Routing

After architecture:

- evidence needed → `journey-research`;
- customer current state → `customer-journey-mapping`;
- employee current state → `employee-journey-mapping`;
- enterprise inventory → `journey-portfolio-management`.

## References

Read `references/ontology.md` for entity definitions and naming.
Read `references/decomposition.md` for splitting and combining rules.
Use `assets/journey-registry.csv` for the hierarchy table.
