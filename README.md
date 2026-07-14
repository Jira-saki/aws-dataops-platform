# Hybrid DataOps Platform — Local-first, Cloud-ready

A production-grade, local-first DataOps platform designed to emulate enterprise cloud architecture for infrastructure automation, data lifecycle management, and cloud-agnostic deployment. It runs on a local Kubernetes cluster (e.g., OrbStack or Hobgoblin), managed with Terraform, uses a self-hosted Prefect orchestration layer, and an S3-compatible data lake (Floci). The environment is fully portable and can be migrated to AWS without changes to core code.

**Why this repo matters for hiring decisions**
- **Proves infrastructure and data engineering skills:** Terraform modules, Kubernetes manifests, and RBAC demonstrate production-oriented infrastructure design.
- **Demonstrates data pipeline best practices:** End-to-end Python pipelines producing Parquet with Hive-style partitioning and efficient storage formats.
- **Cloud parity & portability:** Local emulation of S3 and Prefect shows the candidate can design systems that run locally and scale to AWS.

---

## Key components
- **Infrastructure as Code:** Modular Terraform for environment-specific configs and reusable modules.
- **Storage (Local Data Lake):** Floci provides an S3-compatible endpoint (default port 4566) for local testing.
- **Orchestration:** Prefect self-hosted server (control plane) and Prefect Kubernetes workers (execution plane) with strict RBAC.
- **Pipelines:** Python-based ETL that writes compressed columnar Parquet files with Hive-style partitioning for efficient queries.

## Project structure

```
.
├── k8s/
│   ├── base/
│   │   └── floci.yaml
│   └── prefect/
│       ├── rbac.yaml
│       ├── server.yaml
│       └── worker-deployment.yaml
├── src/
│   ├── pipelines/
│   │   └── mock_transactions.py
│   └── utils/
└── terraform/
    ├── environments/
    │   ├── local/
    │   │   ├── main.tf
    │   │   ├── providers.tf
    │   │   └── outputs.tf
    │   └── aws/
    └── modules/
        └── k8s_namespace/
```

## Quickstart (developer local environment)

Prerequisites:
- Local Kubernetes (OrbStack or Hobgoblin)
- Terraform >= 1.5.0
- kubectl, Python 3.8+, pip, and Prefect CLI

Bootstrap infra (local):

```bash
cd terraform/environments/local/
terraform init
terraform apply -auto-approve
```

Deploy Floci (local S3 emulator):

```bash
kubectl apply -f k8s/base/floci.yaml
kubectl get pvc,pods -n dataops -w
kubectl port-forward svc/floci 4566:4566 -n dataops --address 0.0.0.0
```

Deploy Prefect (self-hosted):

```bash
kubectl apply -f k8s/prefect/server.yaml
kubectl apply -f k8s/prefect/rbac.yaml
kubectl apply -f k8s/prefect/worker-deployment.yaml
```

Run pipeline locally (hybrid mode):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
AWS_S3_ENDPOINT="http://localhost:4566" python3 src/pipelines/mock_transactions.py
```

If using Prefect UI, point the CLI to the control plane URL, e.g.:

```bash
prefect config set PREFECT_API_URL="http://<control-plane-host>:4200/api"
```

## Data architecture highlights
- Uses PyArrow to write compressed, columnar Parquet files.
- Organizes data with Hive-style partitions (year/month/day) for partition pruning and efficient queries.

Example layout on S3:

```
dataops-lake/
└── transactions/
    └── year=2026/
        └── month=07/
            └── day=14/
                └── data.parquet
```

## Migration to AWS (summary)
- Switch `AWS_S3_ENDPOINT` to the production S3 endpoint or use real S3 buckets.
- Replace local Prefect workers with EKS/ECS-based workers and scale compute accordingly.
- Move from static/local credentials to IAM Roles for Service Accounts (IRSA) for production security.

---
