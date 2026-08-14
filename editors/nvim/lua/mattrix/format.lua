require('conform').setup({
  formatters_by_ft = {
    python = { 'ruff_format', 'ruff_organize_imports' },
    sh = { 'shfmt' },
    bash = { 'shfmt' },
    zsh = { 'shfmt' },
    powershell = { 'powershell' },
    rust = { 'rustfmt' },
  },
  default_format_opts = {
    lsp_format = 'fallback',
  },
})
