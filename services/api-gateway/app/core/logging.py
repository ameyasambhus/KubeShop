"""Structured JSON logging configuration for API Gateway."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON with correlation ID and downstream metadata."""

    def __init__(self, service_name: str = "api-gateway"):
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

        req_id = request_id_ctx.get()
        if req_id:
            log_entry["request_id"] = req_id

        for attr in ["request_id", "method", "path", "status_code", "duration_ms", "dependency", "dependency_url", "error_type"]:
            if hasattr(record, attr) and getattr(record, attr) is not None:
                log_entry[attr] = getattr(record, attr)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logger(service_name: str = "api-gateway", log_level: str = "INFO") -> logging.Logger:
    """Configures root logger with JSONFormatter."""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter(service_name=service_name))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
