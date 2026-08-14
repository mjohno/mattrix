# Plan: Neovim Development Configuration

PLAN_ID: PLAN-nvim
Source: `editors/SPEC-nvim.md` and confirmed Neovim baseline decisions
Purpose: Create a small, owned Neovim configuration for Python, Bash, Windows PowerShell, and Rust development.

## Source Summary

- SPEC-nvim PUR-001, FUT-001: Create an `editors` domain with a Neovim baseline for four development languages.
- SPEC-nvim REQ-001 through REQ-005: Provide language-aware support, limit PowerShell to Windows, use Mason for language servers, document tooling, and preserve domain boundaries.
- Confirmed baseline: Use the latest stable Neovim release, selected Kickstart.nvim patterns without its workflow, Mason, `rust-analyzer`, native diagnostics and completion, and no UI or dedicated file-explorer plugins.
- Confirmed language tools: Use `basedpyright`, `ruff`, `bash-language-server`, `shellcheck`, `shfmt`, PowerShell Editor Services, its formatter, `rust-analyzer`, `clippy`, and `rustfmt`.
- Existing Vim preferences: Preserve line numbers, search behavior, no wrapping, an 80-column marker, two-space default indentation, persistent undo, true color support, disabled navigation keys, and Jenkinsfile Groovy detection.

## Gap Map

| Gap ID | Source Summary | Current Problem | Target State |
| --- | --- | --- | --- |
| GAP-1 | FUT-001; SCP-IN-001; SCP-IN-002 | The repository has no `editors` domain or Neovim configuration. | The repository has a self-contained `editors/nvim` configuration. |
| GAP-2 | REQ-003; confirmed baseline | The editor has no managed language-server installation or defined core editing support. | Neovim has a minimal managed baseline for navigation, search, syntax, LSP, diagnostics, completion, and formatting. |
| GAP-3 | REQ-001; REQ-002; confirmed language tools | The selected language development workflows are not configured. | Each in-scope language has the confirmed support and PowerShell loads only on Windows. |
| GAP-4 | REQ-004; ACC-001 through ACC-004 | Setup requirements and manual validation steps are not documented. | Documentation enables installation, manual use, and review of the baseline. |

## Work Plan

### PLAN-nvim-1 — Establish the editor domain and Neovim entry point
Closes: GAP-1
Source refs: SCP-IN-001, SCP-IN-002, QUA-CON-001, confirmed existing Vim preferences
Status: done
Depends on: none
Task: Establish the `editors` domain and a self-contained Neovim configuration entry point so the configuration has a clear owner and preserves the useful behavior of the existing Vim setup. Keep the domain separate from `skills/`, `kb/`, and `agents/`. Completion is observable when the configuration layout and its core preferences are present and readable.

Deliverables:
- `editors/AGENTS.md` with domain ownership and boundary rules.
- `editors/nvim/init.lua`.
- Modular files for options, keymaps, autocommands, plugins, language settings, LSP, and formatting.
- Core settings that preserve the confirmed existing Vim preferences.

Scenarios:
- SCN-PLAN-nvim-1: Neovim loads the owned configuration
  Given the repository Neovim configuration is installed as the active configuration
  When Neovim starts
  Then it loads the configuration entry point
  And the confirmed core editing preferences are active

Done when:
- The domain and Neovim configuration layout exist.
- Neovim can load the entry point without configuration errors.

### PLAN-nvim-2 — Add the minimal managed editing baseline
Closes: GAP-2
Source refs: REQ-003, QUA-PRI-001, DEC-003, confirmed baseline
Status: done
Depends on: PLAN-nvim-1
Task: Add the minimal Neovim editing baseline so development has managed language servers, code navigation, diagnostics, completion, structural syntax support, search, and formatting without adopting a full editor distribution or UI workflow. Use Mason for language-server management and keep the plugin set small. Completion is observable when the baseline features load and are available in a supported source file.

Deliverables:
- Plugin bootstrap and lock file.
- Mason and LSP integration.
- Search, syntax parsing, diagnostics, native completion, and formatting configuration.
- Configuration that uses built-in directory browsing and does not add UI or dedicated file-explorer plugins.

Scenarios:
- SCN-PLAN-nvim-2: A source file exposes core development actions
  Given Neovim opens a supported source file
  When the user invokes navigation, search, diagnostics, completion, or formatting
  Then the related core action is available

Done when:
- Mason opens and shows managed language-server tooling.
- The baseline plugin set is limited to the agreed editing capabilities.
- No full Neovim distribution, UI plugin, or dedicated file-explorer plugin is included.

