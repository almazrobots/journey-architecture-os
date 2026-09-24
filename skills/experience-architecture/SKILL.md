---
name: experience-architecture
description: Orchestrates the full Journey Architecture OS suite from problem framing and evidence through CJM/EJM, service blueprinting, moments that matter, metrics, opportunity prioritization, target experience, governance, portfolio management, and quality audit. Use when the request is broad, cross-functional, enterprise-scale, or requires choosing and sequencing multiple journey/experience methods.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Experience Architecture Orchestrator

## Goal

Choose the smallest coherent set of journey skills that turns an ambiguous experience problem into evidence-backed decisions and an operational management model.

## Core operating loop

`Frame → Evidence → Experience Model → Service Model → Diagnose → Measure → Prioritize → Target → Activate → Govern`

Do not run every skill by default. Route based on the decision required.

## First-pass diagnosis

Determine five things from the request and available material:

1. **Decision** — what must someone decide or change?
2. **Actor** — whose experience is primary?
3. **State** — current, target, transitional, or unknown?
4. **Level** — portfolio/lifecycle, journey, episode, or interaction?
5. **Evidence** — observed evidence, stakeholder assumptions, or no evidence?

If any are unknown, state the working assumption explicitly.

## Routing rules

### Structure is unclear
Use `journey-architecture`.

### Evidence is weak or assumptions dominate
Use `journey-research` before treating the map as validated.

### Primary actor is a customer/user/member/patient/citizen
Use `customer-journey-mapping`.

### Primary actor is an employee/candidate/manager/internal worker
Use `employee-journey-mapping`.

### Goals are feature-led or organization-centric
Use `jobs-and-outcomes`.

### Root cause or delivery mechanics matter
Use `service-blueprinting`.

### Team needs to identify disproportionately important interactions
Use `moments-that-matter`.

### Team needs KPIs, instrumentation, or journey health
Use `journey-metrics`.

### Team asks what to fix first
Use `experience-opportunity-prioritization`.

### Team asks what the future experience should be
Use `target-experience-design`.

### Artifacts must stay current and owned
Use `journey-governance`.

### Many journeys must be managed together
Use `journey-portfolio-management`.

### Work is workshop-led
Use `journey-workshop-facilitation` plus the domain skill.

### Existing artifact/program needs critique
Use `journey-quality-audit`.

## Standard engagement patterns

### Pattern A — Fast diagnostic
`journey-research → (customer-journey-mapping or employee-journey-mapping) → experience-opportunity-prioritization`

Use for a bounded problem where service mechanics are already understood.

### Pattern B — Root-cause redesign
`journey-research → (customer-journey-mapping or employee-journey-mapping) → service-blueprinting → journey-metrics → experience-opportunity-prioritization → target-experience-design`

Use for cross-functional service problems.

### Pattern C — Enterprise journey management
`journey-architecture → journey-governance → journey-portfolio-management → journey-metrics → journey-quality-audit`

Use for operating-model and portfolio work.

### Pattern D — New experience design
`jobs-and-outcomes → journey-research → target-experience-design → service-blueprinting → journey-metrics`

Use when the current experience is missing or being substantially reinvented.

## Universal evidence rule

For every material claim use one of:

- `observed`;
- `inferred`;
- `hypothesis`;
- `unknown`.

Never turn stakeholder agreement into customer/employee evidence.

## Universal output package

For broad projects, maintain a linked set of artifacts rather than one mega-map:

1. engagement brief;
2. journey architecture;
3. evidence register;
4. current-state CJM/EJM;
5. service blueprint(s);
6. moments that matter;
7. metric tree;
8. opportunity register;
9. target-state journey;
10. initiative/experiment links;
11. governance record;
12. journey portfolio entry.

## Quality gates

Before declaring the work complete:

- actor and scope are explicit;
- evidence and assumptions are separable;
- journey level is appropriate to the decision;
- current and target state are distinct;
- operational root causes are modeled where needed;
- opportunities are solution-independent;
- metrics connect to outcomes;
- owners and review rules exist for managed journeys;
- artifacts can be updated without rebuilding the entire system.

## References

Read `references/operating-model.md` for end-to-end sequencing.
Use `assets/engagement-brief.md` to start a new project.
