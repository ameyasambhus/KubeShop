# KubeShop Codebase Navigation & Reading Guide

## Welcome to KubeShop!
This guide is written specifically for an engineer, architect, or student who has received this repository without having written the code. It answers the fundamental question:

> *"If I want to truly understand this system, what files should I read, and in what order?"*

---

## 1. High-Level Documentation Reading Order

Follow this 9-step path to master the architecture before diving into code:

1. **[README.md](file:///Users/ameya/Developer/KubeShop/README.md)**: 5-minute birds-eye summary of KubeShop's mission and architecture.
2. **[docs/architecture.md](file:///Users/ameya/Developer/KubeShop/docs/architecture.md)**: Service boundaries, data ownership, sequence diagrams, and failure domains.
3. **[frontend/README.md](file:///Users/ameya/Developer/KubeShop/frontend/README.md)**: React SPA design and error banner interceptors.
4. **[services/api-gateway/README.md](file:///Users/ameya/Developer/KubeShop/services/api-gateway/README.md)**: Reverse proxy routing, correlation ID injection, and timeout budgets.
5. **[services/product-service/README.md](file:///Users/ameya/Developer/KubeShop/services/product-service/README.md)**: Product catalog domain, availability logic, and seed data.
6. **[services/order-service/README.md](file:///Users/ameya/Developer/KubeShop/services/order-service/README.md)**: Order orchestration, downstream HTTP client, and snapshotting.
7. **[infrastructure/docker/README.md](file:///Users/ameya/Developer/KubeShop/infrastructure/docker/README.md)**: Multi-container Compose topology and DNS networking.
8. **[infrastructure/kubernetes/README.md](file:///Users/ameya/Developer/KubeShop/infrastructure/kubernetes/README.md)**: Cloud-native manifest hierarchy and apply order.
9. **[docs/failure-scenarios.md](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md)**: Step-by-step incident drills and root-cause analysis runbooks.

---

## 2. Code Reading Order (Inside a Microservice)

When reading a backend microservice (e.g. `services/product-service`), read files in this specific sequence:

```
1. app/main.py
   ↳ The application entry point: see lifespan startup, middleware, and exception handlers.
      ↓
2. app/core/config.py
   ↳ Pydantic Settings: see what environment variables and URLs configure the service.
      ↓
3. app/api/routes/
   ↳ HTTP Controllers: inspect endpoint declarations and input query parameters.
      ↓
4. app/schemas/
   ↳ Pydantic Schemas: understand the data contracts for requests and responses.
      ↓
5. app/services/
   ↳ Business Logic: see how business rules are enforced and errors raised.
      ↓
6. app/repositories/
   ↳ Database Operations: see the raw SQL queries and async session transactions.
      ↓
7. app/models/
   ↳ SQLAlchemy ORM Models: examine table columns and relationships.
      ↓
8. app/clients/ (if present)
   ↳ Outbound HTTP Clients: see how calls to other microservices enforce timeouts.
```

### Why This Reading Order?
It follows the natural path of an incoming HTTP request from the outer network boundary down to persistence, allowing you to build an intuitive mental model of the codebase.

---

## 3. "Where Do I Find...?" Quick Reference Index

| What are you looking for? | Exact File / Directory Path |
| :--- | :--- |
| **Product API Endpoints** | [`services/product-service/app/api/routes/products.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/api/routes/products.py) |
| **Product Business Logic** | [`services/product-service/app/services/product_service.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/services/product_service.py) |
| **Product Database Queries** | [`services/product-service/app/repositories/product_repository.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/repositories/product_repository.py) |
| **Product ORM Model** | [`services/product-service/app/models/product.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/models/product.py) |
| **Order Placement Logic** | [`services/order-service/app/services/order_service.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/services/order_service.py) |
| **Order-to-Product HTTP Client** | [`services/order-service/app/clients/product_client.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/clients/product_client.py) |
| **Order Database Model** | [`services/order-service/app/models/order.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/models/order.py) |
| **Order Item Snapshot Model** | [`services/order-service/app/models/order_item.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/models/order_item.py) |
| **Gateway Routing Logic** | [`services/api-gateway/app/api/routes/`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/api/routes/) |
| **Request Correlation & Tracing** | [`*/app/core/logging.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/core/logging.py) & `correlation_and_logging_middleware` in [`main.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/main.py) |
| **Liveness & Readiness Probes** | `*/app/api/routes/health.py` across all services |
| **Fault Injection Knobs** | [`services/product-service/app/api/routes/dev_faults.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/api/routes/dev_faults.py) |
| **Frontend UI Components** | [`frontend/src/components/`](file:///Users/ameya/Developer/KubeShop/frontend/src/components/) |
| **Frontend API Gateway Client**| [`frontend/src/api/client.ts`](file:///Users/ameya/Developer/KubeShop/frontend/src/api/client.ts) |
| **Docker Compose Config** | [`infrastructure/docker/docker-compose.yml`](file:///Users/ameya/Developer/KubeShop/infrastructure/docker/docker-compose.yml) |
| **Postgres Multi-DB SQL Script** | [`infrastructure/docker/init-db.sql`](file:///Users/ameya/Developer/KubeShop/infrastructure/docker/init-db.sql) |
| **Kubernetes Deployments** | [`infrastructure/kubernetes/`](file:///Users/ameya/Developer/KubeShop/infrastructure/kubernetes/) |
| **Failure Incident Drills** | [`docs/failure-scenarios.md`](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md) |

---

## 4. End-to-End Request Walkthroughs with Source File Maps

### Walkthrough 1: Product Browsing Request

1. **Browser**: User loads the catalog view.
2. **Frontend Client**: [`frontend/src/pages/CatalogPage.tsx`](file:///Users/ameya/Developer/KubeShop/frontend/src/pages/CatalogPage.tsx) calls `api.getProducts()` in [`frontend/src/api/client.ts`](file:///Users/ameya/Developer/KubeShop/frontend/src/api/client.ts).
3. **HTTP Call**: GET `http://localhost:3000/api/products`.
4. **Nginx Reverse Proxy**: [`frontend/nginx.conf`](file:///Users/ameya/Developer/KubeShop/frontend/nginx.conf) forwards `/api/` to `http://api-gateway:8000/api/products`.
5. **Gateway Middleware**: [`services/api-gateway/app/main.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/main.py) extracts or generates `X-Request-ID`.
6. **Gateway Route**: [`services/api-gateway/app/api/routes/products.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/api/routes/products.py) delegates to `ProductClient`.
7. **Downstream Call**: [`services/api-gateway/app/clients/product_client.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/clients/product_client.py) calls `http://product-service:8000/products`.
8. **Product Service Middleware**: [`services/product-service/app/main.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/main.py) binds the `X-Request-ID` context.
9. **Product Route**: [`services/product-service/app/api/routes/products.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/api/routes/products.py) invokes `ProductService.list_products()`.
10. **Product Service Layer**: [`services/product-service/app/services/product_service.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/services/product_service.py) queries repository.
11. **Product Repository**: [`services/product-service/app/repositories/product_repository.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/repositories/product_repository.py) runs async SQL query on PostgreSQL.
12. **Return Flow**: PostgreSQL &rarr; Product Service &rarr; API Gateway &rarr; Frontend &rarr; Rendered UI Grid.

---

### Walkthrough 2: Order Creation Request

1. **Browser**: User clicks "Place Order Now" for 2 copies of item #1.
2. **Frontend Form**: [`frontend/src/pages/CheckoutModal.tsx`](file:///Users/ameya/Developer/KubeShop/frontend/src/pages/CheckoutModal.tsx) calls `api.createOrder()`.
3. **Gateway Ingress**: [`services/api-gateway/app/api/routes/orders.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/api/routes/orders.py) receives `POST /api/orders`.
4. **Gateway Client**: [`services/api-gateway/app/clients/order_client.py`](file:///Users/ameya/Developer/KubeShop/services/api-gateway/app/clients/order_client.py) forwards request to `http://order-service:8000/orders`.
5. **Order Service Router**: [`services/order-service/app/api/routes/orders.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/api/routes/orders.py) invokes `OrderService.create_order()`.
6. **Order Service Layer**: [`services/order-service/app/services/order_service.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/services/order_service.py) loops through items.
7. **Downstream Call to Product Service**: [`services/order-service/app/clients/product_client.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/clients/product_client.py) calls `GET http://product-service:8000/products/1/availability?quantity=2` with a 2.5-second timeout.
8. **Product Service Availability Verification**: [`services/product-service/app/services/product_service.py`](file:///Users/ameya/Developer/KubeShop/services/product-service/app/services/product_service.py) confirms stock and returns unit price ($39.99).
9. **Total Calculation**: Order Service calculates: `2 * 39.99 = $79.98`.
10. **Order Persistence**: [`services/order-service/app/repositories/order_repository.py`](file:///Users/ameya/Developer/KubeShop/services/order-service/app/repositories/order_repository.py) inserts into `orders` and `order_items` tables in `kubeshop_order` database.
11. **Response Returned**: HTTP 201 Created &rarr; API Gateway &rarr; Frontend displays success confirmation!
