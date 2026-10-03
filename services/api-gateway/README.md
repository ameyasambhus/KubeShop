# API Gateway

## Purpose
The **API Gateway** serves as the unified entry point for all frontend client traffic in KubeShop. It reverse-proxies requests to internal microservices (`product-service` and `order-service`), injects and forwards distributed tracing correlation IDs (`X-Request-ID`), enforces timeouts, standardizes error envelopes, and records access telemetry.

---

## Responsibilities
- Provide a single public HTTP API interface for the Frontend single-page application.
- Route catalog queries (`/api/products/*`) to the Product Service.
- Route order operations (`/api/orders/*`) to the Order Service.
- Generate unique UUID correlation IDs (`X-Request-ID`) on ingress and forward them downstream.
- Enforce strict request timeout boundaries (`GATEWAY_REQUEST_TIMEOUT_SECONDS`).
- Translate downstream HTTP exceptions into consistent JSON error responses.
- Emit structured JSON access logs with duration, status code, and correlation ID.
- Provide `/health` (process) and `/ready` (dependency check) probes.

---

## What Does NOT Belong Here?
- **No Database Connections**: The API Gateway does not possess its own database and must NEVER query PostgreSQL directly.
- **No Business Logic**: The gateway does not calculate prices, inspect stock levels, or manage cart states. It is strictly a smart routing and correlation layer.

---

## Folder Structure
```
services/api-gateway/
├── Dockerfile                   # Container specification
├── README.md                    # This service guide
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration (pythonpath = .)
├── app/
│   ├── main.py                  # FastAPI entry point, CORS, logging & correlation middleware
│   ├── api/
│   │   ├── router.py            # Central router mounting health and proxy routes
│   │   └── routes/
│   │       ├── health.py        # /health and /ready probe endpoints
│   │       ├── products.py      # /api/products reverse proxy endpoints
│   │       └── orders.py        # /api/orders reverse proxy endpoints
│   ├── clients/
│   │   ├── product_client.py    # HTTP client for Product Service with timeout & error handling
│   │   └── order_client.py      # HTTP client for Order Service with timeout & error handling
│   └── core/
│       ├── config.py            # Pydantic Settings loaded from .env
│       ├── logging.py           # Structured JSON logger & contextvars
│       └── exceptions.py        # Exception definitions & error schemas
└── tests/
    ├── conftest.py              # Test client fixtures
    ├── test_gateway_routing.py  # Request proxying and correlation ID tests
    └── test_error_propagation.py# Timeout and downstream unreachable tests
```

---

## Important Files
- `app/main.py`: Sets up CORS, initializes structured JSON logging, and injects `X-Request-ID` into every incoming and outgoing request.
- `app/clients/product_client.py`: Reverse proxies product queries to `PRODUCT_SERVICE_URL`.
- `app/clients/order_client.py`: Reverse proxies order submissions to `ORDER_SERVICE_URL`.
- `app/core/config.py`: Centralized configuration mapping downstream service URLs and timeout budgets.

---

## Startup Flow
```
main.py
   ↓
Load Settings from Environment (core/config.py)
   ↓
Initialize Structured JSON Logging (core/logging.py)
   ↓
Configure CORS Middleware (allow frontend origins)
   ↓
Register Correlation Middleware (X-Request-ID propagation)
   ↓
Register Exception Handlers (Standardized error envelope)
   ↓
Mount API Routers (/health, /ready, /api/products, /api/orders)
   ↓
Listen for Incoming HTTP Requests on PORT (default 8000)
```

---

## Request Flow
```
Browser / Frontend
   ↓
HTTP GET /api/products (or POST /api/orders)
   ↓
Gateway Middleware:
   - Extract or generate X-Request-ID
   - Set contextvar for async tracing
   ↓
Route Handler (api/routes/products.py or orders.py)
   ↓
Downstream HTTP Client (clients/product_client.py or order_client.py)
   - Add header: X-Request-ID
   - Call downstream service with timeout (default 5.0s)
   ↓
Handle Downstream Response:
   - Success: Forward JSON payload
   - Timeout (>5s): Return 504 GATEWAY_TIMEOUT
   - Network failure: Return 502 SERVICE_UNREACHABLE
   ↓
HTTP Response + Header X-Request-ID + Structured JSON Log (duration_ms)
```

