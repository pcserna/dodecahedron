#!/usr/bin/env python3
"""Tests for EXP-0011, the gauge-series computation.

Run: python database/test_exp_gauge.py
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp_gauge as G  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def test_linear_residual() -> None:
    perfect = [10.0, 12.0, 14.0, 16.0, 18.0]
    check("a perfect arithmetic progression scores zero",
          G.linear_residual(perfect) < 1e-12, f"{G.linear_residual(perfect):.2e}")

    bumpy = [10.0, 10.1, 10.2, 17.9, 18.0]
    check("a clustered set scores worse than a regular one",
          G.linear_residual(bumpy) > G.linear_residual(perfect) + 0.05,
          f"{G.linear_residual(bumpy):.4f} vs {G.linear_residual(perfect):.4f}")

    check("the statistic is scale-invariant",
          abs(G.linear_residual(bumpy)
              - G.linear_residual([v * 3 for v in bumpy])) < 1e-9)
    check("a degenerate set does not divide by zero",
          G.linear_residual([5.0, 5.0, 5.0]) == 0.0)


def test_the_null_is_the_point() -> None:
    """Sorted random values already look like a progression.

    If this were not so the whole comparison would be unnecessary, so the test
    states it explicitly: a random set typically scores a small residual, and
    a naive reading of that number would call it a graded series.
    """
    null = G.null_linear_residual(12, trials=5000)
    med = null[len(null) // 2]
    check("a sorted random set of 12 looks fairly linear", med < 0.10,
          f"median residual {med:.4f}")
    check("but not perfectly", med > 0.01, f"median residual {med:.4f}")
    check("the null is deterministic",
          G.null_linear_residual(8, trials=400) ==
          G.null_linear_residual(8, trials=400))


def test_disagreement() -> None:
    a = [10.0, 12.0, 14.0, 16.0]
    check("a series does not disagree with itself",
          G.series_disagreement(a, a) < 1e-12)
    check("a rescaled series does not disagree with the original",
          G.series_disagreement(a, [v * 2 for v in a]) < 1e-12,
          "normalisation removes overall size, by design")
    b = [10.0, 10.2, 10.4, 16.0]
    check("a differently shaped series does disagree",
          G.series_disagreement(a, b) > 0.05,
          f"{G.series_disagreement(a, b):.3f}")


def test_glans_diameters() -> None:
    d = G.glans_diameters_mm()
    check("glans diameters increase with weight", d == sorted(d))
    check("a 30 g lead ball is about 17 mm across", abs(d[1] - 17.2) < 0.2,
          f"{d[1]:.2f} mm")
    # sanity: volume of a sphere of that diameter times density returns the mass
    import math
    r_cm = d[1] / 20
    mass = 4 / 3 * math.pi * r_cm ** 3 * G.LEAD_DENSITY
    check("the diameter round-trips to the mass", abs(mass - 30.0) < 0.01,
          f"{mass:.3f} g")


def test_gaps() -> None:
    check("smallest gap is found", abs(G.smallest_gap([1.0, 5.0, 5.2, 9.0]) - 0.2) < 1e-9)
    check("identical values give a zero gap",
          G.smallest_gap([3.0, 3.0, 4.0]) == 0.0)


def test_corpus() -> None:
    if not os.path.exists(G.DB_DEFAULT):
        print("  (database absent; skipping corpus checks)")
        return
    series = G.measured_apertures(G.DB_DEFAULT)
    check("at least one specimen has four or more measured apertures",
          len(series) >= 1, f"{len(series)} specimens")
    twelve = [v for v in series.values() if len(v) == 12]
    check("at least two specimens have all twelve measured", len(twelve) >= 2,
          f"{len(twelve)}; PUB-0019 tables II and V supply them")
    check("enough series to compare examples", len(series) >= 4,
          f"{len(series)} - fewer than four and reproducibility is untestable")
    for name, vals in series.items():
        if G.smallest_gap(vals) > G.EYE_RESOLUTION_MM:
            check("no specimen's apertures are all separable by eye", False, name)
            return
    check("no specimen's apertures are all separable by eye", True,
          "every one has a step at or below 1 mm")


def main() -> int:
    print("EXP-0011 gauge-series tests\n")
    test_linear_residual()
    test_the_null_is_the_point()
    test_disagreement()
    test_glans_diameters()
    test_gaps()
    test_corpus()
    print(f"\n{len(FAILURES)} failure(s)"
          + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
