# Changelog

## 2.0.0 — 2026-09-24

A contract, a worked system, methods for every skill, and evidence that the skills work. Major version because the data contract changed in ways that break 1.0.0 artifacts.

### Breaking changes and migration from 1.0.0
- **ID grammar is stricter.** Slug tokens must start with a letter (`JRN-CUST-ONBOARD-001`, not `JRN-CUST-100-001`); nodes use `NOD-{journey key}-{NN}`; `STG-` IDs no longer exist. Rename affected IDs once and record the mapping in the change log.
- **Registers replace free-form files.** `journey-governance/assets/governance-record.yaml` is removed; use `governance-register.csv` and `change-log.csv`. The metric tree's causal links move into `metric-edge-register.csv`.
- **Opportunity columns changed.** `problem_or_root_cause` is split into `problem`, `root_cause`, and `root_cause_status`; `moment_ids` and `metric_ids` are added.
- **Status columns are required.** Every `evidence_status` (and `root_cause_status`) must be filled; use `unknown` when not assessed. `inferred` rows must cite evidence.
- **Metric row status changed meaning.** It now states the measure's validity; causal status lives on metric edges.
- **Templates are header-only.** Copy a template, then add rows.
- **Removed example.** `examples/customer-saas-onboarding.md` is superseded by `examples/saas-onboarding/`.

Run `make validate` on your journey systems after migrating; errors point to `file:line`.

### Contract and data model
- One canonical ontology (`journey-architecture/references/ontology.md`): ID grammar for actors, domains, lifecycles, journeys, nodes, evidence, moments, metrics, opportunities, initiatives, and changes; enumerations; referential rules.
- 13 CSV registers with header-only templates: actors, journeys, relations, nodes, evidence, moments, metrics, metric edges, opportunities, initiatives, portfolio, governance, change log. JSON Schema (draft 2020-12) for one row of each in `schemas/`.
- Journey versions linked by `baseline_journey_id`; stages are L3, episodes and interactions L4.
- Metric trees stored as data: metric rows carry measure validity; causal `drives` and `protects` edges carry their own evidence status; one actor-outcome root per journey.
- Opportunities separate `problem` from `root_cause` (each with its own status) and link the moments and metrics they serve.
- `inferred` claims must cite evidence; `observed` claims must cite observed evidence; stakeholder input never rises above `hypothesis`.
- Every skill carries a generated `references/conventions.md`, so each installs and works standalone.

### Methods
- Fourteen new method guides: synthesis to stages (codebook thematic analysis), research ethics, employee-research ethics, root-cause analysis (fault trees and cause tests), metric-tree method (including reading signal from noise), moment analysis, prioritization, jobs and outcomes (Christensen, Ulwick, Klement), portfolio health, experiment design (sample size, clustering, rare-event guardrails, stop rules), target-state design, audit rubric (anchored 0–3), governance method (freshness, status transitions, change control), and facilitation method. Employee lenses consolidated into one canonical table.
- CJM and EJM include their own stage-derivation procedure; audit findings name the exact repair skill.
- Bibliography extended with verified primary sources.

### Worked example
- `examples/saas-onboarding/`: a complete fictional journey system (Ledgerly) from 20 evidence items to funded initiatives, with a statistics appendix and a candid self-audit. Every link in its trace diagram is a register column.
- Smaller examples moved to their own ID namespaces.

### Tooling and quality
- Validator rewritten: strict frontmatter parsing, no references outside a skill, symlink rejection, schema validation of every register row, all ontology rules, conventions drift check, `path:line` errors. Runs on Python 3.9–3.14; CI matrix 3.9 and 3.12.
- Installer refuses skills containing symlinks and symlinked destinations.
- Mutation testing of the validator (`make mutation`); report in `docs/quality/mutation-report.md`.
- Evaluations (`evals/`, `scripts/run_evals.py`): routing against 14 overlapping distractor skills with held-out cases, and behavior scenarios with subtle traps, run with and without the skill and graded by a judge that does not see which condition produced the answer. Results are refused from an uncommitted tree.
- `service-blueprinting` description sharpened after routing evals showed requests phrased as "process map" going to a generic process-mapping skill.

### Known issues
- Behavior evals do not yet show a statistically clear gain on method traps (+5.6 pp, 95% CI −2.2 to +15.6); the gain on conventions is clear. See `evals/results/`.
- With `journey-quality-audit` loaded, the model missed NPS used as a stage metric in 2 of 3 runs (scenario BH-08).

## 1.0.0 — 2026-09-24

- Initial public release of Journey Architecture OS.
- 15 Agent Skills covering journey architecture, research, CJM, EJM, jobs/outcomes, service blueprints, moments that matter, metrics, opportunities, target experience, governance, portfolio management, facilitation, and quality audit.
- JourneyOps defined as the operational layer (governance, metrics, portfolio management, quality audit).
- Methodology, data model, glossary, adoption guide, anti-patterns, and bibliography.
- Fictional CJM, EJM, and portfolio examples; reusable templates for every artifact.
- `install_skills.py`, `validate_repo.py` (frontmatter, registry, and reference integrity), tests, and CI.
