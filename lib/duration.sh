# Duration helpers shared by scripts in bin/ and shell functions.
#
# Safe to source into an interactive shell: defines functions only.

# parse_duration <spec>
#   Converts a duration like 30m, 1h, 2d or 1w to seconds and prints it.
#   Units: m (minutes), h (hours), d (days), w (weeks).
#   Returns 1 and prints nothing when the spec isn't valid.
parse_duration() {
  local spec="$1"

  if [[ ! "$spec" =~ ^([0-9]+)([mhdw])$ ]]; then
    return 1
  fi

  local amount=$((10#${BASH_REMATCH[1]}))
  local unit_seconds
  case "${BASH_REMATCH[2]}" in
    m) unit_seconds=60 ;;
    h) unit_seconds=3600 ;;
    d) unit_seconds=86400 ;;
    w) unit_seconds=604800 ;;
  esac

  echo $((amount * unit_seconds))
}
