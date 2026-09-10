from __future__ import annotations

from typing import Any


def cache_hit_ratio(usage: dict[str, Any]) -> float:
    """Return cache reads as a share of token input and cache activity."""
    denominator = usage["input"] + usage["cache_read"] + usage["cache_write"]
    return usage["cache_read"] / denominator if denominator else 0.0


def format_usage(usage: dict[str, Any]) -> str:
    """Format cumulative STEP usage fields for structured log messages."""
    return (
        f"input={usage['input']} output={usage['output']} "
        f"cache_read={usage['cache_read']} cache_write={usage['cache_write']} "
        f"total={usage['total']} cost={usage['cost']} "
        f"cache_hit_ratio={cache_hit_ratio(usage):.4f}"
    )


def format_markdown_usage(usage: dict[str, Any]) -> str:
    """Format the compact cumulative-usage line for an Owner review."""
    return (
        f"**Usage:** Total: {usage['total']} · Input: {usage['input']} · "
        f"Output: {usage['output']} · "
        f"Cache hit ratio: {cache_hit_ratio(usage) * 100:.2f}% · "
        f"Cost: {usage['cost']}"
    )
