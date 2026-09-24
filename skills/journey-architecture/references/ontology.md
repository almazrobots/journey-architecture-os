# Journey architecture ontology

This file is the canonical definition of entities, identifiers, and enumerations used by every Journey Architecture OS skill. Other skills restate only what they need; when they disagree with this file, this file wins.

## Object model

| Entity | Meaning | ID prefix |
|---|---|---|
| Actor | Person or role whose experience is modeled | `ACT` |
| Experience domain (L0) | Broad area of experience managed as a portfolio | `DOM` |
| Lifecycle (L1) | Long-running relationship containing several journeys | `LFC` |
| Journey (L2) | Bounded progress toward a meaningful outcome | `JRN` |
| Node (L3/L4) | Stage, episode, step, or interaction inside a journey | `NOD` |
| Evidence | Source-backed finding | `EVD` |
| Moment that matters | Node with disproportionate consequence | `MTM` |
| Metric | Defined measurement attached to a journey or node | `MET` |
| Opportunity | Solution-independent area for improvement | `OPP` |
| Initiative / experiment | Change that addresses one or more opportunities | `INI` |

## ID grammar

Tokens:

- `ACTOR` — actor code, 2–6 uppercase letters: `CUST`, `EMP`, `MGR`, `CAND`, `PART`, `CIT`.
- `SLUG` — one or more uppercase alphanumeric tokens joined by `-`: `ONBOARD`, `SAAS-ONBOARD`.
- `N` — a digit. Numbers are zero-padded to the width shown.

| Entity | Pattern | Example |
|---|---|---|
| Actor | `ACT-{ACTOR}-{SLUG}-{NN}` | `ACT-CUST-SMB-ADMIN-01` |
| Domain | `DOM-{SLUG}-{NNN}` | `DOM-CUSTOMER-RELATIONSHIP-001` |
| Lifecycle | `LFC-{ACTOR}-{SLUG}-{NNN}` | `LFC-CUST-RELATIONSHIP-001` |
| Journey | `JRN-{ACTOR}-{SLUG}-{NNN}` | `JRN-CUST-SAAS-ONBOARD-001` |
| Node | `NOD-{JOURNEY_KEY}-{NN}[-{NN}…]` | `NOD-CUST-SAAS-ONBOARD-001-03` |
| Evidence | `EVD-{YYYY}-{NNNN}` | `EVD-2026-0042` |
| Moment | `MTM-{NNNN}` | `MTM-0003` |
| Metric | `MET-{NNNN}` | `MET-0012` |
| Opportunity | `OPP-{NNNN}` | `OPP-0081` |
| Initiative | `INI-{NNNN}` | `INI-0007` |

`JOURNEY_KEY` is the journey ID without the leading `JRN-`. A node therefore names its journey, and each extra `-{NN}` names a child: `NOD-CUST-SAAS-ONBOARD-001-03` is stage 3, `NOD-CUST-SAAS-ONBOARD-001-03-02` is episode 2 inside it.

Regular expressions (used by `scripts/validate_repo.py`):

```text
ACT  ^ACT-[A-Z]{2,6}(-[A-Z0-9]+)+-[0-9]{2}$
DOM  ^DOM(-[A-Z0-9]+)+-[0-9]{3}$
LFC  ^LFC-[A-Z]{2,6}(-[A-Z0-9]+)+-[0-9]{3}$
JRN  ^JRN-[A-Z]{2,6}(-[A-Z0-9]+)+-[0-9]{3}$
NOD  ^NOD-[A-Z]{2,6}(-[A-Z0-9]+)+-[0-9]{3}(-[0-9]{2})+$
EVD  ^EVD-[0-9]{4}-[0-9]{4}$
MTM  ^MTM-[0-9]{4}$
MET  ^MET-[0-9]{4}$
OPP  ^OPP-[0-9]{4}$
INI  ^INI-[0-9]{4}$
```

Rules:

