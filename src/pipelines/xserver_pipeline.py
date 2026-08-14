import glob
import gzip
import os
import dlt
from src.utils.hasher import hash_ip
from src.utils.parser import parse_access_line, parse_audit_line

TENANT_CACHE = {}

def get_tenant_id(raw_domain: str) -> str:
    clean_domain = raw_domain.lower().replace("www.", "")
    if clean_domain not in TENANT_CACHE:
        tenant_number = len(TENANT_CACHE) + 1
        TENANT_CACHE[clean_domain] = f"tenant_{tenant_number:02d}"
    return TENANT_CACHE[clean_domain]

@dlt.source(name="xserver_data_source")
def xserver_source(log_dir: str = "data/sample"):
    access_files = glob.glob(os.path.join(log_dir, "*access_log*"))
    audit_files = glob.glob(os.path.join(log_dir, "*audit*.txt")) + glob.glob(os.path.join(log_dir, "*report*.txt"))

    # 1. Clean Access Logs Resource
    @dlt.resource(name="xserver_access_logs", write_disposition="replace")
    def access_logs_resource():
        for file_path in access_files:
            open_fn = gzip.open if file_path.endswith(".gz") else open
            with open_fn(file_path, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parsed = parse_access_line(line)
                    if parsed:
                        tenant_id = get_tenant_id(parsed["raw_domain"])
                        yield {
                            "tenant_id": tenant_id,
                            "user_masked_id": hash_ip(parsed["raw_ip"]),
                            "timestamp": parsed["timestamp"],
                            "year": parsed["year"],
                            "month": parsed["month"],
                            "day": parsed["day"],
                            "http_method": parsed["http_method"],
                            "request_path": parsed["request_path"],
                            "status_code": parsed["status_code"],
                            "response_bytes": parsed["response_bytes"],
                            "user_agent": parsed["user_agent"],
                        }

    # 2. Audit Logs Resource
    @dlt.resource(name="xserver_audit_logs", write_disposition="replace")
    def audit_logs_resource():
        for file_path in audit_files:
            filename = os.path.basename(file_path)
            open_fn = gzip.open if file_path.endswith(".gz") else open
            with open_fn(file_path, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parsed = parse_audit_line(line, filename)
                    if parsed:
                        yield parsed

    # 3. Dead Letter Queue Resource (DLQ)
    @dlt.resource(name="dead_letter_queue", write_disposition="append")
    def dlq_resource():
        for file_path in access_files:
            filename = os.path.basename(file_path)
            open_fn = gzip.open if file_path.endswith(".gz") else open
            with open_fn(file_path, "rt", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, start=1):
                    line_clean = line.strip()
                    if line_clean and not parse_access_line(line):
                        yield {
                            "source_file": filename,
                            "line_number": line_no,
                            "raw_corrupted_payload": line_clean,
                            "error_reason": "ACCESS_LOG_REGEX_MISMATCH",
                        }

    return access_logs_resource(), audit_logs_resource(), dlq_resource()

def run_parquet_pipeline(output_dir: str = "data/lakehouse"):
    """รัน pipeline ส่งออกเป็น Parquet Format ลง Filesystem/S3"""
    abs_output_dir = os.path.abspath(output_dir)
    
    pipeline = dlt.pipeline(
        pipeline_name="aws_dataops_parquet_pipeline",
        destination=dlt.destinations.filesystem(
            bucket_url=abs_output_dir,
            layout="{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"
        ),
        dataset_name="dataops_lakehouse",
    )
    
    print(f"🚀 Running Pipeline -> Exporting Parquet to: {abs_output_dir}")
    load_info = pipeline.run(xserver_source(), loader_file_format="parquet")
    print(load_info)

if __name__ == "__main__":
    run_parquet_pipeline()
