# KubeShop Microservices API Catalog

This document details the HTTP REST API endpoints, schemas, request/response models, and error envelopes across all KubeShop backend services.

> [!TIP]
> During local development, interactive Swagger/OpenAPI documentation is available at:
> - **API Gateway**: `http://localhost:8000/docs`
> - **Product Service**: `http://localhost:8001/docs`
> - **Order Service**: `http://localhost:8002/docs`

---

## 1. Standardized Error Response Envelope

All backend services format error responses into a consistent JSON schema:

```json
{
  "error": {
    "code": "PRODUCT_SERVICE_TIMEOUT",
    "message": "Product Service failed to respond within 2.5 seconds",
    "request_id": "c6a2b851-9f93-41bb-bcf4-6a84cbe2ad32",
    "dependency": "product-service",
    "details": {
      "timeout_seconds": 2.5
    }
  }
}
```

### Common HTTP Status Codes
| Status Code | Meaning | Example Trigger |
| :--- | :--- | :--- |
| **400 Bad Request** | Request payload validation failed | Negative quantity, missing required field |
| **404 Not Found** | Target resource does not exist | Invalid product ID or order ID |
| **409 Conflict** | Business rule conflict | Insufficient product stock |
| **500 Internal Error** | Unhandled server exception | Syntax error, unhandled null reference |
| **502 Bad Gateway** | Downstream dependency failed | Product Service process is unreachable or crashed |
| **503 Service Unavailable** | Readiness check failed | Database is disconnected |
| **504 Gateway Timeout** | Downstream call exceeded timeout | Product Service latency exceeded 2.5s |

---

## 2. API Gateway Endpoints (`:8000`)

The API Gateway is the public interface used by the frontend.

| Method | Endpoint | Upstream Target | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None (Local) | Liveness probe: verifies gateway is alive. |
| `GET` | `/ready` | Downstream Services | Readiness probe: verifies configuration & downstream services. |
| `GET` | `/api/products` | `GET /products` | Retrieve catalog items (`?skip=0&limit=50&search=keyword`). |
| `GET` | `/api/products/{id}` | `GET /products/{id}` | Retrieve single product details by ID. |
| `POST` | `/api/products` | `POST /products` | Create a new catalog item. |
| `POST` | `/api/orders` | `POST /orders` | Submit a customer order. |
| `GET` | `/api/orders` | `GET /orders` | List existing orders (`?skip=0&limit=50`). |
| `GET` | `/api/orders/{id}` | `GET /orders/{id}` | Retrieve order details and line items by ID. |

---

## 3. Product Service Endpoints (`:8001`)

Owns product metadata and inventory levels.

### `GET /health`
- **Purpose**: Liveness probe for Kubernetes.
- **Response**: `{"status": "healthy", "service": "product-service"}`

### `GET /ready`
- **Purpose**: Readiness probe for Kubernetes. Executes `SELECT 1` on PostgreSQL.
- **Response (200)**: `{"status": "ready", "service": "product-service", "database": "connected"}`
- **Response (503)**: `{"status": "unready", "reason": "database unreachable"}`

### `GET /products`
- **Query Params**: `skip` (int), `limit` (int), `search` (string)
- **Response Model**:
  ```json
  {
    "total": 5,
    "items": [
      {
        "id": 1,
        "name": "Cloud Native Kubernetes Guide",
        "description": "Comprehensive practical manual...",
        "price": "39.99",
        "stock": 50,
        "created_at": "2026-10-03T15:00:00Z",
        "updated_at": "2026-10-03T15:00:00Z"
      }
    ]
  }
  ```

### `GET /products/{id}/availability`
- **Purpose**: Called by Order Service during checkout.
- **Query Params**: `quantity` (int, default 1)
- **Response Model**:
  ```json
  {
    "product_id": 1,
    "name": "Cloud Native Kubernetes Guide",
    "price": "39.99",
    "requested_quantity": 2,
    "available": true,
    "current_stock": 50
  }
  ```

### `POST /dev/faults/*` (Development Only)
- `POST /dev/faults/crash`: Simulates immediate process exit (SIGKILL).
- `POST /dev/faults/readiness-toggle?unready=true`: Forces `/ready` probe to fail with 503.
- `POST /dev/faults/cpu-burn?duration_seconds=5`: Generates 100% CPU load.
- `POST /dev/faults/memory-burn?mb=100`: Allocates memory chunks to test OOMKilled.

---

## 4. Order Service Endpoints (`:8002`)

Owns customer orders and coordinates checkout.

### `POST /orders`
- **Request Payload**:
  ```json
  {
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ]
  }
  ```
- **Response Model (201 Created)**:
  ```json
  {
    "id": 101,
    "status": "CONFIRMED",
    "total": "79.98",
    "created_at": "2026-10-03T15:30:00Z",
    "updated_at": "2026-10-03T15:30:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Cloud Native Kubernetes Guide",
        "unit_price": "39.99",
        "quantity": 2
      }
    ]
  }
  ```

### `GET /orders`
- **Response Model**:
  ```json
  {
    "total": 1,
    "items": [ ... ]
  }
  ```
