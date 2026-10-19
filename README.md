# FreshShell

My shell aliases, functions, and custom scripts, managed with
[fresh](https://freshshell.com).

## Layout

```
freshrc              fresh manifest — lists what to load
shell/               files sourced into the shell
  aliases/           alias definitions
  functions/         shell function definitions
bin/                 standalone executables (linked via --bin)
```

## Usage

1. Push this repo to GitHub (`ColinElective/FreshShell`).
2. Reference these files from your `~/.freshrc`. The canonical list lives in
   this repo's [`freshrc`](./freshrc) — copy those `fresh …` lines into your
   `~/.freshrc`, or symlink it:

   ```sh
   ln -sf ~/code/freshshell/freshrc ~/.freshrc
   ```

3. Rebuild your shell config and reload:

   ```sh
   fresh
   source ~/.fresh/build/shell.sh   # already sourced by ~/.zshrc on login
   ```

## `mrpost`

Generates the code-review message to paste into the review channel. Run it
inside a GitLab repo:

```sh
mrpost            # print the message and copy it to the clipboard
mrpost --no-copy  # print it without touching the clipboard
mrpost --prev     # re-copy the last saved message, no GitLab calls
```

`--prev` (or `-p`) is for when you generated a message and then forgot to
actually post it: it reprints the most recent saved copy and puts it back on
the clipboard. It touches nothing on GitLab — it doesn't even need `glab`
installed — and records nothing new, since that run already counted as a post
and this is the same message finally reaching the channel.

While it works it shows a single self-overwriting progress line on stderr
(`Fetching MR 1464... (3 of 5)`), so a slow run doesn't look hung. It's
suppressed when stderr isn't a terminal, so pipes and logs stay clean.

It lists your open, non-draft merge requests, oldest first, so the ones that
have been waiting longest lead the message:

```
!401 — Bump node to 22
https://gitlab.com/wize-apps/web/-/merge_requests/401
Ready for review 2 weeks ago

!412 — Fix phone input validation
https://gitlab.com/wize-apps/web/-/merge_requests/412
Ready for review 3 days ago

!418 — Add retry to sync worker
https://gitlab.com/wize-apps/web/-/merge_requests/418
Ready for review 6 hours ago
```

The age is measured from when the MR became **reviewable**, not when it was
opened — a week spent in draft shouldn't read as a week of people ignoring it.
GitLab records the flip as a system note (`marked this merge request as
**ready**`); the newest one wins, since an MR can be flipped more than once. An
MR opened ready has no such note, and for it the creation date *is* the ready
date, so the wording stays true either way.

Deliberately plain text — the chat composer does not interpret markdown on
paste, so any asterisks would show up literally.

### Post history

Every run saves a copy of the message to `$MRPOST_DIR` — by default `.mrpost`
at the repository root, created if missing — as `YYYY-MM-DD-HHMMSS.txt`.
Anchoring to the repo root rather than the working directory matters in a
monorepo: otherwise running from the root and from `apps/core-api` would build
two histories that can't see each other, and the counts would under-report. Those copies are the record of
what has already gone out: **each run is assumed to be posted**, so one file is
one post.

Pass `--post-count` (or `-pc`) and each MR gains `- Posted here N times`,
counted from that history — N counts *files*, not mentions, so a link named
twice in one message still only counts once. An MR appearing for the first time
gets no suffix; from its second appearance onwards the count shows.

The flag is off by default, since naming the count in the channel is a pointed
thing to do. History is recorded either way, so turning it on later still
reports every message that has already gone out.

Re-running by accident does not inflate the history. If the message matches the
previous one, no new file is written and it says so:

```
Same message as 2026-08-31 09:11 - not recording it again.
```

This is why ages are rounded to the hour — "Ready for review 6 hours ago",
never "…12 minutes ago". A finer unit would make the text change between two
runs minutes apart and every repeat would look like a fresh post. The
comparison also ignores the `- Posted here N times` suffix, since that
necessarily differs between a first and second run and would otherwise stop any
repeat from ever matching.

Two consequences: an MR under an hour old reads "Ready for review less than an
hour ago",
and a repeat run that straddles an hour boundary does write a new file, because
the message genuinely changed.

Worth adding `.mrpost/` to the `.gitignore` of any repo you run this in.

### Approved MRs

An approval means the review already happened, so an MR with **any** approval is
dropped from the message automatically — no prompt. The dropped ones are listed
on stderr, below the message, so they stay out of the paste buffer and out of
the saved history:

```
Dropped 2 approved MRs:
  !401 approved by @snaer https://gitlab.com/.../401
  !412 approved by @christofferjohansen, @edmond13 https://gitlab.com/.../412
```

The test is `approved_by` being non-empty, deliberately not `approvals_left ==
0` — a project that requires no approvals reports zero left from the moment an
MR opens, which would drop everything before anyone had looked at it.

### Re-review

An MR that has had a review round you have since answered is asked about as a
second look rather than a first, so the channel can see it is not starting from
nothing:

```
!1523 — Fix the thing
https://gitlab.com/.../1523
Ready for re-review 2 hours ago (last reviewed 2 days ago by @bgerude)
```

The round is whichever came last: the newest review comment (counted by the
same rules as the review-comment check below) or the newest *approved this
merge request* note, in which case it reads "last approved". The re-review age
counts from your first answer after it, and the MR is sorted by that date
rather than by when it first went ready:

- after **comments**, only a push. A reply on its own doesn't count, since it
  usually means the work is still to come, and posting the MR then invites an
  "I already reviewed that". With no push since the newest review comment the
  MR stays plain "Ready for review" and goes through the comment prompt.
- after an **approval**, only once the approval has gone. A push, a revoke or
  a reset note marks when. The reset is detected from the approval going
  missing rather than from GitLab's reset note, since not every GitLab version
  writes one, so an approval that vanished with no note is dated from the
  approval itself.

A round with a push since skips the comment prompt: it is back with the reviewers.

### Merge conflicts

An MR that won't merge can't be usefully reviewed, so any with `conflicts: true`
is dropped from the message and listed on stderr afterwards:

```
Skipped 2 MRs with merge conflicts:
  !1523 https://gitlab.com/.../1523
  !1524 https://gitlab.com/.../1524
```

Checked *before* approvals, so an approved MR that has since gone stale is
reported as needing a rebase rather than filed under "already done".

One limit: GitLab computes mergeability lazily, and an MR it hasn't got to yet
reports `UNCHECKED` with `conflicts: false`. Such an MR stays in the message
even if it would in fact conflict — the error falls on the side of nagging
about one too many rather than silently dropping one.

### Review-comment check

Before an MR goes into the message, `mrpost` checks it for review comments with
no push after them. Those usually mean the next move is yours, so nagging the
channel may be the wrong move. If it finds any, it asks:

```
MR 412 has 1 comment from @valentina824026 https://gitlab.com/...
Post anyway? y/N
```

Answering no drops that MR from the message and from the saved history, so it
does not accrue a post count for a message it never appeared in. `-y`/`--yes`
skips the prompting entirely. Prompts go to stderr and read from the terminal,
so `mrpost | pbcopy` still works.

Three kinds of note are ignored, or the prompt would fire on nearly every MR:

- **System notes** — label changes, assignments, pushes. *approved this merge
  request* is one of these, which is why approvals are handled separately
  above rather than through the comment check.
- **Integration accounts** — CodeRabbit and Linear both post as `ghost1`, which
  accounts for roughly 80% of all non-system comments on `wize-apps/web`.
  Override with `MRPOST_IGNORE_COMMENTERS` (comma-separated; set it empty to
  disable the filter).
- **Your own comments** — context you added yourself, not a review.
- **The Nx Cloud CI summary** — it posts under a real person's GitLab account
  rather than a bot's, so it can't be filtered by username without losing that
  person's genuine reviews. It's matched instead on the marker it signs its
  body with, `NX_CLOUD_APP_COMMENT_END` (`MRPOST_NOTICE_MARKER`; blank it to
  switch the rule off). On `wize-apps/apps` this notice appears on roughly
  four MRs in five, so without it the prompt would fire almost every time.

`MRPOST_AUTHOR` overrides the GitLab username, which otherwise comes from
whoever `glab` is logged in as.

### One request, not 2N+1

Everything — the MR list, each MR's approvals, and each MR's full note history —
arrives in a single GraphQL query via `glab api graphql`. The REST equivalent
needed one list call plus two per MR: on a 12-MR list that was 25 round trips
taking ~14s, against ~2s now.

The project is derived from your `origin` remote rather than looked up, so that
stays one request. Set `MRPOST_AUTHOR` and it really is one: otherwise there is
a second small call to ask `glab` who you are.

Notes come 100 to a page. An MR with more is paged through afterwards, one
extra request per extra page, so its ready date, approvals and review comments
are read from the full history — only the rare long MR costs anything. If one
of those follow-up requests fails, `mrpost` warns that the MR's notes may be
incomplete and carries on with what it has.

The MR list itself is not paged: the query asks for the first 100 of your open
MRs, which is far out of reach.

## Notes

- Homebrew paths resolve via `brew --prefix`, so they work on both Apple
  Silicon and Intel Macs.
- Some functions/aliases are specific to the `core-api` monorepo and its
  branches (e.g. `staging`, `deprecation-station`, the `apps/core-api` test
  aliases) — useful to teammates on that repo, harmless to anyone else.
