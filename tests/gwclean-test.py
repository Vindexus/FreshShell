#!/usr/bin/env python3
#
# Tests for bin/gwclean. Run with: python3 tests/gwclean-test.py
#
# Each test builds a real repo with a local bare "remote" in a temp folder.
# Worktrees are aged by backdating commit dates and their git admin files.

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GWCLEAN = Path(__file__).resolve().parent.parent / "bin" / "gwclean"
DAY = 86400


class Repo:
    def __init__(self, root, default_branch="main"):
        self.root = Path(root)
        self.main = self.root / "main"
        self.default = default_branch
        self.env = {
            **os.environ,
            "HOME": str(self.root),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
        remote = str(self.root / "remote.git")
        self.git("init", "--bare", "-b", default_branch, remote, cwd=self.root)
        self.git("clone", remote, str(self.main), cwd=self.root)
        self.git("checkout", "-b", default_branch)
        self.commit(self.main, "initial", days_ago=30)
        self.git("push", "-u", "origin", default_branch)

    def git(self, *args, cwd=None, env=None):
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.main,
            env=env or self.env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def commit(self, cwd, name, days_ago=0):
        (Path(cwd) / f"{name}.txt").write_text(name)
        self.git("add", ".", cwd=cwd)
        stamp = f"@{int(time.time() - days_ago * DAY)} +0000"
        env = {**self.env, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        self.git("commit", "-m", name, cwd=cwd, env=env)

    def worktree(self, name, days_ago=5, push=True):
        path = self.root / "worktrees" / name
        self.git("worktree", "add", "-b", name, str(path))
        self.commit(path, name, days_ago)
        if push:
            self.git("push", "-u", "origin", name, cwd=path)
        return path

    def age(self, path, days_ago):
        """Backdate the worktree's admin files so it looks idle."""
        admin = Path(self.git("rev-parse", "--path-format=absolute", "--git-dir", cwd=path))
        stamp = time.time() - days_ago * DAY
        for name in ("commondir", "index"):
            if (admin / name).exists():
                os.utime(admin / name, (stamp, stamp))

    def run(self, *args, cwd=None):
        return subprocess.run(
            [str(GWCLEAN), *args],
            cwd=cwd or self.main,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def has_branch(self, name):
        return name in self.git("branch", "--format=%(refname:short)").split()

    def worktree_count(self):
        return self.git("worktree", "list", "--porcelain").count("worktree ")

    def delete_remote_branch(self, name):
        self.git("push", "origin", "--delete", name)
        self.git("fetch", "--prune")


def removed(repo, path, name):
    return not path.exists() and not repo.has_branch(name)


def kept(repo, path, name):
    return path.exists() and repo.has_branch(name)


# --- Tests -----------------------------------------------------------------
# Each returns None on success or a failure message.


def test_removes_when_in_origin_branch(repo):
    path = repo.worktree("done")
    repo.age(path, 5)
    result = repo.run()
    if not removed(repo, path, "done"):
        return f"expected removal; output: {result.stdout}{result.stderr}"
    if "removed" not in result.stdout:
        return f"expected 'removed' line; got {result.stdout!r}"


def test_removes_when_in_local_main(repo):
    path = repo.worktree("merged-locally", push=False)
    repo.git("merge", "--no-ff", "-m", "merge", "merged-locally")
    repo.age(path, 5)
    result = repo.run()
    if not removed(repo, path, "merged-locally"):
        return f"expected removal; output: {result.stdout}{result.stderr}"


def test_removes_when_in_origin_main_after_remote_branch_deleted(repo):
    path = repo.worktree("merged-remotely")
    repo.git("push", "origin", f"merged-remotely:{repo.default}", cwd=path)
    repo.delete_remote_branch("merged-remotely")
    repo.age(path, 5)
    result = repo.run()
    if not removed(repo, path, "merged-remotely"):
        return f"expected removal; output: {result.stdout}{result.stderr}"


def test_keeps_squash_merged_with_remote_branch_deleted(repo):
    path = repo.worktree("squashed")
    repo.git("merge", "--squash", "squashed")
    repo.git("commit", "-m", "squash")
    repo.git("push")
    repo.delete_remote_branch("squashed")
    repo.age(path, 5)
    result = repo.run()
    if not kept(repo, path, "squashed"):
        return "squash-merged worktree was removed"
    if "commits not in main, origin/squashed or origin/main" not in result.stdout:
        return f"expected reason; got {result.stdout!r}"


def test_keeps_recent(repo):
    path = repo.worktree("recent", days_ago=1)
    repo.age(path, 1)
    repo.run()
    if not kept(repo, path, "recent"):
        return "recent worktree was removed"


def test_recent_index_write_counts_as_activity(repo):
    path = repo.worktree("old-commit-new-index", days_ago=10)
    repo.age(path, 10)
    admin = Path(repo.git("rev-parse", "--path-format=absolute", "--git-dir", cwd=path))
    os.utime(admin / "index")  # touched now
    repo.run()
    if not kept(repo, path, "old-commit-new-index"):
        return "worktree with a recent index write was removed"


def test_keeps_untracked_changes(repo):
    path = repo.worktree("dirty")
    (path / "scratch.txt").write_text("wip")
    repo.age(path, 5)
    result = repo.run()
    if not kept(repo, path, "dirty"):
        return "worktree with untracked file was removed"
    if "uncommitted changes" not in result.stdout:
        return f"expected reason; got {result.stdout!r}"


def test_keeps_modified_tracked_file(repo):
    path = repo.worktree("modified")
    (path / "modified.txt").write_text("changed")
    repo.age(path, 5)
    repo.run()
    if not kept(repo, path, "modified"):
        return "worktree with modified file was removed"


def test_keeps_commits_after_push(repo):
    path = repo.worktree("ahead")
    repo.commit(path, "extra", days_ago=5)
    repo.age(path, 5)
    result = repo.run()
    if not kept(repo, path, "ahead"):
        return "worktree with unpushed commit was removed"
    if "commits not in" not in result.stdout:
        return f"expected reason; got {result.stdout!r}"


def test_keeps_never_pushed(repo):
    path = repo.worktree("local-only", push=False)
    repo.age(path, 5)
    repo.run()
    if not kept(repo, path, "local-only"):
        return "never-pushed worktree was removed"


def test_default_branch_from_origin_head():
    with tempfile.TemporaryDirectory() as root:
        repo = Repo(root, default_branch="trunk")
        repo.git("remote", "set-head", "origin", "trunk")
        path = repo.worktree("into-trunk", push=False)
        repo.git("merge", "--no-ff", "-m", "merge", "into-trunk")
        repo.age(path, 5)
        result = repo.run()
        if not removed(repo, path, "into-trunk"):
            return f"didn't use origin/HEAD as default branch; output: {result.stdout}"


def test_default_branch_falls_back_to_master():
    with tempfile.TemporaryDirectory() as root:
        repo = Repo(root, default_branch="master")
        path = repo.worktree("into-master", push=False)
        repo.git("merge", "--no-ff", "-m", "merge", "into-master")
        repo.age(path, 5)
        result = repo.run()
        if not removed(repo, path, "into-master"):
            return f"didn't fall back to master; output: {result.stdout}"


def test_dry_run_changes_nothing(repo):
    path = repo.worktree("dry")
    repo.age(path, 5)
    result = repo.run("-n")
    if not kept(repo, path, "dry"):
        return "dry run removed the worktree"
    if "would remove" not in result.stdout:
        return f"expected 'would remove'; got {result.stdout!r}"


def test_custom_age(repo):
    path = repo.worktree("two-hours", days_ago=2 / 24)
    repo.age(path, 2 / 24)
    repo.run("3h")
    if not kept(repo, path, "two-hours"):
        return "2h-old worktree removed with 3h limit"
    repo.run("1h")
    if not removed(repo, path, "two-hours"):
        return "2h-old worktree kept with 1h limit"


def test_keeps_current_worktree(repo):
    path = repo.worktree("here")
    repo.age(path, 5)
    result = repo.run(cwd=path)
    if not kept(repo, path, "here"):
        return "removed the worktree gwclean ran from"
    if "you're in it" not in result.stdout:
        return f"expected reason; got {result.stdout!r}"


def test_keeps_locked(repo):
    path = repo.worktree("locked")
    repo.git("worktree", "lock", str(path))
    repo.age(path, 5)
    repo.run()
    if not kept(repo, path, "locked"):
        return "locked worktree was removed"


def test_keeps_detached(repo):
    # HEAD is in main, so only the detached check keeps it.
    path = repo.root / "worktrees" / "detached"
    repo.git("worktree", "add", "--detach", str(path))
    repo.age(path, 5)
    result = repo.run()
    if not path.exists():
        return "detached worktree was removed"
    if "(none): detached HEAD" not in result.stdout:
        return f"expected detached reason; got {result.stdout!r} {result.stderr!r}"


def test_quiet_prints_only_removals(repo):
    done = repo.worktree("q-done")
    repo.age(done, 5)
    recent = repo.worktree("q-recent", days_ago=0)
    result = repo.run("-q")
    lines = result.stdout.strip().splitlines()
    if len(lines) != 1 or not lines[0].startswith("removed") or "q-done" not in lines[0]:
        return f"expected one removal line; got {result.stdout!r}"
    if not kept(repo, recent, "q-recent"):
        return "recent worktree was removed"


def test_quiet_silent_when_nothing_to_do(repo):
    repo.worktree("q-quiet", days_ago=0)
    result = repo.run("-q")
    if result.stdout or result.stderr or result.returncode != 0:
        return f"expected silence; got {result.returncode} {result.stdout!r} {result.stderr!r}"


def test_prunes_deleted_worktree_folders(repo):
    path = repo.worktree("vanished")
    shutil.rmtree(path)
    repo.run()
    if repo.worktree_count() != 1:
        return "git still lists the deleted worktree"


def test_bad_age_is_usage_error(repo):
    result = repo.run("2x")
    if result.returncode != 2 or "invalid age" not in result.stderr:
        return f"expected exit 2; got {result.returncode} {result.stderr!r}"


def test_outside_repo(repo):
    outside = repo.root / "not-a-repo"
    outside.mkdir()
    loud = repo.run(cwd=outside)
    quiet = repo.run("-q", cwd=outside)
    if loud.returncode != 1 or "not a git repository" not in loud.stderr:
        return f"expected exit 1 with message; got {loud.returncode} {loud.stderr!r}"
    if quiet.returncode != 0 or quiet.stdout or quiet.stderr:
        return f"expected silent exit 0 with -q; got {quiet.returncode} {quiet.stderr!r}"


def main():
    tests = [(name, fn) for name, fn in globals().items() if name.startswith("test_")]
    failures = 0
    for name, test in tests:
        try:
            if test.__code__.co_argcount:
                with tempfile.TemporaryDirectory() as root:
                    error = test(Repo(root))
            else:
                error = test()
        except subprocess.CalledProcessError as e:
            error = f"setup failed: {e.cmd}: {e.stderr}"
        if error:
            failures += 1
            print(f"FAIL {name}: {error}")
    print(f"{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
