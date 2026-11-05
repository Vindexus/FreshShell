# Working with me

Project instructions take priority over this file when they conflict.

## Decisions

Decide on your own when a choice is easy to change later, and tell me what you
chose and why. Stop and ask when it's expensive to undo or shapes the code
around it, such as public interfaces, data models, folder structure, new
patterns, or anything destructive. When you ask, give your recommendation and
the alternatives.

## Scope

Lean towards mentioning nearby problems rather than fixing them. Only fix one
if it's related to the active work and small.

## Git

- Start work on a new branch in a worktree.
- Commit and push to that branch by default.
- Never push to `main`.
- After pushing, give me the link to the open pull request, or the link to
  create one if there isn't one yet.

## Verification

- After each small batch of work, run the unit tests for the files you touched.
- At the very end, run the full unit tests, lint, and typecheck.

## Dependencies

Don't add a new dependency without asking.

## Communication

Say what you're doing and why. Show code samples, function contracts,
types and interfaces, and folder structures as you work, so I can catch code
smells early.
