#!/usr/bin/env bash
# ==============================================================================
# Smoke-testing script that curls live endpoints to verify connectivity
# ==============================================================================

set -e

GW_URL=${1:-"http://localhost:8000"}
FE_URL=${2:-"http://localhost:3000"}

echo "=== Verifying Live KubeShop Endpoints ==="
echo "Target Gateway: $GW_URL"
echo "Target Frontend: $FE_URL"
echo ""

check_http() {
    local url=$1
    local name=$2
    local expected_code=$3
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    if [ "$code" = "$expected_code" ]; then
        echo " [OK] $name: HTTP $code"
    else
        echo " [FAIL] $name: Expected HTTP $expected_code but got $code ($url)"
    fi
}

echo "-- Health & Readiness Probes --"
check_http "$GW_URL/health" "Gateway Liveness" "200"
check_http "$GW_URL/ready" "Gateway Readiness" "200"

echo ""
echo "-- Business API Routes --"
check_http "$GW_URL/api/products" "Catalog List" "200"
check_http "$GW_URL/api/orders" "Orders List" "200"

echo ""
echo "-- Presentation Layer --"
check_http "$FE_URL/health" "Frontend Liveness" "200"
check_http "$FE_URL" "Frontend UI HTML" "200"

echo ""
echo "=== Endpoint Verification Complete ==="
