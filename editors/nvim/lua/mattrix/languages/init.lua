local M = {}

function M.servers()
  local servers = {
    'ansiblels', 'basedpyright', 'bashls', 'dockerls', 'jsonls', 'ruff',
    'rust_analyzer', 'terraformls', 'yamlls',
  }
  if vim.fn.has('win32') == 1 then
    table.insert(servers, 'powershell_es')
  end
  return servers
end

function M.configurations()
  local configurations = {
    ansiblels = require('mattrix.languages.ansible').lsp,
    basedpyright = require('mattrix.languages.python').lsp,
    ruff = require('mattrix.languages.python').ruff,
    bashls = require('mattrix.languages.bash').lsp,
    dockerls = require('mattrix.languages.docker').lsp,
    jsonls = require('mattrix.languages.json').lsp,
    rust_analyzer = require('mattrix.languages.rust').lsp,
    terraformls = require('mattrix.languages.terraform').lsp,
    yamlls = require('mattrix.languages.yaml').lsp,
  }
  if vim.fn.has('win32') == 1 then
    configurations.powershell_es = require('mattrix.languages.powershell').lsp
  end
  return configurations
end

return M
