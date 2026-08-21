from __future__ import annotations

import io
import logging
import re

import pytest
from stagger_step.logging import StructuredFormatter, StructuredLogger

HEADER = re.compile(
    r"^stagger_step\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*:\d+ "
    r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] "
    r"(DEBUG|INFO|WARNING|ERROR|CRITICAL): "
)


@pytest.fixture
def logger():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ"))
    value = logging.getLogger("stagger_step.testing")
    value.handlers = [handler]
    value.setLevel(logging.DEBUG)
    value.propagate = False
    try:
        yield StructuredLogger("stagger_step.testing"), stream
    finally:
        value.handlers.clear()
        value.propagate = True


@pytest.mark.parametrize(
    "level",
    (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ),
)
def test_structured_formatter_has_a_forwarder_header_for_each_level(
    logger, level
):
    value, stream = logger

    value.log(level, "summary field=value")

    output = stream.getvalue()
    assert HEADER.match(output)
    assert (
        ".test_structured_formatter_has_a_forwarder_header_for_each_level:"
        in output
    )
    assert f"{logging.getLevelName(level)}: summary field=value\n" in output
    assert "\x1b" not in output


def test_structured_formatter_keeps_an_optional_body_raw(logger):
    value, stream = logger
    body = "## Context\n\n```yaml\ngoal: Ship\n```"

    value.debug("harness_prompt role=worker", body=body)

    header, emitted_body = stream.getvalue().split("\n", 1)
    assert HEADER.match(header)
    assert emitted_body == body + "\n"


def test_structured_formatter_places_tracebacks_after_the_header(logger):
    value, stream = logger

    try:
        raise RuntimeError("failed")
    except RuntimeError:
        value.critical("failure event=unhandled", exc_info=True)

    header, traceback = stream.getvalue().split("\n", 1)
    assert HEADER.match(header)
    assert "CRITICAL: failure event=unhandled" in header
    assert traceback.startswith("Traceback (most recent call last):\n")
    assert "RuntimeError: failed" in traceback
