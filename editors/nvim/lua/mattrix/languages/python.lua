local function has_project_config(root_dir, markers)
  return root_dir
    and #vim.fs.find(markers, { path = root_dir, upward = false }) > 0
end

local python_group = vim.api.nvim_create_augroup('mattrix-python', { clear = true })
vim.api.nvim_create_autocmd('FileType', {
  group = python_group,
  pattern = 'python',
  callback = function(event)
    vim.bo[event.buf].textwidth = 80
    vim.wo.colorcolumn = '81'
  end,
})

return {
  lsp = {
    on_new_config = function(new_config, root_dir)
      if has_project_config(root_dir, { 'pyproject.toml', 'pyrightconfig.json' }) then
        return
      end
      new_config.settings = vim.tbl_deep_extend('force', new_config.settings or {}, {
        basedpyright = {
          analysis = {
            typeCheckingMode = 'standard',
          },
        },
      })
    end,
  },
  ruff = {
    init_options = {
      settings = {
        organizeImports = true,
      },
    },
    on_new_config = function(new_config, root_dir)
      if has_project_config(root_dir, { 'pyproject.toml', 'ruff.toml', '.ruff.toml' }) then
        return
      end
      new_config.init_options = new_config.init_options or {}
      new_config.init_options.settings = vim.tbl_deep_extend(
        'force',
        new_config.init_options.settings or {},
        {
          lineLength = 80,
          lint = {
            ignore = { 'E501' },
            select = { 'E', 'F', 'I', 'UP', 'B', 'PL' },
          },
        }
      )
    end,
  },
}
