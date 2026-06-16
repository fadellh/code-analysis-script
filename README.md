# Commit Analyzer

A small Python CLI that pulls your git commits from the last 7 days and produces a markdown
report analyzing **code quality** and **estimated hours** per commit, plus an overall summary.

- Commit data comes from **local git** (`git log`/`git show` via subprocess) — no GitHub API, no token.
- Analysis is one **Groq** call per commit (`llama-3.3-70b-versatile`, JSON mode), validated with pydantic.
- Hours blend a deterministic size baseline with an LLM complexity judgment, plus a commit-gap sanity check.

## Setup

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # then put your real key in .env:  GROQ_API_KEY=...
```

## Usage

```bash
.venv/bin/python analyze.py [repo] [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `repo` (positional) | `.` | path to the git repo to analyze |
| `--author NAME` | all | only commits by this author |
| `--days N` | `7` | look-back window |
| `--max-commits N` | `15` | cap commits analyzed (and truncates very large diffs) |
| `--output FILE` | stdout | write the markdown report to a file |
| `--model NAME` | `llama-3.3-70b-versatile` | Groq model |

Examples:

```bash
.venv/bin/python analyze.py .
.venv/bin/python analyze.py /path/to/repo --author "Jane" --days 7 --output report.md
```

## Tests

```bash
.venv/bin/python -m pytest -q
```

Covers the two trickiest pure functions: git numstat parsing and the hours baseline heuristic.

## How the analysis works

**Quality** — each commit is scored 1–5 on readability, structure, naming, error handling, and
test coverage, with a one-line reason grounded in the diff/stats (not vibes). Overall quality is
the mean of the five, computed in code.

**Hours** — a deterministic baseline (`heuristic.py`) estimates effort from diff size (additions
full weight, deletions half, per-file overhead, ~150 effective lines/hour). The LLM then adjusts
for complexity (boilerplate fast, novel logic slow) and uses the gap since the author's previous
commit only as a sanity-check upper bound. The result is rounded to 0.25h with a confidence level —
no false precision.
