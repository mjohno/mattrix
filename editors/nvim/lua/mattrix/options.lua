vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

local undo_dir = vim.fn.stdpath('state') .. '/undo'
vim.fn.mkdir(undo_dir, 'p')

vim.opt.number = true
vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.wrap = false
vim.opt.colorcolumn = '80'
vim.opt.softtabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true
vim.opt.undodir = undo_dir
vim.opt.undofile = true
vim.opt.termguicolors = true
vim.opt.completeopt = { 'menuone', 'noinsert' }
