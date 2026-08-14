.PHONY: help install test run-duckdb run-parquet tf-init tf-validate clean

help:
	@echo "DataSecOps Platform - CLI Operations"
	@echo "  make test          - Run Pytest unit tests"
	@echo "  make run-duckdb    - Run pipeline and load into local DuckDB"
	@echo "  make run-parquet   - Run pipeline and export Hive Parquet lakehouse"
	@echo "  make tf-validate   - Initialize and validate Terraform configurations"
	@echo "  make clean         - Remove cache, pipeline run state, and temporary files"

test:
	pytest -v tests/

run-duckdb:
	python -c 'from src.pipelines.xserver_pipeline import xserver_source; import dlt; p = dlt.pipeline(pipeline_name="aws_dataops_xserver_pipeline", destination="duckdb", dataset_name="dataops_lakehouse"); print(p.run(xserver_source(log_dir="data/sample")))'

run-parquet:
	python -m src.pipelines.xserver_pipeline

tf-validate:
	cd terraform/environments/aws && terraform init -backend=false && terraform validate

clean:
	rm -rf .pytest_cache .dlt/pipelines *.duckdb
	find . -type d -name "__pycache__" -exec rm -rf {} +
