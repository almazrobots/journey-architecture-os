# Validation

`scripts/validate_repo.py` uses only the Python standard library and runs on Python 3.9 or newer. CI runs it and the unit tests on Python 3.9 and 3.12.

```bash
make validate            # python3 scripts/validate_repo.py [--root PATH]
make test                # python3 -m unittest discover -s tests
make conventions         # regenerate every skill's references/conventions.md from the ontology
make mutation            # mutation testing of the validator (local only, about 25 minutes)
make evals-check         # structural check of evals/, no model calls
```

Errors are reported as `path:line: message`.

## What the validator checks

### Skills

- `SKILL.md` frontmatter is parsed strictly: it must be the first block, top-level keys are unique, and `name` and `description` must be single-line plain or simply quoted values, so no YAML parser can read them differently. Only the Agent Skills keys are allowed (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`); `license`, `compatibility` and `allowed-tools` are single-line strings, and `metadata` is a flat map of string keys to string values at one indentation. Names match directories and `skills.json` matches the skills.
- Every file in `references/` and `assets/` is referenced from `SKILL.md`, is a regular file, and cited `references/…` or `assets/…` paths exist.
- Skills are self-contained. In `SKILL.md` and in every text file under `references/` and `assets/`, every Markdown link target and every backticked path (a token with a folder separator ending in a file name or `/`) is checked: URLs, `mailto:` and `#anchor` links are skipped; a target may not be absolute (`/…`), start with `~`, climb out with `..` or contain `\`; it may not point at repository folders (`skills/`, `docs/`, `scripts/`, `schemas/`, `examples/`, `evals/`, `tests/`) or into any skill by name; every other target must resolve to a file inside the skill (relative to the citing file or to the skill root), so `[x](README.md)` fails when the skill has no such file. All text is read as UTF-8; a file in another encoding is one clear error, never a traceback.
- A skill directory may hold only `SKILL.md`, `references/`, `assets/` and `scripts/`; a `scripts/` directory is reported as a notice because installed skills may be executed by agents. Symbolic links are rejected anywhere under `skills/`, `schemas/` and `examples/`.
- Each skill's `references/conventions.md` must equal the contract card that `scripts/sync_conventions.py` generates from the ontology: the ID grammar, the evidence statuses, and only the registers, enumerations and rules the skill produces or consumes. A skill without a mapping in the generator, or an ontology bullet the generator cannot place, is an error.

### Contract

- `schemas/` holds one JSON Schema (draft 2020-12) per register describing one CSV row: `actor`, `journey`, `relation`, `node`, `evidence`, `moment`, `metric`, `metric-edge`, `opportunity`, `initiative`, `portfolio`, `governance`, `change-log`. An empty cell is an absent property, so `required` means "must be filled"; each schema's `description` explains its required columns.
- The schemas use only `type`, `properties`, `required`, `enum`, `pattern` and `additionalProperties` (plus annotations), so any standard validator can use them.
- The ontology's ID regexes, enumerations and register columns must equal the validator's constants and the schemas; ID-column patterns are derived from the ID regexes, and `review_triggers` from the `review_trigger` enumeration.
- Every register template in `skills/*/assets/` carries the exact schema header and nothing else.

### Journey systems

Any directory under `examples/` containing `journey-registry.csv` is a journey system.

- Files: every CSV under `examples/` must be a stand-alone `examples/*.csv` or sit directly in a journey-system directory; a CSV anywhere else is an error, and a directory holding register-named CSVs without `journey-registry.csv` is reported once.
- Rows: registers are read as UTF-8 (a byte-order mark from spreadsheet tools is accepted; any other encoding is one clear error); every row of every register is validated against its schema, with ECMA-262 pattern semantics (`$` means end of input, so `ID\n` fails as it does in standard JSON Schema validators); `evidence_status` and `root_cause_status` are always filled (`unknown` when not assessed), and every schema must require them; a cell holding only whitespace is an error; dates are real calendar dates; IDs, and relation and metric-edge triples, are unique per register; files that are not registers are rejected.
- References: every cited ID exists in its register, including `parent_node_id`, `journey_or_node_id`, `baseline_journey_id`, `moment_ids`, `affected_node_ids`, `from_id`, `to_id`, `from_metric_id` and `to_metric_id`.
- Hierarchy: `journey_id` prefixes follow `level` (L0 `DOM`, L1 `LFC`, L2 `JRN`); a parent sits at a lower level; `LFC` and `JRN` rows name an actor, and their actor code equals the actor's and the parent lifecycle's; a `target` or `transitional` L2 journey names its `current` L2 journey in `baseline_journey_id`, with the same `actor_id`, and no other row fills it.
- Nodes: a node ID starts with `NOD-` plus its journey key; `parent_node_id` is the node ID minus its last segment; a node without a parent is a `stage`, a node with one is not; `sequence` equals the last ID segment.
- Evidence: a row marked `observed` cites at least one `observed` evidence item, and a row marked `inferred` at least one `observed` or `inferred` item (nodes, relations, moments, metrics, metric edges, opportunities; on opportunities also `root_cause_status`, which additionally needs a stated `root_cause`); `stakeholder-input` evidence is `hypothesis` or `unknown`; a node cited together with a journey belongs to it (evidence, opportunities, change-log affected nodes).
- Scope: an opportunity belongs to a `current` journey; its `moment_ids` are moments on that journey's nodes; its `metric_ids`, a moment's `metric_ids`, and an initiative's `expected_metric_ids` are metrics attached to the journey, its nodes, or the lifecycle and domain above it (for an initiative, of any journey of the opportunities it addresses).
- Metrics: a metric attached to a lifecycle or domain has layer `business`; every journey with metrics has exactly one `actor-outcome` metric attached to the journey itself; every other metric of the journey reaches it through `drives` edges, except `business` metrics, which the root must drive, and `guardrail` metrics, which must `protect` a metric; `drives` edges form no cycle; edges never point to themselves.
- Portfolio: rows agree with the journey registry on parent, level, actor, state and status; `linked_opportunities` belong to the entry's journeys (for lifecycles and domains, the journeys below them; for target and transitional journeys, also the baseline journey), and `linked_initiatives` address one of those opportunities; `metric_coverage` is filled on `JRN` rows only (in systems and in stand-alone portfolio files); a journey's value equals the share of its stage-level nodes with a metric on the stage or below it, and is empty when the journey has no stages.
- Governance: `next_review_due` is on or after `last_reviewed_at`; `review_interval_days` is a positive integer; `review_triggers` uses the enumeration.
- Views: every ID in the system's Markdown and YAML files resolves to a register row.

### Other examples and ID namespaces

- A stand-alone `examples/*.csv` is validated against the register whose header it carries, with parents resolved inside the file. IDs in `examples/*.md` must match the ID grammar.
- IDs in `skills/*/references/*.md` and stand-alone `examples/*.md` must not reuse an ID defined by an example journey system, so a guide's illustration can never be mistaken for the worked example.

## Tests and mutation testing

`tests/test_validator.py` copies `tests/fixtures/minimal-system/` (a small valid system with all thirteen registers and a view) into a temporary repository and proves each rule fires, one test per rule, plus the boundaries that keep each rule from firing too early.

`scripts/mutation_test.py` mutates the validator one site at a time and runs `tests/test_repository.py` and `tests/test_validator.py` against each mutant. Operators: comparison flips (`==`/`!=`, `<`/`<=`, `>`/`>=`, `in`/`not in`, `is`/`is not`), `and`/`or` swaps, `not` removal, `return 0`/`1` swaps, boolean flips, integer constants `n → n + 1`, string literals emptied (docstrings and f-string parts excluded), regex anchors `^`/`$` dropped, call statements (such as `report.error(...)` or `append(...)`) deleted, and collection literals emptied. It fails below `--threshold` (default 90) and writes [`docs/quality/mutation-report.md`](quality/mutation-report.md) with the score, per-operator counts, and every surviving mutant with the reason it is equivalent. It is not run in CI. Latest results: full run over 1808 mutants, 1797 killed; the one non-equivalent survivor was then killed by a corrected test (verified with `--only`), leaving 1798 of 1808 killed (99.4%) with 10 equivalent survivors. Details in the report.
