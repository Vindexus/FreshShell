# Load nvm (Node Version Manager) and select the project's Node version.
# Requires NVM_DIR to be exported first (see shell/env.sh).

echo "Setting up nvm"

BREW_PREFIX="${BREW_PREFIX:-$(brew --prefix 2>/dev/null)}"

# This loads nvm
[ -s "$BREW_PREFIX/opt/nvm/nvm.sh" ] && \. "$BREW_PREFIX/opt/nvm/nvm.sh"
# This loads nvm bash_completion
[ -s "$BREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm" ] && \. "$BREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm"

# Use the Node version specified by the current directory's .nvmrc (if any).
nvm use
