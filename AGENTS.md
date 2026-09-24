# AGENTS.md

## Repository purpose

This repository is Journey Architecture OS: reusable Agent Skills for evidence-based journey architecture and management. JourneyOps is its operational layer (`journey-governance`, `journey-metrics`, `journey-portfolio-management`, `journey-quality-audit`).

## Working rules

- Keep each `SKILL.md` under 500 lines.
- Keep the skill name identical to its parent directory.
- Frontmatter requires `name` and `description`.
- Put detailed procedures, schemas, and examples in one-level-deep `references/`.
- Put reusable templates in one-level-deep `assets/`.
- Reference every `references/` and `assets/` file from the skill's `SKILL.md`; the validator rejects orphans.
- Do not copy proprietary templates or paid course materials.
- Attribute intellectual influences in `docs/bibliography.md`.
- Prefer clear procedural instructions over essays.
- Preserve evidence status: observed, inferred, hypothesis, unknown.
- Never silently convert stakeholder assumptions into research findings.
- Keep current-state and target-state models distinguishable.
- Update `skills.json` when adding, renaming, or removing a skill.
- Run `make validate test` before committing.
