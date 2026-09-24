# AGENTS.md

## Repository purpose

This repository is Journey Architecture OS: reusable Agent Skills for evidence-based journey architecture and management. JourneyOps is its operational layer (`journey-governance`, `journey-metrics`, `journey-portfolio-management`, `journey-quality-audit`).

## The contract

`skills/journey-architecture/references/ontology.md` is the single source of truth for entities, ID grammar, enumerations, register columns, and referential rules. Everything else derives from it:

- `references/conventions.md` in each skill is generated from the ontology (`make conventions`); never edit it by hand;
- `schemas/*.schema.json` define required columns and value formats per register;
- `assets/*.csv` register templates contain the header row only, in ontology column order;
- `scripts/validate_repo.py` enforces all of the above, plus ID patterns and referential rules on `examples/`; `tests/` runs it against the fixtures in `tests/fixtures/`.

If a skill, template, example, or doc disagrees with the ontology, fix the skill, not the ontology, unless the ontology itself is wrong; then change the ontology first and propagate.

## Working rules

- Keep each `SKILL.md` under 500 lines; put procedures, method guides, and worked examples in one-level-deep `references/`, templates in `assets/`.
- Keep the skill name identical to its directory; frontmatter requires `name` and `description`, and `skills.json` mirrors the description exactly.
- Reference every `references/` and `assets/` file from the skill's `SKILL.md`; the validator rejects orphans.
- Each skill is installed standalone: it may point to another skill as optional, but must not depend on it for its core procedure.
- Label every material claim `observed`, `inferred`, `hypothesis`, or `unknown`. Never convert stakeholder input into research findings.
- Keep current, target, and transitional journeys as separate IDs linked by `baseline_journey_id`.
- Examples are fictional and must pass the validator; IDs follow the ontology grammar.
- Do not copy proprietary templates or paid course material; attribute influences in `docs/bibliography.md`.

## Evals

`evals/` holds routing cases (does the agent pick the right skill from its description) and behavior cases (does loading the skill improve the output). Write eval prompts and rubrics as a user or reviewer would; never paste skill text, section headings, or distinctive phrasing from a `SKILL.md` into an eval. An eval that quotes the skill measures recall of the text, not the skill's effect.

## Checks

```bash
make validate test evals-check   # before every commit; CI runs validate and test
make conventions                 # after any ontology change
make mutation                    # after changing the validator; local only, about 25 minutes on 4 workers; `--only` targets changed functions
```

## Adding a register column

Change in this order, in one commit:

1. `ontology.md` — Registers table, plus a column clarification if the meaning is not obvious;
2. `make conventions` — regenerate every skill's `references/conventions.md`;
3. `schemas/<register>.schema.json` — type, pattern, or enum; required or not;
4. `assets/<register>.csv` — header only, same order;
5. `tests/fixtures/minimal-system/` — add the column with a valid value;
6. tests — a case that fails on an invalid value; then any SKILL.md output table that lists the register's columns, and affected examples.
