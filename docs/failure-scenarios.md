# KubeShop Incident Drills & Failure Scenarios

This document provides step-by-step procedures for intentionally triggering, observing, diagnosing, and remediating 12 realistic production microservice incidents.

> [!CAUTION]
> These drills are intended for local test clusters (Minikube / KinD). Never perform destructive fault injection in production environments without authorization.

---

## Template for Failure Analysis

Each incident drill is documented using a standardized structure:
1. **What we intentionally break**
2. **Expected user-visible symptom**
3. **Expected Kubernetes symptom**
4. **What to inspect (`kubectl` commands)**
5. **Expected evidence**
6. **Root cause**
7. **Recovery procedure**
8. **Concepts learned**

---

## Scenario A — Abrupt Process Crash

### 1. What we intentionally break
Kill the active process inside a Product Service Pod using the development crash hook or `pkill`.

### 2. How to trigger
```bash
# Obtain product-service pod name
POD=$(kubectl get pods -n kubeshop -l app=product-service -o jsonpath='{.items[0].metadata.name}')
# Trigger crash endpoint
kubectl exec -it $POD -n kubeshop -- python -c "import os, signal; os.kill(os.getpid(), signal.SIGKILL)"
```

### 3. Expected user-visible symptom
One or two in-flight requests to `/api/products` may return `502 Bad Gateway`. Subsequent requests succeed immediately via the secondary replica.

### 4. Expected Kubernetes symptom
Pod restart count increments (`RESTARTS: 1`). Pod status temporarily transitions from `Running` to `Error` / `Completed` before returning to `Running`.

### 5. What to inspect
```bash
kubectl get pods -n kubeshop -l app=product-service
kubectl describe pod $POD -n kubeshop
kubectl logs $POD -n kubeshop --previous
kubectl get events -n kubeshop --sort-by=.metadata.creationTimestamp
```

### 6. Expected evidence
- `kubectl describe pod`: Shows `Last State: Terminated` with `Exit Code: 137` (SIGKILL).
- Event: `Killing container with id ... Backing off restarting failed container` if repeated.

### 7. Root cause
Container PID 1 terminated abnormally.

### 8. Recovery
The kubelet detects process termination and restarts the container according to `restartPolicy: Always`.

### 9. Concepts learned
Pod lifecycle, restart policies, container exit codes (137 = SIGKILL), replica fault tolerance.

---

## Scenario B — CrashLoopBackOff

### 1. What we intentionally break
Inject an invalid syntax database URL into the Product Service deployment environment.

### 2. How to trigger
```bash
kubectl set env deployment/product-service -n kubeshop PRODUCT_DATABASE_URL="invalid://syntax:bad"
```

### 3. Expected user-visible symptom
Product catalog browsing returns persistent `502 Bad Gateway` from the API Gateway.

### 4. Expected Kubernetes symptom
Pods enter `CrashLoopBackOff`. The restart count increases exponentially while restart backoff delay doubles (10s, 20s, 40s, up to 5m).

### 5. What to inspect
```bash
kubectl get pods -n kubeshop -l app=product-service
kubectl describe pod -l app=product-service -n kubeshop
kubectl logs -l app=product-service -n kubeshop --previous
```

### 6. Expected evidence
- Pod Status: `CrashLoopBackOff`.
- Logs show SQLAlchemy configuration error: `NoSuchModuleError` or `ArgumentError: Could not parse DSN`.

### 7. Root cause
Startup lifespan fails to connect to database; unhandled exception during initialization terminates container before it can accept traffic.

### 8. Recovery
Restore the valid database URL:
```bash
kubectl set env deployment/product-service -n kubeshop PRODUCT_DATABASE_URL-
```

### 9. Concepts learned
Application lifespan errors, kubelet exponential backoff algorithm, config validation.

---

## Scenario C — Readiness Failure (Pod Alive, Traffic Unrouted)

### 1. What we intentionally break
Set the simulated readiness toggle to `true` on one Product Service pod.

### 2. How to trigger
```bash
POD=$(kubectl get pods -n kubeshop -l app=product-service -o jsonpath='{.items[0].metadata.name}')
# Port-forward to pod directly
kubectl port-forward $POD -n kubeshop 8001:8001 &
PF_PID=$!
sleep 1
curl -X POST "http://localhost:8001/dev/faults/readiness-toggle?unready=true"
kill $PF_PID
```

