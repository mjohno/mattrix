#!/usr/bin/env python3
"""
Search MKF bundles and return best metadata matches as JSON.

Examples:
    python search_mkf.py --query checklist
    python search_mkf.py --query template --bundle /knowledge/general --limit 5
    python search_mkf.py --log-level DEBUG --query "skill quality"
    python search_mkf.py --test

Stdout is reserved for JSON result data. Diagnostics and logs go to stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def bundle_label(path: Path) -> str:
    """Return the display label derived from a bundle root path."""
    return path.name or "BUNDLE"


def env_bundles() -> list[tuple[str, Path]]:
    """Resolve ordered MKF bundle roots from colon-delimited MKF_PATH."""
    bundles: list[tuple[str, Path]] = []
    raw = os.environ.get("MKF_PATH", "")
    for path_text in raw.split(":"):
        path_text = path_text.strip()
        if not path_text:
            continue
        path = Path(path_text).expanduser().resolve()
        bundles.append((bundle_label(path), path))
    return bundles


def parse_bundle_arg(value: str) -> tuple[str, Path]:
    """Parse a --bundle value as an explicit bundle root path."""
    path = Path(value).expanduser().resolve()
    return bundle_label(path), path


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Parse the small YAML subset used by MKF frontmatter."""
    data: dict[str, Any] = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, [])
            if isinstance(data[current_key], list):
                data[current_key].append(line[4:].strip().strip("\"'"))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = (
                []
                if not inner
                else [item.strip().strip("\"'") for item in inner.split(",")]
            )
        elif value.lower() in {"true", "false"}:
            data[key] = value.lower() == "true"
        else:
            data[key] = value.strip("\"'")
    return data


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return parsed frontmatter and body, or empty frontmatter when absent."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip("\n")
    body = text[end + len("\n---") :].lstrip("\n")
    return parse_simple_yaml(raw), body


def terms(query: str) -> list[str]:
    """Split a query into searchable lowercase terms."""
    return [
        term for term in re.split(r"[^A-Za-z0-9_/-]+", query.lower()) if term
    ]


def count_matches(haystack: str, query_terms: Iterable[str]) -> int:
    """Count lexical occurrences of query terms in text."""
    text = haystack.lower()
    return sum(text.count(term.lower()) for term in query_terms)


