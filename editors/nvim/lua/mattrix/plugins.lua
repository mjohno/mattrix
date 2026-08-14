local lazypath = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'
if not vim.uv.fs_stat(lazypath) then
  vim.fn.system({
    'git', 'clone', '--filter=blob:none',
    'https://github.com/folke/lazy.nvim.git', '--branch=stable', lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require('lazy').setup({
  spec = {
    { 'neovim/nvim-lspconfig', config = function() require('mattrix.lsp') end },
    { 'mason-org/mason.nvim', opts = {} },
    {
      'mason-org/mason-lspconfig.nvim',
      dependencies = { 'mason-org/mason.nvim', 'neovim/nvim-lspconfig' },
      opts = { ensure_installed = require('mattrix.languages').servers() },
    },
    {
      'nvim-treesitter/nvim-treesitter',
      build = ':TSUpdate',
      config = function()
        local treesitter = require('nvim-treesitter')
        if vim.fn.executable('tree-sitter') == 1 then
          treesitter.install({
            'bash', 'dockerfile', 'hcl', 'json', 'lua', 'markdown', 'powershell',
            'python', 'rust', 'yaml',
          })
        else
          vim.notify('Install tree-sitter-cli to install Treesitter parsers.', vim.log.levels.WARN)
        end

        local group = vim.api.nvim_create_augroup('mattrix-treesitter', { clear = true })
        vim.api.nvim_create_autocmd('FileType', {
          group = group,
          callback = function(event)
            pcall(vim.treesitter.start, event.buf)
          end,
        })
      end,
    },
    {
      'nvim-telescope/telescope.nvim',
      dependencies = { 'nvim-lua/plenary.nvim' },
      opts = {},
    },
    { 'stevearc/conform.nvim', config = function() require('mattrix.format') end },
  },
  install = { colorscheme = { 'habamax' } },
  checker = { enabled = false },
})
