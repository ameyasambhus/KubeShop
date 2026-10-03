#!/usr/bin/env bash
# ==============================================================================
# Executes backend test suites across all KubeShop microservices
# ==============================================================================

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

echo "=================================================="
echo " Running Product Service Test Suite"
echo "=================================================="
cd "$REPO_ROOT/services/product-service"
pytest -v

echo ""
echo "=================================================="
echo " Running Order Service Test Suite"
echo "=================================================="
cd "$REPO_ROOT/services/order-service"
pytest -v

echo ""
echo "=================================================="
echo " Running API Gateway Test Suite"
echo "=================================================="
cd "$REPO_ROOT/services/api-gateway"
pytest -v

echo ""
echo "=================================================="
echo " Testing Frontend Production Build"
echo "=================================================="
cd "$REPO_ROOT/frontend"
npm run build

echo ""
echo "=================================================="
echo " ✅ ALL SERVICE TEST SUITES & BUILDS PASSED!"
echo "=================================================="
