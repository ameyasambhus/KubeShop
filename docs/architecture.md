# KubeShop Architecture Specification

## 1. High-Level System Architecture

KubeShop is built as a set of autonomous, single-purpose microservices adhering to clean architectural boundaries, isolated persistence domains, and container-native operational patterns.

```mermaid
flowchart TD
    User([End User Browser])
    
    subgraph Frontend_Boundary ["Frontend Presentation Layer"]
        FE["Frontend (React 18 + TS + Nginx)<br/>Port: 3000"]
    end

    subgraph Gateway_Boundary ["Edge & Routing Layer"]
        GW["API Gateway (FastAPI)<br/>Port: 8000"]
    end

    subgraph Service_Boundary ["Core Domain Services"]
        PS["Product Service (FastAPI)<br/>Port: 8001"]
        OS["Order Service (FastAPI)<br/>Port: 8002"]
    end

    subgraph Persistence_Boundary ["Storage Layer (PostgreSQL)"]
        PDB[("kubeshop_product DB<br/>(Products Table)")]
        ODB[("kubeshop_order DB<br/>(Orders & OrderItems Tables)")]
    end

    User -->|HTTP / UI| FE
    FE -->|HTTP REST /api| GW
    GW -->|GET, POST /products| PS
    GW -->|GET, POST /orders| OS
    OS -->|HTTP GET /products/{id}/availability| PS
    PS -->|SQLAlchemy Async (DSN 1)| PDB
    OS -->|SQLAlchemy Async (DSN 2)| ODB
```

---

## 2. Service Responsibilities & Boundaries

| Component | In Scope | Out of Scope / Forbidden |
| :--- | :--- | :--- |
| **Frontend** | User UI, client state, rendering product catalog, cart management, error banners. | Connecting to database; making direct internal service calls bypassing the Gateway. |
| **API Gateway** | Unified external entry point; generating and propagating `X-Request-ID`; routing `/api/*`; standardizing JSON errors; enforcing timeouts (5s); structured access logging. | Database storage; domain business logic; total price calculation; order status management. |
| **Product Service** | Catalog metadata (name, description, price); stock inventory; availability validation; ownership of `products` table. | Accessing orders or customer records; approving orders; payment processing. |
| **Order Service** | Order lifecycle (CONFIRMED, PENDING, CANCELLED); price computation; line item snapshotting; ownership of `orders` and `order_items` tables. | Directly querying Product Service database tables; allowing clients to specify arbitrary prices. |
| **PostgreSQL** | Relational ACID storage. | Inter-service shared state (Product and Order tables reside in separate logical databases). |

---

## 3. Data Ownership & Schema Isolation

Data ownership is strictly partitioned by service boundary. Services communicate state changes exclusively via HTTP APIs, never by reading or writing to another service's database tables.

```mermaid
erDiagram
    %% Product Service Domain
    PRODUCT {
        int id PK
        string name
        text description
        numeric price
        int stock
        timestamp created_at
        timestamp updated_at
    }

    %% Order Service Domain
    ORDER {
        int id PK
        string status
        numeric total
        timestamp created_at
        timestamp updated_at
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id
        string product_name
        numeric unit_price
        int quantity
    }

    ORDER ||--|{ ORDER_ITEM : "contains"
```

> [!IMPORTANT]
> `ORDER_ITEM` stores a **snapshot** (`product_name`, `unit_price`) captured at the moment of order placement. If a product's price or description changes in the catalog later, historical order records remain immutable.

---

## 4. End-to-End Request Flows

### Flow A: Product Catalog Browsing
```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant FE as Frontend
    participant GW as API Gateway
    participant PS as Product Service
    participant PDB as Product DB

    User->>FE: Open Catalog View
    FE->>GW: GET /api/products?skip=0&limit=50
    Note over GW: Injects/Adopts X-Request-ID<br/>Starts stopwatch
    GW->>PS: GET /products?skip=0&limit=50 (Header: X-Request-ID)
    PS->>PDB: SELECT * FROM products ORDER BY id ASC LIMIT 50
    PDB-->>PS: Return product records
    PS-->>GW: 200 OK [ProductListResponse]
    Note over GW: Logs request duration_ms
    GW-->>FE: 200 OK [ProductListResponse]
    FE-->>User: Render Product Grid
```

