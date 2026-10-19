# Environment variables, PATH, and shell theme.

# --- General ---------------------------------------------------------------
export DEBUG_COLORS=1
export NX_TUI=false
ZSH_THEME="robbyrussell"

# --- Homebrew prefix -------------------------------------------------------
# Resolve once so paths work on both Apple Silicon (/opt/homebrew) and
# Intel (/usr/local) Macs.
export BREW_PREFIX="${BREW_PREFIX:-$(brew --prefix 2>/dev/null)}"

# --- PATH -------------------------------------------------------------------
# libpq client tools (psql, pg_dump, etc.)
[ -d "$BREW_PREFIX/opt/libpq/bin" ] && export PATH="$BREW_PREFIX/opt/libpq/bin:$PATH"
# PostgreSQL 16 binaries
[ -d "$BREW_PREFIX/opt/postgresql@16/bin" ] && export PATH="$BREW_PREFIX/opt/postgresql@16/bin:$PATH"
# Personal executables
export PATH="$HOME/bin:$PATH"
# User-local binaries (pipx, etc.)
export PATH="$HOME/.local/bin:$PATH"

# --- nvm --------------------------------------------------------------------
export NVM_DIR="$HOME/.nvm"
