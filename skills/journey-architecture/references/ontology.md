# Journey architecture ontology

This file is the canonical definition of entities, identifiers, and enumerations used by every Journey Architecture OS skill. Other skills restate only what they need; when they disagree with this file, this file wins.

## Object model

| Entity | Meaning | ID prefix |
|---|---|---|
| Actor | Person or role whose experience is modeled | `ACT` |
| Experience domain (L0) | Broad area of experience managed as a portfolio | `DOM` |
| Lifecycle (L1) | Long-running relationship containing several journeys | `LFC` |
| Journey (L2) | Bounded progress toward a meaningful outcome | `JRN` |
| Node (L3/L4) | Stage (L3), or an episode, step, or interaction inside a stage (L4) | `NOD` |
| Evidence | Registered finding from a named source, or a registered evidence gap (`unknown`) | `EVD` |
| Moment that matters | Node with disproportionate consequence | `MTM` |
| Metric | Defined measurement attached to a journey or node | `MET` |
| Opportunity | Solution-independent area for improvement | `OPP` |
| Initiative / experiment | Change that addresses one or more opportunities | `INI` |
| Change | Versioned change to a governed journey model | `CHG` |

Metric edges, relations, and governance records have no IDs of their own; they are identified by the IDs they connect.

## ID grammar

Tokens:

- `ACTOR` — actor code, 2–6 uppercase letters: `CUST`, `EMP`, `MGR`, `CAND`, `PART`, `CIT`.
- `SLUG` — one or more uppercase alphanumeric tokens joined by `-`, each starting with a letter: `ONBOARD`, `SAAS-ONBOARD`, `V2`. An all-numeric token such as `100` is not allowed, because it could be mistaken for the `{NNN}` number and would make a node ID ambiguous.
- `N` — a digit. Numbers are zero-padded to the width shown.

| Entity | Pattern | Example |
|---|---|---|
| Actor | `ACT-{ACTOR}-{SLUG}-{NN}` | `ACT-CUST-SHOP-OWNER-01` |
| Domain | `DOM-{SLUG}-{NNN}` | `DOM-CUSTOMER-LIFE-001` |
| Lifecycle | `LFC-{ACTOR}-{SLUG}-{NNN}` | `LFC-CUST-SHOP-LIFE-001` |
| Journey | `JRN-{ACTOR}-{SLUG}-{NNN}` | `JRN-CUST-SHOP-SETUP-001` |
| Node | `NOD-{JOURNEY_KEY}-{NN}[-{NN}…]` | `NOD-CUST-SHOP-SETUP-001-03` |
| Evidence | `EVD-{YYYY}-{NNNN}` | `EVD-2025-0942` |
| Moment | `MTM-{NNNN}` | `MTM-0903` |
| Metric | `MET-{NNNN}` | `MET-0912` |
| Opportunity | `OPP-{NNNN}` | `OPP-0981` |
| Initiative | `INI-{NNNN}` | `INI-0907` |
| Change | `CHG-{NNNN}` | `CHG-0904` |

`JOURNEY_KEY` is the journey ID without the leading `JRN-`. A node therefore names its journey, and each extra `-{NN}` names a child: `NOD-CUST-SHOP-SETUP-001-03` is stage 3 (L3), `NOD-CUST-SHOP-SETUP-001-03-02` is episode 2 inside it (L4). The actor code in `ACT`, `LFC`, `JRN`, and `NOD` IDs is the same code throughout one journey: a `JRN-CUST-…` journey belongs to an `ACT-CUST-…` actor and sits under an `LFC-CUST-…` lifecycle, if any.

Regular expressions (the machine-checkable form of the patterns above; validators use exactly these):

```text
ACT  ^ACT-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{2}$
DOM  ^DOM(-[A-Z][A-Z0-9]*)+-[0-9]{3}$
LFC  ^LFC-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}$
JRN  ^JRN-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}$
NOD  ^NOD-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}(-[0-9]{2})+$
EVD  ^EVD-[0-9]{4}-[0-9]{4}$
MTM  ^MTM-[0-9]{4}$
MET  ^MET-[0-9]{4}$
OPP  ^OPP-[0-9]{4}$
INI  ^INI-[0-9]{4}$
CHG  ^CHG-[0-9]{4}$
```

Rules:

1. An ID never changes and is never reused. Rename the entity, not the ID.
2. Never delete a row to retire an entity whose ID has been published or cited. Where the register has a `status` column (journeys, portfolio, opportunities, initiatives), set it to `archived` or `rejected`; elsewhere (metrics, moments, evidence, nodes), keep the row, set its `evidence_status` honestly, and record the retirement and its reason in the change log. A draft row that was never published or cited may be removed.
3. Do not encode teams, systems, vendors, or channels in IDs; they change more often than the actor's progress.
4. Current, target, and transitional versions of a journey are separate L2 journeys with separate IDs. A `target` or `transitional` journey names the `current` journey it changes in `baseline_journey_id`; a `current` journey leaves it empty.

