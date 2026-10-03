# ☸️ KubeShop

**A Production-Style Microservices Platform for Learning Kubernetes, Cloud-Native Architecture, Observability, and Fault Remediation.**

---

## 1. What is KubeShop?

**KubeShop** is a realistic, locally runnable microservices e-commerce and order-management application. 

It is **NOT** a toy CRUD application contained in a single file. Instead, it deliberately follows clean architectural boundaries, multi-database schema isolation, decoupled configuration management, structured JSON telemetry, distributed correlation tracking (`X-Request-ID`), health/readiness probe separation, and containerization best practices.

Its primary purpose is to serve as an authentic operational workload for learning how to deploy, scale, monitor, break, diagnose, and remediate microservices on **Kubernetes**.

---

## 2. High-Level Architecture & Dependency Graph

```mermaid
flowchart TD
    User([End-User Browser])

    subgraph Presentation_Layer ["Presentation Layer"]
        FE["Frontend (React 18 + TS + Nginx)<br/>Port: 3000"]
    end

    subgraph Edge_Routing ["Edge & Ingress Routing"]
        GW["API Gateway (FastAPI)<br/>Port: 8000"]
    end

    subgraph Microservices_Layer ["Domain Microservices"]
        PS["Product Service (FastAPI)<br/>Port: 8001"]
        OS["Order Service (FastAPI)<br/>Port: 8002"]
    end

    subgraph Persistence_Layer ["PostgreSQL 16 Storage"]
        PDB[("kubeshop_product DB<br/>(Products Table)")]
        ODB[("kubeshop_order DB<br/>(Orders & OrderItems Tables)")]
    end

    User -->|HTTP / UI| FE
    FE -->|HTTP / REST API| GW
    GW -->|GET, POST /api/products| PS
    GW -->|GET, POST /api/orders| OS
    OS -->|HTTP GET /products/{id}/availability| PS
    PS -->|SQLAlchemy Async| PDB
    OS -->|SQLAlchemy Async| ODB
```

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Nginx, Responsive CSS |
| **API Gateway** | Python 3.11+, FastAPI, HTTPX (async client), CORS |
| **Microservices** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, HTTPX |
| **Persistence** | PostgreSQL 16 (Logical DB isolation) / SQLite (in-memory test engine) |
| **Observability** | Structured JSON logging (`stdout`), `X-Request-ID` correlation, separate `/health` (liveness) & `/ready` (readiness) probes |
| **Containerization** | Multi-stage Docker builds, non-root `appuser`, Alpine & Python Slim |
| **Orchestration** | Docker Compose v2 & Plain Native Kubernetes Manifests |

---

## 4. Repository Structure

