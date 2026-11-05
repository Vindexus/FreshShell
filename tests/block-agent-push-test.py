#!/usr/bin/env python3
#
# Tests for bin/block-agent-push. Run with: python3 tests/block-agent-push-test.py

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "bin" / "block-agent-push"
BLOCKED = 2
ALLOWED = 0


@dataclass
class TestCase:
    given: str
    when: str
    then: str
    branch: str
    command: str
    expect: int


def blocks(given, when, branch, command):
    return TestCase(given, when, "the push is blocked", branch, command, BLOCKED)


def allows(given, when, branch, command):
    return TestCase(given, when, "the command is allowed", branch, command, ALLOWED)


test_cases = [
    blocks("on a feature branch", "pushing main by name", "feature", "git push origin main"),
    blocks("on main", "pushing with no arguments", "main", "git push"),
    blocks("on main", "pushing with only a remote", "main", "git push origin"),
    blocks("on main", "pushing HEAD", "main", "git push origin HEAD"),
    blocks("on a feature branch", "pushing a branch onto main", "feature", "git push origin feature:main"),
    blocks("on a feature branch", "pushing HEAD onto main", "feature", "git push origin HEAD:main"),
    blocks("on a feature branch", "using a full ref", "feature", "git push origin HEAD:refs/heads/main"),
    blocks("on a feature branch", "force pushing main", "feature", "git push -f origin main"),
    blocks("on a feature branch", "using a plus refspec", "feature", "git push origin +main"),
    blocks("on a feature branch", "deleting main", "feature", "git push origin :main"),
    blocks("on a feature branch", "pushing master", "feature", "git push origin master"),
    blocks("on a feature branch", "pushing all branches", "feature", "git push --all origin"),
    blocks("on a feature branch", "chaining commands", "feature", "git add . && git commit -m x && git push origin main"),
    blocks("in a feature repo", "changing into a repo on main", "feature", "cd {main_repo} && git push"),
    blocks("in a feature repo", "targeting a repo on main", "feature", "git -C {main_repo} push"),
    blocks("on main", "redirecting output", "main", "git push origin 2>&1 | tail -3"),
    blocks("on a feature branch", "setting an env var first", "feature", "GIT_TRACE=1 git push origin main"),
    blocks("on a feature branch", "pushing on a later line", "feature", "echo hi\ngit push origin main"),
    allows("on a feature branch", "pushing with no arguments", "feature", "git push"),
    allows("on a feature branch", "pushing it by name", "feature", "git push origin feature"),
    allows("on a feature branch", "setting the upstream", "feature", "git push -u origin feature"),
    allows("on a feature branch", "pushing main onto another branch", "feature", "git push origin main:feature"),
    allows("on a feature branch", "pushing a similar name", "feature", "git push origin main-fixes"),
    allows("in a repo on main", "changing into a feature repo", "main", "cd {feature_repo} && git push"),
    allows("on main", "running another git command", "main", "git status"),
    allows("on main", "mentioning a push in a commit message", "main", "git commit -m 'git push origin main'"),
    allows("on main", "printing a push command", "main", "echo git push origin main"),
    allows("on a feature branch", "the command can't be parsed", "feature", "echo 'unterminated"),
]


def create_repo(path, branch):
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", branch], cwd=path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-q", "--allow-empty", "-m", "start"],
        cwd=path,
        check=True,
    )


def run_hook(command, cwd):
    payload = {"cwd": str(cwd), "tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run([HOOK], input=json.dumps(payload), capture_output=True, text=True)
    return result.returncode


def main():
    with tempfile.TemporaryDirectory() as directory:
        repos = {"main": Path(directory) / "on-main", "feature": Path(directory) / "on-feature"}
        for branch, path in repos.items():
            create_repo(path, branch)

        failures = 0
        for test_case in test_cases:
            command = test_case.command.format(main_repo=repos["main"], feature_repo=repos["feature"])
            actual = run_hook(command, repos[test_case.branch])
            passed = actual == test_case.expect
            failures += not passed
            status = "PASS" if passed else f"FAIL (exit {actual})"
            print(f"{status} GIVEN: {test_case.given} WHEN: {test_case.when} THEN: {test_case.then}")

    print(f"\n{len(test_cases) - failures} of {len(test_cases)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
