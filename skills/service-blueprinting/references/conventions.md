<!-- Generated from the ontology of the journey-architecture skill. Do not edit by hand: change the ontology and regenerate the cards. -->

# Conventions

This card is the part of the Journey Architecture OS contract that this skill uses: identifiers, evidence statuses, and the registers the skill produces or consumes. The journey-architecture skill holds the full contract.

## Identifiers

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

Use these patterns exactly, zero-padded. Never invent short forms such as `EVD-001`, `O1`, or `Stage 3`: give a new item the next free number in its register, or describe it in prose until it has a row.

1. An ID never changes and is never reused. Rename the entity, not the ID.
2. Never delete a row to retire an entity whose ID has been published or cited. Where the register has a `status` column (journeys, portfolio, opportunities, initiatives), set it to `archived` or `rejected`; elsewhere (metrics, moments, evidence, nodes), keep the row, set its `evidence_status` honestly, and record the retirement and its reason in the change log. A draft row that was never published or cited may be removed.
3. Do not encode teams, systems, vendors, or channels in IDs; they change more often than the actor's progress.
4. Current, target, and transitional versions of a journey are separate L2 journeys with separate IDs. A `target` or `transitional` journey names the `current` journey it changes in `baseline_journey_id`; a `current` journey leaves it empty.

## Evidence status

`evidence_status` meanings:

- `observed` — directly supported by a cited source or measurement;
- `inferred` — reasoned from observed evidence, with the reasoning stated;
- `hypothesis` — plausible, not yet validated;
- `unknown` — material question with no adequate evidence. Never filled silently.

On an evidence row, `unknown` registers an evidence gap: the `finding` states the open question, so that unknowns are citable like any other evidence.

`stakeholder-input` evidence can support `hypothesis` at most, never `observed` claims about the actor's experience.

## Registers

Registers are CSV files, one per register. List-valued cells separate IDs with `;` and no spaces.

| Register | File | Template in | Columns |
|---|---|---|---|
| Journeys | `journey-registry.csv` | `journey-architecture` skill | `journey_id,level,parent_id,actor_id,name,trigger,start_boundary,end_boundary,desired_outcome,state,baseline_journey_id,status,owner,version,last_reviewed_at` |
| Relations | `relation-register.csv` | `journey-architecture` skill | `from_id,relation,to_id,evidence_ids,evidence_status,note` |
| Nodes | `node-register.csv` | `journey-architecture` skill | `node_id,journey_id,parent_node_id,node_type,sequence,name,actor_goal,evidence_ids,evidence_status` |
| Evidence | `evidence-register.csv` | `journey-research` skill | `evidence_id,source_type,source_reference,collected_at,population_or_sample,journey_id,node_id,finding,evidence_status,limitations` |
| Opportunities | `opportunity-register.csv` | `experience-opportunity-prioritization` skill | `opportunity_id,journey_id,node_id,moment_ids,metric_ids,actor_outcome,problem,root_cause,root_cause_status,evidence_ids,evidence_status,expected_value,feasibility,dependencies,risk,decision,owner,status` |

Dates use ISO 8601 (`YYYY-MM-DD`). Empty cells mean "not yet known", except status columns: `evidence_status` and `root_cause_status` are always filled, with `unknown` when not assessed. A cell holding only whitespace is invalid. Files are UTF-8; a byte-order mark is tolerated. Each register ships as a template in the owning skill's assets folder, holding the header row only.

## Enumerations

| Field | Allowed values |
|---|---|
| `evidence_status` | `observed`, `inferred`, `hypothesis`, `unknown` |
| `level` | `L0`, `L1`, `L2`, `L3`, `L4` (the journey registry and portfolio register use `L0`–`L2` only; L3–L4 are node depths) |
| `state` | `current`, `target`, `transitional` |
| `status` (journey) | `draft`, `validated`, `active`, `stale`, `archived` |
| `node_type` | `stage`, `episode`, `step`, `interaction` |
| `source_type` | `interview`, `observation`, `diary`, `usability-test`, `survey`, `analytics`, `experiment`, `support-log`, `operational-record`, `document`, `stakeholder-input`, `other` |
| `decision` (opportunity) | `act-now`, `investigate`, `sequence`, `monitor`, `deprioritize` |
| `status` (opportunity, initiative) | `draft`, `accepted`, `in-progress`, `done`, `rejected` |
| `relation` | `precedes`, `can_follow`, `branches_to`, `depends_on`, `shares_touchpoint_with`, `shares_capability_with`, `enables` |

