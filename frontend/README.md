# Frontend Application

## Purpose
The **Frontend** is the user-facing web interface for KubeShop. It is built as a single-page application (SPA) using React 18 and TypeScript. It enables browsing products, searching items, managing a cart, and placing orders.

---

## Responsibilities
- Render the product catalog, pricing, and stock levels.
- Provide full-text search filtering over products.
- Allow users to build a shopping cart and specify item quantities.
- Submit customer orders to the API Gateway.
- Render historical customer orders and line item summaries.
- Intercept and display rich, understandable error banners when microservices fail (showing `code`, `dependency`, and `request_id`).

---

## What Does NOT Belong Here?
- **No Direct Database Access**: The frontend NEVER connects to PostgreSQL.
- **No Internal Service Calls**: The frontend NEVER calls `product-service` or `order-service` directly. All network requests target the API Gateway (`/api/*`).
- **No Business Logic Validation**: Pricing calculations and inventory guarantees occur strictly on the backend.

---

## Folder Structure
```
frontend/
├── Dockerfile                   # Multi-stage Docker build (Node.js build -> Nginx runtime)
├── README.md                    # This frontend guide
├── package.json                 # Node dependencies and build scripts
├── tsconfig.json                # TypeScript compiler configuration
├── vite.config.ts               # Vite bundler & local dev server proxy settings
├── nginx.conf                   # Production Nginx reverse-proxy configuration
├── index.html                   # HTML document root
└── src/
    ├── main.tsx                 # DOM mounting entry point
    ├── App.tsx                  # Top-level view switcher and state management
    ├── api/
    │   └── client.ts            # Type-safe API client communicating with /api
    ├── components/
    │   ├── Navbar.tsx           # Navigation bar with cart badge
    │   ├── ProductCard.tsx      # Catalog item card with stock indicator
    │   └── ErrorBanner.tsx      # Diagnostic alert banner for microservice incidents
    ├── pages/
    │   ├── CatalogPage.tsx      # Product listing & search
    │   ├── CheckoutModal.tsx    # Cart review & order placement modal
    │   └── OrdersPage.tsx       # Historical order list
    └── types/
        └── index.ts             # TypeScript interfaces for API models
```

---

## Important Files
- `src/api/client.ts`: Wraps browser `fetch` calls, handles network failures, and extracts the standardized microservice error envelope (`ApiError`).
- `src/components/ErrorBanner.tsx`: Visual component that renders structured incident metadata (`code`, `message`, `dependency`, `request_id`) so students can observe failure propagation in real time.
- `src/App.tsx`: Manages active views (`catalog` vs `orders`) and global cart state.
- `nginx.conf`: Configures Nginx to serve the SPA on port 3000 and proxy `/api/*` requests to `http://api-gateway:8000/api/`.

---

## Startup Flow
- **Development (Vite)**:
  `npm run dev` starts the Vite development server on port 3000 and automatically proxies `/api` calls to `http://localhost:8000`.
- **Production (Docker / K8s)**:
  Nginx starts on port 3000, serving compiled static assets from `/usr/share/nginx/html` and proxying `/api` calls to `http://api-gateway:8000`.

---

## Dependencies
- **API Gateway**: Sole backend dependency for all data operations (`http://localhost:8000` or `http://api-gateway:8000`).
- **Node.js 20+**: Build-time tooling.

---

## Environment Variables
| Variable | Purpose | Required? | Example Local Value | Default |
| :--- | :--- | :--- | :--- | :--- |
| `VITE_API_GATEWAY_URL` | API Gateway endpoint target during local Vite dev | No | `http://localhost:8000` | `http://localhost:8000` |

---

## Running the Frontend Locally
```bash
cd frontend
npm install
npm run dev
# Open browser at http://localhost:3000
```

---

## Building & Verification
```bash
cd frontend
npm run build
```

---

## Docker
Build the container:
```bash
docker build -t kubeshop/frontend:latest -f frontend/Dockerfile frontend/
```
Run the container:
```bash
docker run -p 3000:3000 kubeshop/frontend:latest
```

---

## Kubernetes Mapping
- **Deployment**: `infrastructure/kubernetes/frontend/deployment.yaml` (runs Nginx serving SPA).
- **Service**: `infrastructure/kubernetes/frontend/service.yaml` (NodePort / ClusterIP exposing port 3000).
- **Probes**: `/health` endpoint configured on Nginx returning 200.

---

## Failure Behavior
- **API Gateway Down**: Red warning banner displays: `[NETWORK_FAILURE] Failed to communicate with API Gateway`.
- **Product Service Down**: Banner displays: `[SERVICE_UNREACHABLE] Unable to connect to downstream service 'product-service'`.
- **Order Service Down during Checkout**: Banner displays: `[SERVICE_UNREACHABLE] Unable to connect to downstream service 'order-service'`.
- **Product Out of Stock**: Banner displays: `[INSUFFICIENT_STOCK] Insufficient inventory`.
