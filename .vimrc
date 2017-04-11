" styles
highlight ExtraWhitespace ctermbg=red guibg=red


" filetypes
au BufNewFile,BufRead *.py
    \ set shiftwidth=4 | " indent as 4 spaces
    \ set softtabstop=4 | " TAB/BACKSPACE as 4 spaces
    \ set tabstop=4 | " tab displays as 4 spaces
    \ set textwidth=79 " lines longer than 79 spaces will be broken
au BufNewFile,BufRead *.py,*.pyw,*.c,*.h,*.cpp,*.hpp
    \ match ExtraWhitespace /\s\+$/ " show tailing spaces


" basic
set autoindent " align new line indent with the previous line
set encoding=utf8
set expandtab " replace tab with space
set fileformat=unix
set hlsearch " highlight search
set ignorecase " case insensitive search
set incsearch " search as characters are entered
set laststatus=2
set number " show line number
set shiftround " always indent to multiple of shiftwidth
set showmatch " show match on [{()}]
set smartcase " case insensitive search
set wildmode=longest,list,full
set wildmenu
syntax on


" control split
nnoremap <C-H> <C-W><C-H>
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>


" Enable folding
set foldenable
set foldlevelstart=10
set foldmethod=indent
set foldnestmax=0
nnoremap <space> za

" smart home key
:map <Home> ^
:imap <Home> <Esc>I

" Vundle!
set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" run vim +PluginInstall +qall to install addons!
Plugin 'VundleVim/Vundle.vim' " require
Plugin 'fisadev/vim-isort'
Plugin 'taglist.vim'
Plugin 'ervandew/supertab'
Bundle 'Lokaltog/powerline', {'rtp': 'powerline/bindings/vim/'}
Bundle 'scrooloose/nerdtree'
Bundle 'klen/python-mode'

call vundle#end()
filetype plugin indent on


" taglist
let Tlist_File_Fold_Auto_Close=1
let Tlist_Show_One_File=1
let Tlist_Sort_Type='name'
let Tlist_Use_Right_Window=1
let Tlist_Auto_Open=1


" pymode
set completeopt=menu
let g:pymode_rope=0
let g:pymode_run=1
let g:pymode_run_bind='<F5>'


" startup scripts
autocmd VimEnter * NERDTree
autocmd VimEnter * wincmd p
autocmd BufEnter * call CheckLeftBuffers()


" exit scripts
autocmd BufWritePre *.py :Isort
autocmd BufWritePre *.py,*.css,*.js,*.html :%s/\s\+$//e


" function declarations
function! CheckLeftBuffers()
  if tabpagenr('$') == 1
    let i = 1
    while i <= winnr('$')
      if getbufvar(winbufnr(i), '&buftype') == 'help' ||
        \ getbufvar(winbufnr(i), '&buftype') == 'quickfix' ||
        \ exists('t:NERDTreeBufName') &&
        \   bufname(winbufnr(i)) == t:NERDTreeBufName ||
        \ bufname(winbufnr(i)) == '__Tag_List__'
        let i += 1
      else
        break
      endif
    endwhile
    if i == winnr('$') + 1
      qall
    endif
    unlet i
    endif
endfunction

