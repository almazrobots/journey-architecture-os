# Enterprise adoption guide

## Phase 1 — Prove value on one journey

Select a journey with:

- material actor friction or strategic importance;
- enough evidence access;
- cross-functional ownership;
- plausible improvement horizon;
- measurable outcomes.

Create the evidence register, current state, service blueprint, metric tree, opportunity register, and target experience. Keep them as registers with stable IDs from day one; retrofitting IDs onto a finished deck costs more than the pilot. `examples/saas-onboarding/` shows one journey worked end to end.

## Phase 2 — Establish common grammar

Adopt the ontology (`skills/journey-architecture/references/ontology.md`) as the shared grammar rather than inventing a local one:

- journey levels (L0 domain to L4 episode/step/interaction; stages are L3);
- stable IDs that never encode teams, systems, or channels;
- evidence statuses and their citation rules;
- register columns and required fields (the JSON Schemas in `schemas/`);
- current/target/transitional journeys as separate IDs linked by `baseline_journey_id`;
- metric layers and metric edges;
- opportunity and initiative links;
- review triggers and cadence.

Extend it by adding columns through the ontology, not by forking templates per team. Run `scripts/validate_repo.py` on your registers to catch broken links and unsupported `observed` claims. Do not standardize visual appearance before standardizing semantics.

## Phase 3 — Create journey governance

Define:

- journey owner;
- domain owner;
- research/evidence steward;
- metric owner;
- delivery contributors;
- review forums;
- stale-artifact rules (a `freshness_rule` per journey);
- a change log with an approver for every material change;
- archival rules (archive, never delete or reuse an ID).

## Phase 4 — Build the atlas

Inventory journeys and connect:

- parent/child relationships;
- shared touchpoints;
- shared service capabilities;
- shared systems;
- shared metrics;
- shared opportunities;
- overlapping initiatives.

## Phase 5 — Integrate with operating rhythms

Journey management becomes useful when it enters:

- quarterly planning;
- product/service portfolio reviews;
- OKR or outcome reviews;
- research planning;
- transformation governance;
- architecture/change boards;
- employee-experience councils;
- customer-experience reviews.

## Phase 6 — Measure maturity

Measure actual operational behavior, not slide quality:

- % of strategic journeys with owner;
- % with fresh evidence;
- % of material claims that are `observed`, per journey;
- stage-level metric coverage (`metric_coverage`);
- % of top opportunities linked to initiatives;
- time from evidence to decision;
- % of initiatives with explicit journey/outcome linkage;
- stale journey rate;
- duplicated initiatives detected through journey dependencies.