### 3. Expected user-visible symptom
No user visible errors! Traffic seamlessly routes to the second replica.

### 4. Expected Kubernetes symptom
Pod remains `Running`, but `READY` changes from `1/1` to `0/1`. The Pod's IP is automatically removed from the `product-service` Service `Endpoints`.

### 5. What to inspect
```bash
kubectl get pods -n kubeshop -l app=product-service
kubectl get endpoints product-service -n kubeshop
kubectl describe pod $POD -n kubeshop
```

### 6. Expected evidence
- `kubectl get endpoints`: Shows only 1 IP address under `Subsets.Addresses`, and the unready Pod IP under `Subsets.NotReadyAddresses`.
- Pod events show: `Warning Unhealthy Readiness probe failed: HTTP probe failed with statuscode: 503`.

### 7. Root cause
Readiness probe returned HTTP 503.

### 8. Recovery
```bash
kubectl port-forward $POD -n kubeshop 8001:8001 &
PF_PID=$!
sleep 1
curl -X POST "http://localhost:8001/dev/faults/readiness-toggle?unready=false"
kill $PF_PID
```

### 9. Concepts learned
Difference between liveness (process death) and readiness (traffic routing), Service endpoints controller.

---

## Scenario D — Liveness Failure (Process Deadlock)

### 1. What we intentionally break
Make the `/health` endpoint unresponsive by altering probe configuration to point to an invalid port or path.

### 2. How to trigger
```bash
kubectl patch deployment product-service -n kubeshop --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/httpGet/path", "value": "/healthz-broken"}]'
```

### 3. Expected user-visible symptom
Intermittent 502 errors as replicas are killed and recreated.

### 4. Expected Kubernetes symptom
Kubelet restarts the container every 30 seconds due to failed liveness checks.

### 5. What to inspect
```bash
kubectl describe pod -l app=product-service -n kubeshop
kubectl get events -n kubeshop | grep Unhealthy
```

### 6. Expected evidence
Event: `Warning Unhealthy Liveness probe failed: HTTP probe failed with statuscode: 404`.

### 7. Root cause
Liveness probe path does not return 200-399 status.

### 8. Recovery
```bash
kubectl rollout undo deployment/product-service -n kubeshop
```

### 9. Concepts learned
Liveness probe enforcement, self-healing thresholds, rollout undo.

---

## Scenario E — Database Outage

### 1. What we intentionally break
Stop the PostgreSQL container.

### 2. How to trigger
```bash
kubectl scale deployment/postgres -n kubeshop --replicas=0
```

### 3. Expected user-visible symptom
Product catalog displays error banner: `[DATABASE_UNAVAILABLE] Unable to connect to database`. Placing orders fails.

### 4. Expected Kubernetes symptom
Both `product-service` and `order-service` pods transition to `READY 0/1` as their `/ready` probes fail with 503.

### 5. What to inspect
```bash
kubectl get endpoints -n kubeshop
kubectl logs -l app=product-service -n kubeshop --tail=20
```

### 6. Expected evidence
Logs show `asyncpg.exceptions.CannotConnectNowError` or connection refused to `postgres-service:5432`.

### 7. Root cause
Database pod terminated; port 5432 unreachable.

### 8. Recovery
```bash
kubectl scale deployment/postgres -n kubeshop --replicas=1
kubectl wait --for=condition=ready pod -l app=postgres -n kubeshop --timeout=60s
```

### 9. Concepts learned
Cascading readiness failure, infrastructure dependency degradation.

---

## Scenario F — Product Service Unavailable (Dependency Outage)

### 1. What we intentionally break
Scale Product Service to 0 replicas while Order Service remains alive.

### 2. How to trigger
```bash
kubectl scale deployment/product-service -n kubeshop --replicas=0
```

### 3. Expected user-visible symptom
Product catalog displays: `[SERVICE_UNREACHABLE] Unable to connect to product-service`.
Attempting to create an order displays: `[PRODUCT_SERVICE_UNAVAILABLE] Unable to reach Product Service`.
However, customer can still load historical orders!

### 4. Expected Kubernetes symptom
`product-service` has 0 pods. `order-service` remains `Running` and `Ready (1/1)`.