## Enumerations

| Field | Allowed values |
|---|---|
| `evidence_status` | `observed`, `inferred`, `hypothesis`, `unknown` |
| `level` | `L0`, `L1`, `L2`, `L3`, `L4` (the journey registry and portfolio register use `L0`–`L2` only; L3–L4 are node depths) |
| `state` | `current`, `target`, `transitional` |
| `status` (journey) | `draft`, `validated`, `active`, `stale`, `archived` |
| `node_type` | `stage`, `episode`, `step`, `interaction` |
| `actor_type` | `customer`, `employee`, `manager`, `candidate`, `partner`, `citizen`, `other` |
| `source_type` | `interview`, `observation`, `diary`, `usability-test`, `survey`, `analytics`, `experiment`, `support-log`, `operational-record`, `document`, `stakeholder-input`, `other` |
| `moment_type` | `decision`, `trust`, `transition`, `recovery`, `capability`, `relationship`, `high-risk` |
| `metric layer` | `actor-outcome`, `experience`, `behavior`, `operational`, `employee-service`, `business`, `guardrail` |
| `direction` | `increase`, `decrease`, `maintain` |
| `evidence_freshness` | `current`, `needs-review`, `stale`, `unknown` |
| `decision` (opportunity) | `act-now`, `investigate`, `sequence`, `monitor`, `deprioritize` |
| `status` (opportunity, initiative) | `draft`, `accepted`, `in-progress`, `done`, `rejected` |
| `relation` | `precedes`, `can_follow`, `branches_to`, `depends_on`, `shares_touchpoint_with`, `shares_capability_with`, `enables` |
| `metric relation` | `drives`, `protects` |
| `review_trigger` | `major-service-change`, `policy-change`, `channel-launch`, `metric-shift`, `incident`, `organizational-change`, `new-research` |
| `row_type` (experience) | `action`, `touchpoint`, `channel`, `expectation`, `thought`, `pain`, `workaround`, `emotion`, `question` |
| `valence` (experience) | empty, or an integer from `-2` to `2` |
| `metric_coverage` | empty, or a decimal from `0` to `1` with up to two decimals: `0`, `0.8`, `0.75`, `1` |

`evidence_status` meanings:

- `observed` — directly supported by a cited source or measurement;
- `inferred` — reasoned from observed evidence, with the reasoning stated;
- `hypothesis` — plausible, not yet validated;
- `unknown` — material question with no adequate evidence. Never filled silently.

On an evidence row, `unknown` registers an evidence gap: the `finding` states the open question, so that unknowns are citable like any other evidence.

`stakeholder-input` evidence can support `hypothesis` at most, never `observed` claims about the actor's experience.

## Registers

The machine-readable layer of a journey system is a set of CSV registers, one file per register, named as below. The skill column names the skill that owns the register template. Maps, blueprints, and reports are views over them and cite their IDs. List-valued cells separate IDs with `;` and no spaces.

| Register | Skill | File | Columns |
|---|---|---|---|
| Actors | `journey-architecture` | `actor-register.csv` | `actor_id,name,actor_type,segment,context` |
| Journeys | `journey-architecture` | `journey-registry.csv` | `journey_id,level,parent_id,actor_id,name,trigger,start_boundary,end_boundary,desired_outcome,state,baseline_journey_id,status,owner,version,last_reviewed_at` |
| Relations | `journey-architecture` | `relation-register.csv` | `from_id,relation,to_id,evidence_ids,evidence_status,note` |
| Nodes | `journey-architecture` | `node-register.csv` | `node_id,journey_id,parent_node_id,node_type,sequence,name,actor_goal,evidence_ids,evidence_status` |
| Evidence | `journey-research` | `evidence-register.csv` | `evidence_id,source_type,source_reference,collected_at,population_or_sample,journey_id,node_id,finding,evidence_status,limitations` |
| Moments | `moments-that-matter` | `moment-register.csv` | `moment_id,node_id,moment_type,outcome_at_stake,why_disproportionate,evidence_ids,evidence_status,metric_ids,failure_consequence,owner` |
| Metrics | `journey-metrics` | `metric-register.csv` | `metric_id,journey_or_node_id,layer,name,definition,unit,source,population,cadence,owner,direction,baseline,target,evidence_ids,evidence_status` |
| Metric edges | `journey-metrics` | `metric-edge-register.csv` | `from_metric_id,relation,to_metric_id,evidence_ids,evidence_status,note` |
| Opportunities | `experience-opportunity-prioritization` | `opportunity-register.csv` | `opportunity_id,journey_id,node_id,moment_ids,metric_ids,actor_outcome,problem,root_cause,root_cause_status,evidence_ids,evidence_status,expected_value,feasibility,dependencies,risk,decision,owner,status` |
| Initiatives | `target-experience-design` | `initiative-register.csv` | `initiative_id,opportunity_ids,hypothesis,change,expected_metric_ids,expected_effect,dependencies,owner,status` |
| Portfolio | `journey-portfolio-management` | `portfolio-register.csv` | `journey_id,parent_id,level,actor_id,name,state,status,owner,evidence_freshness,metric_coverage,linked_opportunities,linked_initiatives,last_reviewed_at` |
| Governance | `journey-governance` | `governance-register.csv` | `journey_id,owner,evidence_steward,metric_owners,review_interval_days,last_reviewed_at,next_review_due,review_triggers,freshness_rule` |
| Change log | `journey-governance` | `change-log.csv` | `change_id,journey_id,changed_at,version,change,reason,evidence_ids,affected_node_ids,approved_by` |
| Experience | `customer-journey-mapping` | `experience-register.csv` | `node_id,row_type,text,evidence_ids,evidence_status,valence` |

