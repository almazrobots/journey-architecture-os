---
name: employee-journey-mapping
description: Creates evidence-backed employee journey maps across employee lifecycle events and real work episodes, including goals, manager and team interactions, policies, HR/IT services, tools, cultural and physical context, moments that matter, friction, outcomes, and enabling service dependencies. Use for EJM, employee experience, onboarding, internal mobility, performance, leave, workplace, or HR-service redesign.
license: MIT
metadata:
  author: journey-architecture-os
  version: "1.0.0"
  domain: experience-architecture
---

# Employee Journey Mapping

## Goal

Model employee experience as lived work and organizational interaction, not as an HR process flow.

## Key distinction

An employee journey may be:

- lifecycle-oriented: join, onboard, grow, change roles, leave;
- event-oriented: take parental leave, return to work, relocate;
- task-oriented: request equipment, get paid, access systems;
- work-episode-oriented: collaborate, make a decision, ship work, serve a customer.

Choose the structure that matches the decision.

## Experience lenses

Use only when relevant:

- role clarity;
- manager interaction;
- team/collaboration;
- culture/norms;
- technology/tools;
- physical/remote work environment;
- policy;
- HR/people services;
- IT/workplace services;
- learning/career;
- compensation/benefits;
- well-being/safety;
- organizational change.

## Workflow

### 1. Define employee actor/context
Avoid treating "employee" as one homogeneous persona.

Capture meaningful differences:
- role/work type;
- location/work mode;
- tenure/context;
- manager responsibility;
- accessibility or operational constraints.

### 2. Define the journey outcome
Use employee progress, not HR completion.

Example:
Weak: "complete onboarding workflow."
Better: "become able to perform the role confidently and independently."

### 3. Build stages from the employee's progression
Do not default to recruitment → onboarding → performance → exit unless it fits the question.

### 4. Map employee actions and expectations
Capture what employees actually do, including shadow processes and informal help.

### 5. Map human relationships
Manager/team interactions are often service touchpoints.

### 6. Map environment
Where relevant, record cultural, technological, and physical conditions.

### 7. Map friction and workarounds
Especially:
- repeated data entry;
- unclear ownership;
- policy ambiguity;
- manager dependency;
- access delays;
- fragmented tools;
- approval loops;
- hidden knowledge.

### 8. Add evidence and experience
Never infer morale, engagement, or emotion from process delay alone.

### 9. Identify moments that matter
Route candidates to `moments-that-matter`.

### 10. Connect to service delivery
Use `service-blueprinting` for HR, IT, workplace, finance, manager, and platform dependencies.

### 11. Attach outcomes/metrics
Use `journey-metrics`.

## Output contract

Include:

- employee context;
- journey scope;
- stage table;
- enabling environments;
- manager/team moments;
- friction/workarounds;
- evidence state;
- moments candidates;
- service dependencies;
- outcome metrics.

## Quality gates

- employee goal is distinct from HR process completion;
- no generic lifecycle is imposed without reason;
- manager and informal support are visible when material;
- sensitive data is minimized;
- employee voice is not substituted with leadership opinion;
- current and target states are distinct.

## References

Read `references/employee-lenses.md`.
Use `assets/ejm-template.md`.