### 5. What to inspect
```bash
kubectl logs -l app=order-service -n kubeshop | grep "dependency"
```

### 6. Expected evidence
Order Service structured JSON logs show:
`{"level": "ERROR", "dependency": "product-service", "error_type": "ConnectError"}`

### 7. Root cause
Upstream dependency (`product-service`) has no available endpoints.

### 8. Recovery
```bash
kubectl scale deployment/product-service -n kubeshop --replicas=2
```

### 9. Concepts learned
Downstream dependency isolation, graceful degradation vs whole-system crash.

---

## Scenario G — Slow Downstream Latency & Timeouts

### 1. What we intentionally break
Inject artificial delay of 3000ms (3.0s) into Product Service via ConfigMap. Order Service has a 2.5s client timeout.

### 2. How to trigger
```bash
kubectl patch configmap kubeshop-config -n kubeshop -p '{"data": {"SIMULATED_LATENCY_MS": "3000"}}'
kubectl rollout restart deployment/product-service -n kubeshop
```

### 3. Expected user-visible symptom
Submitting an order takes ~2.5 seconds and fails with:
`[PRODUCT_SERVICE_TIMEOUT] Product Service failed to respond within 2.5 seconds`.

### 4. Expected Kubernetes symptom
Pods remain healthy (`1/1 Ready`), but request latencies spike dramatically.

### 5. What to inspect
```bash
kubectl logs -l app=order-service -n kubeshop | grep "TimeoutException"
```

### 6. Expected evidence
Order Service logs show:
`"duration_ms": 2502.4, "error_type": "TimeoutException", "dependency": "product-service"`

### 7. Root cause
Product Service latency (3000ms) exceeded the caller's timeout budget (2500ms).

### 8. Recovery
```bash
kubectl patch configmap kubeshop-config -n kubeshop -p '{"data": {"SIMULATED_LATENCY_MS": "0"}}'
kubectl rollout restart deployment/product-service -n kubeshop
```

### 9. Concepts learned
Cascading latency, timeout budgets, distributed tail-latency debugging.

---

## Scenario H — CPU Saturation & Throttling

### 1. What we intentionally break
Trigger continuous compute loops under container `limits: { cpu: 300m }`.

### 2. How to trigger
```bash
POD=$(kubectl get pods -n kubeshop -l app=product-service -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD -n kubeshop 8001:8001 &
PF_PID=$!
sleep 1
curl -X POST "http://localhost:8001/dev/faults/cpu-burn?duration_seconds=20" &
kill $PF_PID
```

### 3. Expected user-visible symptom
Catalog response times degrade from ~10ms to >1500ms.

### 4. Expected Kubernetes symptom
Linux kernel CFS (Completely Fair Scheduler) enforces CPU quota throttling.

### 5. What to inspect
```bash
kubectl top pod -n kubeshop
kubectl describe pod $POD -n kubeshop
```

### 6. Expected evidence
CPU usage hits 300m limit.

### 7. Root cause
Workload attempted to consume more CPU than allowed by container limits.

### 8. Recovery
CPU burn finishes automatically after duration. If permanent, adjust `resources.limits.cpu` in deployment.

### 9. Concepts learned
CFS throttling, CPU requests vs limits, latency correlation with CPU saturation.

---

## Scenario I — Memory Pressure & OOMKilled

### 1. What we intentionally break
Allocate 300MB of RAM inside a container with `limits: { memory: 256Mi }`.

### 2. How to trigger
```bash
POD=$(kubectl get pods -n kubeshop -l app=product-service -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD -n kubeshop 8001:8001 &
PF_PID=$!
sleep 1
curl -X POST "http://localhost:8001/dev/faults/memory-burn?mb=300"
kill $PF_PID
```

### 3. Expected user-visible symptom
In-flight request abruptly drops with `Connection reset by peer` or `502 Bad Gateway`.

### 4. Expected Kubernetes symptom
Container is killed immediately by Linux kernel OOM (Out Of Memory) killer. Pod restarts.

### 5. What to inspect
```bash
kubectl describe pod $POD -n kubeshop
kubectl get events -n kubeshop | grep OOMKilled
```

