variable "bucket_prefix" {
  type        = string
  description = "Prefix for the S3 bucket name"
  default     = "dataops-lakehouse"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "production"
}
