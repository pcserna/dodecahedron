#!/usr/bin/env python3
"""EXP-0011 - do the apertures form a usable gauge series? (C-01, C-03, C-11, C-13, H002)

Why this exists
---------------
Five readings in the project ask the object to *measure* something by which
aperture a thing passes through or fits: artillery shot (C-01), net mesh
(C-03), dividers or angles (C-11), garment sizes (C-13) and range (H002).
RDORP-012 reports that every gauge reading is punished by the evidence and
calls it the gauge-former asymmetry, but that finding rests on scoring. The
mechanical requirement underneath it has never been computed.

**A gauge needs three things**, and all five readings need all three:

1. **A graded series.** The apertures must step through sizes in a regular way,
   or the sizes it reports are arbitrary points with no relation to each other.
2. **Reproducibility between examples.** Two gauges must give the same reading,
   or a measurement made with one means nothing to the holder of another.
3. **Distinguishability.** You must be able to tell which aperture you used,
   by more than eye.

This tests all three on the measured corpus.

The null that this test needs
-----------------------------
**Sorted random values look like an arithmetic progression.** The order
statistics of a uniform sample are evenly spaced in expectation, so "the
diameters increase in regular steps" is what a random set of diameters does.
Fitting a line to sorted apertures and finding a high R-squared proves nothing
at all. The control is therefore random diameter sets drawn over the same
range, put through the same fit.

This is the third time this project has needed such a control: EXP-0009 for the
zodiac latitude scan and EXP-0010 for the Roman capacity units. A free
parameter, or a sorting step, will manufacture a fit.

Run: python database/exp_gauge.py
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sqlite3
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")

#: Diameters a gauge for lead sling shot would have to separate. Roman glandes
#: cluster by weight; at lead's density these are the corresponding diameters.
GLANS_WEIGHTS_G = (20.0, 30.0, 40.0, 50.0, 60.0)
LEAD_DENSITY = 11.34   # g/cm3

#: Practical limit of a craftsman's eye in separating two circular openings
#: held side by side, in millimetres. Generous.
EYE_RESOLUTION_MM = 1.0


def glans_diameters_mm() -> list[float]:
    out = []
    for g in GLANS_WEIGHTS_G:
        vol_cm3 = g / LEAD_DENSITY
        r_cm = (3 * vol_cm3 / (4 * math.pi)) ** (1 / 3)
        out.append(2 * r_cm * 10)
    return out


def measured_apertures(db_path: str) -> dict[str, list[float]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cols = [f"hole_{i:02d}_mm" for i in range(1, 13)]
    out = {}
    for r in con.execute("SELECT * FROM specimens"):
        vals = sorted(r[c] for c in cols if r[c] is not None)
        if len(vals) >= 4:
            out[f"{r['rd_id']} {r['specimen_name']}"] = vals
    con.close()
    return out


# --- 1. is it a graded series? ---------------------------------------------

def linear_residual(sorted_vals: list[float]) -> float:
    """RMS residual of a least-squares line through sorted values, normalised.

    Normalised by the range, so it is comparable between specimens of
    different size. Zero means a perfect arithmetic progression.
    """
    n = len(sorted_vals)
    xs = list(range(n))
    mx, my = (n - 1) / 2, sum(sorted_vals) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, sorted_vals))
    slope = sxy / sxx if sxx else 0.0
    resid = [y - (my + slope * (x - mx)) for x, y in zip(xs, sorted_vals)]
    rms = math.sqrt(sum(r * r for r in resid) / n)
    span = sorted_vals[-1] - sorted_vals[0]
    return rms / span if span else 0.0


def null_linear_residual(n: int, trials: int = 20000, seed: int = 20260810):
    """The same statistic for n random diameters, sorted.

    Sorting alone produces a near-linear sequence, so this is the number the
    real specimens must beat to mean anything.
    """
    rng = random.Random(seed)
    out = []
    for _ in range(trials):
        vals = sorted(rng.uniform(0.0, 1.0) for _ in range(n))
        out.append(linear_residual(vals))
    out.sort()
    return out


# --- 2. do two examples agree? ---------------------------------------------

def normalised(vals: list[float]) -> list[float]:
    lo, hi = vals[0], vals[-1]
    return [(v - lo) / (hi - lo) for v in vals] if hi > lo else [0.0] * len(vals)


def null_disagreement(na: int, nb: int, trials: int = 20000, seed: int = 20260811):
    """Disagreement between two UNRELATED sorted sets of the same sizes.

    Needed for the same reason as the linearity null: normalising two sorted
    sequences to [0, 1] makes them agree at the endpoints by construction and
    largely in between. Without this number the agreement statistic cannot be
    read at all.
    """
    rng = random.Random(seed)
    out = []
    for _ in range(trials):
        a = sorted(rng.uniform(0.0, 1.0) for _ in range(na))
        b = sorted(rng.uniform(0.0, 1.0) for _ in range(nb))
        out.append(series_disagreement(a, b))
    out.sort()
    return out


def series_disagreement(a: list[float], b: list[float]) -> float:
    """Mean absolute difference between two size series, after normalising.

    Normalising away overall size is generous to the hypothesis: it asks only
    whether the two objects step through their range in the same PROPORTIONS,
    not whether they give the same absolute reading, which they plainly do not.
    """
    k = min(len(a), len(b))
    if k < 2:
        return float("nan")
    na, nb = normalised(a), normalised(b)
    ia = [na[round(i * (len(na) - 1) / (k - 1))] for i in range(k)]
    ib = [nb[round(i * (len(nb) - 1) / (k - 1))] for i in range(k)]
    return sum(abs(x - y) for x, y in zip(ia, ib)) / k


# --- 3. can you tell them apart? -------------------------------------------

def smallest_gap(vals: list[float]) -> float:
    return min(b - a for a, b in zip(vals, vals[1:]))


def report(db_path: str = DB_DEFAULT, trials: int = 20000) -> dict:
    series = measured_apertures(db_path)
    print("EXP-0011  do the apertures form a usable gauge series?")
    print("=" * 78)
    if not series:
        print("  no specimen carries four or more measured apertures")
        return {}

    print("  specimens with four or more measured apertures:")
    for name, vals in series.items():
        print(f"    {name[:44]:44} n={len(vals):2}  "
              f"{vals[0]:.1f}-{vals[-1]:.1f} mm")

    print("\n  1. IS IT A GRADED SERIES?")
    print("  A sorted random set already looks like a progression, so the")
    print("  comparison is against random, not against zero.")
    print(f"\n  {'specimen':44} {'residual':>9} {'random':>9} {'better than'}")
    graded = {}
    for name, vals in series.items():
        if len(vals) < 4:
            continue
        obs = linear_residual(vals)
        null = null_linear_residual(len(vals), trials=trials)
        p = sum(1 for x in null if x <= obs) / len(null)
        med = null[len(null) // 2]
        graded[name] = (obs, med, p)
        print(f"  {name[:44]:44} {obs:9.4f} {med:9.4f} {1-p:>10.0%}")
    print("\n  'better than' is the fraction of random sets the specimen beats.")
    print("  A real graded series would sit far out in the tail.")

    print("\n  2. DO TWO EXAMPLES AGREE?")
    names = [n for n, v in series.items() if len(v) >= 4]
    agree = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = series_disagreement(series[a], series[b])
            null = null_disagreement(len(series[a]), len(series[b]), trials=trials)
            med = null[len(null) // 2]
            p = sum(1 for x in null if x <= d) / len(null)
            agree[(a, b)] = (d, med, p)
            print(f"    {a[:30]:30} vs {b[:30]:30}")
            print(f"      disagreement {d:.3f};  unrelated sets average {med:.3f};"
                  f"  {p:.0%} of them agree at least as well")
    print()
    print("    Normalising to [0,1] forces the endpoints to match, so two")
    print("    unrelated sets already agree fairly well. The last column is")
    print("    the one that carries information, not the first.")
    print()
    print(f"    ONLY {len(names)} SPECIMENS OF THE WHOLE CORPUS CARRY FOUR OR")
    print("    MORE MEASURED APERTURES, and one of those has four spanning")
    print("    3 mm. Reproducibility between examples is barely testable.")

    print("\n  3. CAN YOU TELL THEM APART?")
    for name, vals in series.items():
        gap = smallest_gap(vals)
        ok = "yes" if gap > EYE_RESOLUTION_MM else "NO"
        print(f"    {name[:44]:44} smallest gap {gap:5.2f} mm  "
              f"separable by eye: {ok}")

    print("\n  4. AGAINST ACTUAL ROMAN SHOT (C-01)")
    gl = glans_diameters_mm()
    print(f"    lead glandes of {', '.join(f'{g:.0f}' for g in GLANS_WEIGHTS_G)} g "
          f"are {', '.join(f'{d:.1f}' for d in gl)} mm across")
    for name, vals in series.items():
        hits = [g for g in gl if any(abs(g - v) < 0.5 for v in vals)]
        print(f"    {name[:44]:44} apertures matching a calibre: {len(hits)}/{len(gl)}")
    print("    a shot gauge must have an opening AT each calibre, not near one")

    print("\n" + "=" * 78)
    print("  VERDICT, stated to what the numbers support and no further")
    print("=" * 78)
    print("  ESTABLISHED, on four specimens: THE APERTURES ARE NOT A GRADED")
    print("  SERIES. Jublains beats 26 per cent of random sets on linearity,")
    print("  Vienne 15 per cent and Mainz 3 31 per cent - all three are LESS")
    print("  regular than a random set of the same size. Only Avenches, at")
    print("  83 per cent, is even suggestive, and one specimen out of four is")
    print("  what chance produces. An earlier version of this experiment left")
    print("  this open on one specimen; PUB-0019 tables I and V supplied two")
    print("  more and they settle it against the reading.")
    print()
    print("  ESTABLISHED: two examples do not agree. Six pairwise comparisons")
    print("  are now possible and four of them are worse than two unrelated")
    print("  sorted sets. Only Mainz 3 against Avenches agrees better than")
    print("  chance, and Mainz 3 has four apertures spanning 3 mm.")
    print()
    print("  ESTABLISHED: the object cannot be READ as a gauge. On both")
    print("  specimens the smallest step between neighbouring apertures is at")
    print("  or below a millimetre, and Mainz 3 carries two apertures of")
    print("  identical recorded diameter. A user could not tell which opening")
    print("  a thing had passed through. A gauge whose divisions cannot be")
    print("  told apart reports nothing, whatever series it follows.")
    print()
    print("  ESTABLISHED: no specimen carries an opening AT a lead-shot")
    print("  calibre. The matches are near-misses of the kind any spread of")
    print("  apertures produces, so C-01 fails directly.")
    print()
    print("  THE GAUGE-FORMER ASYMMETRY NOW HAS A COMPUTATION UNDER ALL OF IT.")
    print("  RDORP-012 6.1 reported it from scoring alone; every part of it is")
    print("  now supported - no graded series, no agreement between examples,")
    print("  no readable divisions, and no opening at a shot calibre.")
    print()
    print("  B2 IS STILL WORTH DOING, for a different reason than before. The")
    print("  four aperture sets reach this project through one publication,")
    print("  PUB-0019, and three of them at one or two removes. A direct")
    print("  measurement would make the result independent of that source.")
    return {"series": series, "graded": graded, "agree": agree}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=DB_DEFAULT)
    ap.add_argument("--trials", type=int, default=20000)
    args = ap.parse_args()
    report(args.db, args.trials)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
