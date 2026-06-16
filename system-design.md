# Task 2 — Commit Analyzer (Design)

## Requirements
- Functional: pull my commits (last 7 days) → markdown report: quality + estimated hours per commit + summary.
- Non-functional: runs locally, no GitHub token, free LLM, language-agnostic.

## Core Entities
- CommitData: hash, message, timestamp, author, diff, stats (files, +/- lines).
- AnalysisResult: quality (score + reasons), hours (estimate + reasoning + confidence).

## Interface
- pull_commits(repo, since) → list[CommitData]   (git log --no-merges + git show)
- analyze(commits) → list[AnalysisResult]         (Groq llama-3.3-70b, structured JSON + rubric, one call/commit)
- render_report(results) → markdown

## High-Level Design
git log --since=7d --no-merges → CommitData[]
   → per-commit → Groq (llama-3.3-70b, JSON mode) + rubric system prompt → AnalysisResult[]
   → markdown report

## Key Decisions (trade-offs)
- Local git over GitHub API → no token, zero setup to run.
- --no-merges → analyze authored code, not merges (avoids noise).
- Hours grounded in diff complexity + timestamps, with a confidence → no false precision.
- Groq for the analyzer → it fires one call per commit; Groq's free tier has far higher
  request throughput.
- Per-commit analysis, not batched → each commit scored in isolation = more accurate.