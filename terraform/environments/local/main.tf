# terraform/environments/local/main.tf

module "dataops_namespace" {
  source = "../../modules/k8s_namespace"

  namespace_name = "dataops"
  labels = {
    environment = "local"
    managed-by  = "terraform"
  }
}
