# Git aliases.

alias ga="git add"
alias gap="git add -p"
alias gc="git commit -m"
alias gca="git commit --amend"
alias gco="git checkout"
alias gcb="git checkout -b"
alias gd="git diff"
alias gs="git status"
alias gfo="git fetch origin"
_gfo_complete() {
  COMPREPLY=($(compgen -W "$(git for-each-ref --format='%(refname:lstrip=3)' refs/remotes/origin/ 2>/dev/null)" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _gfo_complete gfo
alias gpf="git puff"
alias gff="git ff"
alias glb="git lb"
alias glbd="git lbd"
alias glg="git lg"
alias gbd="git brand -D"

# Git's completion loads on first use, and __git_complete needs it loaded.
if declare -F _completion_loader >/dev/null; then
  _completion_loader git
fi

if declare -F __git_complete >/dev/null; then
  __git_complete ga _git_add
  __git_complete gap _git_add
  __git_complete gco _git_checkout
  __git_complete gd _git_diff
  __git_complete gff _git_merge
  __git_complete glg _git_log
  __git_complete gbd _git_branch
fi
