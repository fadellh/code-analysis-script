"""Pull commit data from a local git repo via subprocess (no GitHub API, no token)."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime

UNIT_SEP = "\x1f"  # field separator that will not appear in commit metadata
DIFF_TRUNCATE_CHARS = 12_000  # keep diffs within Groq's tokens-per-minute window


@dataclass
class CommitData:
    hash: str
    short_hash: str
    subject: str
    body: str
    author: str
    author_email: str
    timestamp: datetime
    files_changed: int
    insertions: int
    deletions: int
    diff: str
    diff_truncated: bool = False


class GitError(RuntimeError):
    """Raised when a git command fails or the path is not a repo."""


def _run_git(repo: str, args: list[str]) -> str:
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def is_git_repo(repo: str) -> bool:
    try:
        return _run_git(repo, ["rev-parse", "--is-inside-work-tree"]).strip() == "true"
    except GitError:
        return False


def current_branch(repo: str) -> str:
    try:
        return _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    except GitError:
        return "(unknown)"


def has_commits(repo: str) -> bool:
    """False on an unborn branch (a brand-new repo with no commits yet)."""
    try:
        _run_git(repo, ["rev-parse", "--verify", "HEAD"])
        return True
    except GitError:
        return False


def parse_numstat(text: str) -> tuple[int, int, int]:
    """Parse `git show --numstat` output -> (files_changed, insertions, deletions).

    Each data line is `<added>\\t<deleted>\\t<path>`. Binary files report `-` for the
    counts; we count them as a changed file contributing 0 insertions/deletions.
    """
    files = insertions = deletions = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted = parts[0], parts[1]
        files += 1
        if added.isdigit():
            insertions += int(added)
        if deleted.isdigit():
            deletions += int(deleted)
    return files, insertions, deletions


def _list_hashes(repo: str, days: int, author: str | None) -> list[str]:
    args = ["log", "--no-merges", f"--since={days} days ago", "--pretty=%H"]
    if author:
        args.append(f"--author={author}")
    return [h for h in _run_git(repo, args).splitlines() if h.strip()]


def _load_commit(repo: str, h: str) -> CommitData:
    fmt = UNIT_SEP.join(["%H", "%h", "%an", "%ae", "%aI", "%s", "%b"])
    fields = _run_git(repo, ["show", "-s", f"--format={fmt}", h]).rstrip("\n").split(UNIT_SEP)
    full_hash, short, an, ae, aiso, subject = fields[:6]
    body = fields[6].strip() if len(fields) > 6 else ""

    files, ins, dels = parse_numstat(_run_git(repo, ["show", h, "--numstat", "--format="]))

    diff = _run_git(repo, ["show", h, "-p", "--format="]).strip("\n")
    truncated = len(diff) > DIFF_TRUNCATE_CHARS
    if truncated:
        diff = diff[:DIFF_TRUNCATE_CHARS] + (
            f"\n\n[diff truncated: showing {DIFF_TRUNCATE_CHARS} of {len(diff)} chars]"
        )

    return CommitData(
        hash=full_hash,
        short_hash=short,
        subject=subject,
        body=body,
        author=an,
        author_email=ae,
        timestamp=datetime.fromisoformat(aiso),
        files_changed=files,
        insertions=ins,
        deletions=dels,
        diff=diff,
        diff_truncated=truncated,
    )


def pull_commits(
    repo: str, days: int = 7, author: str | None = None, max_commits: int = 15
) -> tuple[list[CommitData], int]:
    """Return (commits, total_in_window). Commits are newest-first, capped at max_commits."""
    if not has_commits(repo):
        return [], 0
    hashes = _list_hashes(repo, days, author)
    commits = [_load_commit(repo, h) for h in hashes[:max_commits]]
    return commits, len(hashes)