---

## Dependencies
- **Product Service**: Downstream HTTP microservice (`PRODUCT_SERVICE_URL`).
- **Order Service**: Downstream HTTP microservice (`ORDER_SERVICE_URL`).
- **Python 3.11+ / 3.14**: Async runtime.

---

## Environment Variables
| Variable | Purpose | Required? | Example Local Value | Default |
| :--- | :--- | :--- | :--- | :--- |
| `APP_ENV` | Environment mode | No | `development` | `development` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` | `INFO` |
| `PORT` | HTTP port | No | `8000` | `8000` |
| `HOST` | HTTP interface binding | No | `0.0.0.0` | `0.0.0.0` |
| `PRODUCT_SERVICE_URL` | Base URL of Product Service | Yes | `http://localhost:8001` (or `http://product-service:8000` in K8s) | `http://localhost:8001` |
| `ORDER_SERVICE_URL` | Base URL of Order Service | Yes | `http://localhost:8002` (or `http://order-service:8000` in K8s) | `http://localhost:8002` |
| `GATEWAY_REQUEST_TIMEOUT_SECONDS` | Downstream request timeout | No | `5.0` | `5.0` |

---

## API Endpoints
| Method | Path | Description | Downstream Target |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe: returns 200 if gateway process is alive | None |
| `GET` | `/ready` | Readiness probe: checks downstream microservices reachability | Product & Order Services |
| `GET` | `/api/products` | Retrieve catalog list (`?skip=0&limit=50&search=`) | `GET http://product-service/products` |
| `GET` | `/api/products/{id}` | Get product details by ID | `GET http://product-service/products/{id}` |
| `POST` | `/api/products` | Create product (dev/catalog management) | `POST http://product-service/products` |
| `POST` | `/api/orders` | Place a customer order | `POST http://order-service/orders` |
| `GET` | `/api/orders` | List existing orders | `GET http://order-service/orders` |
| `GET` | `/api/orders/{id}` | Get order details by ID | `GET http://order-service/orders/{id}` |

---

## Running the Service
```bash
# From repository root:
source .venv/bin/activate
export PRODUCT_SERVICE_URL="http://localhost:8001"
export ORDER_SERVICE_URL="http://localhost:8002"
cd services/api-gateway
uvicorn app.main:app --port 8000 --reload
```

---

## Running Tests
```bash
cd services/api-gateway
pytest -v
```

---

## Docker
Build the container:
```bash
docker build -t kubeshop/api-gateway:latest -f services/api-gateway/Dockerfile services/api-gateway/
```
Run the container:
```bash
docker run -p 8000:8000 -e PRODUCT_SERVICE_URL="http://product-service:8001" -e ORDER_SERVICE_URL="http://order-service:8002" kubeshop/api-gateway:latest
```

---

## Kubernetes Mapping
- **Deployment**: `infrastructure/kubernetes/gateway/deployment.yaml`
- **Service**: `infrastructure/kubernetes/gateway/service.yaml` (ClusterIP / NodePort exposing port 8000)
- **ConfigMap**: Supplies `PRODUCT_SERVICE_URL: http://product-service:8000` and `ORDER_SERVICE_URL: http://order-service:8000`.
- **Probes**: `/health` (every 10s) and `/ready` (every 5s).

---

## Failure Behavior
- **Downstream Service Crash**: If Product Service or Order Service terminates, calls to the respective endpoint return `502 Bad Gateway` with clear error detail: `SERVICE_UNREACHABLE`. The Gateway itself does not crash.
- **Downstream Latency**: If a downstream service delays longer than 5 seconds, the Gateway returns `504 Gateway Timeout` without hanging indefinitely.
