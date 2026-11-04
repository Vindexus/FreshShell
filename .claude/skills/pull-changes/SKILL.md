---
name: pull-changes
description: Bring improvements to shared agent files from another project back into FreshShell.
argument-hint: <project-path>
disable-model-invocation: true
---

Compare the project at $ARGUMENTS with this repo. Files in `agents/rules/`
match `.claude/rules/` in the project, and `agents/skills/` matches
`.claude/skills/`.

1. Compare the files that exist on both sides. List any rule or skill that
   only exists in the project, and ask whether it belongs here.
2. Check `git log` on both sides before calling a difference an improvement.
   The project's copy may just be older.
3. Take in changes that would help any project. Leave out project details,
   and reword general lessons so they don't mention the project. This repo
   is public.
4. Ask me about anything unclear.
5. Show me the proposed changes. Once I agree, commit them to the current
   branch.
