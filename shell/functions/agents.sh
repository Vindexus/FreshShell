# Agent config helpers.

# Copy the shared agent rules into the current project. Keeps existing files.
#   Usage: copy-agent-rules
copy-agent-rules() {
  mkdir -p .claude
  cp -r --update=none ~/.fresh/source/Vindexus/FreshShell/agents/rules .claude/
}
