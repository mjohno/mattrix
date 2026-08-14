#!/usr/bin/env python3
"""Search MKF/OKF bundles and return metadata matches as JSON."""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - startup dependency guard
    print("PyYAML is required to search MKF bundles. Install PyYAML and rerun.", file=sys.stderr)
    sys.exit(2)

log = logging.getLogger(__name__)
RESERVED = {"index.md", "log.md"}
ADVANCED_FIELDS = {"resource", "status", "stale_after", "generated", "verified", "sources"}
CORE_FIELDS = ("type", "title", "tags", "description")


def bundle_label(path: Path) -> str:
    return path.name or "BUNDLE"


def env_bundles() -> list[tuple[str, Path]]:
    bundles: list[tuple[str, Path]] = []
    for raw_path in os.environ.get("MKF_PATH", "").split(":"):
        if raw_path.strip():
            path = Path(raw_path.strip()).expanduser().resolve()
            bundles.append((bundle_label(path), path))
    return bundles


def parse_bundle_arg(value: str) -> tuple[str, Path]:
    path = Path(value).expanduser().resolve()
    return bundle_label(path), path


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter opening delimiter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter closing delimiter '---'")
    try:
        frontmatter = yaml.safe_load(text[4:end].strip("\n"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    concept_type = frontmatter.get("type")
    if not isinstance(concept_type, str) or not concept_type.strip():
        raise ValueError("missing or empty required field: type")
    return frontmatter, text[end + len("\n---") :].lstrip("\n")


def terms(query: str) -> list[str]:
    return [term for term in re.split(r"[^A-Za-z0-9_/-]+", query.lower()) if term]


def count_matches(haystack: str, query_terms: Iterable[str]) -> int:
    lowered = haystack.lower()
    return sum(lowered.count(term.lower()) for term in query_terms)


def first_excerpt(text: str, query_terms: Iterable[str], width: int = 180) -> str:
    lowered = text.lower()
    positions = [lowered.find(term.lower()) for term in query_terms if lowered.find(term.lower()) >= 0]
    if not positions: return ""
    pos = min(positions)
    return re.sub(r"\s+", " ", text[max(0, pos - width // 2): pos + width // 2]).strip()


def concept_id(bundle_root: Path, path: Path) -> str:
    return path.relative_to(bundle_root).as_posix()[:-3]


def text_value(value: Any) -> str:
    """Return searchable text for arbitrary permitted YAML extension values."""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except (TypeError, ValueError):
        return repr(value)


def parse_advanced_filters(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for value in values:
        if ":" not in value: raise ValueError("advanced fields must use FIELD:VALUE")
        field, expected = value.split(":", 1)
        if field not in ADVANCED_FIELDS: raise ValueError(f"unsupported advanced field: {field}")
        filters[field] = expected.lower()
    return filters


def search_file(bundle_name: str, bundle_root: Path, path: Path, query_terms: list[str], advanced_filters: dict[str, str]) -> dict[str, Any] | None:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "\ufffd" in text:
        log.warning("%s: invalid UTF-8 replaced while reading Markdown", path)
    frontmatter, body = split_frontmatter(text)
    for field, expected in advanced_filters.items():
        if expected not in text_value(frontmatter.get(field, "")).lower(): return None
    cid = concept_id(bundle_root, path)
    path_hits = count_matches(" ".join(path.relative_to(bundle_root).as_posix().split("/") + [cid, path.stem]), query_terms)
    if path_hits:
        tier, fields, score, excerpt = "path", ["directory", "filename", "concept_id"], 300 + path_hits * 10, cid
    else:
        fields = [field for field in CORE_FIELDS if count_matches(text_value(frontmatter.get(field, "")), query_terms)]
        if fields:
            tier, score = "frontmatter", 200 + sum(count_matches(text_value(frontmatter.get(field, "")), query_terms) for field in fields) * 10
            excerpt = "; ".join(f"{field}: {text_value(frontmatter[field])}" for field in fields)
        else:
            hits = count_matches(body, query_terms)
            if not hits: return None
            tier, fields, score, excerpt = "content", ["body"], 100 + hits, first_excerpt(body, query_terms)
    tags = frontmatter.get("tags", [])
    return {"bundle": bundle_name, "bundle_root": str(bundle_root), "concept_id": cid, "path": str(path), "match_tier": tier, "matched_fields": fields, "score": score, "type": frontmatter.get("type", ""), "title": frontmatter.get("title", ""), "description": frontmatter.get("description", ""), "tags": tags if isinstance(tags, list) else [str(tags)], "excerpt": excerpt}


def walk_concepts(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.md")):
        if path.is_file() and path.name not in RESERVED: yield path


def search_bundles(query: str, bundles: list[tuple[str, Path]], limit: int, advanced_filters: dict[str, str] | None = None) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    filters = advanced_filters or {}
    query_terms = terms(query)
    for order, (name, root) in enumerate(bundles):
        if not root.is_dir():
            errors.append({"bundle": name, "root": str(root), "error": "bundle root not found"})
            continue
        for path in walk_concepts(root):
            try:
                match = search_file(name, root, path, query_terms, filters)
            except (OSError, ValueError, TypeError) as exc:
                errors.append({"bundle": name, "path": str(path), "error": str(exc)})
                continue
            if match:
                match["bundle_order"] = order
                results.append(match)
    results.sort(key=lambda result: (result["bundle_order"], -int(result["score"]), result["concept_id"]))
    for result in results:
        result.pop("bundle_order", None)
    return {"query": query, "results": results[:max(limit, 0)], "errors": errors}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search MKF/OKF bundles and return JSON metadata matches.")
    parser.add_argument("--query"); parser.add_argument("--bundle", action="append", default=[]); parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--advanced-field", action="append", default=[], metavar="FIELD:VALUE")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]) 
    args = parser.parse_args(argv)
    if not args.test and not args.query: parser.error("--query is required unless --test is used")
    try: args.advanced_filters = parse_advanced_filters(args.advanced_field)
    except ValueError as exc: parser.error(str(exc))
    return args


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level), stream=sys.stderr, format="%(levelname)s: %(message)s")


def main(args: argparse.Namespace) -> int:
    bundles = [parse_bundle_arg(value) for value in args.bundle] if args.bundle else env_bundles()
    output = search_bundles(args.query, bundles, args.limit, args.advanced_filters)
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    return 0 if output["results"] or not output["errors"] else 2


def run_tests() -> int:
    class TestSearchMkf(unittest.TestCase):
        def test_excludes_reserved_and_returns_invalid_error(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "good.md").write_text("---\ntype: Metric\ntitle: Needle\n---\n", encoding="utf-8")
                (root / "index.md").write_text("# Needle index\n", encoding="utf-8")
                (root / "log.md").write_text("# Needle log\n", encoding="utf-8")
                (root / "bad.md").write_text("Needle\n", encoding="utf-8")
                output = search_bundles("needle", [("root", root)], 10)
                self.assertEqual([item["concept_id"] for item in output["results"]], ["good"])
                self.assertEqual(len(output["errors"]), 1)
        def test_type_only_and_advanced_filter(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "metric.md").write_text("---\ntype: Metric\nstatus: stable\nsources:\n  - resource: https://example.test\n---\nneedle\n", encoding="utf-8")
                output = search_bundles("needle", [("root", root)], 10, {"status": "stable"})
                self.assertEqual(len(output["results"]), 1)
        def test_accepts_invalid_utf8_with_warning_and_mixed_keys(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "bytes.md").write_bytes(b"---\ntype: Note\n---\nneedle\xff")
                (root / "keys.md").write_text("---\ntype: Note\ntitle: {1: one, two: two}\n---\nneedle\n", encoding="utf-8")
                output = search_bundles("needle", [("root", root)], 10)
                self.assertEqual(len(output["results"]), 2)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(unittest.TestLoader().loadTestsFromTestCase(TestSearchMkf))
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    configure_logging(args.log_level)
    sys.exit(run_tests() if args.test else main(args))
