# Glossary

**Actor** — the person or role whose experience is being modeled.

**CJM** — Customer Journey Map; a model of a customer's progress and experience across a defined journey.

**EJM** — Employee Journey Map; a model of employee progress and experience across lifecycle or work episodes.

**Experience map** — broader map that can extend beyond interaction with one organization.

**Journey architecture** — hierarchy and relationships among experience domains, lifecycles, journeys, episodes, and interactions.

**Journey atlas / portfolio** — managed inventory of journeys and their metadata, ownership, health, metrics, and dependencies.

**Node** (journey node) — stage, episode, step, or interaction inside one journey (levels L3–L4), identified as `NOD-{JOURNEY_KEY}-{NN}[-{NN}…]` so the ID names its journey and position. Nodes are where evidence, moments, metrics, and opportunities attach.

**Stage** — a top-level node of a journey (L3, no parent node): a phase of the actor's progress, such as "Set up the account". Its ID has one `-{NN}` segment after the journey key.

**Episode** — a node inside a stage (L4): a bounded sequence of activity toward a sub-goal, such as "Import users". Steps and interactions are also L4 nodes; a node's depth fixes whether it is a stage.

**Moment that matters** — a moment with disproportionate effect on an important actor or organizational outcome.

**Service blueprint** — linked model of actor experience and the frontstage/backstage mechanisms that deliver it.

**Frontstage** — service activity visible to or directly interacting with the actor.

**Backstage** — service activity not directly visible but necessary for delivery.

**Touchpoint** — a concrete interaction between actor and organization/service ecosystem.

**Channel** — medium through which one or more touchpoints occur.

**Job** — progress an actor is trying to make in a context.

**Outcome** — result the actor or organization seeks, preferably defined independently of a specific solution.

**Opportunity** — evidence-backed area where improving an unmet need, friction, or outcome could create value.

**Current state** — modeled experience as it occurs now.

**Target state** — intentionally designed future experience.

**Transitional state** — intermediate experience while capabilities or processes are changing.

**Evidence register** — traceable inventory of sources and findings used to support journey claims.

**Evidence status** — label on every material claim: `observed` (directly supported by a cited source or measurement), `inferred` (reasoned from observed evidence, reasoning stated), `hypothesis` (plausible, not yet validated), or `unknown` (material question with no adequate evidence). Stakeholder input supports `hypothesis` at most.

**Register** — a CSV table with a fixed header that holds one entity type or link type: actors, journeys, relations, nodes, evidence, moments, metrics, metric edges, opportunities, initiatives, portfolio, governance, and the change log. Registers are the system of record; maps and blueprints are views that cite register IDs. Columns are defined in `skills/journey-architecture/references/ontology.md`, and each skill's `references/conventions.md` restates the ones it uses.

**Relation register** — register of lateral relationships between journeys, lifecycles, domains, and nodes (`precedes`, `can_follow`, `branches_to`, `depends_on`, `shares_touchpoint_with`, `shares_capability_with`, `enables`), each with its evidence and status. Hierarchy is not a relation; it lives in `parent_id` and `parent_node_id`.

**Metric edge** — a row of the metric-edge register: a causal claim that one metric `drives` another, or that a guardrail metric `protects` another. Edges carry their own evidence status; correlation alone supports `inferred` at most. Together the edges form a journey's metric tree, rooted in one actor-outcome metric attached to the journey.

**Experience register** — optional register of what a map shows per node: actions, touchpoints, channels, expectations, thoughts, pains, workarounds, emotions (with a valence from −2 to 2), and questions, each with its evidence and status. An emotion claimed as `observed` or `inferred` must rest on an interview, observation, diary, survey, or usability test.

**Change log** — register of material changes to a governed journey model (`CHG-{NNNN}`): what changed, when, why, on what evidence, which nodes it affected, and who approved it.

**JourneyOps** — the operational layer that keeps journeys current after mapping: ownership, versioning, evidence freshness, review cadence, metric stewardship, and portfolio decisions. In this repository: `journey-governance`, `journey-metrics`, `journey-portfolio-management`, with `journey-quality-audit` as the health check.

**Journey owner** — accountable owner for journey health and cross-functional outcome movement; not necessarily owner of every touchpoint.
