local configurations = require('mattrix.languages').configurations()

vim.diagnostic.config({
  severity_sort = true,
  float = { border = 'rounded', source = 'if_many' },
  signs = true,
  underline = true,
  update_in_insert = false,
  virtual_text = true,
})

local group = vim.api.nvim_create_augroup('mattrix-lsp', { clear = true })
vim.api.nvim_create_autocmd('LspAttach', {
  group = group,
  callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    if client and client:supports_method('textDocument/completion') then
      vim.lsp.completion.enable(true, client.id, event.buf, { autotrigger = true })
    end

    local map = function(keys, action, description)
      vim.keymap.set('n', keys, action, { buffer = event.buf, desc = description })
    end
    map('gd', vim.lsp.buf.definition, 'Go to definition')
    map('gr', vim.lsp.buf.references, 'Find references')
    map('K', vim.lsp.buf.hover, 'Hover documentation')
    map('<leader>rn', vim.lsp.buf.rename, 'Rename symbol')
    map('<leader>ca', vim.lsp.buf.code_action, 'Code action')
    map('[d', function() vim.diagnostic.jump({ count = -1 }) end, 'Previous diagnostic')
    map(']d', function() vim.diagnostic.jump({ count = 1 }) end, 'Next diagnostic')
  end,
})

for server, configuration in pairs(configurations) do
  vim.lsp.config(server, configuration)
  vim.lsp.enable(server)
end
