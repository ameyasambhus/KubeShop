# KubeShop Infrastructure Documentation

This directory contains container definitions and orchestration manifests for running KubeShop in local and cloud-native environments.

---

## Directory Organization

```
infrastructure/
├── README.md              # Infrastructure topology overview (this file)
├── docker/
│   ├── README.md          # Docker Compose workflow, container networking & Postgres setup
│   ├── docker-compose.yml # Compose file defining frontend, gateway, services, and PostgreSQL
│   └── init-db.sql        # Database initialization script creating isolated product and order databases
└── kubernetes/
    ├── README.md          # Kubernetes deployment architecture, apply order, and probe guide
    ├── namespace.yaml     # kubeshop namespace
    ├── config/            # ConfigMaps and Secrets
    ├── storage/           # PersistentVolumeClaim for database state
    ├── database/          # PostgreSQL Deployment & ClusterIP Service
    ├── product-service/   # Product Service Deployment & ClusterIP Service
    ├── order-service/     # Order Service Deployment & ClusterIP Service
    ├── gateway/           # API Gateway Deployment & Service
    ├── frontend/          # Frontend Web Deployment & Service
    └── ingress/           # Ingress controller configuration
```

---

## Infrastructure Progression

KubeShop is designed to be learned and verified in three distinct steps:

1. **Step 1: Bare-Metal Development (No Containers)**
   Services run directly on Python and Node. Fast iterative code changes, unit testing with in-memory SQLite or local Postgres.
2. **Step 2: Docker Compose Multi-Container Setup**
   Verifies container images, Docker bridge networking, environment variable injection, and cross-service communication via Docker DNS names (`product-service`, `order-service`, `postgres`).
3. **Step 3: Kubernetes Local Cluster (Minikube / KinD / k3s)**
   Transitions the application to genuine cloud-native deployment primitives: Deployments, ReplicaSets, Services (CoreDNS resolution), ConfigMaps, Secrets, PVCs, liveness/readiness probes, and resource requests/limits.
