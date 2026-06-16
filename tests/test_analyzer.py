"""Two focused unit tests: git numstat parsing + the hours baseline heuristic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gitlog import classify_commit, parse_numstat
from heuristic import baseline_hours


def test_parse_numstat():
    # two text files plus a binary file (reported as `-` / `-`)
    text = "10\t2\tsrc/app.py\n5\t0\tREADME.md\n-\t-\tassets/logo.png\n"
    ns = parse_numstat(text)
    assert ns.files_changed == 3            # binary file still counts as a changed file
    assert ns.insertions == 15              # 10 + 5 (+ 0 for binary)
    assert ns.deletions == 2                # 2 + 0 (+ 0 for binary)
    assert ns.paths == ["src/app.py", "README.md", "assets/logo.png"]


def test_classify_commit():
    # every file is documentation -> docs
    assert classify_commit(["README.md", "docs/guide.rst", "CHANGELOG"]) == "docs"
    # any source file present -> code
    assert classify_commit(["README.md", "src/app.py"]) == "code"
    # config-only (e.g. requirements.txt, .gitignore) counts as code, not docs
    assert classify_commit(["requirements.txt", ".gitignore"]) == "code"
    # no files -> code (nothing to treat as docs)
    assert classify_commit([]) == "code"


def test_baseline_hours():
    # an empty change floors at 0.10h, never zero
    assert baseline_hours(0, 0, 0) == 0.10
    # more insertions -> more hours (monotonic)
    assert baseline_hours(200, 0, 1) > baseline_hours(50, 0, 1)
    # deletions are weighted less than equal-sized additions
    assert baseline_hours(100, 0, 1) > baseline_hours(0, 100, 1)
    # touching more files adds context-switch overhead
    assert baseline_hours(50, 0, 5) > baseline_hours(50, 0, 1)
