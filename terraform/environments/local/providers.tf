# terraform/environments/local/providers.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24.0"
    }
  }
}

provider "kubernetes" {
  # สำหรับ Mac Studio / Linux โค้ดนี้จะวิ่งไปอ่าน kubeconfig มาตรฐานอัตโนมัติ
  config_path = "~/.kube/config"
}
