from __future__ import annotations

import logging
import time
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Format Stagger Step records for multiline-aware log forwarders."""

    def formatTime(
        self, record: logging.LogRecord, datefmt: str | None = None
    ) -> str:
        return time.strftime(
            datefmt or "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
        )

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        header = (
            f"{record.name}.{record.funcName}:{record.lineno} "
            f"[{self.formatTime(record, self.datefmt)}] "
            f"{record.levelname}: {message}"
        )
        sections = [header]
        body = getattr(record, "body", None)
        if body is not None:
            sections.append(body)
        if record.exc_info:
            sections.append(self.formatException(record.exc_info))
        if record.stack_info:
            sections.append(self.formatStack(record.stack_info))
        return "\n".join(sections)


def log_record(
    logger: logging.Logger,
    level: int,
    summary: str,
    *args: object,
    body: str | None = None,
    **kwargs: Any,
) -> None:
    """Emit one structured record with an optional raw multiline body."""
    extra = dict(kwargs.pop("extra", {}) or {})
    if body is not None:
        extra["body"] = body
    logger.log(level, summary, *args, extra=extra, **kwargs)


class StructuredLogger:
    """Use one record-emission interface for Stagger Step logging."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def is_enabled_for(self, level: int) -> bool:
        return self._logger.isEnabledFor(level)

    def log(
        self,
        level: int,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 3)
        log_record(self._logger, level, summary, *args, body=body, **kwargs)

    def debug(
        self,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 4)
        self.log(logging.DEBUG, summary, *args, body=body, **kwargs)

    def info(
        self,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 4)
        self.log(logging.INFO, summary, *args, body=body, **kwargs)

    def warning(
        self,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 4)
        self.log(logging.WARNING, summary, *args, body=body, **kwargs)

    def error(
        self,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 4)
        self.log(logging.ERROR, summary, *args, body=body, **kwargs)

    def critical(
        self,
        summary: str,
        *args: object,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("stacklevel", 4)
        self.log(logging.CRITICAL, summary, *args, body=body, **kwargs)
