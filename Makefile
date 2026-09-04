PYTHON ?= python

.PHONY: install lint test fixtures benchmark verify

install:
	$(PYTHON) -m pip install -e '.[dev]'

lint:
	ruff check .
	ruff format --check .

test:
	pytest --cov=multimodal_receipt --cov-report=term-missing --cov-fail-under=85 -q

fixtures:
	$(PYTHON) scripts/generate_fixtures.py

benchmark:
	multimodal-receipt benchmark --report evidence/benchmark-report.json

verify: lint test benchmark
