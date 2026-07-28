#!/usr/bin/env python3
"""Validate a STEP role YAML packet without accessing STEP state."""
from __future__ import annotations
import argparse
import re
import sys
import unittest
from pathlib import Path
from typing import Any
import yaml

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESULTS = {"success", "partial", "failure", "blocked"}
OUTCOMES = {"progressed", "partial", "blocked", "failed"}

class PacketError(ValueError): pass

def mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict): raise PacketError(f"{label} must be a mapping")
    return value

def strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value): raise PacketError(f"{label} must be a list of non-empty strings")
    if nonempty and not value: raise PacketError(f"{label} must not be empty")
    return value

def task(value: Any, label: str = "packet", complete: bool = False) -> dict[str, Any]:
    obj = mapping(value, label)
    if not isinstance(obj.get("slug"), str) or not SLUG.fullmatch(obj["slug"]): raise PacketError(f"{label}.slug must be lowercase kebab-case")
    if not isinstance(obj.get("intent"), str) or not obj["intent"].strip(): raise PacketError(f"{label}.intent is required")
    strings(obj.get("criteria"), f"{label}.criteria", True)
    if complete:
        for field in ("do", "validate"):
            part = mapping(obj.get(field), f"{label}.{field}")
            strings(part.get("evidence"), f"{label}.{field}.evidence")
        if not isinstance(obj["do"].get("summary"), str) or not obj["do"]["summary"].strip(): raise PacketError(f"{label}.do.summary is required")
        if obj["validate"].get("result") not in RESULTS: raise PacketError(f"{label}.validate.result is invalid")
    return obj

def proposals(obj: dict[str, Any]) -> None:
    packets = obj.get("proposed_next_packets")
    if not isinstance(packets, list): raise PacketError("proposed_next_packets must be a list")
    slugs = [task(x, f"proposed_next_packets[{i}]")["slug"] for i, x in enumerate(packets)]
    if len(set(slugs)) != len(slugs): raise PacketError("proposed_next_packets contains duplicate slugs")
    rec = obj.get("recommendation")
    if rec is not None and rec not in slugs: raise PacketError("recommendation must name a proposed packet or be null")

def validate(role: str, obj: Any) -> dict[str, Any]:
    obj = mapping(obj, role)
    if role == "coordinator":
        strings(obj.get("lessons"), "lessons")
        proposals(obj)
    elif role == "worker": task(obj.get("packet"), "packet", True)
    else:
        task(obj.get("current_packet"), "current_packet", True)
        if obj.get("outcome") not in OUTCOMES: raise PacketError("outcome is invalid")
        retro = mapping(obj.get("retro"), "retro")
        for key in ("wins", "issues", "actions"): strings(retro.get(key), f"retro.{key}")
        if not isinstance(obj.get("clarification_needed"), bool): raise PacketError("clarification_needed must be boolean")
    return obj

class NormalizerTests(unittest.TestCase):
    coordinator = {"lessons": ["Keep evidence"], "proposed_next_packets": [{"slug": "next-task", "intent": "Continue", "criteria": ["done"]}], "recommendation": "next-task"}
    worker = {"packet": {"slug": "next-task", "intent": "Continue", "criteria": ["done"], "do": {"summary": "Worked", "evidence": ["file"]}, "validate": {"result": "success", "evidence": ["test"]}}}
    assessor = {"current_packet": worker["packet"], "outcome": "progressed", "retro": {"wins": ["work"], "issues": [], "actions": ["continue"]}, "clarification_needed": False}
    def test_valid_role_packets(self) -> None:
        for role, packet in (("coordinator", self.coordinator), ("worker", self.worker), ("assessor", self.assessor)):
            self.assertEqual(validate(role, packet), packet)
    def test_invalid_role_packets(self) -> None:
        duplicate = {**self.coordinator, "proposed_next_packets": [self.coordinator["proposed_next_packets"][0]] * 2}
        with self.assertRaises(PacketError): validate("coordinator", duplicate)
        with self.assertRaises(PacketError): validate("worker", {"packet": {"slug": "bad slug"}})
        with self.assertRaises(PacketError): validate("assessor", {**self.assessor, "outcome": "unknown"})

# TODO(cli-1): Add coordinator, worker, and assessor subcommands with one option per packet field; accept repeated options for list fields (for example, `--retro-wins`). Guide required fields in role-specific help rather than requiring callers to construct YAML.
# refs: [../references/packet_contract.md]
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="run script-local packet tests")
    parser.add_argument("role", nargs="?", choices=("coordinator", "worker", "assessor"))
    parser.add_argument("input", nargs="?", help="YAML packet path or - for stdin")
    args = parser.parse_args(argv)
    if args.test:
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NormalizerTests))
        return 0 if result.wasSuccessful() else 1
    if not args.role or not args.input: parser.error("role and input are required unless --test is supplied")
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text()
        print(yaml.safe_dump(validate(args.role, yaml.safe_load(raw)), sort_keys=False), end="")
    except (OSError, yaml.YAMLError, PacketError) as exc:
        print(f"packet error: {exc}", file=sys.stderr); return 2
    return 0
if __name__ == "__main__": raise SystemExit(main())
