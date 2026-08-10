#!/usr/bin/env python3
"""EXP-0009 - does the dodecahedron's geometry fit the zodiac better than chance?

Why this exists
---------------
`EXP-0002` and `EXP-0003` refute the solar-zodiac readings on resolution and on
the number of reachable elevations. A separate claim then appeared in
RDORP-012: that the *apparent* fit between the object's calendar events and the
zodiac sign boundaries is no better than chance. That claim carried a statistic
- a best mean distance of 5.84 deg at 51.8 N against 7.50 deg expected at
random - which had been computed once in a scratch session and never committed.
It was removed from the document for that reason. This module puts it back on a
footing where anyone can check it.

The question, precisely
-----------------------
Suspending or resting a dodecahedron makes a small set of face-pair axes
horizontal-relative elevations available (`EXP-0003` finds seven distinct ones
across all modes of support). If the object were a calendar, the sun reaching
one of those elevations at noon would mark a date. The zodiac divides the year
into twelve 30-degree arcs of solar longitude.

**Do the dates the object can mark fall on sign boundaries more closely than
an arbitrary set of elevations would?**

Method
------
1. Derive the solid from first principles; take the seven distinct elevations.
2. At latitude phi, solar noon altitude is ``90 - phi + delta``. Invert that for
   each elevation to get the declination, and invert the declination to get the
   solar longitudes at which it occurs (two per year, ascending and descending).
3. Each such longitude is an event. Measure its distance to the nearest
   multiple of 30 degrees.
4. The fit statistic is the mean distance over all events. Lower is a better
   fit.
5. Scan latitude across the corpus range and report the best fit found.
6. Compare against chance.

The chance baseline is exact, not simulated. If event longitudes were
independent and uniform on the circle, the distance to the nearest 30-degree
boundary is uniform on [0, 15], with mean **7.5 degrees**. A Monte Carlo over
random elevation sets is also run, with a fixed seed, as a check on the
analytic value and to give the spread.

What a "good" fit would need to mean
------------------------------------
A mean distance well below 7.5 that survives the latitude scan being *free*.
The scan tries every latitude and keeps the best, so it is a maximisation over
a nuisance parameter and it will beat 7.5 by construction. The honest test is
therefore the Monte Carlo: how often does an ARBITRARY set of elevations,
given the same freedom to pick the best latitude, do at least as well?

Run: python database/exp_zodiac.py
"""

from __future__ import annotations

import argparse
import itertools
import math
import random

def obliquity_at(year: float) -> float:
    """Obliquity of the ecliptic, degrees, by the IAU secular expression.

    THIS IS NOT A CONSTANT AND USING THE MODERN VALUE WAS AN ERROR. Obliquity
    was 23.67 degrees in AD 200 against 23.44 today - a difference of 0.22
    degrees, which is LARGER than every precision this project argues about:
    Wagemans's reported deviations of 0.11 and 0.29 degrees, and the 0.18
    degree sight tolerance of the best aperture pair in EXP-0004.

    Valid for a few millennia either side of J2000, which is all that is
    needed here.
    """
    T = (year - 2000) / 100.0
    return 23.439291 - 0.0130042 * T - 1.64e-7 * T ** 2 + 5.04e-7 * T ** 3


#: Mid-point of the corpus date range, 2nd to 4th century AD.
ROMAN_EPOCH = 250
OBLIQUITY = obliquity_at(ROMAN_EPOCH)     # 23.664 degrees, not the modern 23.44
SIGN_ARC = 30.0            # degrees of solar longitude per zodiac sign
PHI = (1 + math.sqrt(5)) / 2

#: Latitude range covered by the recorded corpus, from Arles to Corbridge.
LAT_MIN, LAT_MAX = 40.0, 58.0
LAT_STEP = 0.1


# --- geometry ---------------------------------------------------------------

def _normalise(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _angle(a, b) -> float:
    d = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))
    return math.degrees(math.acos(d))


def face_normals() -> list[tuple[float, float, float]]:
    """The twelve face axes, as the vertices of the dual icosahedron."""
    out = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            out += [(0, s1 * 1, s2 * PHI), (s1 * 1, s2 * PHI, 0), (s2 * PHI, 0, s1 * 1)]
    return [_normalise(v) for v in out]


def vertices(normals) -> list[tuple[float, float, float]]:
    """The twenty knobs, as centroids of the icosahedron's faces.

    Checked against the property that caught an earlier error in EXP-0003:
    every vertex must sit at equal angle to exactly three face normals.
    """
    edge = min(_angle(a, b) for a, b in itertools.combinations(normals, 2))
    out = []
    for tri in itertools.combinations(range(12), 3):
        if all(abs(_angle(normals[i], normals[j]) - edge) < 1e-6
               for i, j in itertools.combinations(tri, 2)):
            c = [sum(normals[i][k] for i in tri) / 3 for k in range(3)]
            out.append(_normalise(c))
    assert len(out) == 20, f"expected 20 vertices, got {len(out)}"
    classes = {round(sorted(_angle(v, n) for n in normals)[0], 6) for v in out}
    assert len(classes) == 1, "vertices are not equivalent; coordinates are wrong"
    return out


def edge_midpoints(verts) -> list[tuple[float, float, float]]:
    edge = min(_angle(a, b) for a, b in itertools.combinations(verts, 2))
    return [_normalise([(x + y) / 2 for x, y in zip(a, b)])
            for a, b in itertools.combinations(verts, 2)
            if abs(_angle(a, b) - edge) < 1e-6]


