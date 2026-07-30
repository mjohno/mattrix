# SPEC-commit-afk-mode: Commit and AFK Session Modes

## 1. Purpose

- PUR-001: Allow an owner to review each completed STEP packet before its packet-attributable workspace changes are locally committed, while optionally continuing approved work without repeatedly entering `approved`.

## 2. Current State Summary

- CUR-001: Stagger Step presents a gate after preparing a completed packet; the owner explicitly enters `approved`, `break`, or revision feedback.
- CUR-002: Pi role processes inherit the CLI process working directory; Stagger Step does not currently provide, persist, or enforce a workspace path.
- CUR-003: STEP state is separate from the Git worktree and is not a Git artifact.

## 3. Future State

- FUT-001: Commit mode creates one local Git commit for each approved packet with attributable changes, after owner approval and before persistence of the resulting approved STEP state.
- FUT-002: Session-only AFK mode automatically approves subsequent gates while active, subject to its failure fallback and owner interruption controls.
- FUT-003: Git activity and mode changes are observable through INFO diagnostics without granting agents Git-history-changing authority.

## 4. Scope

### In Scope

- SCP-IN-001: A `--commit` mode usable with the existing CLI gate and session flows.
- SCP-IN-002: An in-memory AFK mode usable only in an active session.
- SCP-IN-003: Git repository readiness checks, packet-attributable commit creation, commit-to-packet traceability, and INFO diagnostics.
- SCP-IN-004: AFK/manual interruption, `break`, revision, and failure-fallback behavior.

### Out of Scope

- SCP-OUT-001: Defining, changing, or evaluating the STEP goal.
- SCP-OUT-002: Remote Git operations, including push, pull, fetch, rebase, merge, reset, stash, or branch selection.
- SCP-OUT-003: Containerization, filesystem sandboxing, or hard enforcement of an agent workspace boundary.
- SCP-OUT-004: Persisting AFK mode in STEP state or reconstructing it after a process exit.

## 5. Requirements

- REQ-001: When `--commit` is active, Stagger Step must require a non-bare Git worktree with no Git lock, a clean initial baseline, and configured author and committer identity before work begins.
- REQ-002: The repository branch selected by the owner before invocation may be any branch and must remain unchanged by Stagger Step.
- REQ-003: Worker, assessor, and coordinator processes must operate from the invoking CLI process's current working directory, not the Stagger Step binary directory.
- REQ-004: For an approved packet in commit mode, Stagger Step must determine the changes made since that packet's clean baseline, reject pre-existing unrelated changes, and commit only packet-attributable changes. Git-ignored files remain governed by the repository's `.gitignore` policy.
- REQ-005: An approved packet with no attributable Git changes must advance without creating an empty commit.
- REQ-006: `success`, `partial`, `failure`, and `blocked` packets may have their attributable changes committed after approval.
- REQ-007: For a non-no-op commit, the commit message must use the assessed current packet in this format:

  ```text
  step(<slug>): <intent>

  <do.summary>

  Result: <success|partial|failure|blocked>
  ```

- REQ-008: The subject in REQ-007 must normalize embedded whitespace and be deterministically limited to 72 characters; the body omits the summary paragraph when `do.summary` is empty.
- REQ-009: In commit mode, the completed packet history must record the resulting local commit SHA after normal completion. Commit SHA recording is not required when commit mode is inactive, or when a restart follows interruption before state persistence.
- REQ-010: If Git validation, staging, or commit creation fails, Stagger Step must not persist approval and must return to an ordinary approval gate with the failure available to the owner.
- REQ-011: At a session gate, the `afk` response must approve that gate and enable AFK for later gates in the same running session only.
- REQ-012: While AFK is active, each later gate must receive an implicit `approved` response and follow the normal commit-mode behavior when `--commit` is active.
- REQ-013: While AFK is active, Ctrl+C must disable AFK and return to a manual gate without approving that gate. In manual mode, Ctrl+C retains the existing crash/debug behavior; `break` exits the session gracefully without approval.
- REQ-014: Revision feedback is available only after AFK has been stopped with `break` or Ctrl+C.
- REQ-015: AFK must disable itself and return to manual approval when at least one of the last ten completed tasks has an assessed result of `failure` or `blocked`. Before ten tasks are completed, one such result disables AFK. `partial` does not contribute to this failure tracking. The owner must explicitly enter `afk` to enable it again.
- REQ-016: Stagger Step must not itself perform Git operations other than deterministic local staging and committing for an approved packet.

