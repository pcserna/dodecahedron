#!/usr/bin/env python3
"""Tests for EXP-0010, the volumetric-measure computation.

Run: python database/test_exp_volume.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp_volume as V  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def test_constants() -> None:
    """The volume coefficient is where this went wrong first time.

    An earlier scratch calculation used 2.785, which is not the dodecahedron's
    volume coefficient at all, and it understated every volume by a factor of
    about 2.75. That error made the candidate look refuted when the nominal
    figures do not refute it.
    """
    check("volume coefficient is (15+7*sqrt5)/4",
          abs(V.VOL_COEFF - 7.663119) < 1e-5, f"{V.VOL_COEFF:.6f}")
    check("inradius coefficient", abs(V.INRADIUS_COEFF - 1.113516) < 1e-5,
          f"{V.INRADIUS_COEFF:.6f}")
    check("circumradius coefficient", abs(V.CIRCUMRADIUS_COEFF - 1.401259) < 1e-5,
          f"{V.CIRCUMRADIUS_COEFF:.6f}")
    check("the wrong coefficient is not in use", abs(V.VOL_COEFF - 2.785) > 1)


def test_geometry_consistency() -> None:
    """Volume from the edge must agree with volume from the inradius."""
    a = 20.0
    direct = V.VOL_COEFF * a ** 3 / 1000.0
    f2f = 2 * V.INRADIUS_COEFF * a
    via_shell = V.internal_volume_ml(f2f, 0.0)
    check("volume via inradius matches volume via edge",
          abs(direct - via_shell) < 1e-9, f"{direct:.4f} vs {via_shell:.4f} ml")

    check("circumradius exceeds inradius",
          V.CIRCUMRADIUS_COEFF > V.INRADIUS_COEFF)

    big = V.internal_volume_ml(80.0, 2.0)
    small = V.internal_volume_ml(40.0, 2.0)
    check("volume scales faster than length", big / small > 8,
          f"ratio {big/small:.1f} for a 2:1 size ratio")


def test_shell() -> None:
    check("a wall thicker than the radius encloses nothing",
          V.internal_volume_ml(40.0, 25.0) == 0.0)
    thin = V.internal_volume_ml(60.0, 0.5)
    thick = V.internal_volume_ml(60.0, 5.0)
    check("a thicker wall encloses less", thick < thin,
          f"{thick:.1f} < {thin:.1f} ml")


def test_units() -> None:
    check("a sextarius is two heminae",
          abs(V.ROMAN_UNITS_ML["sextarius"] - 2 * V.ROMAN_UNITS_ML["hemina"]) < 1)
    check("a hemina is two quartarii",
          abs(V.ROMAN_UNITS_ML["hemina"] - 2 * V.ROMAN_UNITS_ML["quartarius"]) < 1)
    name, rel = V.nearest_unit(546.0)
    check("an exact sextarius matches at zero distance",
          name == "sextarius" and rel < 1e-9, f"{name} {rel}")


def test_null_is_honest() -> None:
    """The null must show that near-matches are easy, or the test is empty."""
    null = V.null_distribution(40.0, 1300.0, n=20000)
    mean = sum(null) / len(null)
    check("a random volume is typically within 30 % of some unit", mean < 0.30,
          f"mean {mean:.1%}")
    check("the null is deterministic",
          V.null_distribution(40.0, 1300.0, n=500) ==
          V.null_distribution(40.0, 1300.0, n=500))


def test_retention() -> None:
    """The structural argument, which is what actually refutes the candidate."""
    for d in (40.0, 60.0, 80.0, 127.7):
        if V.retained_volume_ml(d, 2.0) != 0.0:
            check("retained volume is zero at every size", False, f"at {d} mm")
            return
    check("retained volume is zero at every size", True,
          "an aperture in the centre of every face")


def test_headline() -> None:
    if not os.path.exists(V.DB_DEFAULT):
        print("  (database absent; skipping corpus checks)")
        return
    rows, wall = V.corpus_rows(V.DB_DEFAULT)
    check("the corpus supplies measured specimens", len(rows) >= 8, f"{len(rows)}")
    vols = [V.internal_volume_ml(r["max_diameter_mm"],
                                 r["wall_thickness_mm"] or wall) for r in rows]
    check("no specimen reaches a congius", max(vols) < V.ROMAN_UNITS_ML["congius"],
          f"largest {max(vols):.0f} ml")
    rels = [V.nearest_unit(v)[1] for v in vols]
    observed = sum(rels) / len(rels)
    null = V.null_distribution(min(vols), max(vols), n=20000)
    p = sum(1 for x in null if x <= observed) / len(null)
    check("the corpus is no closer to Roman units than chance", p > 0.05,
          f"observed {observed:.1%}, p = {p:.2f}")


def main() -> int:
    print("EXP-0010 volumetric-measure tests\n")
    test_constants()
    test_geometry_consistency()
    test_shell()
    test_units()
    test_null_is_honest()
    test_retention()
    test_headline()
    print(f"\n{len(FAILURES)} failure(s)"
          + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
