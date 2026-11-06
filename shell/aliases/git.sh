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
alias gpo="git push origin"
_gpo_complete() {
  COMPREPLY=($(compgen -W "$(git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null)" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _gpo_complete gpo
alias gpf="git puff"
alias glb="git lb"
alias glbd="git lbd"
alias glg="git lg"
