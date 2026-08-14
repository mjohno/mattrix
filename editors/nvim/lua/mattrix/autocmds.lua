local group = vim.api.nvim_create_augroup('mattrix', { clear = true })

vim.api.nvim_create_autocmd({ 'BufRead', 'BufNewFile' }, {
  group = group,
  pattern = '*Jenkinsfile*',
  command = 'setfiletype groovy',
})

vim.api.nvim_create_autocmd({ 'BufRead', 'BufNewFile' }, {
  group = group,
  pattern = {
    '*/playbooks/*.yaml', '*/playbooks/*.yml',
    '*/roles/*/tasks/*.yaml', '*/roles/*/tasks/*.yml',
    '*/roles/*/handlers/*.yaml', '*/roles/*/handlers/*.yml',
    '*/roles/*/defaults/*.yaml', '*/roles/*/defaults/*.yml',
    '*/roles/*/vars/*.yaml', '*/roles/*/vars/*.yml',
  },
  command = 'setfiletype yaml.ansible',
})
