variable "database_name" {
  type        = string
  description = "Glue Catalog Database name"
  default     = "dataops_lakehouse"
}

variable "s3_bucket_id" {
  type        = string
  description = "Target S3 Bucket ID"
}
