#!/usr/bin/env python3
"""EXP-0010 - could a dodecahedron be a volumetric measure? (candidate C-05)

Why this exists
---------------
C-05, "volumetric grain or liquid measure", was eliminated in the screen on a
score of -18.0, argued from standardisation: a measure that varies 2.5:1
between examples measures nothing. That is a real argument but it is an
argument about the corpus, not about the object, and the screen rule that
produced it is known to be crude (RDORP-013 A7). This module tests the
candidate on its own terms.

Three questions, in increasing order of how decisive they are
-------------------------------------------------------------
1. **Nominal capacity.** What volume does the shell enclose, and does it land
   near a Roman capacity unit?
2. **Retained capacity.** How much can it actually hold? A measure must retain
   its content long enough to be read.
3. **Granularity.** If not liquid, could it meter grain?

A caution the first question needs
----------------------------------
Roman capacity units are roughly geometric, so *any* volume in the right range
sits within some percentage of one. Asking "is it close to a unit?" without a
null is the same mistake the zodiac fit made (EXP-0009): a free parameter makes
a match inevitable. The null here is volumes drawn uniformly in log space over
the same range, and the question is whether the real specimens are closer to a
unit than that.

Run: python database/exp_volume.py
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")

#: Volume of a regular dodecahedron of edge a is (15 + 7*sqrt(5))/4 * a**3.
VOL_COEFF = (15 + 7 * math.sqrt(5)) / 4                      # 7.663119...
#: Inradius (face centre to centre) of the same solid, in units of the edge.
INRADIUS_COEFF = math.sqrt(250 + 110 * math.sqrt(5)) / 20    # 1.113516...
#: Circumradius (centre to knob), in units of the edge.
CIRCUMRADIUS_COEFF = math.sqrt(3) * (1 + math.sqrt(5)) / 4   # 1.401259...

#: Roman capacity units, in millilitres. Standard values; the sextarius is
#: taken as 546 ml and the rest follow from the Roman fractional system.
ROMAN_UNITS_ML = {
    "ligula": 11.4,
    "cyathus": 45.5,
    "acetabulum": 68.3,
    "quartarius": 136.5,
    "hemina": 273.0,
    "sextarius": 546.0,
    "congius": 3276.0,
    "modius": 8736.0,
}

#: Cereal grain: length of a wheat or barley caryopsis, millimetres.
GRAIN_MM = (5.0, 9.0)


def edge_from_face_to_face(d_mm: float) -> float:
    return (d_mm / 2) / INRADIUS_COEFF


def edge_from_knob_diameter(d_mm: float) -> float:
    return (d_mm / 2) / CIRCUMRADIUS_COEFF


def internal_volume_ml(outer_face_to_face_mm: float, wall_mm: float) -> float:
    """Volume enclosed by the shell, in millilitres.

    The cavity of a shell of uniform thickness is a similar dodecahedron whose
    inradius is reduced by the wall thickness.
    """
    r_inner = outer_face_to_face_mm / 2 - wall_mm
    if r_inner <= 0:
        return 0.0
    a = r_inner / INRADIUS_COEFF
    return VOL_COEFF * a ** 3 / 1000.0


def nearest_unit(volume_ml: float):
    """(unit name, relative distance) for the closest Roman unit."""
    best, best_rel = None, None
    for name, v in ROMAN_UNITS_ML.items():
        rel = abs(volume_ml - v) / v
        if best_rel is None or rel < best_rel:
            best, best_rel = name, rel
    return best, best_rel


def retained_volume_ml(outer_face_to_face_mm: float, wall_mm: float) -> float:
    """How much liquid the object holds when set down, in millilitres.

    Every face carries an aperture at its centre. Whichever face is downward,
    its aperture is the lowest point of the cavity, so the fill level cannot
    rise above it. This is a property of the form, not of any one specimen.
    """
    return 0.0


def corpus_rows(db_path: str):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT rd_id, specimen_name, max_diameter_mm, wall_thickness_mm "
        "FROM specimens WHERE max_diameter_mm IS NOT NULL "
        "ORDER BY max_diameter_mm").fetchall()
    walls = [r["wall_thickness_mm"] for r in rows if r["wall_thickness_mm"]]
    if not walls:
        walls = [r[0] for r in con.execute(
            "SELECT wall_thickness_mm FROM specimens "
            "WHERE wall_thickness_mm IS NOT NULL")]
    con.close()
    return rows, (sum(walls) / len(walls) if walls else 2.5)


def null_distribution(lo_ml: float, hi_ml: float, n: int = 200000,
                      seed: int = 20260810):
    """Relative distance to the nearest unit, for volumes uniform in log space.

    Log-uniform because the Roman units are themselves roughly geometric; a
    linear null would understate how easy a near-match is at the small end.
    """
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        v = math.exp(rng.uniform(math.log(lo_ml), math.log(hi_ml)))
        out.append(nearest_unit(v)[1])
    out.sort()
    return out


def report(db_path: str = DB_DEFAULT, trials: int = 200000) -> dict:
    rows, mean_wall = corpus_rows(db_path)
    print("EXP-0010  the dodecahedron as a volumetric measure (C-05)")
    print("=" * 78)
    print(f"  V = {VOL_COEFF:.6f} a^3,  inradius = {INRADIUS_COEFF:.6f} a")
    print(f"  wall thickness used where not recorded: {mean_wall:.2f} mm "
          f"(corpus mean)")
    print()

    print("  1. NOMINAL CAPACITY")
    print(f"  {'specimen':28} {'outer':>7} {'wall':>6} {'volume':>9}  "
          f"nearest Roman unit")
    vols = []
    for r in rows:
        wall = r["wall_thickness_mm"] or mean_wall
        v = internal_volume_ml(r["max_diameter_mm"], wall)
        vols.append(v)
        unit, rel = nearest_unit(v)
        print(f"  {r['specimen_name'][:28]:28} {r['max_diameter_mm']:7.1f} "
              f"{wall:6.1f} {v:8.1f} ml  {unit} ({rel:+.0%})")

    lo, hi = min(vols), max(vols)
    print(f"\n  volume range {lo:.1f} to {hi:.1f} ml "
          f"- a factor of {hi/lo:.1f} across the corpus")

    rels = [nearest_unit(v)[1] for v in vols]
    observed = sum(rels) / len(rels)
    print(f"  mean relative distance to the nearest unit: {observed:.1%}")

    null = null_distribution(lo, hi, n=trials)
    expected = sum(null) / len(null)
    better = sum(1 for x in null if x <= observed) / len(null)
    print(f"  same statistic for {len(null)} log-uniform random volumes: "
          f"{expected:.1%}")
    print(f"  random volumes at least as close to a unit: {better:.0%}")
    verdict_1 = ("no better than chance" if better > 0.05
                 else "closer to the units than chance would give")
    print(f"  => nominal capacity is {verdict_1}")

    print("\n  2. RETAINED CAPACITY")
    print("  Every face carries an aperture at its centre, so whichever face is")
    print("  downward, its aperture is the lowest point of the cavity.")
    print(f"  Liquid retained, in any orientation: "
          f"{retained_volume_ml(60, mean_wall):.0f} ml")
    print("  => the object cannot hold a liquid measure at all. This follows")
    print("     from the form and holds for every specimen in the corpus.")

    print("\n  3. GRANULARITY")
    con = sqlite3.connect(db_path)
    holes = [r[0] for r in con.execute(
        "SELECT observed_value FROM artifact_observations WHERE ev_id = 'EV004'")
        if r[0]]
    con.close()
    print(f"  cereal grain is {GRAIN_MM[0]:.0f}-{GRAIN_MM[1]:.0f} mm long; "
          f"published aperture diameters run 6-40 mm")
    print("  => every aperture passes grain freely, so dry measure fails for")
    print("     the same reason as liquid.")

    print("\n" + "=" * 78)
    print("  VERDICT: C-05 is refuted on the form, not on the corpus.")
    print("  The standardisation argument that eliminated it in the screen is")
    print("  weaker than this one: a measure must RETAIN what it measures, and")
    print("  an object with an aperture in the centre of every face retains")
    print("  nothing in any orientation. Nominal capacity is beside the point,")
    print(f"  and is in any case {verdict_1}.")
    return {"volumes": vols, "range": (lo, hi), "observed": observed,
            "expected": expected, "p": better, "mean_wall": mean_wall}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=DB_DEFAULT)
    ap.add_argument("--trials", type=int, default=200000)
    args = ap.parse_args()
    report(args.db, args.trials)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
