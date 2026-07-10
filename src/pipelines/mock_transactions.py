import datetime
import random
import pandas as pd
import boto3
from botocore.client import Config
from prefect import flow, task

# คอนฟิกปลายทาง MinIO (เน็ตเวิร์กภายใน Kubernetes Cluster)
MINIO_ENDPOINT = "http://minio-service:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin@123"
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
            # สร้างคอลัมน์สำหรับทำ Hive Partitioning
            "year": current_date.year,
            "month": f"{current_date.month:02d}",
            "day": f"{current_date.day:02d}"
        })
        
    return pd.DataFrame(data)

@task
def upload_to_minio_parquet(df: pd.DataFrame):
    """Task สำหรับแปลงข้อมูลเป็น Parquet และยิงตรงเข้าโกดัง MinIO ด้วย S3 API"""
    # เชื่อมต่อกับ MinIO client ผ่านโครงข่ายภายใน
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_key_id=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    
    # ดึงค่าวันที่ปัจจุบันจากแถวแรกเพื่อนำมาสร้างพิกัดโฟลเดอร์ปลายทาง
    year = df['year'].iloc[0]
    month = df['month'].iloc[0]
    day = df['day'].iloc[0]
    
    # กำหนดโครงสร้างโฟลเดอร์ปลายทางแบบ Hive-style Partitioning
    s3_key = f"transactions/year={year}/month={month}/day={day}/data.parquet"
    
    # แปลง DataFrame ให้กลายเป็น Parquet ไบนารีในหน่วยความจำ (Buffer)
    parquet_buffer = df.to_parquet(index=False, engine='pyarrow')
    
    # อัปโหลดไฟล์ตรงเข้าโกดัง
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=parquet_buffer
    )
    print(f"Successfully uploaded Parquet data to S3 at: {BUCKET_NAME}/{s3_key}")

@flow(name="E-commerce DataOps Pipeline")
def ecommerce_pipeline():
    """Main Flow สำหรับควบคุมลำดับการทำงานของ DataOps Platform"""
    raw_df = generate_mock_data(num_records=500)
    upload_to_minio_parquet(raw_df)

if __name__ == "__main__":
    ecommerce_pipeline()
