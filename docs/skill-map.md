# Skill routing map

## If the user asks...

| Request | Primary skill | Often pair with |
|---|---|---|
| Broad / ambiguous experience problem | `experience-architecture` | Routes to the minimum required skill set |
| "What journeys do we even have?" | `journey-architecture` | `journey-portfolio-management` |
| "Research this journey" | `journey-research` | `jobs-and-outcomes` |
| "Build a CJM" | `customer-journey-mapping` | `journey-research`, `moments-that-matter` |
| "Build an employee journey" | `employee-journey-mapping` | `service-blueprinting`, `journey-metrics` |
| "What is the customer really trying to achieve?" | `jobs-and-outcomes` | `journey-research` |
| "Show how the service actually works" | `service-blueprinting` | `customer-journey-mapping` or `employee-journey-mapping` |
| "Which moments matter most?" | `moments-that-matter` | `journey-research`, `journey-metrics` |
| "How should we measure it?" | `journey-metrics` | `journey-governance` |
| "What should we fix first?" | `experience-opportunity-prioritization` | `journey-metrics` |
| "Design the future journey" | `target-experience-design` | `experience-opportunity-prioritization` |
| "Make journeys operational" | `journey-governance` | `journey-portfolio-management` |
| "Manage dozens of journey maps" | `journey-portfolio-management` | `journey-governance` |
| "Run a workshop" | `journey-workshop-facilitation` | task-specific skill |
| "Review whether this map is actually good" | `journey-quality-audit` | whichever skill created the artifact |

## Shared contract

Every skill reads and writes the same registers, defined in `skills/journey-architecture/references/ontology.md` and shipped with each skill as `references/conventions.md`. Output from one skill is input to the next without translation:

| Skill | Writes | Reads |
|---|---|---|
| `journey-architecture` | actors, journeys, relations, nodes | — |
| `journey-research` | evidence | journeys, nodes |
| `customer-journey-mapping`, `employee-journey-mapping` | nodes (stages) | evidence |
| `service-blueprinting` | node-level blueprint views, root-cause candidates | nodes, evidence |
| `moments-that-matter` | moments | nodes, evidence, metrics |
| `journey-metrics` | metrics, metric edges | nodes, evidence |
| `experience-opportunity-prioritization` | opportunities | evidence, moments, metrics |
| `target-experience-design` | initiatives, target and transitional journeys | opportunities, metrics |
| `journey-governance` | governance, change log | journeys, metrics |
| `journey-portfolio-management` | portfolio | all of the above |
| `journey-quality-audit` | audit findings | any artifact |

## Orchestration rule

Prefer the smallest set of skills that covers the decision.

Do not automatically run every skill. A tactical support-flow redesign may need only:

`journey-research → customer-journey-mapping → service-blueprinting → experience-opportunity-prioritization`

An enterprise transformation may need the full chain.