### 6. Expected evidence
- `kubectl describe pod`: Shows `Last State: Terminated`, `Reason: OOMKilled`, `Exit Code: 137`.

### 7. Root cause
Container allocated memory in excess of the cgroup hard limit (256Mi).

### 8. Recovery
Kubelet automatically restarts container with fresh memory space.

### 9. Concepts learned
Cgroup memory limits, kernel OOM Killer, sizing memory requests vs limits.

---

## Scenario J — Misconfigured Service Discovery DNS

### 1. What we intentionally break
Set `PRODUCT_SERVICE_URL` in ConfigMap to a non-existent hostname.

### 2. How to trigger
```bash
kubectl patch configmap kubeshop-config -n kubeshop -p '{"data": {"PRODUCT_SERVICE_URL": "http://wrong-product-dns:8000"}}'
kubectl rollout restart deployment/order-service -n kubeshop
```

### 3. Expected user-visible symptom
Order creation fails with `[SERVICE_UNREACHABLE] Unable to connect to downstream service 'product-service'`.

### 4. Expected Kubernetes symptom
Order Service pod runs normally, but CoreDNS lookups for `wrong-product-dns` fail with NXDOMAIN.

### 5. What to inspect
```bash
kubectl logs -l app=order-service -n kubeshop | grep "NameResolutionError"
```

### 6. Expected evidence
Logs: `gaierror: [Errno -2] Name or service not known` or `NameResolutionError`.

### 7. Root cause
CoreDNS cannot resolve `wrong-product-dns`.

### 8. Recovery
```bash
kubectl patch configmap kubeshop-config -n kubeshop -p '{"data": {"PRODUCT_SERVICE_URL": "http://product-service:8000"}}'
kubectl rollout restart deployment/order-service -n kubeshop
```

### 9. Concepts learned
Kubernetes CoreDNS architecture, environment variable propagation.

---

## Scenario K — Replica Deletion Under Traffic

### 1. What we intentionally break
Manually delete a running Pod while user traffic is flowing.

### 2. How to trigger
```bash
POD=$(kubectl get pods -n kubeshop -l app=product-service -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD -n kubeshop
```

### 3. Expected user-visible symptom
Zero downtime! All requests are serviced by the remaining replica.

### 4. Expected Kubernetes symptom
Deleted Pod enters `Terminating` and is removed from endpoints. ReplicaSet immediately launches a replacement Pod.

### 5. What to inspect
```bash
kubectl get pods -n kubeshop -l app=product-service -w
```

### 6. Expected evidence
A new Pod with a distinct random hash suffix appears in `ContainerCreating` -> `Running` within seconds.

### 7. Root cause
Manual deletion triggers reconciliation loop in ReplicaSet controller.

### 8. Recovery
Automatic self-healing via Kubernetes ReplicaSet.

### 9. Concepts learned
Declarative state management, ReplicaSet reconciliation loops.

---

## Scenario L — Bad Deployment Rollout (`ImagePullBackOff`)

### 1. What we intentionally break
Update the Order Service image to a tag that does not exist (`v99.9.9`).

### 2. How to trigger
```bash
kubectl set image deployment/order-service order-service=kubeshop/order-service:v99.9.9 -n kubeshop
```

### 3. Expected user-visible symptom
Zero downtime! Existing Order Service replicas continue serving traffic without disruption.

### 4. Expected Kubernetes symptom
Deployment rollout stalls. New Pod gets stuck in `ImagePullBackOff`. Because of `maxUnavailable: 0`, old Pods are NOT terminated!

### 5. What to inspect
```bash
kubectl rollout status deployment/order-service -n kubeshop
kubectl get pods -n kubeshop -l app=order-service
```

### 6. Expected evidence
- `kubectl rollout status`: `Waiting for deployment "order-service" rollout to finish: 1 out of 2 new replicas have been updated...`
- `kubectl describe pod`: `Failed to pull image "kubeshop/order-service:v99.9.9": rpc error: not found`.

### 7. Root cause
Image registry cannot locate requested tag.

### 8. Recovery
Roll back the deployment:
```bash
kubectl rollout undo deployment/order-service -n kubeshop
```

### 9. Concepts learned
Rolling update safety margins (`maxSurge` / `maxUnavailable`), zero-downtime deployments, `kubectl rollout undo`.
