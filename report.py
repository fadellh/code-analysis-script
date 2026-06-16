"""Render CommitData + CommitAnalysis into a clean markdown report.

The summary is templated deterministically from the per-commit results (no extra LLM
call), so the report shape is consistent run to run. Documentation-only commits carry an
hours estimate but no quality scorecard, so they are excluded from quality averages.
"""
from __future__ import annotations

from datetime import datetime, timedelta

# An item bundles everything we know about one commit: (commit, analysis, baseline, gap).
# analysis.quality is None for docs-only commits.


def _round_quarter(x: float) -> float:
    return round(x * 4) / 4


def _esc(text: str) -> str:
    """Make a reason safe for a single markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _plural(n: int, noun: str) -> str:
    return f"{n} {noun}" + ("" if n == 1 else "s")


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


def _hours_block(out: list[str], a, baseline: float, gap: float | None) -> None:
    est = _round_quarter(a.hours.estimate_hours)
    out.append(
        f"**Estimated hours: {est} h** "
        f"(complexity: {a.hours.complexity}, confidence: {a.hours.confidence})"
    )
    out.append(f"> {_esc(a.hours.reasoning)}")
    out.append(">")
    gap_str = f"{gap} h" if gap is not None else "n/a"
    out.append(f"> _size-only baseline: {baseline} h · prev-commit gap: {gap_str}_")


def _narrative(n_code: int, n_docs: int, total_hours: float, avg_overall: float | None,
               ins: int, dels: int) -> str:
    if avg_overall is None:
        return (
            f"{_plural(n_docs, 'documentation commit')} totaling +{ins}/-{dels} lines; "
            f"estimated effort ~{round(total_hours, 2)} h. No code commits to score this window."
        )
    word = (
        "strong" if avg_overall >= 4
        else "solid" if avg_overall >= 3
        else "uneven" if avg_overall >= 2
        else "weak"
    )
    docs_note = f" plus {_plural(n_docs, 'docs commit')} (hours only)" if n_docs else ""
    return (
        f"Across {_plural(n_code, 'code commit')}{docs_note} totaling +{ins}/-{dels} lines, "
        f"estimated effort is ~{round(total_hours, 2)} h. Code quality looks {word} "
        f"(avg {avg_overall}/5). Hours are size-and-complexity estimates with explicit "
        f"confidence — read them as ranges, not stopwatch readings."
    )


def render_report(items, *, repo: str, branch: str, days: int, total_in_window: int,
                  author: str | None) -> str:
    now = datetime.now().astimezone()
    since = now - timedelta(days=days)
    n = len(items)

    code_items = [it for it in items if it[1].quality is not None]
    n_code, n_docs = len(code_items), n - len(code_items)

    total_hours = sum(a.hours.estimate_hours for _, a, _, _ in items)
    total_ins = sum(c.insertions for c, _, _, _ in items)
    total_dels = sum(c.deletions for c, _, _, _ in items)
    total_files = sum(c.files_changed for c, _, _, _ in items)

    def avg(attr: str) -> float:
        return round(sum(getattr(a.quality, attr).score for _, a, _, _ in code_items) / n_code, 1)

    avg_overall = (
        round(sum(a.quality.overall() for _, a, _, _ in code_items) / n_code, 1)
        if code_items else None
    )

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
    out.append(f"- **Commits analyzed:** {n}{cap} — {n_code} code, {n_docs} docs")
    out.append(f"- **Total estimated effort:** {round(total_hours, 2)} h")
    out.append(f"- **Total churn:** +{total_ins}/-{total_dels} across {total_files} files")
    if code_items:
        out.append(
            f"- **Average quality (code only):** readability {avg('readability')}, "
            f"structure {avg('structure')}, naming {avg('naming')}, "
            f"error-handling {avg('error_handling')}, tests {avg('test_coverage')} "
            f"→ **overall {avg_overall}/5**"
        )
        best = max(code_items, key=lambda it: it[1].quality.overall())
        biggest = max(items, key=lambda it: it[0].insertions + it[0].deletions)
        out.append(
            f"- **Highlights:** highest quality `{best[0].short_hash}` ({best[1].quality.overall()}/5) · "
            f"largest `{biggest[0].short_hash}` (+{biggest[0].insertions}/-{biggest[0].deletions})"
        )
    out.append("")
    out.append(_narrative(n_code, n_docs, total_hours, avg_overall, total_ins, total_dels))
    out.append("")

    # ---- Per commit -----------------------------------------------------------------
    out.append("## Commits")
    for i, (c, a, baseline, gap) in enumerate(items, 1):
        is_docs = a.quality is None
        label = " 📄 docs" if is_docs else ""
        out.append("")
        out.append(f"### {i}. `{c.short_hash}` — {c.subject}{label}")
        trunc = " · diff truncated" if c.diff_truncated else ""
        out.append(
            f"_{c.author} · {c.timestamp:%Y-%m-%d %H:%M} · "
            f"+{c.insertions}/-{c.deletions} · {_plural(c.files_changed, 'file')}{trunc}_"
        )
        out.append("")
        if a.failed:
            out.append("> ⚠️ Automated analysis was unavailable for this commit.")
            out.append("")
        if is_docs:
            out.append("_Documentation-only commit — code-quality scorecard n/a; hours only._")
            out.append("")
            _hours_block(out, a, baseline, gap)
            continue
        out.append("**Quality**")
        out.append("")
        out.append(_quality_table(a.quality))
        out.append("")
        out.append(f"**Overall quality: {a.quality.overall()}/5**")
        out.append("")
        _hours_block(out, a, baseline, gap)
    out.append("")
    return "\n".join(out)
