resource "aws_glue_catalog_database" "dataops_db" {
  name = var.database_name
}

resource "aws_glue_catalog_table" "xserver_access_logs" {
  name          = "xserver_access_logs"
  database_name = aws_glue_catalog_database.dataops_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification"                 = "parquet"
    "projection.enabled"             = "true"
    "projection.year.type"           = "integer"
    "projection.year.range"          = "2024,2030"
    "projection.month.type"          = "integer"
    "projection.month.range"         = "1,12"
    "projection.month.digits"        = "2"
    "projection.day.type"            = "integer"
    "projection.day.range"           = "1,31"
    "projection.day.digits"          = "2"
    "storage.location.template"      = "s3://${var.s3_bucket_id}/dataops_lakehouse/xserver_access_logs/year=$${year}/month=$${month}/day=$${day}/"
  }

  storage_descriptor {
    location      = "s3://${var.s3_bucket_id}/dataops_lakehouse/xserver_access_logs/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "ParquetHiveSerDe"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "tenant_id"
      type = "string"
    }
    columns {
      name = "user_masked_id"
      type = "string"
    }
    columns {
      name = "timestamp"
      type = "string"
    }
    columns {
      name = "http_method"
      type = "string"
    }
    columns {
      name = "request_path"
      type = "string"
    }
    columns {
      name = "status_code"
      type = "int"
    }
    columns {
      name = "response_bytes"
      type = "bigint"
    }
    columns {
      name = "user_agent"
      type = "string"
    }
  }

  partition_keys {
    name = "year"
    type = "string"
  }
  partition_keys {
    name = "month"
    type = "string"
  }
  partition_keys {
    name = "day"
    type = "string"
  }
}
