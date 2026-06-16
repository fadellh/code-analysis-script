# Commit Analyzer — Design

## Requirements
- Functional: pull a user's commits (last 7 days) → markdown report with code quality +
  estimated hours per commit, plus an overall summary.
- Non-functional: runs locally, no GitHub token, free LLM, language-agnostic.

## Core Entities
- `CommitData`: hash, message, timestamp, author, diff, stats (files, +/- lines), paths.
- `CommitAnalysis`: quality (per-dimension score + reason) and hours (estimate +
  step-by-step reasoning + confidence). Quality is omitted for documentation-only commits.

## Interface
- `pull_commits(repo, days, author)` → `list[CommitData]`   (git log --no-merges + git show)
- `analyze_commit(commit)` → `CommitAnalysis`               (Groq llama-3.3-70b, JSON mode + rubric, one call/commit)
- `render_report(items)` → markdown

## High-Level Design
```
git log --since=7d --no-merges  →  CommitData[]
   → classify each commit (code vs docs-only, deterministic)
   → per commit → Groq (llama-3.3-70b, JSON mode) + rubric → CommitAnalysis[]
   → deterministic markdown report
```

## Key Decisions (trade-offs)
- **Local git over GitHub API** → no token, zero setup to run, works on any repo.
- **`--no-merges`** → analyze authored code, not merges (avoids noise).
- **Deterministic size baseline + LLM complexity judgment** for hours → estimates are
  grounded in a transparent number, then adjusted for complexity, with a confidence level
  so there is no false precision.
- **Commit gap as a sanity-check only** → time between a commit and the author's previous
  one is a noisy signal (it includes breaks), so it bounds the estimate rather than driving it.
- **Per-commit analysis, not batched** → each commit is scored in isolation for accuracy;
  Groq's free tier comfortably handles the request volume.
- **Deterministic commit classification** → documentation-only commits get an hours
  estimate but no code-quality scorecard, and are excluded from quality averages.
