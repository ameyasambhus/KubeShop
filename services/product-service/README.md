# Product Service

## Purpose
The **Product Service** is an autonomous microservice responsible for the product catalog, item descriptions, retail pricing, and inventory availability in KubeShop.

---

## Responsibilities
- Manage product catalog items (CRUD operations).
- Expose inventory availability and pricing checks for the Order Service.
- Support full-text search and pagination across catalog items.
- Own and manage the `products` table in the PostgreSQL database.
- Expose `/health` (liveness) and `/ready` (database-backed readiness) probes.
- Provide safe developer hooks for simulating latency, crashes, and resource limits during Kubernetes learning drills.

---

## What Does NOT Belong Here?
- **No Order Data**: Product Service has zero knowledge of orders, customers, shopping carts, or payment states. It must never read or write to order tables.
- **No Direct Frontend Routing**: Client requests reach Product Service strictly through the API Gateway.
- **No Order Validation Logic**: Product Service only answers whether a quantity is available; it does not decide whether an order should be approved or cancelled.

---

## Folder Structure
```
services/product-service/
├── Dockerfile                   # Container specification
├── README.md                    # This service guide
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest settings (pythonpath = .)
├── app/
│   ├── main.py                  # FastAPI entry point, lifespan, error middleware
│   ├── api/
│   │   ├── router.py            # Central router mounting routes
│   │   └── routes/
│   │       ├── health.py        # /health and /ready probe endpoints
│   │       ├── products.py      # /products CRUD and /availability endpoints
│   │       └── dev_faults.py    # /dev/faults crash/CPU/memory/readiness hooks
│   ├── core/
│   │   ├── config.py            # Pydantic Settings loaded from .env
│   │   ├── logging.py           # Structured JSON logger & contextvars
│   │   └── exceptions.py        # Application exceptions & error schemas
│   ├── db/
│   │   ├── base.py              # SQLAlchemy 2.0 DeclarativeBase
│   │   ├── session.py           # Async engine & session factory (get_db)
│   │   └── init_db.py           # Table creation & automatic catalog seed
│   ├── models/
│   │   └── product.py           # Product ORM Model
│   ├── repositories/
│   │   └── product_repository.py# Isolated database queries & SQL transactions
│   ├── schemas/
│   │   └── product.py           # Pydantic request & response validation schemas
│   └── services/
│       └── product_service.py   # Business logic & simulated latency injection
└── tests/
    ├── conftest.py              # In-memory SQLite async test database fixture
    ├── test_health_checks.py    # Liveness and readiness probe unit tests
    ├── test_product_api.py      # API route integration tests
    └── test_product_repository.py# Repository CRUD tests
```

---

## Important Files
- `app/main.py`: Bootstraps FastAPI, configures structured logging, runs database initialization, and registers the global `X-Request-ID` correlation middleware.
- `app/core/config.py`: Centralized Pydantic settings loading `PRODUCT_DATABASE_URL`, `PORT`, and `SIMULATED_LATENCY_MS`.
- `app/db/init_db.py`: Executes schema creation and automatically seeds initial products on startup if the database is empty.
- `app/repositories/product_repository.py`: Isolates all SQL interactions from routes and business logic.
- `app/services/product_service.py`: Contains catalog business rules and handles simulated latency for timeout testing.
- `app/api/routes/health.py`: Defines separate liveness (`/health`) and readiness (`/ready`) endpoints.

---

## Startup Flow
```
main.py
   ↓
Load Settings from Environment (core/config.py)
   ↓
Initialize Structured JSON Logging (core/logging.py)
   ↓
Lifespan Startup:
   - Call db/init_db.py -> Create tables if missing
   - Seed sample products if catalog is empty
   ↓
Register Middleware (X-Request-ID propagation & Access Logging)
   ↓
Register Exception Handlers (Standardized JSON error envelope)
   ↓
Mount API Routers (/health, /ready, /products, /dev/faults)
   ↓
Listen for Incoming HTTP Requests on PORT (default 8001)
```

---

## Request Flow
```
HTTP Request (e.g. GET /products/1)
   ↓
FastAPI Router (api/routes/products.py)
   ↓
Extract X-Request-ID into async context
   ↓
ProductService (services/product_service.py)
   - Checks for SIMULATED_LATENCY_MS delay
   ↓
ProductRepository (repositories/product_repository.py)
   - Executes async SELECT query against PostgreSQL
   ↓
Product ORM Model (models/product.py)
   ↓
ProductResponse Pydantic Schema (schemas/product.py)
   ↓
HTTP 200 Response + X-Request-ID Header + Structured JSON Access Log
```

