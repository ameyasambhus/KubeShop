#!/usr/bin/env bash
# ==============================================================================
# KubeShop - Prerequisites Checker
# ==============================================================================
# This script inspects the host environment to verify required runtimes
# and tools for running KubeShop locally, in Docker, or in Kubernetes.
# ==============================================================================

set -e

echo "=== Checking KubeShop Prerequisites ==="

check_tool() {
    local tool=$1
    local name=$2
    local required=$3
    if command -v "$tool" >/dev/null 2>&1; then
        local version
        version=$("$tool" --version 2>&1 | head -n 1)
        echo " [OK] $name: $version"
    else
        if [ "$required" = "true" ]; then
            echo " [MISSING] $name (REQUIRED) - Please install $tool"
        else
            echo " [OPTIONAL] $name (Optional for initial local dev, needed for K8s) - Not found"
        fi
    fi
}

echo ""
echo "-- Core Development Runtimes --"
check_tool python3 "Python (Backend)" true
check_tool node "Node.js (Frontend)" true
check_tool npm "NPM (Package Manager)" true

echo ""
echo "-- Container & Orchestration Tools --"
check_tool docker "Docker Engine" false
check_tool kubectl "Kubernetes CLI (kubectl)" false
check_tool minikube "Minikube (Local K8s)" false
check_tool kind "KinD (Kubernetes in Docker)" false

echo ""
echo "=== Check Complete ==="
