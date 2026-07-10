# Hybrid DataOps Platform (Cloud-Ready Infrastructure)

A production-grade, local-first DataOps platform designed to demonstrate enterprise-level infrastructure automation, data lifecycle management, and a cloud-agnostic architecture. Built on a local Kubernetes cluster (OrbStack/Hobgoblin) using Terraform, this platform runs a self-hosted orchestration engine and an S3-compatible data lake, executing optimized data pipelines that are ready for seamless migration to AWS.

## Architecture Overview

The platform isolates components into distinct operational planes within a dedicated `dataops` Kubernetes namespace, ensuring low overhead and high portability.

* **Infrastructure as Code (IaC):** Modularized Terraform architecture separating environment-specific configurations from reusable resource modules.
* **Storage Plane (Local Data Lake):** MinIO deployed as a `StatefulSet` with dynamic `PersistentVolumeClaim` (PVC) binding, exposing a local S3-compatible API.
* **Orchestration & Compute Plane:** Self-hosted Prefect Server (Control Plane) decoupled from an independent Prefect Kubernetes Worker (Execution Plane) running with dedicated RBAC permissions to dynamically spawn ephemeral data processing pods.
* **Data Pipeline & Lifecycle:** A Python-based processing pipeline converting unstructured mock transaction streams into highly compressed columnar **Parquet** formats, enforced with **Hive-style partitioning** for cost and query optimization.

---

## Project Structure

```text
.
├── k8s/
│   ├── base/
│   │   └── minio/
│   │       ├── pvc.yaml          # Local storage persistence provisioning
│   │       ├── service.yaml      # Internal ClusterIP routing for API/Console
│   │       └── statefulset.yaml  # Stateful storage workloads with dedicated volume mounts
│   └── prefect/
│       ├── rbac.yaml             # ServiceAccount, Role, and Binding for Pod lifecycle control
│       ├── server.yaml           # Self-hosted Prefect open-source Control Plane
│       └── worker-deployment.yaml # Custom Kubernetes worker with dynamic dependencies installation
├── src/
│   ├── pipelines/
│   │   └── mock_transactions.py  # End-to-end Python ELT Pipeline (Pandas/PyArrow/Boto3)
│   └── utils/                    # Shared data engineering utilities
└── terraform/
    ├── environments/
    │   ├── local/                # Bootstrapping environment for Hobgoblin/OrbStack
    │   │   ├── main.tf           # Root module invocation
    │   │   ├── providers.tf      # Kubernetes provider scoping
    │   │   └── outputs.tf
    │   └── aws/                  # Production Target Migration environment (S3, EKS, IAM)
    └── modules/
        └── k8s_namespace/        # Reusable component for namespace isolation and tagging

```

## Prerequisites

* **Kubernetes Cluster:** OrbStack (macOS) or Hobgoblin Lab (ThinkPad L15 with a local K8s engine).
* **Terraform:** `>= 1.5.0`
* **Command Line Tools:** `kubectl`, `nvim`

---

## Deployment Blueprint

### Phase 1: Infrastructure Bootstrapping (IaC)
Initialize and apply the Terraform configuration to provision the isolated namespace environment.

```bash
cd terraform/environments/local/
terraform init
terraform plan
terraform apply -auto-approve
```
## Phase 2: Deploying the Storage Plane (MinIO)
Deploy the local data lake. The storage controller leverages the cluster's default storage class to dynamically bind a 5Gi persistent volume.

```bash
kubectl apply -f k8s/base/minio/
```

Verify storage binding and pod lifecycle:

```bash
kubectl get pvc,pods -n dataops
```
## Phase 3: Launching Orchestration (Prefect Self-Hosted)
Deploy the central coordination system and the execution workers. The deployment utilizes a shell abstraction wrapper to dynamically inject container dependencies (prefect-kubernetes) upon initialization.

```bash
kubectl apply -f k8s/prefect/server.yaml
kubectl apply -f k8s/prefect/rbac.yaml
kubectl apply -f k8s/prefect/worker-deployment.yaml
```

## Data Architecture & Storage Strategy
The data pipeline utilizes PyArrow to enforce strong type casting and highly compressed data serialization. To mimic cloud cost optimization best practices (AWS DEA standards), files are committed into the MinIO storage node using Hive-style partitioning.

Storage Layout Pattern:
```Plaintext
dataops-lake/
└── transactions/
     └── year=2026/
          └── month=07/
               └── day=10/
                    └── data.parquet
```
Benefits: This directory topology enables immediate Partition Pruning when querying via analytical layers (e.g., AWS Athena), decreasing compute scanning costs and minimizing data retrieval latency.

## Multi-Environment AWS Migration Strategy
This platform is intentionally engineered with a Cloud-Agnostic architectural pattern. Transitioning from the local lab cluster to full cloud execution on AWS involves a 3-step configuration switch without altering the core pipeline application code:

Storage Layer Abstraction: Swap the internal MinIO S3 endpoint configuration out for native AWS S3 Buckets.

Compute Infrastructure Scaling: Migrate the Prefect Worker deployment into an AWS EKS Cluster or AWS ECS Fargate task definitions.

Identity Realignment: Replace standard Kubernetes RBAC configurations with AWS IAM Roles for Service Accounts (IRSA) to achieve fine-grained, secure infrastructure communication.
