# Changelog

All notable changes to the commit analyzer are documented here.

## [Unreleased]

### Added
- Per-commit code-quality scorecard (readability, structure, naming, error handling,
  test coverage), each 1–5 with a one-line reason grounded in the diff.
- Per-commit hours estimate combining a deterministic size baseline with an LLM
  complexity judgment, plus a commit-gap sanity check, a confidence level, and reasoning.
- Deterministic overall summary (totals, averages, highlights) — no extra LLM call.
- Deterministic commit classification: documentation-only commits are reported with an
  hours estimate but no code-quality scorecard, and are excluded from quality averages.

### Changed
- Quality rubric no longer lets code commits hide behind a "non-code" label: source code
  that changes logic without adding tests is now scored low on test coverage, not marked
  not-applicable.

### Notes
- Commit data comes from local git only (no GitHub API, no token).
- One LLM call per commit via Groq (`llama-3.3-70b-versatile`, JSON mode).
