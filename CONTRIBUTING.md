# Contributing

Contributions are welcome when they improve repeatability, evidence quality, interoperability, or practical usability.

## Before opening a PR

1. Explain the problem the change solves.
2. Keep procedures tool-agnostic unless a tool is intrinsically required.
3. Separate original synthesis from external frameworks and cite external influences.
4. Do not include proprietary workshop templates, paid course content, or confidential client artifacts.
5. Keep examples fictional or explicitly licensed.
6. Run:
   ```bash
   python3 scripts/validate_repo.py
   python3 -m unittest discover -s tests
   ```

## Adding a skill

A new skill must:

- solve a distinct recurring workflow;
- have a precise trigger description;
- define inputs, workflow, outputs, and quality gates;
- avoid duplicating another skill;
- use progressive disclosure for long supporting material;
- be added to `skills.json`;
- include at least one example or template when useful;
- reference every file in `references/` and `assets/` from its `SKILL.md`.

## Commit style

Prefer concise conventional prefixes:

- `feat:` new capability
- `fix:` correction
- `docs:` documentation
- `refactor:` structural change
- `test:` validation
