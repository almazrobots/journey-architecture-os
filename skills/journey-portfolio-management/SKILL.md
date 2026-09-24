---
name: journey-portfolio-management
description: Creates and manages an enterprise journey atlas or portfolio across actors, lifecycles, products, channels, teams, service capabilities, metrics, opportunities, and initiatives. Use when an organization has many journey maps, needs prioritization and coverage views, wants to detect duplication/dependencies, or needs journey management at portfolio scale.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
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
Useful indicators:
- owner coverage;
- evidence freshness;
- metric coverage;
- top-opportunity coverage;
- stale rate;
- duplicate rate;
- initiative linkage;
- unresolved ownership conflicts.

### 7. Prioritize management attention
Do not rank journeys only by customer volume. Include consequence, strategic role, risk, value, and transformation dependency.

### 8. Establish review
Create portfolio review cadence and decision rights.

## Output contract

1. Journey registry.
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
- current and target versions are linked, not confused;
- journey/capability and journey/initiative relationships are queryable.

## References

Use `assets/portfolio-register.csv`.
