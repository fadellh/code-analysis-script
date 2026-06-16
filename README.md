# Git Commit Analyzer

> A command-line tool that reads your recent git history and produces a markdown report
> rating **code quality** and **estimated hours** for every commit — powered by an LLM,
> grounded in real diff data.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LLM: Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-orange.svg)](https://groq.com/)

It pulls commits from the last 7 days of a repository, sends each one to an LLM with a
structured rubric, and renders a clean report you can drop into a standup, a retro, or a
weekly review.

---

## Why it exists

Reviewing a week of work by hand is slow and inconsistent. This tool gives every commit the
same structured treatment: a five-dimension quality scorecard with reasons, and an hours
estimate that combines a transparent size baseline with an LLM's judgment of complexity — so
the numbers are explainable, not magic.

## Features

- **Local git only** — reads history via `git log`/`git show`. No GitHub API, no token, works offline against any repo.
- **Per-commit quality scorecard** — readability, structure, naming, error handling, and test coverage, each scored 1–5 with a one-line reason grounded in the diff.
- **Explainable hours estimate** — a deterministic size baseline adjusted by the LLM for complexity, sanity-checked against the gap between commits, with a confidence level (no false precision).
- **Smart commit classification** — documentation-only commits get an hours estimate but skip the code-quality scorecard, and are excluded from quality averages.
- **Structured & validated** — the LLM replies in JSON mode and every response is validated with Pydantic, with a retry and a graceful degraded entry so one bad commit never breaks the run.
- **Deterministic summary** — totals, averages, and highlights are computed in code, so the report shape is consistent run to run.

## How it works

```
git log --since="7 days ago" --no-merges
        │
        ▼
   CommitData[]  ──►  classify (code vs docs-only)
        │
        ▼  one Groq call per commit (JSON mode + rubric)
   CommitAnalysis[]  ──►  validate with Pydantic
        │
        ▼
   deterministic markdown report
```

**The hours estimate is two layers.** A pure-Python baseline scores raw size (additions at
full weight, deletions at half, a small per-file overhead, ~150 effective lines/hour). The
LLM then *adjusts* that baseline for complexity — boilerplate scales down, novel logic scales
up — and uses the time gap since the author's previous commit only as an upper-bound sanity
check. Keeping the arithmetic in code and the judgment in the model is what makes the output
trustworthy instead of hand-wavy.

## Installation

Requires **Python 3.11+** and a free [Groq API key](https://console.groq.com/keys).

```bash
git clone https://github.com/fadellh/code-analysis-script.git
cd code-analysis-script

python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env        # then edit .env and add your key:  GROQ_API_KEY=gsk_...
```

## Usage

```bash
.venv/bin/python analyze.py [repo] [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `repo` (positional) | `.` | Path to the git repository to analyze |
| `--author NAME` | all | Only include commits by this author |
| `--days N` | `7` | Look-back window in days |
| `--max-commits N` | `15` | Cap on commits analyzed (also truncates very large diffs) |
| `--output FILE` | stdout | Write the markdown report to a file |
| `--model NAME` | `llama-3.3-70b-versatile` | Groq model to use |

```bash
# Analyze the current repo, print to the terminal
.venv/bin/python analyze.py .

# Analyze a specific repo, only your commits, write to a file
.venv/bin/python analyze.py ~/projects/api --author "Jane Doe" --output weekly-report.md
```

## Example report

```markdown
# Commit Analysis Report

_Repo: `.` · Branch: `main` · Window: last 7 days (2025-05-26 → 2025-06-02) · Author: all authors_

## Summary
- **Commits analyzed:** 4 — 3 code, 1 docs
- **Total estimated effort:** 9.5 h
- **Total churn:** +612/-87 across 14 files
- **Average quality (code only):** readability 4.3, structure 4.0, naming 4.7, error-handling 3.7, tests 2.7 → **overall 3.9/5**
- **Highlights:** highest quality `a1b2c3d` (4.4/5) · largest `e4f5a6b` (+243/-51)

Across 3 code commits plus 1 docs commit (hours only) totaling +612/-87 lines, estimated
effort is ~9.5 h. Code quality looks solid (avg 3.9/5). Hours are size-and-complexity
estimates with explicit confidence — read them as ranges, not stopwatch readings.

## Commits

### 1. `e4f5a6b` — Add JWT auth middleware and token refresh
_Jane Doe · 2025-06-01 14:32 · +243/-51 · 6 files_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 4/5 | clear handler names, but the refresh flow nests three levels deep |
| Structure | 4/5 | middleware cleanly separated; token logic could be its own module |
| Naming | 5/5 | descriptive identifiers (`verifyAccessToken`, `rotateRefreshToken`) |
| Error handling | 4/5 | 401/403 paths covered; missing-secret case falls through |
| Test coverage | 2/5 | +243 lines of auth logic, only one happy-path test added |

**Overall quality: 3.8/5**

**Estimated hours: 3.5 h** (complexity: high, confidence: medium)
> Baseline 1.9 h scaled up for novel, security-critical logic (token rotation, expiry
> handling); the six-file spread and partial tests indicate real design effort, capped by
> the 4 h gap since the previous commit.
>
> _size-only baseline: 1.9 h · prev-commit gap: 4.0 h_

### 4. `c7d8e9f` — docs: document auth environment variables 📄 docs
_Jane Doe · 2025-05-28 09:10 · +41/-3 · 1 file_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.5 h** (complexity: low, confidence: high)
> Routine README edit documenting four environment variables; prose with no novel technical
> content, so it lands below the size baseline.
>
> _size-only baseline: 0.6 h · prev-commit gap: 1.5 h_
```

## Project layout

| File | Responsibility |
|------|----------------|
| `analyze.py` | CLI entry — argument parsing, `.env` loading, orchestration, exit codes |
| `gitlog.py` | Pull commits from local git; parse stats; classify code vs docs commits |
| `heuristic.py` | Deterministic hours baseline and commit-gap helpers (pure functions) |
| `analysis.py` | Pydantic models, the rubric/prompt, and the one-call-per-commit Groq analysis |
| `report.py` | Render the markdown report and the deterministic summary |
| `tests/` | Unit tests for git parsing, commit classification, and the hours heuristic |

## Testing

```bash
.venv/bin/python -m pytest -q
```

The tests cover the deterministic, network-free core: numstat parsing, commit
classification, and the hours baseline.

## Design notes & limitations

- **Cost & rate limits** — one LLM call per commit; commits are capped (default 15) and very
  large diffs are truncated to stay within the model's tokens-per-minute window.
- **Estimates are ranges** — hours are explainable approximations with a confidence level,
  not time-tracking. They are most useful in aggregate and for relative comparison.
- **Per-commit isolation** — each commit is judged on its own diff, so a feature whose tests
  land in a later commit will read as "untested" at the point the logic was introduced.

A full design rationale lives in [`system-design.md`](system-design.md).

## License

[MIT](LICENSE)
