# Fresh auto-update helpers.

# Update fresh sources now, then re-source the rebuilt shell so the changes
# apply to the *current* shell. Skips the daily throttle entirely.
#
# Re-sources ~/.fresh/build/shell.sh, NOT ~/.zshrc, so there is no infinite
# loop: these functions are only ever *called* from ~/.zshrc, never sourced.
fresh_update() {
  command -v fresh >/dev/null 2>&1 || return 0

  if fresh update; then
    touch ~/.fresh/.last-update
    source ~/.fresh/build/shell.sh
  fi
}

# Run fresh_update at most once per day. Call this at the very bottom of
# ~/.zshrc (after the line that sources ~/.fresh/build/shell.sh, since that's
# where these functions are defined):
#
#   fresh_daily_update
fresh_daily_update() {
  local stamp=~/.fresh/.last-update

  # Skip if we updated within the last day (stamp exists and is <24h old).
  if [[ -f "$stamp" && -z "$(find "$stamp" -mtime +1 2>/dev/null)" ]]; then
    return 0
  fi

  fresh_update
}
