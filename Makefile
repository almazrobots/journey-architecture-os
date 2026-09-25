.PHONY: validate test mutation conventions evals-check render

validate:
	python3 scripts/validate_repo.py

test:
	python3 -m unittest discover -s tests

# Regenerate every skill's references/conventions.md from the ontology.
conventions:
	python3 scripts/sync_conventions.py

# Local only (several minutes), not run in CI. Writes the committed report.
mutation:
	python3 scripts/mutation_test.py --report docs/quality/mutation-report.md

evals-check:
	python3 scripts/run_evals.py --check

# Render the flagship example as one self-contained HTML map into build/ (gitignored).
render:
	python3 scripts/render_map.py examples/saas-onboarding -o build/saas-onboarding-map.html
