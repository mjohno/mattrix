return {
  lsp = {
    settings = {
      basedpyright = {
        analysis = {
          typeCheckingMode = 'standard',
        },
      },
    },
  },
  ruff = {
    init_options = {
      settings = {
        organizeImports = true,
      },
    },
  },
}
