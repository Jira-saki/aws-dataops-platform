output "s3_bucket_name" {
  description = "S3 Data Lake Bucket Name"
  value       = module.s3_lakehouse.bucket_id
}

output "glue_database" {
  description = "Glue Catalog Database Name"
  value       = module.glue_catalog.database_name
}
