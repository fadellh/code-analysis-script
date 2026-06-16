#!/usr/bin/env python3
"""Analyze the last N days of git commits into a markdown quality + hours report.

Usage:  python analyze.py [repo] [--author NAME] [--days 7] [--max-commits 15]
                          [--output report.md] [--model llama-3.3-70b-versatile]
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from dotenv import load_dotenv

import gitlog
import report
from analysis import analyze_commit
from heuristic import baseline_hours, commit_gap_hours


def _previous_timestamp(commits, idx):
    """The timestamp of the next-older commit by the SAME author (gap is per-author)."""
    author_email = commits[idx].author_email
    for j in range(idx + 1, len(commits)):
        if commits[j].author_email == author_email:
            return commits[j].timestamp
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Git commit quality + hours analyzer")
    parser.add_argument("repo", nargs="?", default=".", help="path to git repo (default: .)")
    parser.add_argument("--author", default=None, help="filter to this author (default: all)")
    parser.add_argument("--days", type=int, default=7, help="look back this many days (default: 7)")
    parser.add_argument("--max-commits", type=int, default=15, help="cap commits analyzed (default: 15)")
    parser.add_argument("--output", default=None, help="write report to this file (default: stdout)")
    parser.add_argument("--model", default="llama-3.3-70b-versatile", help="Groq model")
    args = parser.parse_args()

    load_dotenv()

    if not gitlog.is_git_repo(args.repo):
        print(f"error: '{args.repo}' is not a git repository", file=sys.stderr)
        return 1

    branch = gitlog.current_branch(args.repo)
    commits, total = gitlog.pull_commits(
        args.repo, days=args.days, author=args.author, max_commits=args.max_commits
    )
    if not commits:
        who = f" by {args.author}" if args.author else ""
        print(f"No commits found in the last {args.days} days{who} on branch '{branch}'.")
        return 0

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("error: GROQ_API_KEY is not set. Add it to a .env file or export it.",
              file=sys.stderr)
        return 1

    from groq import Groq

    client = Groq(api_key=api_key)

    items = []
    for idx, c in enumerate(commits):
        baseline = baseline_hours(c.insertions, c.deletions, c.files_changed)
        gap = commit_gap_hours(c.timestamp, _previous_timestamp(commits, idx))
        print(f"analyzing {c.short_hash} ({idx + 1}/{len(commits)})...", file=sys.stderr)
        analysis = analyze_commit(client, args.model, c, baseline, gap)
        items.append((c, analysis, baseline, gap))
        if idx + 1 < len(commits):
            time.sleep(1.0)  # pace requests to respect Groq's tokens-per-minute window

    md = report.render_report(
        items, repo=args.repo, branch=branch, days=args.days,
        total_in_window=total, author=args.author,
    )
    if args.output:
        with open(args.output, "w") as f:
            f.write(md)
        print(f"wrote report to {args.output}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
