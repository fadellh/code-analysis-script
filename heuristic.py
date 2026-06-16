"""Deterministic, transparent baselines that ground the LLM's hours estimate.

Pure functions only — no network, no LLM. These are the numbers a calculator can produce
honestly; the LLM only *adjusts* them for complexity, so the estimate can't be pure vibes.
"""
from __future__ import annotations

from datetime import datetime


def baseline_hours(insertions: int, deletions: int, files_changed: int) -> float:
    """Size-only effort baseline, in hours.

    - additions cost full weight, deletions half (removing code is cheaper than writing it)
    - each touched file adds a small context-switch overhead
    - ~150 effective lines/hour, with a 0.10h floor so even a trivial commit isn't zero
    """
    effective_churn = insertions + 0.5 * deletions
    file_overhead = 0.15 * files_changed
    churn_hours = effective_churn / 150.0
    return round(max(0.10, 0.10 + file_overhead + churn_hours), 2)


def commit_gap_hours(current: datetime, previous: datetime | None) -> float | None:
    """Hours between a commit and the author's previous (older) commit.

    A noisy *sanity-check* signal — gaps include breaks, sleep, and meetings — so it is
    only ever used as a soft upper bound on the estimate, never as the estimate itself.
    Returns None when there is no earlier commit to compare against.
    """
    if previous is None:
        return None
    delta = (current - previous).total_seconds() / 3600.0
    if delta <= 0:
        return None
    return round(delta, 2)
