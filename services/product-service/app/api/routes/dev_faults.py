"""Development-only fault injection endpoints for controlled Kubernetes incident drills."""

import os
import signal
import sys
import time
from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from app.api.routes import health
from app.core.config import settings

router = APIRouter(prefix="/dev/faults", tags=["Fault Simulation (Dev Only)"])

# Module-level variable to hold allocated memory for OOM testing
_memory_leak_holder: List[bytes] = []


def _ensure_dev_environment():
    """Safety guard: prevents fault endpoints from functioning outside development."""
    if settings.APP_ENV != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fault injection endpoints are disabled outside the development environment.",
        )


@router.post("/crash")
def simulate_crash():
    """Simulates an abrupt process crash (Scenario A).

    Terminates the Python process with exit code 1 to test Kubernetes pod restart and CrashLoopBackOff.
    """
    _ensure_dev_environment()
    # Schedule exit after brief delay so client receives response
    pid = os.getpid()
    os.kill(pid, signal.SIGKILL)
    return {"message": "Crashing process"}


@router.post("/readiness-toggle")
def toggle_readiness(unready: bool = Query(..., description="Set to true to fail readiness probe")):
    """Toggles readiness probe failure without killing the container (Scenario C).

    Demonstrates how Kubernetes removes unready pods from Service endpoints while keeping them alive.
    """
    _ensure_dev_environment()
    health.SIMULATED_UNREADY = unready
    return {
        "message": f"Readiness probe failure set to {unready}",
        "simulated_unready": health.SIMULATED_UNREADY,
    }


@router.post("/cpu-burn")
def burn_cpu(duration_seconds: int = Query(5, ge=1, le=30, description="Seconds to consume 100% CPU")):
    """Generates continuous CPU load to test Kubernetes CPU limits and throttling (Scenario H)."""
    _ensure_dev_environment()
    start_time = time.time()
    # Busy-wait compute loop
    while time.time() - start_time < duration_seconds:
        _ = [x**2 for x in range(1000)]
    return {"message": f"Consumed CPU for {duration_seconds} seconds"}


@router.post("/memory-burn")
def burn_memory(mb: int = Query(50, ge=10, le=1000, description="Megabytes of memory to allocate")):
    """Allocates memory to exceed container limits and test OOMKilled behavior (Scenario I)."""
    _ensure_dev_environment()
    # Allocate byte chunks of 1MB each
    chunk = b"x" * (1024 * 1024)
    for _ in range(mb):
        _memory_leak_holder.append(chunk)
    return {
        "message": f"Allocated {mb} MB of memory",
        "total_allocated_mb": len(_memory_leak_holder),
    }
