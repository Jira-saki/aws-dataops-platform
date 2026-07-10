# terraform/environments/local/outputs.tf

output "dataops_namespace" {
  value       = module.dataops_namespace.namespace_name
  description = "Namespace created for DataOps platform"
}
