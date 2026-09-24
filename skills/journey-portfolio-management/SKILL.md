---
name: journey-portfolio-management
description: Creates and manages an enterprise journey atlas or portfolio across actors, lifecycles, products, channels, teams, service capabilities, metrics, opportunities, and initiatives. Use when an organization has many journey maps, needs prioritization and coverage views, wants to detect duplication/dependencies, or needs journey management at portfolio scale.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Journey Portfolio Management

## Goal

Turn many journey artifacts into a navigable portfolio that supports prioritization, reuse, dependency management, and executive decisions.

## Portfolio views

Maintain linked views rather than one giant diagram:

- hierarchy/atlas;
- actor coverage;
- lifecycle coverage;
- journey health;
- evidence freshness;
- journey-to-capability;
- journey-to-system;
- journey-to-metric;
- journey-to-opportunity;
- journey-to-initiative;
- cross-journey moments;
- risk/regulatory coverage.

## Workflow

### 1. Inventory journeys
Normalize names, IDs, actors, levels, and state.

### 2. Detect duplicates
Two maps may be:
- duplicates;
- different states;
- different actor contexts;
- different granularity;
- channel variants.

Do not delete before resolving semantics.

### 3. Build parent/child hierarchy
Use `journey-architecture`.

### 4. Connect shared capabilities
Examples:
- identity;
- payment;
- case management;
- knowledge;
- notification;
- access provisioning;
- manager approval.

### 5. Connect metrics and initiatives
This exposes:
- orphan initiatives;
- duplicated investment;
- unmeasured journeys;
- overloaded capabilities.

### 6. Assess portfolio health
A journey's health rating is only as strong as its evidence; report the share of `observed` claims alongside freshness. Useful indicators:
- owner coverage;
- evidence freshness;
- metric coverage;
- top-opportunity coverage;
- stale rate;
- duplicate rate;
- initiative linkage;
- unresolved ownership conflicts.

Compute these as defined in `references/portfolio-health.md` (definitions, denominators, thresholds, deficit lists) and present them as a panel, not a score. The same guide covers duplicate resolution in step 2, attention gates in step 7, and cadence and decision rights in step 8.

### 7. Prioritize management attention
Do not rank journeys only by customer volume. Include consequence, strategic role, risk, value, and transformation dependency.

### 8. Establish review
Create portfolio review cadence and decision rights.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

1. Journey registry, using the portfolio register columns:

| journey_id | parent_id | level | actor_id | name | state | status | owner | evidence_freshness | metric_coverage | linked_opportunities | linked_initiatives | last_reviewed_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

Rows are `DOM` (L0), `LFC` (L1), or `JRN` (L2) entries and agree with the journey registry on `parent_id`, `level`, `actor_id`, `state`, and `status`. `metric_coverage` is filled on `JRN` rows only: the share of the journey's stages with at least one metric at or below them (`0`–`1`, two decimals); empty on `DOM` and `LFC` rows, on journeys with no stages, and when not assessed. Journey-level metrics do not count.

2. Hierarchy/atlas.
3. Coverage matrix.
4. Shared capability map.
5. Health dashboard definition.
6. Dependency list.
7. Governance issues.
8. Portfolio-level decisions required.

## Quality gates

- portfolio contains stable IDs;
- duplicates are resolved semantically;
- health is not reduced to one unexplained score;
- current and target versions are linked through `baseline_journey_id`, not confused;
- journey/capability and journey/initiative relationships are queryable.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Use `assets/portfolio-register.csv`.
Read `references/portfolio-health.md` before normalizing an inventory, resolving duplicates, reporting health, or setting review cadence.
