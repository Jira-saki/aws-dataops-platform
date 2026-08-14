module "s3_lakehouse" {
  source        = "../../modules/s3"
  bucket_prefix = "dataops-lake"
  environment   = var.environment
}

module "glue_catalog" {
  source        = "../../modules/glue_catalog"
  database_name = "dataops_lakehouse_${var.environment}"
  s3_bucket_id  = module.s3_lakehouse.bucket_id
}
