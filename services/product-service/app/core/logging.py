"""Structured JSON logging configuration for Product Service."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variable to store correlation ID across async task execution
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter producing structured log entries for cloud-native ingestion."""

    def __init__(self, service_name: str = "product-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Include request ID if present in async context
        req_id = request_id_ctx.get()
        if req_id:
            log_entry["request_id"] = req_id

        # Include any extra attributes passed via extra={}
        if hasattr(record, "request_id") and record.request_id:
            log_entry["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "path"):
            log_entry["path"] = record.path
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "dependency"):
            log_entry["dependency"] = record.dependency
        if hasattr(record, "dependency_url"):
            log_entry["dependency_url"] = record.dependency_url
        if hasattr(record, "error_type"):
            log_entry["error_type"] = record.error_type

        # Include exception info if logged
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logger(service_name: str = "product-service", log_level: str = "INFO") -> logging.Logger:
    """Configures the root logger with the structured JSON formatter."""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicate log entries
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter(service_name=service_name))
    logger.addHandler(handler)

    # Prevent propagation to avoid unformatted default root output
    logger.propagate = False
    return logger