## 6. Acceptance

- ACC-001: Starting commit mode outside a valid clean Git worktree, with a Git lock, or without configured identity fails before a role executes and reports the relevant condition.
- ACC-002: A packet with workspace changes produces exactly one local commit after approval, uses REQ-007's message format, and records that commit's SHA in its completed history.
- ACC-003: A no-op approved packet advances without a Git commit.
- ACC-004: A Git commit failure leaves the packet unapproved and returns the owner to a manual approval gate.
- ACC-005: An AFK session approves subsequent gates without owner input until its interruption or failure fallback condition occurs.
- ACC-006: Ctrl+C during AFK returns the session to manual mode; `break` from manual mode exits gracefully; Ctrl+C from manual mode follows the existing crash/debug path.
- ACC-007: Evidence confirms no Stagger Step Git operation pushes, changes branches, rebases, merges, resets, or stashes.

## 7. Quality

### Constraints / Non-Negotiables

- QUA-CON-001: STEP state files must not be staged or committed by this feature.
- QUA-CON-002: A commit must not include changes that predate the packet's clean baseline.
- QUA-CON-003: AFK mode must have no durable STEP-state representation.
- QUA-CON-004: Automatic approval must not bypass the same state validation and commit checks used by an explicit approval.

### Priorities

- QUA-PRI-001: Preserve owner control and recoverability over uninterrupted automation.
- QUA-PRI-002: Keep Git behavior deterministic, local, and auditable.

## 8. Expectations

- EXP-001: INFO diagnostics report the repository branch, configured author and committer identity, commit-mode state, AFK activation/deactivation, automatic approvals, commit SHA, commit failures, and failure-fallback reason.
- EXP-002: Validation evidence covers explicit approval, AFK approval, no-op work, attributable changes, unrelated-change rejection, Git failure recovery, AFK interruption, manual `break`, and the failure fallback.

## 9. Uncertainties

### Risks

- UNC-RISK-001: Reliably distinguishing packet-attributable changes from unrelated concurrent edits depends on the clean-baseline contract.

### Questions

- None.

### Assumptions

- UNC-ASM-001: Git identity is provisioned by the environment before commit mode starts.
- UNC-ASM-002: The invoking project is intentionally selected by the owner through its current working directory and branch.
- UNC-ASM-003: External container or deployment policy supplies any stronger workspace isolation required for agents.

### Pre-Work Needed

- None.

## 10. Decisions

- DEC-001: AFK is session-memory-only and is enabled by entering `afk` at a manual gate; it is never written to STEP state.
- DEC-002: Commit mode commits after approval and before persistence of the approved STEP state so the owner can review the completed packet before committing.
- DEC-003: No-op packets create no empty commit.
- DEC-004: The repository's `.gitignore` controls excluded files; Stagger Step adds no separate sensitive-file exclusion policy.
- DEC-005: Stagger Step makes local commits only and does not perform remote or Git-history-rewriting operations.
- DEC-006: If interruption occurs after a successful commit but before approved STEP-state persistence, the commit SHA may be absent from STEP history. On restart, the CLI derives a new recommended next step from the persisted state and continues; it does not reconcile the intervening commit. The code implementing this boundary must state this as a `DECISION` comment.
- DEC-007: AFK failure tracking uses the last ten completed tasks: one `failure` or `blocked` disables AFK; before ten tasks exist, one such result also disables it. `partial` is excluded.