def first_excerpt(
    text: str, query_terms: Iterable[str], width: int = 180
) -> str:
    """Return a compact excerpt around the first matching query term."""
    lower = text.lower()
    positions = [
        lower.find(term.lower())
        for term in query_terms
        if lower.find(term.lower()) >= 0
    ]
    if not positions:
        return ""
    pos = min(positions)
    start = max(0, pos - width // 2)
    end = min(len(text), pos + width // 2)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def concept_id(bundle_root: Path, path: Path) -> str:
    """Return the OKF/MKF concept ID for a bundle-relative Markdown path."""
    rel = path.relative_to(bundle_root).as_posix()
    return rel[:-3] if rel.endswith(".md") else rel


def search_file(
    bundle_name: str,
    bundle_root: Path,
    path: Path,
    query_terms: list[str],
) -> dict[str, Any] | None:
    """Search one Markdown concept and return a match record when matched."""
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = split_frontmatter(text)
    cid = concept_id(bundle_root, path)
    rel_parts = path.relative_to(bundle_root).as_posix().split("/")
    dir_file_text = " ".join(rel_parts + [cid, path.stem])

    tier = None
    matched_fields: list[str] = []
    score = 0
    excerpt = ""

    path_hits = count_matches(dir_file_text, query_terms)
    if path_hits:
        tier = "path"
        matched_fields = ["directory", "filename", "concept_id"]
        score = 300 + path_hits * 10
        excerpt = cid
    else:
        metadata_fields = {
            "type": frontmatter.get("type", ""),
            "title": frontmatter.get("title", ""),
            "tags": " ".join(
                str(x) for x in frontmatter.get("tags", []) if x is not None
            ),
            "description": frontmatter.get("description", ""),
        }
        metadata_hits = 0
        for field, value in metadata_fields.items():
            hits = count_matches(str(value), query_terms)
            if hits:
                metadata_hits += hits
                matched_fields.append(field)
        if metadata_hits:
            tier = "frontmatter"
            score = 200 + metadata_hits * 10
            excerpt = "; ".join(
                f"{field}: {metadata_fields[field]}" for field in matched_fields
            )
        else:
            body_hits = count_matches(body, query_terms)
            if body_hits:
                tier = "content"
                matched_fields = ["body"]
                score = 100 + body_hits
                excerpt = first_excerpt(body, query_terms)

    if not tier:
        return None

    tags = frontmatter.get("tags", [])
    if not isinstance(tags, list):
        tags = [str(tags)] if tags else []

    return {
        "bundle": bundle_name,
        "bundle_root": str(bundle_root),
        "concept_id": cid,
        "path": str(path),
        "match_tier": tier,
        "matched_fields": matched_fields,
        "score": score,
        "type": frontmatter.get("type", ""),
        "title": frontmatter.get("title", ""),
        "description": frontmatter.get("description", ""),
        "tags": tags,
        "excerpt": excerpt,
    }


def walk_markdown(root: Path) -> Iterable[Path]:
    """Yield Markdown files under a bundle root in deterministic order."""
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            yield path


def search_bundles(
    query: str,
    bundles: list[tuple[str, Path]],
    limit: int,
) -> dict[str, Any]:
    """Search resolved bundles and return a JSON-serializable result object."""
    query_terms = terms(query)
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for order, (name, root) in enumerate(bundles):
        if not root.exists() or not root.is_dir():
            errors.append(
                {
                    "bundle": name,
                    "root": str(root),
                    "error": (
                        "bundle root not found; provide an existing path "
                        "or add it to MKF_PATH"
                    ),
                }
            )
            continue
        for path in walk_markdown(root):
            try:
                match = search_file(name, root, path, query_terms)
            except OSError as exc:
                errors.append(
                    {
                        "bundle": name,
                        "path": str(path),
                        "error": f"could not read concept file: {exc}",
                    }
                )
                continue
            if match:
                match["bundle_order"] = order
                results.append(match)

    results.sort(
        key=lambda r: (r["bundle_order"], -int(r["score"]), r["concept_id"])
    )
    for result in results:
        result.pop("bundle_order", None)

    return {
        "query": query,
        "results": results[: max(limit, 0)],
        "errors": errors,
    }


def configure_logging(log_level: str) -> None:
    """Configure diagnostic logging to stderr."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] [%(funcName)s]: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
        force=True,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search MKF bundles and return JSON metadata matches."
    )
    parser.add_argument("--query", help="Search query")
    parser.add_argument(
        "--bundle",
        action="append",
        default=[],
        help="Explicit bundle root path; repeatable",
    )
    parser.add_argument("--limit", type=int, default=10, help="Maximum results")
    parser.add_argument(
        "--log-level",
        default="CRITICAL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: CRITICAL)",
    )
    parser.add_argument("--test", action="store_true", help="Run inline tests")
    args = parser.parse_args(argv)
    if not args.test and not args.query:
        parser.error("--query is required unless --test is used")
    return args


def main(args: argparse.Namespace) -> int:
    """Run the search workflow and return an exit code."""
    bundles = (
        [parse_bundle_arg(value) for value in args.bundle]
        if args.bundle
        else env_bundles()
    )
    output = search_bundles(args.query, bundles, args.limit)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output["results"] or not output["errors"] else 2


def run_tests() -> int:
    """Run inline tests using unittest. Return 0 if all pass, 1 if any fail."""

    class TestSearchMkf(unittest.TestCase):
        def run_cli(
            self, args: list[str], environment: dict[str, str]
        ) -> subprocess.CompletedProcess[str]:
            """Run the script as a CLI with an isolated MKF_PATH."""
            env = os.environ.copy()
            env.pop("MKF_PATH", None)
            env.update(environment)
            return subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), *args],
                capture_output=True,
                check=False,
                encoding="utf-8",
                env=env,
            )

        def write_concept(self, root: Path, relative_path: str) -> None:
            """Create a minimal searchable MKF concept."""
            concept = root / relative_path
            concept.parent.mkdir(parents=True, exist_ok=True)
            concept.write_text(
                "---\n"
                "type: undefined\n"
                "title: Example\n"
                "description: Example concept.\n"
                "tags: []\n"
                "---\n\nBody\n",
                encoding="utf-8",
            )

        def test_cli_searches_mkf_path_in_order(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                first = root / "first"
                second = root / "second"
                self.write_concept(first, "needle-first.md")
                self.write_concept(second, "needle-second.md")
                result = self.run_cli(
                    ["--query", "needle", "--limit", "10"],
                    {"MKF_PATH": f"{first}::{second}"},
                )
                output = json.loads(result.stdout)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    [match["bundle"] for match in output["results"]],
                    ["first", "second"],
                )

        def test_cli_explicit_bundle_bypasses_mkf_path(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                configured = root / "configured"
                explicit = root / "explicit"
                self.write_concept(configured, "needle-configured.md")
                self.write_concept(explicit, "needle-explicit.md")
                result = self.run_cli(
                    ["--query", "needle", "--bundle", str(explicit)],
                    {"MKF_PATH": str(configured)},
                )
                output = json.loads(result.stdout)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    [match["bundle"] for match in output["results"]],
                    ["explicit"],
                )

        def test_cli_missing_configured_root_returns_error(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                missing = Path(temp_dir) / "missing"
                result = self.run_cli(
                    ["--query", "needle"], {"MKF_PATH": str(missing)}
                )
                output = json.loads(result.stdout)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(output["results"], [])
                self.assertIn(
                    "bundle root not found", output["errors"][0]["error"]
                )

        def test_parse_bundle_arg_derives_basename(self) -> None:
            name, path = parse_bundle_arg("/knowledge/general")
            self.assertEqual(name, "general")
            self.assertEqual(path, Path("/knowledge/general").resolve())

        def test_parse_simple_yaml_preserves_list_values(self) -> None:
            output = parse_simple_yaml("tags: [one, two]\ntitle: Example\n")
            self.assertEqual(
                output, {"tags": ["one", "two"], "title": "Example"}
            )

        def test_search_prefers_path_matches_and_applies_limit(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                self.write_concept(root, "needle.md")
                self.write_concept(root, "metadata.md")
                metadata = root / "metadata.md"
                metadata.write_text(
                    metadata.read_text(encoding="utf-8").replace(
                        "title: Example", "title: Needle"
                    ),
                    encoding="utf-8",
                )
                output = search_bundles("needle", [("root", root)], 1)
                self.assertEqual(output["errors"], [])
                self.assertEqual(output["results"][0]["concept_id"], "needle")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchMkf)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    cli_args = parse_args(sys.argv[1:])
    configure_logging(cli_args.log_level)
    if cli_args.test:
        sys.exit(run_tests())
    sys.exit(main(cli_args))
