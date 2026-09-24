---
name: journey-governance
description: Establishes operational governance for journey artifacts and outcomes, including ownership, lifecycle status, versioning, evidence freshness, review cadence, change control, metric stewardship, contributor roles, and links to initiatives. Use when journey maps must remain current, become enterprise assets, support recurring decisions, or avoid becoming abandoned workshop deliverables.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Journey Governance

## Goal

Make journeys durable decision assets rather than static deliverables.

## Governance objects

For every managed journey maintain:

- stable ID;
- name and scope;
- actor;
- owner;
- contributors;
- lifecycle status;
- current version;
- evidence window;
- last review;
- next review;
- metric owner(s);
- evidence steward;
- linked opportunities;
- linked initiatives;
- linked service capabilities;
- dependency journeys;
- change log.

## Roles

### Journey owner
Accountable for end-to-end outcome and journey health.

### Domain/portfolio owner
Resolves cross-journey priorities and boundaries.

### Evidence steward
Maintains research traceability/freshness.

### Metric owner
Maintains metric definitions and instrumentation.

### Capability/touchpoint owners
Own parts of delivery, not the whole journey.

### Governance forum
Makes cross-functional decisions when ownership conflicts.

## Workflow

### 1. Define managed scope
Not every map deserves enterprise governance. Select strategic or reusable journeys.

### 2. Assign accountable owner
Avoid committees as sole owner.

### 3. Set lifecycle states
Recommended:
- draft;
- validated;
- active;
- stale;
- archived.

### 4. Set evidence freshness
Freshness depends on volatility.

Examples:
- stable regulated process: longer interval;
- rapidly changing digital onboarding: shorter interval.

### 5. Set review triggers
Review can be time-based or event-based:
- major product release;
- policy change;
- channel launch;
- metric shift;
- incident;
- organizational change;
- new research.

### 6. Define change control
Material change requires:
- reason;
- evidence;
- affected nodes;
- version update;
- owners notified.

### 7. Link initiatives
No strategic journey should have an opportunity backlog disconnected from delivery planning.

### 8. Define operating cadence
Journey review should enter existing planning/review forums where possible.

## Output contract

Create:
- governance charter;
- RACI-like role model;
- journey lifecycle;
- review cadence;
- freshness rules;
- change log;
- minimum metadata standard.

## Quality gates

- one accountable owner exists;
- ownership is not confused with touchpoint control;
- review triggers are explicit;
- stale journeys can be detected;
- changes preserve evidence provenance;
- journey links to metrics and initiatives.

## References

Use `assets/governance-record.yaml`.