### PLAN-nvim-3 — Configure Python and Bash development support
Closes: GAP-3
Source refs: REQ-001, ACC-003, confirmed language tools
Status: verifying
Depends on: PLAN-nvim-2
Task: Configure the confirmed Python and Bash development support so their source files provide language feedback and consistent formatting in the owned Neovim baseline. Retain the defined roles of type analysis, linting, and formatting rather than adding overlapping tools. Completion is observable through manual use in representative Python and Bash files.

Deliverables:
- Python configuration for `basedpyright` and `ruff`.
- Bash configuration for `bash-language-server`, `shellcheck`, and `shfmt`.
- Mason installation definitions for applicable language servers.
- Formatter definitions for Python and Bash.

Scenarios:
- SCN-PLAN-nvim-3: Python source receives development feedback
  Given the user opens a Python source file
  When the file contains a type or lint issue and the user requests formatting
  Then Neovim presents relevant diagnostics
  And formatting is available
- SCN-PLAN-nvim-3b: Bash source receives development feedback
  Given the user opens a Bash source file
  When the file contains a shell issue and the user requests formatting
  Then Neovim presents relevant diagnostics
  And formatting is available

Done when:
- Manual use confirms Python and Bash diagnostics and formatting.
- The configured tools match the confirmed language baseline.

### PLAN-nvim-4 — Configure Rust development support
Closes: GAP-3
Source refs: REQ-001, ACC-003, confirmed `rust-analyzer` preference
Status: verifying
Depends on: PLAN-nvim-2
Task: Configure Rust development support with the confirmed Rust toolchain so Rust files provide language feedback, navigation, and formatting without an additional Rust framework plugin. Completion is observable through manual use in a representative Rust project.

Deliverables:
- Rust configuration for `rust-analyzer`.
- Formatter integration for `rustfmt`.
- Documentation of `clippy` as part of the Rust development toolchain.

Scenarios:
- SCN-PLAN-nvim-4: Rust source receives language support
  Given the user opens a Rust source file in a Rust project
  When the user navigates code, inspects diagnostics, or requests formatting
  Then Neovim provides the corresponding Rust development action

Done when:
- Manual use confirms Rust language support and formatting.
- The configuration uses `rust-analyzer` directly.

### PLAN-nvim-5 — Configure Windows PowerShell development support
Closes: GAP-3
Source refs: REQ-002, ACC-004, QUA-CON-002, confirmed language tools
Status: verifying
Depends on: PLAN-nvim-2
Task: Configure PowerShell development support for Windows so PowerShell files receive language feedback and formatting on that platform without making PowerShell tooling a dependency on other operating systems. Completion is observable through manual use on Windows and through safe configuration loading elsewhere.

Deliverables:
- Windows-gated PowerShell configuration for PowerShell Editor Services and its formatter.
- Mason installation definition for applicable PowerShell tooling.
- Documentation of Windows-specific prerequisites.

Scenarios:
- SCN-PLAN-nvim-5: Windows PowerShell source receives language support
  Given Neovim runs on Windows and the user opens a PowerShell source file
  When the user inspects diagnostics or requests formatting
  Then Neovim provides the corresponding PowerShell development action
- SCN-PLAN-nvim-5b: Non-Windows Neovim does not require PowerShell tooling
  Given Neovim runs on a non-Windows operating system
  When Neovim starts
  Then the configuration loads without requiring PowerShell tooling

Done when:
- Manual use on Windows confirms PowerShell diagnostics and formatting.
- Manual startup on a non-Windows system confirms that PowerShell tooling is not required.

### PLAN-nvim-6 — Document installation and manual validation
Closes: GAP-4
Source refs: REQ-004, ACC-001 through ACC-004, EXP-001, UNC-Q-003
Status: done
Depends on: PLAN-nvim-3, PLAN-nvim-4, PLAN-nvim-5
Task: Document the owned Neovim configuration so a user can install it, distinguish Mason-managed tools from other supported installation methods, and manually validate each supported language workflow. Keep the instructions direct and identify Windows-only PowerShell requirements. Completion is observable when the README covers setup and the agreed manual validation activities.

Deliverables:
- `editors/nvim/README.md`.
- An update to the repository `README.md` that identifies the `editors` domain and links to the Neovim configuration documentation.
- A tool inventory that identifies Mason-managed and externally installed tools.
- Manual validation instructions for Python, Bash, Rust, and Windows PowerShell.

Scenarios:
- SCN-PLAN-nvim-6: A user prepares and checks the configuration
  Given a user has the repository configuration and its documented prerequisites
  When the user follows the setup and manual validation instructions
  Then the user can prepare the configuration and check each applicable language workflow

Done when:
- `editors/nvim/README.md` documents installation, tool ownership, and manual validation.
- The repository `README.md` identifies the `editors` domain and links to the Neovim configuration documentation.
- The Neovim README identifies Windows-only PowerShell requirements.
