output "database_name" {
  value = aws_glue_catalog_database.dataops_db.name
}

output "access_logs_table_name" {
  value = aws_glue_catalog_table.xserver_access_logs.name
}
