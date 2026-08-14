# Mattrix Neovim Configuration

This is a small Neovim configuration owned by Mattrix. It uses selected
Kickstart.nvim patterns, but it is not a Neovim distribution. The configuration
uses `lazy.nvim` for plugins, Mason for language-server installation, built-in
`netrw` for directory browsing, and Neovim's native LSP completion.

## Quick start

Install the latest stable Neovim release, `git`, `ripgrep`, Node.js, and npm.
Nightly Neovim releases are not supported. A Nerd Font is optional.

1. Install the Treesitter command-line interface:

   ```sh
   npm install -g tree-sitter-cli
   tree-sitter --version
   ```

   Expected output ends with a `tree-sitter <version>` line.

2. Link this directory as the active Neovim configuration.

   Linux and macOS:

   ```sh
   mkdir -p ~/.config
   ln -s /path/to/mattrix/editors/nvim ~/.config/nvim
   readlink ~/.config/nvim
   ```

   Expected output is the absolute path to `mattrix/editors/nvim`.

   Windows PowerShell:

   ```powershell
   New-Item -ItemType SymbolicLink -Path "$env:LOCALAPPDATA\nvim" -Target "C:\path\to\mattrix\editors\nvim"
   (Get-Item "$env:LOCALAPPDATA\nvim").Target
   ```

   Expected output is `C:\path\to\mattrix\editors\nvim`. Use a directory
   junction if Windows policy prevents symbolic links.

3. Start Neovim:

   ```sh
   nvim
   ```

   `lazy.nvim` installs plugins. Mason installs the configured language
   servers. Treesitter installs parsers when `tree-sitter` is available.

4. In Neovim, run:

   ```vim
   :checkhealth
   :Mason
   ```

   Expected result: `:checkhealth` reports no errors for Neovim, `git`, and
   Mason. `:Mason` lists the configured language servers as installed or
   installing.

5. Install the remaining Bash tools and Rust components:

   ```vim
   :MasonInstall shellcheck shfmt
   ```

   ```sh
   rustup component add rustfmt clippy
   ```

   Expected result: Mason reports successful installation for `shellcheck` and
   `shfmt`; Rustup reports that `rustfmt` and `clippy` are installed.

## Core workflow

- `<leader>ff`: Find files.
- `<leader>fg`: Search text with `ripgrep`.
- `<leader>fb`: Find open buffers.
- `<leader>e`: Browse the current directory with built-in `netrw`.
- `<leader>f`: Format the current buffer.
- `gd`, `gr`, and `K`: Definition, references, and hover documentation.
- `<leader>rn` and `<leader>ca`: Rename and code action.
- `[d` and `]d`: Previous and next diagnostic.

The leader key is Space. The configuration preserves line numbers, incremental
search, highlighted search results, no wrapping, an 80-column marker, two-space
default indentation, persistent undo, true-color support, disabled navigation
keys, and Jenkinsfile Groovy detection.

## Tool management

Open `:Mason` to view installed tools. Mason installs these language servers:

- `basedpyright` and `ruff` for Python.
- `bash-language-server` for Bash.
- `rust-analyzer` for Rust.
- `yamlls` for YAML and schema validation.
- `jsonls` for JSON and schema validation.
- `terraformls` for Terraform and HCL.
- `dockerls` for Dockerfiles.
- `ansiblels` for Ansible YAML files.
- `powershell_es` on Windows only.

Mason can also install tools that the configuration calls directly:

```vim
:MasonInstall shellcheck shfmt
```

Use native toolchains where they are the better owner:

- Install `rustfmt` and `clippy` with `rustup component add rustfmt clippy`.
- Install PowerShell and its formatter on Windows. PowerShell Editor Services is managed by Mason.
- `ruff` may instead be installed with `uv tool install ruff` or `pipx install ruff` when you need it outside Neovim.

Do not install both `pyright` and `basedpyright`. This configuration uses
`basedpyright` for type analysis. It uses `ruff` for linting, import actions,
and formatting.

## Language support

| Language | Diagnostics and language support | Formatter |
| --- | --- | --- |
| Python | `basedpyright`, `ruff` | `ruff format` |
| Bash | `bash-language-server`, `shellcheck` | `shfmt` |
| Rust | `rust-analyzer`, `clippy` | `rustfmt` |
| PowerShell (Windows only) | PowerShell Editor Services | PowerShell formatter |
| YAML | `yamlls` | None configured |
| JSON | `jsonls` | None configured |
| Terraform / HCL | `terraformls` | None configured |
| Dockerfile | `dockerls` | None configured |
| Ansible | `ansiblels` | None configured |

YAML schema validation is enabled. Ansible support applies to files in
`playbooks/` and common Ansible role directories. Ansible LSP linting is
disabled; no standalone linter integration is configured.

PowerShell configuration loads only on Windows. Non-Windows Neovim does not
install or require PowerShell tooling.

## Manual validation

After Mason finishes installation, open a representative file for each language.
Check diagnostics, code navigation, completion, and `<leader>f` formatting.

1. For Python, create a type or lint issue and confirm diagnostics and Ruff formatting.
2. For Bash, create a shell issue and confirm diagnostics and `shfmt` formatting.
3. For Rust, open a Cargo project and confirm `rust-analyzer` navigation, diagnostics, and `rustfmt` formatting.
4. On Windows, open a PowerShell file and confirm diagnostics and formatting.
5. For YAML, JSON, Terraform, Dockerfile, and Ansible files, confirm diagnostics, navigation, and completion.
6. On a non-Windows system, start Neovim and confirm that no PowerShell tool is required.

Manual use is the required acceptance method. Use `:checkhealth` and `:Mason`
to investigate setup problems.