## Column rules

- In `journey-registry` and `portfolio-register`, `journey_id` identifies an entry of the hierarchy, so its prefix follows `level`: `L0` → `DOM`, `L1` → `LFC`, `L2` → `JRN`. `level` is `L0`–`L4` overall, but L3–L4 are nodes and live in the node register, so these two registers use `L0`–`L2` only.
- `parent_id` points to an entry one or more levels up. It is empty for `DOM` rows, and may be empty for an L2 journey (or L1 lifecycle) not yet placed in the hierarchy.
- `actor_id` may be empty only for `DOM` rows, which span actors; every `LFC` and `JRN` row names its actor.
- `baseline_journey_id` links journey versions: empty when `state` is `current` or `level` is not `L2`; required when `state` is `target` or `transitional`, and then it names an L2 `JRN` whose `state` is `current` and whose `actor_id` is the same.
- Node depth fixes its level and type: a node with no parent is a `stage` (L3); a node with a parent is an `episode`, `step`, or `interaction` (L4). `sequence` equals the number in the node ID's last segment.
- On an opportunity row, `evidence_status` qualifies `problem`; `root_cause_status` qualifies `root_cause`. When the cause is not established, `root_cause` states the leading candidate or `unknown`, and `root_cause_status` is `hypothesis` or `unknown`. `moment_ids` and `metric_ids` link the moments the opportunity serves and the metrics expected to move. An opportunity belongs to one primary journey; another journey reaches it through a relation (for example `enables`), not by listing it.
- On an evidence row, `journey_id` without `node_id` means the finding concerns the whole journey.
- The relation register holds lateral relationships between hierarchy entries and nodes (`DOM`, `LFC`, `JRN`, or `NOD` IDs). Read a row as "`from_id` `relation` `to_id`": `precedes` (normally happens before), `can_follow` (may happen after), `branches_to` (an alternative path leads to), `depends_on` (cannot complete without), `shares_touchpoint_with`, `shares_capability_with`, `enables` (an employee or partner journey makes the other possible). Hierarchy is not a relation: it lives in `parent_id` and `parent_node_id`, and there is no `parent_of`. Journey versions are linked by `baseline_journey_id`, not by relations.

## Referential rules

- `node_id` must start with `NOD-` + the key of its `journey_id`.
- `parent_node_id` equals the node ID minus its last `-{NN}` segment, or is empty for stage-level nodes.
- Every ID cited in `evidence_ids`, `metric_ids`, `moment_ids`, `opportunity_ids`, `expected_metric_ids`, `affected_node_ids`, `linked_*`, `node_id`, `parent_node_id`, `journey_id`, `journey_or_node_id`, `parent_id`, `baseline_journey_id`, `actor_id`, `from_id`, `to_id`, `from_metric_id`, or `to_metric_id` must exist in its register.
- A parent sits at a lower level number than its child.
- A row with `evidence_status = observed` must cite at least one evidence ID whose own status is `observed`; a row with `inferred` must cite at least one evidence ID whose status is `observed` or `inferred`. This applies to every register with an `evidence_ids` column: nodes, relations, moments, metrics, metric edges, and opportunities. `hypothesis` and `unknown` rows may cite nothing.
- The actor code in a `JRN` or `LFC` ID equals the actor code of its `actor_id`, and a journey's parent lifecycle carries the same actor code.
- `stakeholder-input` evidence has `evidence_status` `hypothesis` or `unknown`, never `inferred` or `observed`.
- When a row cites both `journey_id` and `node_id`, the node belongs to that journey.
- Links stay inside a journey's scope. A journey's scope is the journey, its nodes, and the lifecycle and domain above it. An opportunity belongs to a `current` journey; its `moment_ids` are moments on that journey's nodes, and its `metric_ids` are metrics attached within its scope. A moment's `metric_ids` are metrics attached within the scope of the moment's journey. An initiative's `expected_metric_ids` are metrics attached within the scope of a journey of one of the opportunities it addresses.
- A relation never points from an ID to itself, and each (`from_id`, `relation`, `to_id`) triple appears once.
