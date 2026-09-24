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

Each of these lives in a CSV register (actors, journeys, relations, nodes, evidence, moments, metrics, metric edges, opportunities, initiatives, portfolio, governance, change log) keyed by stable IDs. Maps, blueprints, and reports are views over the registers. The columns, ID grammar, and rules are defined once, in [`skills/journey-architecture/references/ontology.md`](../skills/journey-architecture/references/ontology.md); see also [data-model.md](data-model.md).

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
Build one metric tree per journey, rooted in a single actor-outcome metric. Attach experience, behavioral, operational, employee-service, business, and guardrail metrics to the right node, and record each causal link as an edge with its own evidence status. A metric is "leading" only once its predictive link has been checked.

### Phase G — Prioritize opportunities
Turn findings into opportunity statements before jumping to solutions. Prioritize with explicit evidence and trade-offs.

### Phase H — Design target experience
Define experience principles, desired outcomes, target-state scenarios, service implications, transitional states, and assumptions to test.

### Phase I — Activate
Connect opportunities to initiatives, experiments, owners, dependencies, milestones, and expected outcome movement.

### Phase J — Govern
Version the journey, set evidence freshness rules, assign owners, define review cadence, record every material change with its reason, evidence, and approver in a change log, and manage the journey inside a portfolio.

## 3. Evidence state

Every material claim should have one of four states:

| State | Meaning |
|---|---|
| `observed` | Directly supported by research, analytics, logs, observation, or a reliable record |
| `inferred` | Reasoned conclusion derived from observed evidence |
| `hypothesis` | Plausible but unvalidated statement |
| `unknown` | Material question with insufficient evidence |

Citation rules make the status checkable: an `observed` claim cites at least one evidence item that is itself `observed`; an `inferred` claim cites at least one `observed` or `inferred` item and states the reasoning. Stakeholder input supports `hypothesis` at most. The status belongs to the claim, not the source: the same analytics export can show an `observed` drop-off and support only an `inferred` reason for it. Open questions are registered as `unknown` evidence rows so they can be cited and closed.

Do not encode confidence through visual polish. Encode it explicitly.

## 4. Journey hierarchy

Use hierarchy to avoid maps that are either impossibly broad or microscopically tactical.

| Level | Typical scope | Example |
|---|---|---|
| L0 | Experience domain / portfolio | Customer relationship |
| L1 | Lifecycle | Become and remain a customer |
| L2 | Journey | Start using the service |
| L3 | Stage | Get the account ready to use |
| L4 | Episode, step, or interaction inside a stage | Verify identity; upload identity document |

L0–L2 entries live in the journey registry; stages (L3) and everything inside them (L4) are nodes in the node register, with IDs that embed their journey (`NOD-CUST-SAAS-ONBOARD-001-03` is stage 3, `…-03-02` an episode within it). Current, target, and transitional versions of a journey are separate L2 journeys linked by `baseline_journey_id`.

A journey can contain nonlinear branches, loops, skips, and channel switches. Channel switches and loops stay inside a stage; they do not create new stages.

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