### Flow B: Order Placement & Cross-Service Coordination
```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant FE as Frontend
    participant GW as API Gateway
    participant OS as Order Service
    participant PS as Product Service
    participant ODB as Order DB

    User->>FE: Click "Place Order Now"
    FE->>GW: POST /api/orders {"items": [{"product_id": 1, "quantity": 2}]}
    Note over GW: Generates X-Request-ID: abc-123<br/>Applies 5.0s timeout
    GW->>OS: POST /orders (Header: X-Request-ID: abc-123)
    Note over OS: Receives request, initiates OrderService
    
    OS->>PS: GET /products/1/availability?quantity=2 (Header: X-Request-ID: abc-123, Timeout: 2.5s)
    alt Product Available
        PS-->>OS: 200 OK {"available": true, "price": 39.99, "name": "K8s Guide"}
        Note over OS: Calculates total: 2 * 39.99 = 79.98
        OS->>ODB: INSERT INTO orders ... INSERT INTO order_items ...
        ODB-->>OS: Commit successful
        OS-->>GW: 201 Created {"id": 101, "status": "CONFIRMED", "total": 79.98}
        GW-->>FE: 201 Created {"id": 101, "status": "CONFIRMED", "total": 79.98}
        FE-->>User: Show Success Notification
    else Product Out of Stock
        PS-->>OS: 200 OK {"available": false, "current_stock": 1}
        OS-->>GW: 409 Conflict {"error": {"code": "INSUFFICIENT_STOCK"}}
        GW-->>FE: 409 Conflict [Standardized Error]
        FE-->>User: Render Error Banner: "Insufficient inventory"
    else Product Service Down / Slow (Incident)
        PS--xOS: Connection Refused or Timeout > 2.5s
        Note over OS: Catches TimeoutException<br/>Logs structured error
        OS-->>GW: 504 Gateway Timeout {"error": {"code": "PRODUCT_SERVICE_TIMEOUT"}}
        GW-->>FE: 504 Gateway Timeout [Standardized Error]
        FE-->>User: Render Diagnostic Incident Banner
    end
```

---

## 5. Configuration Flow & Environment Decoupling

Configuration follows the 12-Factor App methodology. No hostnames, ports, or credentials are hardcoded into application source code.

```mermaid
flowchart LR
    subgraph Config_Sources ["Configuration Sources"]
        CM["Kubernetes ConfigMap<br/>(kubeshop-config)"]
        SEC["Kubernetes Secret<br/>(kubeshop-secrets)"]
        ENV[".env / Environment Variables"]
    end

    subgraph Service_Runtime ["Application Runtime"]
        CFG["Pydantic BaseSettings<br/>(core/config.py)"]
        APP["Application Logic"]
    end

    CM -->|Injected as Env| CFG
    SEC -->|Injected as Env| CFG
    ENV -->|Injected as Env| CFG
    CFG -->|Type-validated settings| APP
```

---

## 6. Failure Domains & Blast Radius Isolation

| Failure Event | Affected Components | Unaffected Components | Recovery Mechanism |
| :--- | :--- | :--- | :--- |
| **Product DB Crash** | Product Service `/ready` probe; Catalog browsing; New order placement. | Frontend remains online; Order Service process remains alive; Order history retrieval remains functional. | Kubernetes unroutes traffic from Product Service until DB reconnects. |
| **Product Service Crash** | Catalog browsing; New order placement. | Order history viewing; Frontend UI; Postgres database. | Kubernetes kubelet restarts Product Service container (livenessProbe). |
| **Order DB Crash** | Order Service `/ready` probe; Order placement; Order history. | Product catalog browsing remains 100% operational. | Kubernetes unroutes traffic from Order Service until DB reconnects. |
| **Gateway Crash** | External API ingress temporarily degraded. | Backend microservices and databases continue running normally. | Kubernetes rolls traffic to secondary Gateway replica. |
