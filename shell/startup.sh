# Login banner. Sourced last so it prints after everything is set up.

printf "\e[1;37mToday is \e[34m%s \e[35m%s\e[0m\n" "$(date '+%Y-%m-%d')" "$(date '+%H:%M:%S')"

# Clean up stale worktrees when a terminal opens in a repo, like a new Cursor
# session. Silent unless something gets removed.
if [[ -e .git ]] && command -v gwclean >/dev/null; then
  gwclean -q
fi
