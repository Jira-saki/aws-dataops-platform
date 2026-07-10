# terraform/modules/k8s_namespace/variables.tf
variable "namespace_name" {
  type        = string
  description = "Name of the Kubernetes namespace"
}

variable "labels" {
  type        = map(string)
  description = "Labels to apply to the namespace"
  default     = {}
}
