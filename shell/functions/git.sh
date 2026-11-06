# Git workflow functions.

# Squash a feature branch into a single commit that follows the tip of a
# target branch. Saves a backup branch first.
#   Usage: git-squash <feature-branch> follows <target-branch>
function git-squash() {
  local feature="${1}"
  local onto_keyword="${2}"
  local target="${3}"

  if [[ -z "$feature" || -z "$onto_keyword" || -z "$target" ]]; then
    echo "Usage: git-squash <feature-branch> follows <target-branch>"
    return 1
  fi

  if [[ "$onto_keyword" != "follows" ]]; then
    echo "Error: second argument must be 'follows'"
    echo "Usage: git-squash <feature-branch> follows <target-branch>"
    return 1
  fi

  local backup="backup-${feature}"

  echo "This will squash '${feature}' into a single commit that follows the tip of '${target}'."
  echo "A backup will be saved as '${backup}'."
  echo -n "Continue? (y/N) "
  read confirm
  [[ "$confirm" != "y" && "$confirm" != "Y" ]] && echo "Aborted." && return 1

  git checkout "$feature" || return 1
  git branch -m "$feature" "$backup" || return 1
  git fetch origin "$target" || return 1
  git checkout -b "$feature" "origin/$target" || return 1
  git restore --source="$backup" --worktree --no-overlay -- . || return 1
  git add -A
  git commit -m "feat: squashed ${feature} onto ${target}"

  echo ""
  echo "Done! Backup saved as '${backup}'."
  echo "To push: git push --force-with-lease origin ${feature}"
  echo "To clean up backup later: git branch -D ${backup}"
}

# Reset a local branch to exactly match origin (destroys local changes).
#   Usage: breset <branch>
breset () {
  git fetch origin $1
  git checkout origin/$1
  git branch -D $1
  git checkout -b $1
}

# Print the URL of the open pull request for a branch, if there is one. Without
# a logged-in gh this can only see public repos.
_open_pr_url() {
  local repo="$1" branch="$2"
  local url=""

  if command -v gh >/dev/null; then
    url=$(gh pr list --repo "$repo" --head "$branch" --state open --json url --jq '.[0].url' 2>/dev/null)
  fi

  if [ -z "$url" ]; then
    url=$(curl -fsS -m 5 "https://api.github.com/repos/$repo/pulls?head=${repo%%/*}:$branch&state=open" 2>/dev/null \
      | grep -oiE "https://github\.com/$repo/pull/[0-9]+" | head -1)
  fi

  echo "$url"
}

# Print a link to a branch's open pull request, or to create one.
#   Usage: print_pr_link <branch>
print_pr_link() {
  local branch="$1"
  local repo pr_url

  if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
    return 0
  fi

  repo=$(git remote get-url origin 2>/dev/null \
    | sed -nE 's#^(git@github\.com:|ssh://git@github\.com/|https://github\.com/)(.*)#\2#p')
  repo="${repo%.git}"

  if [ -z "$repo" ]; then
    return 0
  fi

  pr_url=$(_open_pr_url "$repo" "$branch")

  if [ -n "$pr_url" ]; then
    echo "PR: $pr_url"
  else
    echo "Create PR: https://github.com/$repo/pull/new/$branch"
  fi
}

# Push to origin, then print the pull request link. GitHub only prints its own
# link when a push sends something new.
#   Usage: gpo [git push arguments]
gpo() {
  local branch arg

  git push origin "$@" || return $?

  branch=$(git branch --show-current)
  for arg in "$@"; do
    case "$arg" in
      -*) ;;
      HEAD) ;;
      *) branch="${arg##*:}" ;;
    esac
  done

  print_pr_link "$branch"
}

_gpo_complete() {
  COMPREPLY=($(compgen -W "$(git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null)" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _gpo_complete gpo
