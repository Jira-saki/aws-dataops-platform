import dlt
from prefect import flow, task
from typing import Iterator, Dict, Any
import datetime
import random

@dlt.resource(name="transactions", write_disposition="append")
def generate_transactions() -> Iterator[list[Dict[str, Any]]]:
    """สร้าง Mock Transactions"""
    batch = []
    for _ in range(100):
        batch.append({
            "transaction_id": f"tx_{random.randint(10000, 99999)}",
            "customer_id": f"cust_{random.randint(100, 999)}",
            "amount": round(random.uniform(10.0, 500.0), 2),
            "currency": "USD",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    yield batch

@task(name="ingest_to_s3_floci")
def run_dlt_ingestion():
    pipeline = dlt.pipeline(
        pipeline_name="mock_transactions_ingest",
        destination="filesystem",
        dataset_name="transactions"
    )
    load_info = pipeline.run(generate_transactions(), loader_file_format="parquet")
    print(load_info)

@flow(name="mock_transactions_pipeline")
def main_flow():
    run_dlt_ingestion()

if __name__ == "__main__":
    main_flow()