---

## Dependencies
- **PostgreSQL 16**: Relational storage for products (`kubeshop_product` database).
- **Python 3.11+ / 3.14**: Async runtime.

---

## Environment Variables
| Variable | Purpose | Required? | Example Local Value | Default |
| :--- | :--- | :--- | :--- | :--- |
| `APP_ENV` | Application environment mode | No | `development` | `development` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` | `INFO` |
| `PORT` | HTTP port | No | `8001` | `8001` |
| `HOST` | HTTP interface binding | No | `0.0.0.0` | `0.0.0.0` |
| `PRODUCT_DATABASE_URL` | Async PostgreSQL connection string | Yes | `postgresql+asyncpg://postgres:postgres@localhost:5432/kubeshop_product` | SQLite in memory for tests |
| `SIMULATED_LATENCY_MS` | Inject artificial delay (ms) for timeout drills | No | `0` (or `3000` to test timeout) | `0` |
| `SIMULATED_FAILURE_RATE` | Inject artificial error rate (0.0 - 1.0) | No | `0.0` | `0.0` |

---

## API Endpoints
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe: returns 200 if process is running |
| `GET` | `/ready` | Readiness probe: returns 200 if database is reachable |
| `GET` | `/products` | List catalog items (supports `?skip=0&limit=50&search=keyword`) |
| `GET` | `/products/{id}` | Get product details by ID |
| `GET` | `/products/{id}/availability` | Verify stock and price for Order Service (`?quantity=N`) |
| `POST` | `/products` | Create a new catalog product |
| `PATCH` | `/products/{id}` | Update product information or stock |
| `POST` | `/dev/faults/crash` | Crash container process with exit code (dev only) |
| `POST` | `/dev/faults/readiness-toggle`| Force `/ready` to return 503 (dev only) |
| `POST` | `/dev/faults/cpu-burn` | Consume 100% CPU for N seconds (dev only) |
| `POST` | `/dev/faults/memory-burn` | Allocate N MB memory to test OOMKilled (dev only) |

---

## Health vs. Readiness Endpoints
- **`/health` (Liveness)**: Informs Kubernetes whether the Python process has locked up or crashed. If `/health` fails, Kubernetes **restarts** the container. It does NOT check external databases.
- **`/ready` (Readiness)**: Informs Kubernetes whether the service can accept user traffic. It runs a query (`SELECT 1`) against the database. If `/ready` fails, Kubernetes **removes the Pod from Service endpoints** so traffic is not routed to a failing pod, without needlessly restarting it.

---

## Running the Service
```bash
# From repository root:
source .venv/bin/activate
export PRODUCT_DATABASE_URL="sqlite+aiosqlite:///./product_dev.db" # or local Postgres
cd services/product-service
uvicorn app.main:app --port 8001 --reload
```

---

## Running Tests
```bash
cd services/product-service
pytest -v
```

---

## Docker
Build the container:
```bash
docker build -t kubeshop/product-service:latest -f services/product-service/Dockerfile services/product-service/
```
Run the container:
```bash
docker run -p 8001:8001 -e PRODUCT_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/kubeshop_product" kubeshop/product-service:latest
```

---

## Kubernetes Mapping
- **Deployment**: `infrastructure/kubernetes/product-service/deployment.yaml` (maintains desired replicas with rolling updates).
- **Service**: `infrastructure/kubernetes/product-service/service.yaml` (ClusterIP exposing `http://product-service:8000`).
- **ConfigMap**: Supplies `LOG_LEVEL` and `SIMULATED_LATENCY_MS`.
- **Secret**: Supplies `PRODUCT_DATABASE_URL`.
- **Probes**: Configured to poll `/health` every 10s and `/ready` every 5s.

---

## Failure Behavior
- **Database Unavailable**: `/ready` fails with 503; Kubernetes removes Pod from Service endpoints. Queries return HTTP 503 with code `DATABASE_UNAVAILABLE`.
- **High Latency Injection (`SIMULATED_LATENCY_MS=3000`)**: Causes dependent Order Service calls to time out after 2.5s, allowing investigation of cascading latency and timeout errors.
