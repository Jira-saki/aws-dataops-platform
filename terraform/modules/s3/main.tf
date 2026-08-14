resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.bucket_prefix}-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = false

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "EP3-DataOps-Platform"
  }
}

resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_crypto" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake_block_public" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
