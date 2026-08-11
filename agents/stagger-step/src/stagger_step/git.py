from __future__ import annotations

import logging
import re
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

from .state import StateError

logger = logging.getLogger("stagger_step.git")
SHA = re.compile(r"^[0-9a-f]{40,64}$")


def _wrap_body(text: str) -> str:
    """Wrap every paragraph deterministically for a Git commit body."""
    return "\n".join(
        "\n".join(textwrap.wrap(line, width=72)) if line else ""
        for line in text.splitlines()
    )


@dataclass
class CommitMode:
    """Deterministic local Git boundary for one STEP invocation."""

    step_path: Path
    cwd: Path
    root: Path | None = None

    def _run(self, *args: str, check: bool = True) -> str:
        result = subprocess.run(
            ("git", *args),
            cwd=self.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and result.returncode:
            detail = (
                result.stderr.strip()
                or result.stdout.strip()
                or "git command failed"
            )
            raise StateError(f"git {' '.join(args)}: {detail}")
        return result.stdout.strip()

    def begin(self, *, require_clean: bool = True) -> str | None:
        bare = self._run("rev-parse", "--is-bare-repository")
        if bare != "false":
            raise StateError("commit mode requires a non-bare Git worktree")
        self.root = Path(self._run("rev-parse", "--show-toplevel"))
        git_dir = Path(self._run("rev-parse", "--git-dir"))
        if not git_dir.is_absolute():
            git_dir = self.cwd / git_dir
        if (git_dir / "index.lock").exists():
            raise StateError(
                "commit mode cannot run while the Git index is locked"
            )
        author = self._run("var", "GIT_AUTHOR_IDENT")
        committer = self._run("var", "GIT_COMMITTER_IDENT")
        branch = self._run("branch", "--show-current") or "(detached HEAD)"
        logger.info(
            "commit mode repository branch=%s author=%s committer=%s",
            branch,
            author,
            committer,
        )
        if require_clean:
            self._require_clean()
        return self.head()

    def head(self) -> str | None:
        result = subprocess.run(
            ("git", "rev-parse", "--verify", "HEAD"),
            cwd=self.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            return None
        sha = result.stdout.strip()
        if not SHA.fullmatch(sha):
            raise StateError("git returned an invalid HEAD SHA")
        return sha

    def _state_relative(self) -> str | None:
        assert self.root is not None
        try:
            return str(
                self.step_path.resolve().relative_to(self.root.resolve())
            )
        except ValueError:
            return None

    def _status(self) -> list[str]:
        ignored = self._state_relative()
        result = subprocess.run(
            ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
            cwd=self.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            detail = result.stderr.strip() or "git status failed"
            raise StateError(f"git status: {detail}")
        paths: list[str] = []
        records = iter(result.stdout.split("\0"))
        for record in records:
            if not record:
                continue
            path = record[3:]
            if record[:1] in {"R", "C"} or record[1:2] in {"R", "C"}:
                next(records, None)
            if path != ignored:
                paths.append(path)
        return paths

    def _require_clean(self) -> None:
        dirty = self._status()
        if dirty:
            raise StateError(
                "commit mode requires a clean Git baseline: " + ", ".join(dirty)
            )

    def clean_baseline(self) -> str | None:
        self._require_clean()
        return self.head()

    def commit(self, packet: dict[str, object], base: str | None) -> str | None:
        if self.root is None:
            raise AssertionError("commit mode was not initialized")
        if self.head() != base:
            raise StateError(
                "Git HEAD changed since this packet's clean baseline"
            )
        paths = self._status()
        if not paths:
            logger.info(
                "commit mode packet=%s has no Git changes", packet["slug"]
            )
            return None
        self._run("add", "-A", "--", *paths)
        staged = subprocess.run(
            ("git", "diff", "--cached", "--quiet"), cwd=self.cwd, check=False
        )
        if staged.returncode == 0:
            logger.info(
                "commit mode packet=%s has no staged Git changes",
                packet["slug"],
            )
            return None
        subject = f"step: {packet['slug']}"[:50].rstrip()
        intent = str(packet["intent"]).strip()
        work = packet.get("work")
        validation = packet.get("validate")
        done = str(
            work.get("summary", "") if isinstance(work, dict) else ""
        ).strip()
        verified = str(
            validation.get("summary", "")
            if isinstance(validation, dict)
            else ""
        ).strip()
        result = str(
            validation.get("result", "") if isinstance(validation, dict) else ""
        )
        sections = [f"Intent:\n{_wrap_body(intent)}"]
        if done:
            sections.append(f"Done:\n{_wrap_body(done)}")
        if verified:
            sections.append(f"Verified:\n{_wrap_body(verified)}")
        sections.append(f"Result: {result}")
        body = "\n\n".join(sections)
        self._run("commit", "-m", subject, "-m", body)
        sha = self.head()
        if sha is None:
            raise StateError("git commit did not produce a HEAD SHA")
        logger.info(
            "commit mode committed packet=%s sha=%s", packet["slug"], sha
        )
        return sha
