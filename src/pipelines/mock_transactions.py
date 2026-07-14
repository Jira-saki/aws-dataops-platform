import datetime
import os
import random
import pandas as pd
import boto3
from botocore.client import Config
from prefect import flow, task

# สลับ Endpoint อัตโนมัติ: 
# - ถ้ารันใน K8s (ผ่าน Worker) จะใช้: http://floci:4566
# - ถ้ารันโลคัลบน Hobgoblin Host จะใช้: http://localhost:4566 (ผ่าน port-forward)
S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "http://floci:4566")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "mock_key")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret")
BUCKET_NAME = "dataops-lake"

@task(retries=3, retry_delay_seconds=10)
def generate_mock_data(num_records: int = 1000) -> pd.DataFrame:
    """Task E-commerce Transactions"""
    products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Smartwatch"]
    categories = ["Electronics", "Accessories", "Accessories", "Electronics", "Audio", "Electronics"]
    
    current_date = datetime.date.today()
    
    data = []
    for i in range(num_records):
        prod_idx = random.randint(0, len(products) - 1)
        data.append({
            "transaction_id": f"TXN-{current_date.strftime('%Y%m%d')}-{i:04d}",
            "product_name": products[prod_idx],
            "category": categories[prod_idx],
            "amount": round(random.uniform(10.0, 1500.0), 2),
            "quantity": random.randint(1, 5),
            "year": current_date.year,
            "month": f"{current_date.month:02d}",
            "day": f"{current_date.day:02d}"
        })
        
    return pd.DataFrame(data)

@task
def upload_to_s3_parquet(df: pd.DataFrame):
    """Task สำหรับแปลงข้อมูลเป็น Parquet และอัปโหลดเข้า Floci (S3 API)"""
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    
    # ตรวจสอบและสร้าง Bucket ปลายทางบน Floci (S3) หากยังไม่มี
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except Exception:
        print(f"Bucket '{BUCKET_NAME}' not found. Creating it in Floci...")
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    
    year = df['year'].iloc[0]
    month = df['month'].iloc[0]
    day = df['day'].iloc[0]
    
    s3_key = f"transactions/year={year}/month={month}/day={day}/data.parquet"
    
    # แปลง DataFrame เป็น Parquet binary ใน memory buffer
    parquet_buffer = df.to_parquet(index=False, engine='pyarrow')
    
    # อัปโหลดเข้า S3 (Floci)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=parquet_buffer
    )
    print(f"Successfully uploaded Parquet data to Floci (S3) at: {BUCKET_NAME}/{s3_key}")

@flow(name="E-commerce DataOps Pipeline")
def ecommerce_pipeline():
    """Main Flow สำหรับควบคุมลำดับการทำงานของ DataOps Platform"""
    raw_df = generate_mock_data(num_records=500)
    upload_to_s3_parquet(raw_df)

if __name__ == "__main__":
    ecommerce_pipeline()