```
kubeshop/
├── README.md                          # Root system overview & quickstart (this file)
├── .env.example                       # Canonical template of all environment variables
├── .gitignore
│
├── frontend/                          # React + TypeScript Web Application
│   ├── README.md                      # Frontend architecture & components guide
│   ├── Dockerfile                     # Multi-stage Docker build (Node -> Nginx)
│   ├── nginx.conf                     # Production Nginx reverse-proxy config
│   ├── package.json
│   ├── tsconfig.json
│   └── src/                           # Components, pages, hooks, types, API client
│
├── services/                          # Independently Deployable Microservices
│   ├── api-gateway/                   # Central reverse-proxy, tracing, and routing
│   │   ├── README.md
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/                       # Routing, clients, logging, middleware
│   │   └── tests/                     # Gateway unit & proxy tests
│   │
│   ├── product-service/               # Product catalog & stock inventory service
│   │   ├── README.md
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/                       # Models, schemas, repositories, services, routes
│   │   └── tests/                     # Catalog & inventory availability tests
│   │
│   └── order-service/                 # Order processing & lifecycle service
│       ├── README.md
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app/                       # Models, schemas, product client, repositories
│       └── tests/                     # Order creation & dependency failure tests
│
├── infrastructure/                    # Container & Orchestration Manifests
│   ├── README.md
│   ├── docker/                        # Docker Compose multi-container environment
│   │   ├── README.md
│   │   ├── docker-compose.yml
│   │   └── init-db.sql                # Multi-database PostgreSQL init script
│   └── kubernetes/                    # Plain Kubernetes manifests
│       ├── README.md
│       ├── namespace.yaml             # kubeshop namespace
│       ├── config/                    # ConfigMaps and Secrets
│       ├── storage/                   # PersistentVolumeClaim for Postgres
│       ├── database/                  # PostgreSQL Deployment & ClusterIP Service
│       ├── product-service/           # Product Service Deployment & Service
│       ├── order-service/             # Order Service Deployment & Service
│       ├── gateway/                   # API Gateway Deployment & Service
│       ├── frontend/                  # Frontend Deployment & Service
│       └── ingress/                   # Ingress controller configuration
│
├── scripts/                           # Developer & Operational Helper Scripts
│   ├── README.md
│   ├── setup/                         # Prerequisites checker & environment loader
│   ├── seed/                          # Catalog product seeding script
│   └── testing/                       # Test runner & endpoint verification
│
└── docs/                              # Comprehensive Documentation Suite
    ├── README.md                      # Documentation index & reading guide
    ├── architecture.md                # Deep architectural breakdown & request flows
    ├── services.md                    # Complete OpenAPI endpoint specifications
    ├── local-development.md           # Bare-metal guide (running without containers)
    ├── kubernetes.md                  # Conceptual mapping: App -> K8s primitives
    ├── observability.md               # Structured logging & incident telemetry
    ├── failure-scenarios.md           # 12 Step-by-step incident drills & RCA runbooks
    ├── codebase-guide.md              # Reading order & "Where do I find...?" index
    └── handover.md                    # Complete project status matrix & handover report
```

---

## 5. Prerequisites

Before getting started, verify your environment runtimes:

```bash
./scripts/setup/check_prereqs.sh
```

- **Required for local development**: Python 3.11+, Node.js 20+, npm 10+.
- **Required for container/K8s workflows**: Docker Engine, `kubectl`, Minikube or KinD.

---

## 6. Three Ways to Run KubeShop

### Method 1: Local Bare-Metal (Fastest for Code Edits)
Run services natively on your host using Python and Node. In this mode, services run on distinct local ports and utilize SQLite or local PostgreSQL:

