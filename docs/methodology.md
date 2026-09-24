# Journey Architecture OS: methodology

## 1. The unit of work is not a map

A journey map is one representation of a larger model. The actual unit of work is a **journey system** containing:

- actor and context;
- scope and boundary;
- evidence;
- stages, episodes, and interactions;
- goals/jobs/outcomes;
- touchpoints and channels;
- experience signals;
- service-delivery dependencies;
- metrics;
- opportunities;
- target-state decisions;
- initiatives;
- ownership and governance.

## 2. The canonical loop

### Phase A — Frame
Define the decision the work must support, the actor, the scope, the journey level, and what is explicitly out of scope.

### Phase B — Evidence
Collect behavioral, attitudinal, operational, and contextual evidence. Create an evidence register before producing confident journey claims.

### Phase C — Model the actor experience
Build the current-state journey from the actor's perspective: goals, actions, expectations, touchpoints, friction, workarounds, and outcomes.

### Phase D — Model delivery
Use a service blueprint to show what makes the experience happen: frontstage, backstage, supporting processes, policies, people, data, systems, automation, and AI.

### Phase E — Diagnose
Find moments that matter, failure points, root causes, unmet outcomes, and evidence gaps.

### Phase F — Measure
Attach leading, lagging, experience, behavioral, operational, employee, business, and guardrail metrics to the right level of the journey.

### Phase G — Prioritize opportunities
Turn findings into opportunity statements before jumping to solutions. Prioritize with explicit evidence and trade-offs.

### Phase H — Design target experience
Define experience principles, desired outcomes, target-state scenarios, service implications, transitional states, and assumptions to test.

### Phase I — Activate
Connect opportunities to initiatives, experiments, owners, dependencies, milestones, and expected outcome movement.

### Phase J — Govern
Version the journey, set evidence freshness rules, assign owners, define review cadence, and manage it inside a journey portfolio.

## 3. Evidence state

Every material claim should have one of four states:

| State | Meaning |
|---|---|
| `observed` | Directly supported by research, analytics, logs, observation, or a reliable record |
| `inferred` | Reasoned conclusion derived from observed evidence |
| `hypothesis` | Plausible but unvalidated statement |
| `unknown` | Material question with insufficient evidence |

Do not encode confidence through visual polish. Encode it explicitly.

## 4. Journey hierarchy

Use hierarchy to avoid maps that are either impossibly broad or microscopically tactical.

| Level | Typical scope | Example |
|---|---|---|
| L0 | Experience domain / portfolio | Customer relationship |
| L1 | Lifecycle | Become and remain a customer |
| L2 | Journey | Start using the service |
| L3 | Episode | Verify identity |
| L4 | Interaction | Upload identity document |

A journey can contain nonlinear branches, loops, skips, and channel switches.

## 5. Three linked architectures

### Experience architecture
What actors try to achieve and experience.

### Service architecture
How the organization, partners, policies, systems, data, and automation deliver that experience.

### Change architecture
How opportunities become decisions, initiatives, experiments, and measurable outcomes.

The strongest programs maintain all three.

### JourneyOps

JourneyOps is the operational layer that keeps the three architectures current after the initial work: ownership, versioning, evidence freshness, review cadence, metric stewardship, and portfolio-level decisions (phases I and J above). It is implemented by `journey-governance`, `journey-metrics`, and `journey-portfolio-management`, with `journey-quality-audit` as the recurring health check.

## 6. CJM and EJM are siblings, not copies

CJM and EJM share a structural grammar but differ in context.

Customer journeys often emphasize acquisition, use, support, value realization, renewal, and relationship outcomes.

Employee journeys often require additional attention to:

- manager behavior;
- role clarity;
- organizational policy;
- collaboration and team norms;
- tools and workplace environment;
- career and capability;
- payroll/benefits/HR operations;
- moments of organizational change.

Do not assume a generic employee lifecycle is the employee's actual experience. Research work episodes and moments that matter.

## 7. Service blueprint boundary

A journey map answers primarily:

> What is the actor trying to do, and what do they experience?

A service blueprint answers primarily:

> What people, processes, policies, data, systems, and resources create that experience?

Keep them linked but not collapsed into an unreadable mega-map.

## 8. AI and automation layer

When AI or automation participates in service delivery, capture:

- trigger;
- input data;
- decision/action;
- human visibility;
- human override or escalation;
- confidence or uncertainty handling;
- failure mode;
- auditability;
- privacy/security constraints;
- customer/employee communication;
- operational metric.

AI is a service actor, not a decorative technology row.

## 9. Definition of done

A journey artifact is not done because the visual is polished. It is ready for use when:

- scope and actor are explicit;
- evidence and assumptions are distinguishable;
- key stages and outcomes are coherent;
- critical claims are traceable;
- moments/failures have rationale;
- opportunities have evidence and owners;
- metrics exist at the appropriate level;
- relationships to service delivery are known where relevant;
- lifecycle and review ownership are defined.
