.PHONY: install install-dev test test-unit test-regression test-integration test-cov lint

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,notebook]"

test:
	pytest

test-unit:
	pytest tests/unit -m "not integration and not regression"

test-regression:
	pytest tests/regression -m regression

test-integration:
	pytest tests/integration -m integration

test-cov:
	pytest -m "not integration" --cov=fhir_validator_agent --cov-report=term-missing

lint:
	python -m compileall src tests

security:
	bandit -r src/ -ll -q
	pip-audit