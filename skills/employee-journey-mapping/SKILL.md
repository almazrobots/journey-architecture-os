---
name: employee-journey-mapping
description: Creates evidence-backed employee journey maps across employee lifecycle events and real work episodes, including goals, manager and team interactions, policies, HR/IT services, tools, cultural and physical context, moments that matter, friction, outcomes, and enabling service dependencies. Use for EJM, employee experience, onboarding, internal mobility, performance, leave, workplace, or HR-service redesign.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
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

Choose the two to four lenses from `references/employee-lenses.md` that explain the friction behind the decision (role clarity, manager, team, culture, tools, environment, policy, organizational services, capability, pay, well-being, organizational change). Lenses are questions to ask of stages, not mandatory rows.

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
Derive stages from evidence, not from the org chart:

1. Walk each employee's notes in time order and mark boundary signals: goal change, commitment point (costly to reverse), waiting or handoff the employee experiences as a distinct period, knowledge threshold, sub-outcome reached or lost.
2. Not a boundary on its own: channel change, department or system change, a calendar interval the employee does not organize around. Record these as attributes of a stage.
3. Keep a boundary when two employees, or one employee plus a non-interview source, show it.
4. Keep a span between boundaries as a stage only if it passes all four tests: the employee would recognize it; it has its own goal; it ends on an exit condition visible from the employee's side; renaming it after the team or channel serving it would lose meaning.
5. Loops and retries stay inside a stage. Aim for 3–7 stages in an L2 journey; fewer suggests an episode, more suggests steps.
6. A stage (L3) is `observed` only when its goal and boundaries are supported by at least two clusters, or by one cluster that draws on at least two independent source types; a stage resting on one cluster from a single source type is at most `inferred`; a stage with no observed evidence is `hypothesis`. A stage is never stronger than its weakest defining finding. Episodes (L4) use a lighter rule: an episode is `observed` when at least one observed finding directly shows its actions, start, and end; otherwise it takes the status of its best supporting finding.

If the `journey-research` skill is installed, its synthesis-to-stages method gives the full procedure with coding and a worked example.

### 4. Map employee actions and expectations
Capture what employees actually do, including shadow processes and informal help.

### 5. Map human relationships
Manager/team interactions are often service touchpoints.

### 6. Apply the chosen lenses
Record only the conditions from the chosen lenses that change what the employee does or achieves.

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
Collect and report employee evidence under `references/employee-research-ethics.md` (voluntariness, reporting thresholds, no manager access to raw data).
Never infer morale, engagement, or emotion from process delay alone. HR, manager, and leadership accounts of the employee experience are `stakeholder-input` and support `hypothesis` at most.

### 9. Identify moments that matter
Route candidates to `moments-that-matter`.

### 10. Connect to service delivery
Use `service-blueprinting` for HR, IT, workplace, finance, manager, and platform dependencies.

### 11. Attach outcomes/metrics
Use `journey-metrics`.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Include:

- employee context;
- journey scope;
- stage table with `node_id`, `evidence_status`, and `evidence_ids` on every row;
- enabling environments;
- manager/team moments;
- friction/workarounds;
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

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/employee-lenses.md`.
Read `references/employee-research-ethics.md` before interviewing employees or using HR/IT system data.
Use `assets/ejm-template.md`.
