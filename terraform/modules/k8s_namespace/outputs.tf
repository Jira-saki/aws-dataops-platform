# terraform/modules/k8s_namespace/outputs.tf
output "namespace_name" {
  value       = kubernetes_namespace.this.metadata[0].name
  description = "The actual name of the created namespace"
}
