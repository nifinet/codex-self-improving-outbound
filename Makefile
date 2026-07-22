.PHONY: help setup gate propose dry test tune clean reset

help:
	@echo "make setup    create .venv and install requirements"
	@echo "make gate     run the eval gate"
	@echo "make propose  propose one improvement (writes config)"
	@echo "make dry      propose one improvement (writes nothing)"
	@echo "make test     run the test suite"
	@echo "make tune     the full weekly run, opens a PR"
	@echo "make reset    restore config/scoring.yaml to its shipped state"
	@echo "make clean    remove caches and generated outputs"

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	@echo "now run: source .venv/bin/activate"

gate:
	python3 evals/score.py

propose:
	python3 scripts/propose_improvement.py

dry:
	python3 scripts/propose_improvement.py --dry-run

test:
	python3 -m tests.test_repo

tune:
	./scripts/weekly_tune.sh

# Put the known miss back so you can watch the loop fix it again.
reset:
	git checkout -- config/scoring.yaml
	@python3 evals/score.py || true

clean:
	rm -rf **/__pycache__ .pytest_cache outputs/proposal.json outputs/pr-summary.md
	@echo "cleaned"
