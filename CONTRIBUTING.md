# Contributing

Contributions are welcome when they improve repeatability, evidence quality, interoperability, or practical usability.

## The contract comes first

`skills/journey-architecture/references/ontology.md` defines every entity, ID pattern, enumeration, register column, and referential rule. Skills, templates, schemas, examples, and the validator follow it. A change that needs a new field or value starts as a change to the ontology, not as a local variant in one skill.

Each skill ships a generated `references/conventions.md` (IDs, evidence statuses, register columns) so it works when installed alone. Do not edit those files by hand; run `make conventions`.

## Before opening a PR

1. Explain the problem the change solves and which skills it affects.
2. Keep procedures tool-agnostic unless a tool is intrinsically required.
3. Separate original synthesis from external frameworks and cite external influences in `docs/bibliography.md`.
4. Do not include proprietary workshop templates, paid course content, or confidential client artifacts.
5. Keep examples fictional or explicitly licensed; they must pass the validator.
6. Run:
   ```bash
   make validate test evals-check
   ```
   After changing the validator, also run `make mutation` (local only, about 25 minutes on 4 workers; `--only` targets changed functions) and report the mutation score.

## Adding a register column

Change in this order, in one PR:

1. `skills/journey-architecture/references/ontology.md` — Registers table and, if needed, a column clarification;
2. `make conventions` — regenerates `references/conventions.md` in every skill;
3. `schemas/<register>.schema.json`;
4. the header-only template in the owning skill's `assets/`;
5. `tests/fixtures/minimal-system/` — a valid value in the new column;
6. tests — at least one case that fails on an invalid value; then the output tables in `SKILL.md` files and examples that list the register's columns.

## Adding a skill

A new skill must:

- solve a distinct recurring workflow;
- have a precise trigger description, mirrored exactly in `skills.json`;
- define inputs, workflow, outputs, and quality gates;
- work standalone: other skills may be pointed to as optional, not required;
- avoid duplicating another skill;
- use progressive disclosure: long material goes to `references/`;
- reference every file in `references/` and `assets/` from its `SKILL.md`;
- come with routing eval cases, and a behavior case if it changes output quality.

## Evals

Write eval prompts and rubrics in the words a user or reviewer would use. Never paste skill text, headings, or distinctive phrases from a `SKILL.md` into `evals/`: that measures whether the agent can echo the skill, not whether the skill helps.

## Commit style

Prefer concise conventional prefixes:

- `feat:` new capability
- `fix:` correction
- `docs:` documentation
- `refactor:` structural change
- `test:` validation
