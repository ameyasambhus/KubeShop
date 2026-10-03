#!/usr/bin/env python3
"""Script to seed additional sample products into KubeShop via the API Gateway."""

import sys
import httpx

GATEWAY_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

SAMPLE_PRODUCTS = [
    {
        "name": "Kubernetes Production Patterns",
        "description": "Architecting resilient distributed systems on cloud clusters.",
        "price": 49.99,
        "stock": 25,
    },
    {
        "name": "Chaos Engineering in Practice",
        "description": "Controlled failure injection, game days, and automated resilience testing.",
        "price": 44.50,
        "stock": 30,
    },
    {
        "name": "Cloud Native Logging Guide",
        "description": "Mastering fluentd, promtail, log aggregation, and structured JSON parsing.",
        "price": 34.00,
        "stock": 40,
    },
]


def seed():
    print(f"Connecting to API Gateway at: {GATEWAY_URL}")
    for item in SAMPLE_PRODUCTS:
        try:
            resp = httpx.post(f"{GATEWAY_URL}/api/products", json=item, timeout=5.0)
            if resp.status_code == 201:
                print(f" [OK] Seeded: {item['name']} (ID: {resp.json().get('id')})")
            else:
                print(f" [SKIP/FAIL] {item['name']} -> HTTP {resp.status_code}: {resp.text}")
        except Exception as exc:
            print(f" [ERROR] Could not connect: {exc}")
            break


if __name__ == "__main__":
    seed()
