.PHONY: setup generate run incremental kpis models diagnose lineage validate test coverage lint format-check smoke dashboard docker-dashboard docker-pipeline

setup:
	python3 -m pip install -e ".[dev]"

generate:
	retail-kpi generate-data

run:
	retail-kpi run-pipeline --mode full

incremental:
	retail-kpi run-pipeline --mode incremental

kpis:
	retail-kpi run-kpis

models:
	retail-kpi run-models

diagnose:
	retail-kpi diagnose-quality

lineage:
	retail-kpi export-lineage

validate:
	retail-kpi validate-contracts

test:
	pytest

coverage:
	pytest --cov=src/pipeline --cov-report=term-missing

lint:
	ruff check .

format-check:
	ruff format --check .

smoke:
	retail-kpi generate-data
	retail-kpi run-pipeline --mode full
	retail-kpi run-pipeline --mode incremental
	retail-kpi run-kpis
	retail-kpi run-models
	retail-kpi diagnose-quality
	retail-kpi export-lineage
	retail-kpi validate-contracts

dashboard:
	streamlit run app/streamlit_dashboard.py

docker-dashboard:
	docker compose up dashboard

docker-pipeline:
	docker compose run --rm pipeline retail-kpi run-pipeline --mode full