def achievable_elevations() -> list[float]:
    """Every distinct face-axis elevation, over every mode of support."""
    normals = face_normals()
    verts = vertices(normals)
    mids = edge_midpoints(verts)
    out = set()
    for support in list(normals) + list(verts) + list(mids):
        up = _normalise(support)
        for n in normals:
            c = abs(sum(a * b for a, b in zip(up, n)))
            out.add(round(math.degrees(math.asin(min(1.0, c))), 6))
    return sorted(out)


# --- the fit ----------------------------------------------------------------

def longitudes_for_declination(dec: float) -> list[float]:
    """Solar longitudes at which the sun has this declination.

    sin(dec) = sin(obliquity) * sin(lambda), so each reachable declination
    occurs twice a year - once ascending, once descending.
    """
    s = math.sin(math.radians(dec)) / math.sin(math.radians(OBLIQUITY))
    if abs(s) > 1:
        return []
    lam = math.degrees(math.asin(max(-1.0, min(1.0, s))))
    return sorted({lam % 360.0, (180.0 - lam) % 360.0})


def events_at_latitude(elevations, latitude: float) -> list[float]:
    """Solar longitudes of every date the object could mark at this latitude."""
    out = []
    for e in elevations:
        dec = e - 90.0 + latitude          # noon altitude = 90 - phi + dec
        if abs(dec) <= OBLIQUITY:
            out.extend(longitudes_for_declination(dec))
    return sorted(out)


def distance_to_boundary(longitude: float) -> float:
    """Angular distance to the nearest zodiac sign boundary, in degrees."""
    r = longitude % SIGN_ARC
    return min(r, SIGN_ARC - r)


def fit(elevations, latitude: float):
    """Mean distance to the nearest sign boundary. Lower is a closer fit."""
    ev = events_at_latitude(elevations, latitude)
    if not ev:
        return None, 0
    return sum(distance_to_boundary(x) for x in ev) / len(ev), len(ev)


def scan(elevations, lat_min=LAT_MIN, lat_max=LAT_MAX, step=LAT_STEP):
    """Best fit over the latitude range, and the latitude that achieves it."""
    best = (None, None, 0)
    steps = int(round((lat_max - lat_min) / step))
    for i in range(steps + 1):
        phi = lat_min + i * step
        m, n = fit(elevations, phi)
        if m is not None and (best[0] is None or m < best[0]):
            best = (m, phi, n)
    return best


# --- the chance baseline ----------------------------------------------------

#: Distance from a uniformly random longitude to the nearest 30-degree
#: boundary is uniform on [0, 15]; its mean is exactly 7.5 degrees.
EXPECTED_AT_RANDOM = SIGN_ARC / 4


def monte_carlo(n_elevations: int, trials: int = 20000, seed: int = 20260810):
    """How well does an ARBITRARY elevation set do, given the same free scan?

    The latitude scan is a maximisation over a nuisance parameter, so the real
    object is guaranteed to beat 7.5 degrees. The question is whether it beats
    what a random set of the same size achieves with the same freedom.
    """
    rng = random.Random(seed)
    out = []
    for _ in range(trials):
        elev = sorted(rng.uniform(0.0, 90.0) for _ in range(n_elevations))
        m, _phi, _n = scan(elev, step=0.5)
        if m is not None:
            out.append(m)
    out.sort()
    return out


def report(trials: int = 20000) -> dict:
    elevations = achievable_elevations()
    best, lat, n_events = scan(elevations)

    print("EXP-0009  zodiac fit versus chance")
    print("=" * 72)
    print(f"  distinct face-axis elevations       {len(elevations)}")
    print("  " + ", ".join(f"{e:.2f}" for e in elevations) + " deg")
    print()
    print(f"  latitude scanned                    {LAT_MIN}-{LAT_MAX} N "
          f"in {LAT_STEP} deg steps")
    print(f"  best mean distance to a boundary    {best:.2f} deg")
    print(f"  at latitude                         {lat:.1f} N")
    print(f"  events at that latitude             {n_events}")
    at_edge = abs(lat - LAT_MIN) < LAT_STEP or abs(lat - LAT_MAX) < LAT_STEP
    if at_edge:
        print("  NOTE: the optimum sits at the edge of the scanned range, so it")
        print("        is a boundary artefact rather than a real alignment.")
    print(f"  expected at random (exact)          {EXPECTED_AT_RANDOM:.2f} deg")
    print()

    sims = monte_carlo(len(elevations), trials=trials)
    better = sum(1 for x in sims if x <= best)
    p = better / len(sims)
    median = sims[len(sims) // 2]
    print(f"  Monte Carlo, {len(sims)} random elevation sets, same free scan:")
    print(f"    median best fit                   {median:.2f} deg")
    print(f"    5th percentile                    {sims[len(sims)//20]:.2f} deg")
    print(f"    random sets doing at least as well as the real solid: "
          f"{better} of {len(sims)}  (p = {p:.3f})")
    print()
    if p > 0.05:
        print("  VERDICT: the fit is NOT better than chance.")
        print("  A free latitude scan beats 7.5 deg for almost any elevation set,")
        print("  because the scan is a maximisation over a nuisance parameter.")
        if best > median:
            print(f"  The real solid does WORSE than the median random set "
                  f"({best:.2f} against {median:.2f} deg): its elevations are, if")
            print("  anything, unusually badly placed for marking sign boundaries.")
    else:
        print("  VERDICT: the fit is better than chance would give. "
              "This would need explaining.")
    return {"elevations": elevations, "best": best, "latitude": lat,
            "events": n_events, "expected_random": EXPECTED_AT_RANDOM,
            "p": p, "median_random": median, "trials": len(sims)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=20000,
                    help="Monte Carlo trials (default 20000)")
    args = ap.parse_args()
    report(trials=args.trials)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
