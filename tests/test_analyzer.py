"""Two focused unit tests: git numstat parsing + the hours baseline heuristic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gitlog import parse_numstat
from heuristic import baseline_hours


def test_parse_numstat():
    # two text files plus a binary file (reported as `-` / `-`)
    text = "10\t2\tsrc/app.py\n5\t0\tREADME.md\n-\t-\tassets/logo.png\n"
    files, insertions, deletions = parse_numstat(text)
    assert files == 3            # binary file still counts as a changed file
    assert insertions == 15      # 10 + 5 (+ 0 for binary)
    assert deletions == 2        # 2 + 0 (+ 0 for binary)


def test_baseline_hours():
    # an empty change floors at 0.10h, never zero
    assert baseline_hours(0, 0, 0) == 0.10
    # more insertions -> more hours (monotonic)
    assert baseline_hours(200, 0, 1) > baseline_hours(50, 0, 1)
    # deletions are weighted less than equal-sized additions
    assert baseline_hours(100, 0, 1) > baseline_hours(0, 100, 1)
    # touching more files adds context-switch overhead
    assert baseline_hours(50, 0, 5) > baseline_hours(50, 0, 1)
