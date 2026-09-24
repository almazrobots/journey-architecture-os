---
name: journey-architecture
description: Defines and maintains a hierarchy of experience domains, lifecycles, journeys, episodes, and interactions with explicit actors, boundaries, stable IDs, states, and relationships. Use when scoping CJM/EJM work, decomposing an end-to-end experience, building a journey taxonomy or atlas, or deciding what should be one journey versus multiple linked journeys.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
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

- L0 experience domain / portfolio (`DOM`);
- L1 lifecycle (`LFC`);
- L2 journey (`JRN`);
- L3 stage (`NOD`, node without a parent);
- L4 episode, step, or interaction inside a stage (`NOD` with a parent; `-{NN}` segments may nest deeper, the level stays L4).

L0–L2 live in the journey registry, L3–L4 in the node register. Not every program needs all five levels.

### 5. Set boundaries
For every L2 journey define:

- trigger;
- start condition;
- desired end state;
- failure/alternate end states;
- important preconditions;
- out-of-scope boundaries.

### 6. Map relationships
Hierarchy is already recorded in `parent_id` and `parent_node_id`, and journey versions in `baseline_journey_id`. Record every other relationship between journeys, lifecycles, domains, or nodes as a row of the relation register (`from_id, relation, to_id, evidence_ids, evidence_status, note`), read as "from `relation` to", using exactly these relations:

- `precedes` — normally happens before;
- `can_follow` — may happen after;
- `branches_to` — an alternative path leads to;
- `depends_on` — cannot complete without;
- `shares_touchpoint_with`;
- `shares_capability_with`;
- `enables` — an employee or partner journey makes the other possible.

No self-relations, and each `from_id, relation, to_id` triple appears once.

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

The hierarchy table uses the journey registry columns:

| journey_id | level | parent_id | actor_id | name | trigger | start_boundary | end_boundary | desired_outcome | state | baseline_journey_id | status | owner | version | last_reviewed_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

A `target` or `transitional` L2 journey names the `current` journey it changes in `baseline_journey_id`; leave it empty otherwise. The relationship map is the relation register, rows `from_id, relation, to_id, evidence_ids, evidence_status, note`. The actor inventory uses `actor_id, name, actor_type, segment, context`. When stages are defined, list them with the node register columns `node_id, journey_id, parent_node_id, node_type, sequence, name, actor_goal, evidence_ids, evidence_status`.

Follow `references/conventions.md` for IDs, evidence statuses, and register columns. A boundary or hierarchy agreed in a workshop is `hypothesis` until research confirms the actor experiences it that way.

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

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/ontology.md` for entity definitions and naming.
Read `references/decomposition.md` for splitting and combining rules.
Use `assets/journey-registry.csv` for the hierarchy table (L0–L2 rows).
Use `assets/actor-register.csv` for the actor inventory.
Use `assets/relation-register.csv` for the relationship map (step 6).
Use `assets/node-register.csv` for stages, episodes, steps, and interactions (L3/L4).
