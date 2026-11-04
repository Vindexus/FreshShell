# FreshShell

My shell aliases, functions, and custom scripts, managed with
[fresh](https://freshshell.com).

## Layout

```
.freshrc.sample      fresh manifest — lists what to load
shell/               files sourced into the shell
  aliases/           alias definitions
  functions/         shell function definitions
git/                 git config, included from ~/.gitconfig
bin/                 standalone executables (linked via --bin)
agents/              agent instructions and shared rules
```

## Usage

1. Reference these files from your `~/.freshrc`. The canonical list lives in
   this repo's [`.freshrc.sample`](./.freshrc.sample) — copy those `fresh …`
   lines into your `~/.freshrc`, or symlink it:

   ```sh
   ln -sf ~/github/freshshell/.freshrc.sample ~/.freshrc
   ```

2. Push any changes here, then rebuild your shell config and reload. fresh
   builds from its own clone of this repo, not from this working copy:

   ```sh
   fresh update
   source ~/.fresh/build/shell.sh   # already sourced by ~/.bashrc on login
   ```

## Agent config

`agents/AGENTS.md` is how I work with agents. fresh installs it as
`~/.claude/CLAUDE.md`, so it applies everywhere.

`agents/rules/` holds code standards shared across projects. Copy them into a
project from its root folder, then commit them there:

```sh
copy-agent-rules
```

To bring improvements back, run `/pull-changes <project-path>` in Claude Code
from this repo. It commits to the current branch.
