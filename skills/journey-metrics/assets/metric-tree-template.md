# Journey Metric Tree

- Journey ID:
- Desired actor outcome:
- Owner:
- Version:

## Metrics

One row per metric; rows map one-to-one to `metric-register.csv`.

| metric_id | journey_or_node_id | layer | name | definition | unit | source | population | cadence | owner | direction | baseline | target | evidence_ids | evidence_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | actor-outcome | | | | | | | | | | | | |
| | | behavior | | | | | | | | | | | | |
| | | operational | | | | | | | | | | | | |
| | | guardrail | | | | | | | | | | | | |

One `actor-outcome` root attached to the journey; 15 metrics or fewer. `evidence_status` qualifies measure validity (does the metric measure what its name claims, for its population?): `observed` · `inferred` · `hypothesis` · `unknown`. A missing baseline goes in `baseline` ("not yet measured"), not in `evidence_status`.

## Metric edges

One row per causal claim; rows map one-to-one to `metric-edge-register.csv`.

| from_metric_id | relation | to_metric_id | evidence_ids | evidence_status | note |
|---|---|---|---|---|---|
| | drives | | | | |
| | protects | | | | |

`drives`: moving the first metric is expected to move the second. `protects`: a guardrail that must not degrade while the second is optimized. `evidence_status` here qualifies the causal claim; correlation alone supports `inferred` at most.

## Causal narrative
One sentence per `drives` edge (operational driver → behavior → actor outcome → business outcome), citing evidence IDs.

## Experience signals

## Employee/service signals

## Guardrails and trade-offs

## Instrumentation gaps
