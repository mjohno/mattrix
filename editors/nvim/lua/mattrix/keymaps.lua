local map = vim.keymap.set

for _, key in ipairs({
  '<Up>', '<Down>', '<Left>', '<Right>', '<Insert>', '<Delete>',
  '<Home>', '<End>', '<PageUp>', '<PageDown>',
}) do
  map({ 'n', 'i', 'v' }, key, '<Nop>')
end

map('n', '<leader>ff', '<cmd>Telescope find_files<cr>', { desc = 'Find files' })
map('n', '<leader>fg', '<cmd>Telescope live_grep<cr>', { desc = 'Search text' })
map('n', '<leader>fb', '<cmd>Telescope buffers<cr>', { desc = 'Find buffers' })
map('n', '<leader>e', '<cmd>Explore<cr>', { desc = 'Browse directory' })
map('n', '<leader>f', function()
  require('conform').format({ lsp_format = 'fallback' })
end, { desc = 'Format buffer' })
