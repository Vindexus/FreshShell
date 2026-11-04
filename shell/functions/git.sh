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
