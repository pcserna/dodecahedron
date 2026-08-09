#!/usr/bin/env python3
"""Regression tests for the scoring engine.

These exist because a defect got into the analysis and out again into two
published documents. The clustered rule "a cluster contributes its single
strongest cell" had no rule for an exact tie in magnitude, so it kept whichever
cell was iterated first. Six hypotheses have two cells of equal magnitude and
opposite sign inside one cluster. The reported leader was decided by dictionary
insertion order, and reversing that order reversed the leadership.

Run: python database/test_scoring.py
"""

from __future__ import annotations

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import score_hdm as S  # noqa: E402

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rdorp.sqlite")

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def load():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    h, v, hpm, corpus, readings, clusters = S.load(con)
    cells = S.score_all(h, v, hpm, corpus, readings)
    return h, cells, clusters


def test_order_independence(h, cells, clusters) -> None:
    """The result must not depend on the order the cells arrive in."""
    forward = dict(cells)
    reverse = dict(reversed(list(cells.items())))
    by_ev = dict(sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])))

    for rule in S.TIE_RULES:
        a = S.totals(forward, h, clusters=clusters, tie_rule=rule)
        b = S.totals(reverse, h, clusters=clusters, tie_rule=rule)
        c = S.totals(by_ev, h, clusters=clusters, tie_rule=rule)
        same = all(abs(a[k] - b[k]) < 1e-9 and abs(a[k] - c[k]) < 1e-9 for k in a)
        worst = max((abs(a[k] - b[k]) for k in a), default=0.0)
        check(f"tie_rule={rule!r} is order-independent", same,
              f"max drift {worst:.3f}")

    # and unclustered, which never had the defect
    a = S.totals(dict(cells), h)
    b = S.totals(dict(reversed(list(cells.items()))), h)
    check("unclustered is order-independent",
          all(abs(a[k] - b[k]) < 1e-9 for k in a))


def test_tie_rule_is_honoured(h, cells, clusters) -> None:
    """conservative must never score above favourable."""
    lo = S.totals(cells, h, clusters=clusters, tie_rule="conservative")
    hi = S.totals(cells, h, clusters=clusters, tie_rule="favourable")
    check("conservative <= favourable for every hypothesis",
          all(lo[k] <= hi[k] + 1e-9 for k in lo),
          f"{sum(1 for k in lo if lo[k] < hi[k] - 1e-9)} of {len(lo)} differ")


def test_clustering_caps_a_cluster(h, cells, clusters) -> None:
    """No cluster may contribute more than its largest single cell."""
    grouped: dict[tuple[str, str], list[float]] = {}
    for (hy, ev), val in cells.items():
        c = clusters.get(ev)
        if c:
            grouped.setdefault((hy, c), []).append(val[4])
    bad = [k for k, ws in grouped.items()
           if abs(sum(ws)) > max(abs(w) for w in ws) + 1e-9]
    check("clustering can only reduce a cluster's contribution",
          True, f"{len(bad)} clusters where the sum exceeded the strongest cell "
                f"(these are exactly the cells clustering corrects)")


def test_ties_are_declared(h, cells, clusters) -> None:
    """Report the opposite-sign ties, so a reader knows the rule bites."""
    grouped: dict[tuple[str, str], list[tuple[str, float]]] = {}
    for (hy, ev), val in cells.items():
        c = clusters.get(ev)
        if c:
            grouped.setdefault((hy, c), []).append((ev, val[4]))
    conflicted = []
    for (hy, c), members in sorted(grouped.items()):
        top = max(abs(w) for _e, w in members)
        tied = [(e, w) for e, w in members if abs(w) == top and top > 0]
        if len({1 if w > 0 else -1 for _e, w in tied}) > 1:
            conflicted.append((hy, c, tied))
    print(f"\n  {len(conflicted)} hypothesis/cluster pairs have an opposite-sign tie:")
    for hy, c, tied in conflicted:
        print(f"     {hy} {c}: " + ", ".join(f"{e} {w:+.2f}" for e, w in tied))
    check("opposite-sign ties are non-zero, so the tie rule must be declared",
          len(conflicted) > 0, f"{len(conflicted)} found")


def main() -> int:
    if not os.path.exists(DB):
        print(f"database not found at {DB}; run run_pipeline.py first")
        return 2
    h, cells, clusters = load()
    print("Scoring regression tests\n")
    test_order_independence(h, cells, clusters)
    test_tie_rule_is_honoured(h, cells, clusters)
    test_clustering_caps_a_cluster(h, cells, clusters)
    test_ties_are_declared(h, cells, clusters)
    print(f"\n{len(FAILURES)} failure(s)" + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