Column clarifications:

- In `journey-registry` and `portfolio-register`, `journey_id` identifies an entry of the hierarchy, so its prefix follows `level`: `L0` → `DOM`, `L1` → `LFC`, `L2` → `JRN`. `level` is `L0`–`L4` overall, but L3–L4 are nodes and live in the node register, so these two registers use `L0`–`L2` only.
- `parent_id` points to an entry one or more levels up. It is empty for `DOM` rows, and may be empty for an L2 journey (or L1 lifecycle) not yet placed in the hierarchy.
- `actor_id` may be empty only for `DOM` rows, which span actors; every `LFC` and `JRN` row names its actor.
- `baseline_journey_id` links journey versions: empty when `state` is `current` or `level` is not `L2`; required when `state` is `target` or `transitional`, and then it names an L2 `JRN` whose `state` is `current` and whose `actor_id` is the same.
- Node depth fixes its level and type: a node with no parent is a `stage` (L3); a node with a parent is an `episode`, `step`, or `interaction` (L4). `sequence` equals the number in the node ID's last segment.
- `metric_coverage` applies to `JRN` rows only and is empty on `LFC` and `DOM` rows. It is the share of the journey's stage-level nodes that have at least one metric, written as a decimal from `0` to `1` with up to two decimals (`0.75`), or empty when not assessed. A stage counts as covered when a metric is attached to it or to any node below it; metrics attached to the journey itself do not count. For a `JRN` row with stage-level nodes, the value equals that share rounded to two decimals; for a `JRN` row with no stage-level nodes it is empty.
- A metric attaches (`journey_or_node_id`) to a `NOD`, a `JRN`, or, for business outcomes that span journeys, an `LFC` or `DOM`; a metric attached to an `LFC` or `DOM` has layer `business`.
- On a metric row, `evidence_status` qualifies the measure's validity: is it observed that this metric measures what its `name` claims, for its `population`? `evidence_ids` cites that evidence; `source` names where the measurement comes from and the evidence item behind the baseline. A metric with no baseline yet can still be valid; say so in `baseline` ("not yet measured"), not in `evidence_status`.
- Causal claims between metrics live in the metric-edge register. Read a row as "`from_metric_id` `drives` `to_metric_id`" (moving the first is expected to move the second) or "`from_metric_id` `protects` `to_metric_id`" (a guardrail that must not degrade while the second is optimized). The edge's `evidence_status` is the status of that causal claim; correlation alone supports `inferred` at most.
- Every `JRN` that has metrics has exactly one `actor-outcome` metric attached to the `JRN` itself: the root of that journey's tree. Every other metric of the journey reaches the root through `drives` edges, except `business` metrics (which the root drives) and `guardrail` metrics (which `protect` a metric).
- On an opportunity row, `evidence_status` qualifies `problem`; `root_cause_status` qualifies `root_cause`. When the cause is not established, `root_cause` states the leading candidate or `unknown`, and `root_cause_status` is `hypothesis` or `unknown`. `moment_ids` and `metric_ids` link the moments the opportunity serves and the metrics expected to move. An opportunity belongs to one primary journey; another journey reaches it through a relation (for example `enables`), not by listing it.
- In the governance register, `metric_owners` lists the roles that own the journey's metrics (the per-metric owner stays in the metric register) and `review_triggers` lists trigger values, both `;`-separated; `review_interval_days` is a positive integer; `next_review_due` is on or after `last_reviewed_at`. The change log records every material change to a governed journey with its reason, evidence, affected nodes, and approver.
- On an evidence row, `journey_id` without `node_id` means the finding concerns the whole journey.
- The relation register holds lateral relationships between hierarchy entries and nodes (`DOM`, `LFC`, `JRN`, or `NOD` IDs). Read a row as "`from_id` `relation` `to_id`": `precedes` (normally happens before), `can_follow` (may happen after), `branches_to` (an alternative path leads to), `depends_on` (cannot complete without), `shares_touchpoint_with`, `shares_capability_with`, `enables` (an employee or partner journey makes the other possible). Hierarchy is not a relation: it lives in `parent_id` and `parent_node_id`, and there is no `parent_of`. Journey versions are linked by `baseline_journey_id`, not by relations.
- The experience register holds what a map shows per node: what the actor does (`action`), where (`touchpoint`, `channel`), expects (`expectation`), thinks (`thought`, a paraphrase or a quote marked as such), what hurts (`pain`), how they cope (`workaround`), how they feel (`emotion`), and what they ask in their own words (`question`: the actor's question, not a research question; research questions are `unknown` rows in the evidence register). Rows have no IDs; each (`node_id`, `row_type`, `text`) triple appears once. `valence` is required on `emotion` rows (−2 very negative … 2 very positive) and empty on all others. The experience register is optional: a journey system without it is valid, and a map renderer then shows only what the other registers hold.

Dates use ISO 8601 (`YYYY-MM-DD`). Empty cells mean "not yet known", except status columns: `evidence_status` and `root_cause_status` are always filled, with `unknown` when not assessed. A cell holding only whitespace is invalid. Files are UTF-8; a byte-order mark is tolerated. Each register ships as a template in the owning skill's assets folder, holding the header row only.

## Referential rules

- `node_id` must start with `NOD-` + the key of its `journey_id`.
- `parent_node_id` equals the node ID minus its last `-{NN}` segment, or is empty for stage-level nodes.
- Every ID cited in `evidence_ids`, `metric_ids`, `moment_ids`, `opportunity_ids`, `expected_metric_ids`, `affected_node_ids`, `linked_*`, `node_id`, `parent_node_id`, `journey_id`, `journey_or_node_id`, `parent_id`, `baseline_journey_id`, `actor_id`, `from_id`, `to_id`, `from_metric_id`, or `to_metric_id` must exist in its register.
- A parent sits at a lower level number than its child.
- A row with `evidence_status = observed` must cite at least one evidence ID whose own status is `observed`; a row with `inferred` must cite at least one evidence ID whose status is `observed` or `inferred`. This applies to every register with an `evidence_ids` column: nodes, relations, moments, metrics, metric edges, opportunities, and experience rows. `hypothesis` and `unknown` rows may cite nothing.
- The actor code in a `JRN` or `LFC` ID equals the actor code of its `actor_id`, and a journey's parent lifecycle carries the same actor code.
- A portfolio row's `linked_opportunities` belong to that entry's journeys (for `LFC` and `DOM` rows, to journeys below them; for a `target` or `transitional` journey, to its `baseline_journey_id`, whose opportunities it realizes), and its `linked_initiatives` address at least one of those opportunities.
- An `emotion` row with `evidence_status` `observed` or `inferred` must cite at least one evidence item whose `source_type` is `interview`, `observation`, `diary`, `survey`, or `usability-test`: documents, analytics, and stakeholder input cannot show how someone felt. Every `node_id` in the experience register exists in the node register.
- Metric edges never point from a metric to itself, each (`from_metric_id`, `relation`, `to_metric_id`) triple appears once, and `drives` edges contain no cycle.
- `stakeholder-input` evidence has `evidence_status` `hypothesis` or `unknown`, never `inferred` or `observed`.
- When a row cites both `journey_id` and `node_id`, the node belongs to that journey.
- Links stay inside a journey's scope. A journey's scope is the journey, its nodes, and the lifecycle and domain above it. An opportunity belongs to a `current` journey; its `moment_ids` are moments on that journey's nodes, and its `metric_ids` are metrics attached within its scope. A moment's `metric_ids` are metrics attached within the scope of the moment's journey. An initiative's `expected_metric_ids` are metrics attached within the scope of a journey of one of the opportunities it addresses.
- A portfolio row agrees with the journey registry on `parent_id`, `level`, `actor_id`, `state`, and `status`.
- A relation never points from an ID to itself, and each (`from_id`, `relation`, `to_id`) triple appears once.

## Naming

Name journeys with verbs and actor outcomes:

- good: "Become a customer", "Start using the service", "Resolve a billing problem", "Return to work after leave";
- weak: "CRM process", "Onboarding workflow", "Contact center", "HRIS".
