# Order Service

## Purpose
The **Order Service** manages the lifecycle of customer orders in KubeShop. It orchestrates order validation by communicating with the Product Service, calculates total amounts, and persists order records.

---

## Responsibilities
- Accept and validate order creation requests.
- Communicate with Product Service to verify product existence, current retail price, and stock availability.
- Calculate order total prices securely on the backend.
- Persist orders and child line items in the `kubeshop_order` PostgreSQL database.
- Retrieve orders by ID and list historical orders.
- Enforce explicit request timeouts when calling downstream dependencies.
- Expose `/health` (process) and `/ready` (database-backed readiness) probes.

---

## What Does NOT Belong Here?
- **No Master Product Catalog**: Order Service does not store master product metadata or manage inventory levels. It only captures a snapshot of the item (`product_id`, `product_name`, `unit_price`, `quantity`) at the moment of order placement.
- **No Direct Product DB Access**: Order Service must NEVER query the Product Service's database directly. Communication occurs exclusively over HTTP via the Product Service API.
- **No Payment Processing**: Payment processing is out of scope for the educational workload.

---

## Folder Structure
```
services/order-service/
├── Dockerfile                   # Container specification
├── README.md                    # This service guide
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration (pythonpath = .)
├── app/
│   ├── main.py                  # FastAPI entry point, lifespan, error middleware
│   ├── api/
│   │   ├── router.py            # Central router mounting health and order routes
│   │   └── routes/
│   │       ├── health.py        # /health and /ready probe endpoints
│   │       └── orders.py        # /orders POST and GET routes
│   ├── clients/
│   │   └── product_client.py    # HTTP client calling Product Service with timeout
│   ├── core/
│   │   ├── config.py            # Pydantic Settings loaded from .env
│   │   ├── logging.py           # Structured JSON logger & contextvars
│   │   └── exceptions.py        # Application exceptions & error schemas
│   ├── db/
│   │   ├── base.py              # SQLAlchemy 2.0 DeclarativeBase
│   │   ├── session.py           # Async engine & session factory (get_db)
│   │   └── init_db.py           # Database schema initialization
│   ├── models/
│   │   ├── order.py             # Order ORM Model (status, total)
│   │   └── order_item.py        # OrderItem ORM Model (item snapshot)
│   ├── repositories/
│   │   └── order_repository.py  # Isolated database queries for orders & items
│   ├── schemas/
│   │   └── order.py             # Pydantic request & response validation schemas
│   └── services/
│       └── order_service.py     # Order placement business logic & coordination
└── tests/
    ├── conftest.py              # In-memory SQLite async test database fixture
    ├── test_health_checks.py    # Liveness and readiness probe unit tests
    ├── test_order_creation.py   # Order placement & total calculation tests
    └── test_product_dependency_failure.py # Downstream timeout & failure tests
```

---

## Important Files
- `app/main.py`: Bootstraps FastAPI, configures structured logging, runs database initialization, and registers the global `X-Request-ID` correlation middleware.
- `app/clients/product_client.py`: HTTPX client with explicit timeout (`ORDER_TO_PRODUCT_TIMEOUT_SECONDS`) calling Product Service.
- `app/services/order_service.py`: Core order placement logic: calls `product_client.check_availability`, calculates totals, and persists orders.
- `app/repositories/order_repository.py`: Manages SQL transactions across `orders` and `order_items` tables.
- `app/core/config.py`: Loads `PRODUCT_SERVICE_URL`, `ORDER_TO_PRODUCT_TIMEOUT_SECONDS`, and database credentials.

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
   - Call db/init_db.py -> Create orders and order_items tables if missing
   ↓
Register Middleware (X-Request-ID propagation & Access Logging)
   ↓
Register Exception Handlers (Standardized JSON error envelope)
   ↓
Mount API Routers (/health, /ready, /orders)
   ↓
Listen for Incoming HTTP Requests on PORT (default 8002)
```

---

## Request Flow: Order Creation
```
HTTP POST /orders (Body: {"items": [{"product_id": 1, "quantity": 2}]})
   ↓
FastAPI Router (api/routes/orders.py)
   ↓