1. An ID never changes and is never reused. Rename the entity, not the ID.
2. Retire an entity by setting its status to `archived`, not by deleting the row.
3. Do not encode teams, systems, vendors, or channels in IDs; they change more often than the actor's progress.
4. Current, target, and transitional versions of a journey are separate journeys with separate IDs, linked through the portfolio register.

## Enumerations

| Field | Allowed values |
|---|---|
| `evidence_status` | `observed`, `inferred`, `hypothesis`, `unknown` |
| `level` | `L0`, `L1`, `L2`, `L3`, `L4` |
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

`evidence_status` meanings:

- `observed` — directly supported by a cited source or measurement;
- `inferred` — reasoned from observed evidence, with the reasoning stated;
- `hypothesis` — plausible, not yet validated;
- `unknown` — material question with no adequate evidence. Never filled silently.

`stakeholder-input` evidence can support `hypothesis` at most, never `observed` claims about the actor's experience.

## Registers

The machine-readable layer of a journey system is a set of CSV registers. Maps, blueprints, and reports are views over them and cite their IDs. List-valued cells separate IDs with `;` and no spaces.

| Register | Asset | Columns |
|---|---|---|
| Actors | `journey-architecture/assets/actor-register.csv` | `actor_id,name,actor_type,segment,context` |
| Journeys | `journey-architecture/assets/journey-registry.csv` | `journey_id,level,parent_id,actor_id,name,trigger,start_boundary,end_boundary,desired_outcome,state,status,owner,version,last_reviewed_at` |
| Nodes | `journey-architecture/assets/node-register.csv` | `node_id,journey_id,parent_node_id,node_type,sequence,name,actor_goal,evidence_ids,evidence_status` |
| Evidence | `journey-research/assets/evidence-register.csv` | `evidence_id,source_type,source_reference,collected_at,population_or_sample,journey_id,node_id,finding,evidence_status,limitations` |
| Moments | `moments-that-matter/assets/moment-register.csv` | `moment_id,node_id,moment_type,outcome_at_stake,why_disproportionate,evidence_ids,evidence_status,metric_ids,failure_consequence,owner` |
| Metrics | `journey-metrics/assets/metric-register.csv` | `metric_id,journey_or_node_id,layer,name,definition,unit,source,population,cadence,owner,direction,baseline,target,evidence_status` |
| Opportunities | `experience-opportunity-prioritization/assets/opportunity-register.csv` | `opportunity_id,journey_id,node_id,actor_outcome,problem_or_root_cause,evidence_ids,evidence_status,expected_value,feasibility,dependencies,risk,decision,owner,status` |
| Initiatives | `target-experience-design/assets/initiative-register.csv` | `initiative_id,opportunity_ids,hypothesis,change,expected_metric_ids,expected_effect,dependencies,owner,status` |
| Portfolio | `journey-portfolio-management/assets/portfolio-register.csv` | `journey_id,parent_id,level,actor_id,name,state,status,owner,evidence_freshness,metric_coverage,linked_opportunities,linked_initiatives,last_reviewed_at` |

Dates use ISO 8601 (`YYYY-MM-DD`). Empty cells mean "not yet known"; required columns are defined by the JSON Schemas in `schemas/`.

## Referential rules

- `node_id` must start with `NOD-` + the key of its `journey_id`.
- `parent_node_id` equals the node ID minus its last `-{NN}` segment, or is empty for stage-level nodes.
- Every ID cited in `evidence_ids`, `metric_ids`, `opportunity_ids`, `expected_metric_ids`, `linked_*`, `node_id`, `journey_id`, `parent_id`, or `actor_id` must exist in its register.
- A row with `evidence_status = observed` must cite at least one evidence ID whose own status is `observed`.

## Naming

Name journeys with verbs and actor outcomes:

- good: "Become a customer", "Start using the service", "Resolve a billing problem", "Return to work after leave";
- weak: "CRM process", "Onboarding workflow", "Contact center", "HRIS".
