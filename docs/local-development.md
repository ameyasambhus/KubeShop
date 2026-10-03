# Bare-Metal Local Development Guide

This guide explains how to run and debug individual KubeShop services directly on your host machine without Docker or Kubernetes.

---

## Prerequisites
- Python 3.11+
- Node.js 20+ & npm 10+
- (Optional) PostgreSQL 16 (or you can use the built-in SQLite in-memory mode for rapid development)

---

## 1. Initial Workspace Setup

From the repository root:

```bash
# 1. Verify your installed tool versions
./scripts/setup/check_prereqs.sh

# 2. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install backend dependencies for development
pip install -r services/product-service/requirements.txt
pip install -r services/order-service/requirements.txt
pip install -r services/api-gateway/requirements.txt

# 4. Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## 2. Running Services Independently

You can run each service in a separate terminal window:

### Terminal 1: Product Service (`:8001`)
```bash
source .venv/bin/activate
export PRODUCT_DATABASE_URL="sqlite+aiosqlite:///./product_dev.db"
export PORT=8001
cd services/product-service
uvicorn app.main:app --port 8001 --reload
```
*Swagger docs available at: `http://localhost:8001/docs`*

### Terminal 2: Order Service (`:8002`)
```bash
source .venv/bin/activate
export ORDER_DATABASE_URL="sqlite+aiosqlite:///./order_dev.db"
export PRODUCT_SERVICE_URL="http://localhost:8001"
export PORT=8002
cd services/order-service
uvicorn app.main:app --port 8002 --reload
```
*Swagger docs available at: `http://localhost:8002/docs`*

### Terminal 3: API Gateway (`:8000`)
```bash
source .venv/bin/activate
export PRODUCT_SERVICE_URL="http://localhost:8001"
export ORDER_SERVICE_URL="http://localhost:8002"
export PORT=8000
cd services/api-gateway
uvicorn app.main:app --port 8000 --reload
```
*Swagger docs available at: `http://localhost:8000/docs`*

### Terminal 4: Frontend (`:3000`)
```bash
cd frontend
npm run dev
```
*Open your browser at: `http://localhost:3000`*

---

## 3. Running Automated Tests

Run all unit and integration test suites:
```bash
./scripts/testing/run_all_tests.sh
```

Or run tests for a single service:
```bash
cd services/product-service && pytest -v
cd services/order-service && pytest -v
cd services/api-gateway && pytest -v
```

---

## 4. Troubleshooting Local Development

### Issue: `Address already in use`
Check which process is listening on the port:
```bash
lsof -i :8000  # Gateway
lsof -i :8001  # Product Service
lsof -i :8002  # Order Service
```

### Issue: `Product Service unreachable from Order Service`
Ensure `PRODUCT_SERVICE_URL` is set to `http://localhost:8001` in your environment and Terminal 1 is running.
