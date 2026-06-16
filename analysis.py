"""Groq-backed per-commit analysis: quality rubric + hours estimate, validated by pydantic.

One LLM call per commit. The reply is forced into JSON mode and validated against the
pydantic contract below; on failure we retry once with the error fed back, then fall back
to a degraded entry so a single bad commit never kills the whole run.
"""
from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from gitlog import CommitData


# ---- Output contract (what the LLM must return, validated) -----------------------------

class Dimension(BaseModel):
    score: int = Field(ge=1, le=5)
    reason: str


class Quality(BaseModel):
    readability: Dimension
    structure: Dimension
    naming: Dimension
    error_handling: Dimension
    test_coverage: Dimension

    def overall(self) -> float:
        scores = [
            self.readability.score,
            self.structure.score,
            self.naming.score,
            self.error_handling.score,
            self.test_coverage.score,
        ]
        return round(sum(scores) / len(scores), 1)


class Hours(BaseModel):
    estimate_hours: float = Field(ge=0)
    complexity: Literal["low", "medium", "high"]
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class CommitAnalysis(BaseModel):
    quality: Quality
    hours: Hours
    failed: bool = False  # set only on the degraded fallback path


# ---- Prompt (the tunable bit) ----------------------------------------------------------

SYSTEM_PROMPT = """You are a meticulous senior engineer reviewing ONE git commit.
You are given the commit's metadata, diff stats, a size-only effort BASELINE (hours), an
optional GAP (hours since the author's previous commit), and a possibly-truncated diff.

Return ONLY a JSON object matching this exact schema (no prose, no markdown fences):

{
  "quality": {
    "readability":    {"score": 1-5, "reason": "one line"},
    "structure":      {"score": 1-5, "reason": "one line"},
    "naming":         {"score": 1-5, "reason": "one line"},
    "error_handling": {"score": 1-5, "reason": "one line"},
    "test_coverage":  {"score": 1-5, "reason": "one line"}
  },
  "hours": {
    "estimate_hours": number,
    "complexity": "low" | "medium" | "high",
    "confidence": "low" | "medium" | "high",
    "reasoning": "step-by-step, a few sentences"
  }
}

QUALITY RUBRIC — score each 1-5 and GROUND every reason in a concrete signal from the
diff/stats (e.g. "added try/except around the subprocess call", "+120/-4 in one file, no
test files touched"). Never speculate about code that is not shown.
- readability: clarity, formatting, nesting depth, comments where the logic is non-obvious.
- structure: separation of concerns, decomposition, cohesion (does the change do one thing?).
- naming: descriptive, consistent identifiers; no cryptic abbreviations.
- error_handling: input validation, exceptions, edge/failure paths, meaningful messages.
- test_coverage: were tests added or updated for the changed logic?
Anchors: 5 exemplary; 4 solid, minor nits; 3 acceptable with clear gaps; 2 weak; 1 poor/absent.
N/A rule: if a dimension cannot apply (e.g. a docs-only or config-only change has no error
handling), score 3 and say "n/a - non-code change" rather than penalizing it.

HOURS — reason step by step, then commit to a number:
1. Start from BASELINE (a pure size estimate).
2. Judge complexity: boilerplate/generated/config is FAST (scale down, ~0.3-0.7x); novel
   logic, algorithms, or tricky edge cases are SLOW (scale up, ~1.3-2.0x). Weigh
   complexity over raw line count.
3. Use GAP only as a sanity-check upper bound: a commit minutes after the previous one
   cannot represent hours of work; a commit after a long gap may bundle more. Do NOT treat
   GAP as the answer — gaps include breaks.
4. Output estimate_hours rounded to the nearest 0.25, with a confidence (low/med/high).
   Avoid false precision."""


def _user_prompt(commit: CommitData, baseline: float, gap: float | None) -> str:
    gap_str = f"{gap} h" if gap is not None else "n/a (no earlier commit by this author)"
    return f"""COMMIT {commit.short_hash} - {commit.subject}
author: {commit.author}
timestamp: {commit.timestamp.isoformat()}
stats: {commit.files_changed} files, +{commit.insertions}/-{commit.deletions} lines
BASELINE (size-only hours): {baseline}
GAP since previous commit by author: {gap_str}

message body:
{commit.body or '(none)'}

diff:
{commit.diff or '(empty)'}"""


def _degraded(note: str) -> CommitAnalysis:
    d = lambda: Dimension(score=3, reason=f"analysis unavailable - {note}")
    return CommitAnalysis(
        quality=Quality(
            readability=d(), structure=d(), naming=d(), error_handling=d(), test_coverage=d()
        ),
        hours=Hours(estimate_hours=0.0, complexity="low", confidence="low",
                    reasoning=f"analysis failed: {note}"),
        failed=True,
    )


def analyze_commit(client, model: str, commit: CommitData, baseline: float,
                   gap: float | None) -> CommitAnalysis:
    """Run one Groq call for a commit and return a validated CommitAnalysis."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _user_prompt(commit, baseline, gap)},
    ]
    last_err: Exception | None = None
    for _ in range(2):
        try:
            resp = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=0.2,
            )
            return CommitAnalysis.model_validate_json(resp.choices[0].message.content)
        except ValidationError as e:
            last_err = e
            messages.append({
                "role": "user",
                "content": f"Your previous reply failed validation: {e}. "
                           "Return ONLY corrected JSON matching the schema.",
            })
        except Exception as e:  # network / API / rate-limit after the SDK's own retries
            last_err = e
            time.sleep(1.0)
    return _degraded(str(last_err)[:200])
