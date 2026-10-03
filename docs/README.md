# KubeShop Documentation Library

Welcome to the comprehensive documentation suite for **KubeShop**, a production-style microservices application designed for learning Kubernetes, cloud-native architecture, observability, and incident diagnostics.

---

## Documentation Index

| Guide | Description | Target Audience |
| :--- | :--- | :--- |
| **[architecture.md](file:///Users/ameya/Developer/KubeShop/docs/architecture.md)** | Deep architectural breakdown, data ownership, request flow sequence diagrams, and service boundaries. | All Engineers & Architects |
| **[codebase-guide.md](file:///Users/ameya/Developer/KubeShop/docs/codebase-guide.md)** | "Where do I find...?" quick reference, file navigation map, and code reading order. | Developers & Maintainers |
| **[services.md](file:///Users/ameya/Developer/KubeShop/docs/services.md)** | OpenAPI endpoint catalog, schemas, request/response contracts, and error structures. | Frontend & Backend Engineers |
| **[local-development.md](file:///Users/ameya/Developer/KubeShop/docs/local-development.md)** | Guide to running and debugging services independently on your local machine without containers. | Developers |
| **[kubernetes.md](file:///Users/ameya/Developer/KubeShop/docs/kubernetes.md)** | Mapping of KubeShop application concepts to Kubernetes resources (Deployments, Services, ConfigMaps, PVCs, Probes). | DevOps & K8s Learners |
| **[observability.md](file:///Users/ameya/Developer/KubeShop/docs/observability.md)** | Structured JSON logging specifications, `X-Request-ID` correlation, and `/health` vs `/ready` probe mechanics. | SREs & Observability Learners |
| **[failure-scenarios.md](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md)** | Step-by-step incident drills (CrashLoopBackOff, readiness failure, dependency failure, latency injection, OOMKilled). | SREs & Incident Responders |
| **[handover.md](file:///Users/ameya/Developer/KubeShop/docs/handover.md)** | Complete implementation status, architectural summary, known limitations, and next steps. | Project Reviewers & Evaluators |

---

## Recommended Reading Path for Newcomers

1. Start with the root **[README.md](file:///Users/ameya/Developer/KubeShop/README.md)** for a 5-minute system overview.
2. Read **[architecture.md](file:///Users/ameya/Developer/KubeShop/docs/architecture.md)** to understand how services communicate and where data lives.
3. Review **[codebase-guide.md](file:///Users/ameya/Developer/KubeShop/docs/codebase-guide.md)** to understand folder conventions and code navigation.
4. Deep dive into individual service READMEs:
   - [frontend/README.md](file:///Users/ameya/Developer/KubeShop/frontend/README.md)
   - [services/api-gateway/README.md](file:///Users/ameya/Developer/KubeShop/services/api-gateway/README.md)
   - [services/product-service/README.md](file:///Users/ameya/Developer/KubeShop/services/product-service/README.md)
   - [services/order-service/README.md](file:///Users/ameya/Developer/KubeShop/services/order-service/README.md)
5. Read **[kubernetes.md](file:///Users/ameya/Developer/KubeShop/docs/kubernetes.md)** before deploying to a local cluster.
6. Explore **[failure-scenarios.md](file:///Users/ameya/Developer/KubeShop/docs/failure-scenarios.md)** to run controlled production incident drills.