```bash
# Set up virtual environment and install dependencies:
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/product-service/requirements.txt
pip install -r services/order-service/requirements.txt
pip install -r services/api-gateway/requirements.txt
cd frontend && npm install && cd ..

# Run all test suites across the project:
./scripts/testing/run_all_tests.sh
```
*See **[docs/local-development.md](file:///Users/ameya/Developer/KubeShop/docs/local-development.md)** for launching each service terminal.*

---

### Method 2: Docker Compose (Full Multi-Container Stack)
Run the complete containerized platform with PostgreSQL and Docker bridge networking with a single command:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up --build -d
```
- Open **Web UI**: `http://localhost:3000`
- Open **API Gateway Swagger**: `http://localhost:8000/docs`
- Open **Product Service Swagger**: `http://localhost:8001/docs`
- Open **Order Service Swagger**: `http://localhost:8002/docs`

*To stop the stack:*
```bash
docker compose -f infrastructure/docker/docker-compose.yml down -v
```

---

### Method 3: Kubernetes Local Cluster (Minikube / KinD)
Deploy the full cloud-native architecture using plain, annotated manifests:

```bash
# 1. Apply Namespace, ConfigMaps, Secrets, and Storage:
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/config/
kubectl apply -f infrastructure/kubernetes/storage/

# 2. Deploy Database:
kubectl apply -f infrastructure/kubernetes/database/
kubectl wait --for=condition=ready pod -l app=postgres -n kubeshop --timeout=60s

# 3. Deploy Microservices, Gateway, and Frontend:
kubectl apply -f infrastructure/kubernetes/product-service/
kubectl apply -f infrastructure/kubernetes/order-service/
kubectl apply -f infrastructure/kubernetes/gateway/
kubectl apply -f infrastructure/kubernetes/frontend/

# 4. Verify Cluster State:
kubectl get all -n kubeshop
```
*See **[infrastructure/kubernetes/README.md](file:///Users/ameya/Developer/KubeShop/infrastructure/kubernetes/README.md)** for detailed manifest explanations and NodePort access commands.*

---

## 7. Testing & Verification

Execute the unified test runner to execute unit/integration tests and verify frontend TypeScript compilation:

```bash
./scripts/testing/run_all_tests.sh
```

**Test Coverage Summary:**
- **Product Service**: Catalog CRUD, availability logic, stock decrementing, `/health` and `/ready` probes (8 tests).
- **Order Service**: Order placement, item snapshotting, price computation, downstream timeout handling, dependency failure handling (6 tests).
- **API Gateway**: Route proxying, `X-Request-ID` propagation, 502/504 error translation (5 tests).
- **Frontend**: Full TypeScript compilation and production bundle build.

---

## 8. Failure Scenarios & Incident Learning

KubeShop is pre-configured to simulate **12 realistic production incidents**:

| Incident Drill | What We Break | What You Learn in Kubernetes |
| :--- | :--- | :--- |
| **A: Container Crash** | Kill container process (SIGKILL) | Exit codes, pod restarts, `kubectl logs --previous` |
| **B: CrashLoopBackOff** | Misconfigure database DSN | Kubelet exponential backoff delay, pod state |
| **C: Readiness Failure** | Simulate DB disconnect | Liveness vs readiness, removing Pods from Endpoints |
| **D: Liveness Failure** | Break health check path | Deadlock detection, container termination & replacement |
| **E: Database Outage** | Scale PostgreSQL to 0 | Downstream failure cascades, connection pool retry |
| **F: Dependency Outage**| Scale Product Service to 0 | Dependency isolation, graceful degradation in UI |
| **G: Downstream Latency**| Inject 3000ms latency | Timeout budgets, cascading delay, tail-latency |
| **H: CPU Throttling** | Trigger CPU burn | CFS quota throttling, sizing CPU requests vs limits |
| **I: OOMKilled** | Allocate 300MB memory | Linux OOM killer (Exit 137), memory limit tuning |
| **J: DNS / Config Error** | Point URL to invalid hostname | CoreDNS resolution, ConfigMap updates |
| **K: Replica Fault** | Delete Pod under active load | Stateless resilience, ReplicaSet reconciliation |
| **L: Failed Rollout** | Deploy non-existent image tag | Zero-downtime rolling updates, `rollout undo` |

*Step-by-step procedures and commands for every drill are in **[docs/failure-scenarios.md](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md)**.*

---

## 9. Comprehensive Documentation Index

- **[docs/architecture.md](file:///Users/ameya/Developer/KubeShop/docs/architecture.md)**: System design, data ownership, sequence diagrams, failure domains.
- **[docs/codebase-guide.md](file:///Users/ameya/Developer/KubeShop/docs/codebase-guide.md)**: "Where do I find...?" quick index, code reading order, request walkthroughs.
- **[docs/services.md](file:///Users/ameya/Developer/KubeShop/docs/services.md)**: Complete OpenAPI endpoint specifications and schemas.
- **[docs/local-development.md](file:///Users/ameya/Developer/KubeShop/docs/local-development.md)**: Running without containers.
- **[docs/kubernetes.md](file:///Users/ameya/Developer/KubeShop/docs/kubernetes.md)**: Application concepts mapped to Kubernetes primitives.
- **[docs/observability.md](file:///Users/ameya/Developer/KubeShop/docs/observability.md)**: Structured JSON logging, correlation IDs, incident evidence.
- **[docs/failure-scenarios.md](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md)**: Step-by-step incident drills and RCA guide.
- **[docs/handover.md](file:///Users/ameya/Developer/KubeShop/docs/handover.md)**: Implementation handover report and status matrix.
