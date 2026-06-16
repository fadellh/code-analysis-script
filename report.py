"""Render CommitData + CommitAnalysis into a clean markdown report.

The summary is templated deterministically from the per-commit results (no extra LLM
call), so the report shape is consistent run to run.
"""
from __future__ import annotations

from datetime import datetime, timedelta

# An item bundles everything we know about one commit: (commit, analysis, baseline, gap).


def _round_quarter(x: float) -> float:
    return round(x * 4) / 4


def _esc(text: str) -> str:
    """Make a reason safe for a single markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _quality_table(q) -> str:
    rows = [
        ("Readability", q.readability),
        ("Structure", q.structure),
        ("Naming", q.naming),
        ("Error handling", q.error_handling),
        ("Test coverage", q.test_coverage),
    ]
    lines = ["| Dimension | Score | Reason |", "|---|---|---|"]
    lines += [f"| {name} | {dim.score}/5 | {_esc(dim.reason)} |" for name, dim in rows]
    return "\n".join(lines)


def _narrative(n: int, total_hours: float, avg_overall: float, ins: int, dels: int) -> str:
    word = (
        "strong" if avg_overall >= 4
        else "solid" if avg_overall >= 3
        else "uneven" if avg_overall >= 2
        else "weak"
    )
    return (
        f"Across {n} commit(s) totaling +{ins}/-{dels} lines, estimated effort is "
        f"~{round(total_hours, 2)} h. Overall code quality looks {word} (avg {avg_overall}/5). "
        f"Hours are size-and-complexity estimates with explicit confidence — read them as "
        f"ranges, not stopwatch readings."
    )


def render_report(items, *, repo: str, branch: str, days: int, total_in_window: int,
                  author: str | None) -> str:
    now = datetime.now().astimezone()
    since = now - timedelta(days=days)
    n = len(items)

    total_hours = sum(a.hours.estimate_hours for _, a, _, _ in items)
    total_ins = sum(c.insertions for c, _, _, _ in items)
    total_dels = sum(c.deletions for c, _, _, _ in items)
    total_files = sum(c.files_changed for c, _, _, _ in items)

    def avg(attr: str) -> float:
        return round(sum(getattr(a.quality, attr).score for _, a, _, _ in items) / n, 1)

    avg_overall = round(sum(a.quality.overall() for _, a, _, _ in items) / n, 1)

    out: list[str] = []
    out.append("# Commit Analysis Report")
    out.append("")
    out.append(
        f"_Repo: `{repo}` · Branch: `{branch}` · Window: last {days} days "
        f"({since:%Y-%m-%d} → {now:%Y-%m-%d}) · Author: {author or 'all authors'}_"
    )
    out.append("")

    # ---- Summary --------------------------------------------------------------------
    out.append("## Summary")
    cap = f" (of {total_in_window} in window)" if total_in_window > n else ""
    out.append(f"- **Commits analyzed:** {n}{cap}")
    out.append(f"- **Total estimated effort:** {round(total_hours, 2)} h")
    out.append(f"- **Total churn:** +{total_ins}/-{total_dels} across {total_files} files")
    out.append(
        f"- **Average quality:** readability {avg('readability')}, structure {avg('structure')}, "
        f"naming {avg('naming')}, error-handling {avg('error_handling')}, tests {avg('test_coverage')} "
        f"→ **overall {avg_overall}/5**"
    )
    best = max(items, key=lambda it: it[1].quality.overall())
    biggest = max(items, key=lambda it: it[0].insertions + it[0].deletions)
    out.append(
        f"- **Highlights:** highest quality `{best[0].short_hash}` ({best[1].quality.overall()}/5) · "
        f"largest `{biggest[0].short_hash}` (+{biggest[0].insertions}/-{biggest[0].deletions})"
    )
    out.append("")
    out.append(_narrative(n, total_hours, avg_overall, total_ins, total_dels))
    out.append("")

    # ---- Per commit -----------------------------------------------------------------
    out.append("## Commits")
    for i, (c, a, baseline, gap) in enumerate(items, 1):
        out.append("")
        out.append(f"### {i}. `{c.short_hash}` — {c.subject}")
        trunc = " · diff truncated" if c.diff_truncated else ""
        out.append(
            f"_{c.author} · {c.timestamp:%Y-%m-%d %H:%M} · "
            f"+{c.insertions}/-{c.deletions} · {c.files_changed} files{trunc}_"
        )
        out.append("")
        if a.failed:
            out.append("> ⚠️ Automated analysis was unavailable for this commit.")
            out.append("")
        out.append("**Quality**")
        out.append("")
        out.append(_quality_table(a.quality))
        out.append("")
        out.append(f"**Overall quality: {a.quality.overall()}/5**")
        out.append("")
        est = _round_quarter(a.hours.estimate_hours)
        out.append(
            f"**Estimated hours: {est} h** "
            f"(complexity: {a.hours.complexity}, confidence: {a.hours.confidence})"
        )
        out.append(f"> {_esc(a.hours.reasoning)}")
        out.append(">")
        gap_str = f"{gap} h" if gap is not None else "n/a"
        out.append(f"> _size-only baseline: {baseline} h · prev-commit gap: {gap_str}_")
    out.append("")
    return "\n".join(out)
