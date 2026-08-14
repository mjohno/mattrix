# SPEC-nvim: Neovim Development Configuration

## 1. Purpose

- PUR-001: The repository needs an `editors` domain for editor-based configuration, starting with Neovim, to support development in Python, Bash, Windows PowerShell, and Rust.

## 2. Current State Summary

- CUR-001: The repository has no top-level `editors` directory.
- CUR-002: The requested editor is Neovim.

## 3. Future State

- FUT-001: The repository contains an `editors/nvim` configuration that provides a defined baseline development experience for Python, Bash, Windows PowerShell, and Rust.

## 4. Scope

### In Scope

- SCP-IN-001: A new top-level `editors` domain.
- SCP-IN-002: Neovim configuration under `editors/nvim`.
- SCP-IN-003: Baseline support for Python, Bash, Windows PowerShell, and Rust development.
- SCP-IN-004: Operating-system-specific handling for Windows PowerShell support.

### Out of Scope

- SCP-OUT-001: Editor configuration other than Neovim.
- SCP-OUT-002: Application source, knowledge-base, skill, or agent behavior changes.
- SCP-OUT-003: PowerShell support on non-Windows systems.

## 5. Requirements

- REQ-001: The Neovim configuration must provide language-aware development support for Python, Bash, and Rust.
- REQ-002: The Neovim configuration must provide language-aware PowerShell development support only when it runs on Windows.
- REQ-003: The configuration must use Mason to manage Neovim language-server installation.
- REQ-004: The configuration must document Mason-managed tools and tools installed through other supported methods.
- REQ-005: The `editors` domain must remain independent from editor-specific changes in `skills/`, `kb/`, and `agents/`.

## 6. Acceptance

- ACC-001: Review confirms that `editors/nvim` exists and documents the supported languages, Mason-managed tools, and other installation methods.
- ACC-002: Review confirms that Mason manages the configured language-server installation.
- ACC-003: Review confirms that Python, Bash, and Rust support is configured.
- ACC-004: Review confirms that PowerShell support is limited to Windows.

## 7. Quality

### Constraints / Non-Negotiables

- QUA-CON-001: The configuration must not introduce editor-specific dependencies into `skills/`, `kb/`, or `agents/`.
- QUA-CON-002: Windows-only PowerShell configuration must not be required on other operating systems.

### Priorities

- QUA-PRI-001: Keep the baseline configuration small, clear, and maintainable.

## 8. Expectations

- EXP-001: The initial implementation should include setup and tool requirements in `editors/nvim/README.md`.
- EXP-002: Future implementation work should trace to this specification's requirement and acceptance IDs.

## 9. Uncertainties

### Risks

- UNC-RISK-001: Language tools may differ by operating system and project environment, which can make setup less portable.

### Questions

- UNC-Q-001: Which Neovim release and plugin manager should the configuration support?
- UNC-Q-002: Which language servers, formatters, linters, and completion tools should be standard for each language?
- UNC-Q-003: What validation method will confirm that each language baseline works?

### Assumptions

- UNC-ASM-001: `editors/nvim` is the intended location for the Neovim configuration.
- UNC-ASM-002: PowerShell support is required only on Windows, as stated in the request.

### Pre-Work Needed

- UNC-PRE-001: Select and document the Neovim version, plugin manager, Mason-managed language servers, and other language tooling.
- UNC-PRE-002: Define repeatable acceptance checks for each supported language.

## 10. Decisions

- DEC-001: Proposed — create `editors` as a top-level domain and place Neovim configuration in `editors/nvim`.
- DEC-002: Confirmed — include Python, Bash, Windows PowerShell, and Rust in the initial Neovim scope.
- DEC-003: Confirmed — use Mason to manage Neovim language-server installation; allow other supported installation methods for tools that need them.
