# KubeShop Developer & Operational Scripts

This directory houses helper scripts for environment verification, database seeding, testing, and service verification.

> [!NOTE]
> These scripts exist strictly to eliminate repetitive commands (like checking dependencies or running multi-service test suites). They do NOT hide Kubernetes operations. Kubernetes manifests must be applied and inspected using standard `kubectl` commands to maximize educational value.

---

## Directory Organization

```
scripts/
├── README.md                  # This file
├── setup/
│   ├── check_prereqs.sh       # Verifies local tool installations (Python, Node, Docker, kubectl)
│   └── local_env.sh           # Loads and exports .env variables into current shell
├── seed/
│   └── seed_products.py       # Seeds initial products into the catalog database
└── testing/
    ├── run_all_tests.sh       # Executes pytest test suites across all backend microservices
    └── verify_endpoints.sh    # Issues HTTP curl requests to test health and flow connectivity
```

---

## Usage Guide

### 1. Verify Your Development Environment
```bash
./scripts/setup/check_prereqs.sh
```

### 2. Export Environment Variables for Bare-Metal Running
```bash
source scripts/setup/local_env.sh
```

### 3. Run Backend Test Suite
```bash
./scripts/testing/run_all_tests.sh
```

### 4. Verify Live Services
```bash
./scripts/testing/verify_endpoints.sh
```
