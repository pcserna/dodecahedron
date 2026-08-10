#!/usr/bin/env python3
"""Tests for EXP-0009, the zodiac-fit computation.

Run: python database/test_exp_zodiac.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp_zodiac as Z  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def test_geometry() -> None:
    normals = Z.face_normals()
    verts = Z.vertices(normals)
    check("twelve face axes", len(normals) == 12)
    check("twenty vertices", len(verts) == 20)
    check("thirty edge midpoints", len(Z.edge_midpoints(verts)) == 30)

    elev = Z.achievable_elevations()
    check("seven distinct elevations, as EXP-0003 found", len(elev) == 7,
          str([round(e, 2) for e in elev]))
    check("a horizontal axis exists (edge suspension)", min(elev) == 0.0)
    check("a vertical axis exists (face rest)", abs(max(elev) - 90) < 1e-9)


def test_solar_inversion() -> None:
    """The declination inversion must round-trip."""
    for lam in (0, 15, 45, 90, 135, 180, 271, 359):
        dec = math.degrees(math.asin(math.sin(math.radians(Z.OBLIQUITY))
                                     * math.sin(math.radians(lam))))
        back = Z.longitudes_for_declination(dec)
        near = min(abs((b - lam + 180) % 360 - 180) for b in back)
        if near > 1e-6:
            check(f"longitude {lam} round-trips", False, f"nearest {near:.4f} deg")
            return
    check("declination inversion round-trips at every test longitude", True)

    check("solstice declination is the obliquity",
          abs(Z.longitudes_for_declination(Z.OBLIQUITY)[0] - 90) < 1e-6)
    check("beyond the obliquity there is no solution",
          Z.longitudes_for_declination(Z.OBLIQUITY + 1) == [])


def test_boundary_distance() -> None:
    check("a boundary is at distance zero", Z.distance_to_boundary(30.0) == 0)
    check("mid-sign is at distance 15", Z.distance_to_boundary(45.0) == 15.0)
    check("distance never exceeds half a sign",
          all(Z.distance_to_boundary(x) <= 15.0 + 1e-9 for x in range(0, 360)))


def test_chance_baseline() -> None:
    """The analytic 7.5 must match a uniform sample."""
    import random
    rng = random.Random(1)
    mean = sum(Z.distance_to_boundary(rng.uniform(0, 360))
               for _ in range(200000)) / 200000
    check("uniform longitudes average 7.5 deg from a boundary",
          abs(mean - Z.EXPECTED_AT_RANDOM) < 0.05,
          f"sampled {mean:.3f}, exact {Z.EXPECTED_AT_RANDOM}")


def test_perfect_fit_is_detected() -> None:
    """A contrived elevation set that lands on boundaries must score ~0.

    Guards against the statistic being insensitive - a test that cannot
    distinguish a real alignment from a random one proves nothing.
    """
    lat = 50.0
    elevations = []
    for lam in (30.0, 60.0, 120.0, 150.0):
        dec = math.degrees(math.asin(math.sin(math.radians(Z.OBLIQUITY))
                                     * math.sin(math.radians(lam))))
        elevations.append(90.0 - lat + dec)
    m, n = Z.fit(sorted(elevations), lat)
    check("a contrived on-boundary set scores near zero", m is not None and m < 0.01,
          f"mean {m:.4f} deg over {n} events")


def test_determinism() -> None:
    a = Z.monte_carlo(7, trials=300)
    b = Z.monte_carlo(7, trials=300)
    check("the Monte Carlo is deterministic under its fixed seed", a == b)


def test_headline() -> None:
    elev = Z.achievable_elevations()
    best, lat, n = Z.scan(elev)
    check("the real solid's best fit is worse than 5 deg", best > 5.0,
          f"{best:.2f} deg at {lat:.1f} N over {n} events")
    sims = Z.monte_carlo(len(elev), trials=2000)
    p = sum(1 for x in sims if x <= best) / len(sims)
    check("random elevation sets usually do at least as well", p > 0.5,
          f"p = {p:.3f}")


def main() -> int:
    print("EXP-0009 zodiac-fit tests\n")
    test_geometry()
    test_solar_inversion()
    test_boundary_distance()
    test_chance_baseline()
    test_perfect_fit_is_detected()
    test_determinism()
    test_headline()
    print(f"\n{len(FAILURES)} failure(s)"
          + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
