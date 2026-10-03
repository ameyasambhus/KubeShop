#!/usr/bin/env bash
# ==============================================================================
# Helper script to export local development environment variables
# Usage: source scripts/setup/local_env.sh
# ==============================================================================

if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env found. Copying .env.example to .env..."
    cp .env.example .env
    export $(grep -v '^#' .env | xargs)
fi

echo "Environment variables loaded successfully for KubeShop."