Extract X-Request-ID into async context
   ↓
OrderService (services/order_service.py)
   ↓
ProductServiceClient (clients/product_client.py)
   - HTTP GET {PRODUCT_SERVICE_URL}/products/1/availability?quantity=2
   - Forward Header: X-Request-ID
   - Enforce Timeout: 2.5 seconds
   ↓
Receive Product Price & Availability
   - If stock < quantity: raise InsufficientStockException (409)
   - If timeout exceeded: raise ProductTimeoutException (504)
   - If connection error: raise ProductDependencyException (502)
   ↓
Calculate Total Amount: unit_price * quantity
   ↓
OrderRepository (repositories/order_repository.py)
   - Insert into orders
   - Insert into order_items
   ↓
HTTP 201 Created Response + X-Request-ID Header + Structured JSON Access Log
```

---

## Dependencies
- **PostgreSQL 16**: Relational storage for orders (`kubeshop_order` database).
- **Product Service**: HTTP service dependency for catalog verification.
- **Python 3.11+ / 3.14**: Async runtime.

---

## Environment Variables
| Variable | Purpose | Required? | Example Local Value | Default |
| :--- | :--- | :--- | :--- | :--- |
| `APP_ENV` | Application environment mode | No | `development` | `development` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` | `INFO` |
| `PORT` | HTTP port | No | `8002` | `8002` |
| `HOST` | HTTP interface binding | No | `0.0.0.0` | `0.0.0.0` |
| `ORDER_DATABASE_URL` | Async PostgreSQL connection string | Yes | `postgresql+asyncpg://postgres:postgres@localhost:5432/kubeshop_order` | SQLite in memory for tests |
| `PRODUCT_SERVICE_URL` | URL of Product Service | Yes | `http://localhost:8001` (or `http://product-service:8000` in K8s) | `http://localhost:8001` |
| `ORDER_TO_PRODUCT_TIMEOUT_SECONDS` | Downstream call timeout | No | `2.5` | `2.5` |

---

## API Endpoints
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe: returns 200 if process is running |
| `GET` | `/ready` | Readiness probe: returns 200 if Order database is reachable |
| `POST` | `/orders` | Create an order with product price/stock verification |
| `GET` | `/orders` | List existing orders (supports `?skip=0&limit=50`) |
| `GET` | `/orders/{id}` | Retrieve order details and line items by ID |

---

## Running the Service
```bash
# From repository root:
source .venv/bin/activate
export ORDER_DATABASE_URL="sqlite+aiosqlite:///./order_dev.db" # or local Postgres
export PRODUCT_SERVICE_URL="http://localhost:8001"
cd services/order-service
uvicorn app.main:app --port 8002 --reload
```

---

## Running Tests
```bash
cd services/order-service
pytest -v
```

---

## Docker
Build the container:
```bash
docker build -t kubeshop/order-service:latest -f services/order-service/Dockerfile services/order-service/
```
Run the container:
```bash
docker run -p 8002:8002 -e ORDER_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/kubeshop_order" -e PRODUCT_SERVICE_URL="http://product-service:8001" kubeshop/order-service:latest
```

---

## Kubernetes Mapping
- **Deployment**: `infrastructure/kubernetes/order-service/deployment.yaml`
- **Service**: `infrastructure/kubernetes/order-service/service.yaml` (ClusterIP: `http://order-service:8000`)
- **ConfigMap**: Supplies `PRODUCT_SERVICE_URL` (`http://product-service:8000`) and `ORDER_TO_PRODUCT_TIMEOUT_SECONDS`.
- **Secret**: Supplies `ORDER_DATABASE_URL`.
- **Probes**: `/health` (every 10s) and `/ready` (every 5s).

---

## Failure Behavior
- **Product Service Down**: When Product Service is stopped or unready, order placement returns `502 Bad Gateway` with `dependency: product-service`. The Order Service process itself remains healthy and ready to serve other requests (like viewing existing orders).
- **Product Service Slow**: If Product Service latency exceeds 2.5s, the client aborts and returns `504 Gateway Timeout`.
- **Order Database Down**: `/ready` returns 503; Kubernetes removes Pod from service endpoints.
