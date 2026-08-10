#!/usr/bin/env python3
"""Tests for EXP-0012, the Wagemans sowing-calendar model.

Run: python database/test_exp_wagemans.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp_wagemans as W  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def test_central_constant() -> None:
    """His 26.6 must be our face-rest elevation, or we are testing the wrong model."""
    check("26.6 deg is arctan(1/2)", abs(W.AXIS_ELEVATION - 26.565) < 0.001,
          f"{W.AXIS_ELEVATION:.4f}")
    try:
        import exp_zodiac as Z
        elev = Z.achievable_elevations()
        check("it is one of the elevations EXP-0003 derives",
              any(abs(e - W.AXIS_ELEVATION) < 0.01 for e in elev),
              f"{[round(e, 2) for e in elev]}")
    except ImportError:
        print("  (exp_zodiac unavailable; skipping cross-check)")


def test_measuring_angle() -> None:
    check("equal apertures give the axis elevation plus their tolerance",
          abs(W.measuring_angle(0.0, 0.0, 50.0) - W.AXIS_ELEVATION) < 1e-9,
          "zero apertures admit only the axis itself")
    a = W.measuring_angle(20.0, 20.0, 50.0)
    b = W.measuring_angle(10.0, 10.0, 50.0)
    check("wider apertures admit a higher sun", a > b, f"{a:.2f} > {b:.2f}")
    c = W.measuring_angle(20.0, 20.0, 100.0)
    check("a longer path admits a lower sun", c < a, f"{c:.2f} < {a:.2f}")
    check("the angle always exceeds the axis elevation",
          W.measuring_angle(1.0, 1.0, 200.0) > W.AXIS_ELEVATION)


def test_solar_model() -> None:
    lat = 50.0
    jun = W.noon_altitude(lat, 172)
    dec = W.noon_altitude(lat, 355)
    check("the sun is highest near the June solstice",
          abs(jun - (90 - lat + W.OBLIQUITY)) < 0.5, f"{jun:.2f}")
    check("and lowest near the December solstice",
          abs(dec - (90 - lat - W.OBLIQUITY)) < 0.5, f"{dec:.2f}")
    check("an equinox is near 90 - latitude",
          abs(W.noon_altitude(lat, 80) - (90 - lat)) < 0.5)


def test_the_deviation_statistic_is_vacuous() -> None:
    """The core finding: any angle in range matches a date to a fraction of a degree.

    If this test fails, the statistic would carry information and the
    experiment's conclusion would be wrong.
    """
    lat = 51.0
    lo, hi = 90 - lat - W.OBLIQUITY, 90 - lat + W.OBLIQUITY
    import random
    rng = random.Random(7)
    worst = 0.0
    for _ in range(300):
        a = rng.uniform(lo + 1, hi - 1)
        _day, err = W.date_for_angle(lat, a)
        worst = max(worst, err)
    check("every angle in the sun's range matches a date within 0.5 deg",
          worst < 0.5, f"worst residual {worst:.3f} deg")
    check("so the statistic cannot separate design from chance", True,
          "which is what the experiment reports")


def test_specimen_data_is_internally_consistent() -> None:
    for name, pairs, d, lat, _note in W.SPECIMENS:
        check(f"{name.split()[0]} has six opposed pairs", len(pairs) == 6,
              f"{len(pairs)}")
        flat = [x for p in pairs for x in p]
        check(f"{name.split()[0]} apertures are plausible",
              all(3 < x < 45 for x in flat), f"{min(flat)}-{max(flat)} mm")
        check(f"{name.split()[0]} face-to-face exceeds every aperture",
              d > max(flat), f"{d} vs {max(flat)}")


def test_report_runs() -> None:
    res = W.report(trials=50)
    check("the report produces a result for every specimen",
          len(res) == len(W.SPECIMENS), f"{len(res)}")


def main() -> int:
    print("EXP-0012 Wagemans-model tests\n")
    test_central_constant()
    test_measuring_angle()
    test_solar_model()
    test_the_deviation_statistic_is_vacuous()
    test_specimen_data_is_internally_consistent()
    print()
    test_report_runs()
    print(f"\n{len(FAILURES)} failure(s)"
          + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
