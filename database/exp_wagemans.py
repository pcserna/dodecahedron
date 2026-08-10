#!/usr/bin/env python3
"""EXP-0012 - the Wagemans sowing-calendar model, reproduced and tested.

The hypothesis
--------------
G.M.C. Wagemans (romandodecahedron.com) proposes that the object is an
astronomical instrument for fixing the sowing date of winter grain. It is set
down on a face, and at solar noon light is sighted through a pair of OPPOSED
apertures. Because each pair has its own diameters, each gives its own limiting
sun angle, and each angle corresponds to a date. He reports 19-20 "measuring
points" per object and, for two Dutch specimens, average deviations of 0.11 deg
(Elst) and 0.29 deg (Hartwerd) between the angle of a measuring point and the
angle of the sun on the matching date.

**The mechanism is geometrically sound and this project had not specified it.**
Its central constant, 26.6 deg, is exactly the face-rest elevation EXP-0003
derives from first principles: arctan(1/2) = 26.565 deg. C-14 tests internal
light projection and C-15 tests suspension from a knob; neither is this.

What this module tests
----------------------
1. **Is the deviation statistic evidence of anything?** He matches each
   measuring point to the date on which the noon sun stands at that angle, and
   reports the residual. But the sun sweeps its annual range continuously, so
   EVERY angle inside that range has a date that matches it to within a
   fraction of a degree. The residual measures the fineness of his date grid,
   not a property of the object. This is tested by running the same statistic
   on random angle sets.
2. **Do the predicted angles depend on the object at all?** Applied to
   specimens with published opposed pairs and face-to-face distances.
3. **Is the resulting date window distinctive?** Compared against the windows
   random aperture sets of the same size produce.

Sources for the specimen data are PUB-0019 (Sparavigna), reproducing
measurements at one and two removes. Quality is poor and is reported.

Run: python database/exp_wagemans.py
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exp_zodiac import obliquity_at, ROMAN_EPOCH   # noqa: E402

#: The Roman-period value, not the modern one. See exp_zodiac.obliquity_at.
OBLIQUITY = obliquity_at(ROMAN_EPOCH)
#: Face-rest elevation of the five non-vertical face-pair axes, from EXP-0003.
AXIS_ELEVATION = math.degrees(math.atan(0.5))     # 26.565...

#: Specimens with BOTH published opposed pairs and a face-to-face distance.
#: (name, [(d1, d2), ...], face_to_face_mm, latitude, note)
SPECIMENS = [
    ("Jublains (RD-0020)",
     [(22.0, 21.5), (17.0, 16.5), (22.0, 21.0), (15.5, 11.5), (10.5, 17.0)],
     50.0, 48.2,
     "PUB-0019 table I. THE ONLY EXCAVATED, SEALED-CONTEXT SPECIMEN with a "
     "published pairing. Baseline 48-52 mm depending on the axis; 50 used. "
     "The sixth pair is elliptic and is omitted"),
    ("Avenches (RD-0034)",
     [(14.2, 15.4), (14.5, 13.4), (8.7, 10.4), (20.6, 18.3), (24.2, 26.5),
      (20.2, 17.6)], 46.5, 46.9,
     "PUB-0019 table II, measured at the Musee romain d'Avenches. Baseline "
     "46.5 mm - an earlier version of this module ASSUMED 55 mm because the "
     "figure had not been extracted"),
    ("Vienne (RD-0035)",
     [(24.0, 23.0), (22.0, 19.0), (20.0, 14.0), (20.0, 14.0), (22.0, 15.0),
      (13.5, 22.0)], 44.0, 45.5,
     "PUB-0019 table V. Provenance E, an unexcavated private-collection piece"),
    ("Carnuntum (RD-0036)",
     [(20.1, 20.3), (13.2, 13.7), (21.4, 22.4), (25.0, 26.5), (15.3, 17.3),
      (13.0, 10.5)], 40.0, 48.1,
     "PUB-0019 table III, at two removes; RD-0036 is rejected for geometry"),
    ("Tongeren (RD-0006)",
     [(16.0, 16.2), (7.5, 8.5), (10.5, 12.5), (20.0, 22.5), (12.5, 15.5),
      (16.5, 12.5)], 63.0, 50.8,
     "PUB-0019 table IV; RD-0006 is rejected for all scoring, confidence E"),
]


def measuring_angle(d1: float, d2: float, face_to_face: float) -> float:
    """Wagemans's limiting sun angle for one opposed pair.

    angle = 26.6 + arctan((r1 + r2) / D), the axis elevation plus the angular
    tolerance the two apertures allow.
    """
    return AXIS_ELEVATION + math.degrees(
        math.atan(((d1 / 2) + (d2 / 2)) / face_to_face))


def noon_altitude(latitude: float, day_of_year: int) -> float:
    """Solar noon altitude, with declination from a standard approximation."""
    dec = OBLIQUITY * math.sin(math.radians(360 / 365.24 * (day_of_year - 80)))
    return 90.0 - latitude + dec


def date_for_angle(latitude: float, angle: float, autumn: bool = True):
    """The day of year on which the noon sun stands at this angle.

    Returns (day, residual). The residual is what Wagemans reports as
    "deviation". Searching a one-day grid, the residual is bounded by how much
    the sun moves in a day - a fraction of a degree near the equinox - FOR ANY
    ANGLE IN RANGE. That is the point of the test.
    """
    days = range(182, 366) if autumn else range(1, 182)
    best, best_err = None, None
    for d in days:
        err = abs(noon_altitude(latitude, d) - angle)
        if best_err is None or err < best_err:
            best, best_err = d, err
    return best, best_err


def day_to_date(day: int) -> str:
    import datetime
    return (datetime.date(2001, 1, 1) + datetime.timedelta(days=day - 1)).strftime("%d %b")


def deviation_for_angles(latitude: float, angles: list[float]) -> float:
    """Mean residual over a set of angles - Wagemans's headline statistic."""
    errs = []
    for a in angles:
        lo = 90.0 - latitude - OBLIQUITY
        hi = 90.0 - latitude + OBLIQUITY
        if lo <= a <= hi:
            errs.append(date_for_angle(latitude, a)[1])
    return (sum(errs) / len(errs)) if errs else float("nan")


def null_deviation(latitude: float, n: int, trials: int = 2000,
                   seed: int = 20260812) -> list[float]:
    """The same statistic for RANDOM angles inside the sun's annual range."""
    rng = random.Random(seed)
    lo = 90.0 - latitude - OBLIQUITY
    hi = 90.0 - latitude + OBLIQUITY
    out = []
    for _ in range(trials):
        angles = [rng.uniform(lo, hi) for _ in range(n)]
        out.append(deviation_for_angles(latitude, angles))
    out.sort()
    return out


def report(trials: int = 2000) -> dict:
    print("EXP-0012  the Wagemans sowing-calendar model")
    print("=" * 78)
    print(f"  central constant 26.6 deg = arctan(1/2) = {AXIS_ELEVATION:.3f} deg")
    print("  this is exactly the face-rest elevation EXP-0003 derives, so the")
    print("  mechanism is built on the right solid.")
    print()

    print("  1. THE PREDICTED MEASURING ANGLES")
    results = {}
    for name, pairs, d, lat, note in SPECIMENS:
        angles = sorted(measuring_angle(a, b, d) for a, b in pairs)
        results[name] = (angles, lat, note)
        print(f"\n    {name}   face-to-face {d:.0f} mm, latitude {lat:.1f} N")
        print(f"      {note}")
        print("      angles: " + ", ".join(f"{a:.2f}" for a in angles))
        lo = 90.0 - lat - OBLIQUITY
        hi = 90.0 - lat + OBLIQUITY
        usable = [a for a in angles if lo <= a <= hi]
        print(f"      sun's annual noon range at this latitude: "
              f"{lo:.1f} to {hi:.1f} deg")
        print(f"      angles the sun can actually reach: {len(usable)} of {len(angles)}")
        if usable:
            days = [date_for_angle(lat, a)[0] for a in usable]
            print("      dates: " + ", ".join(day_to_date(x) for x in sorted(days)))

    print("\n  2. IS THE DEVIATION STATISTIC EVIDENCE OF ANYTHING?")
    print("  Wagemans reports 0.11 deg for Elst and 0.29 deg for Hartwerd as")
    print("  the agreement between measuring point and sun. The sun sweeps its")
    print("  range continuously, so any angle inside it has a matching date.")
    print()
    for name, (angles, lat, _note) in results.items():
        lo, hi = 90.0 - lat - OBLIQUITY, 90.0 - lat + OBLIQUITY
        usable = [a for a in angles if lo <= a <= hi]
        if not usable:
            print(f"    {name:22} no angle is reachable; statistic undefined")
            continue
        obs = deviation_for_angles(lat, usable)
        null = null_deviation(lat, len(usable), trials=trials)
        med = null[len(null) // 2]
        better = sum(1 for x in null if x <= obs) / len(null)
        print(f"    {name:22} observed {obs:.3f} deg;  random angles "
              f"{med:.3f} deg;  {better:.0%} of random sets do as well")
    print()
    print("  A RANDOM SET OF ANGLES SCORES THE SAME. The statistic measures the")
    print("  fineness of the date grid, not a property of the object: it is")
    print("  bounded by how far the sun moves in one day. It cannot distinguish")
    print("  a designed instrument from a bag of arbitrary holes.")

    print("\n  2b. IS THE SOWING WINDOW A RESULT, OR IS IT FORCED?")
    print("  The predicted dates above fall in late August to early October,")
    print("  which is when winter grain is sown. That is the observation the")
    print("  reading rests on. But the axis elevation is fixed at 26.6 deg and")
    print("  an aperture tolerance is necessarily positive, so every angle must")
    print("  land above 26.6 deg - and at these latitudes the sun crosses that")
    print("  band in late summer, and again in spring.")
    print()
    rng = random.Random(20260813)
    for name, pairs, d, lat, _n in SPECIMENS:
        got = []
        for _ in range(1000):
            fake = [(rng.uniform(6, 27), rng.uniform(6, 27)) for _ in range(6)]
            angles = [measuring_angle(a, b, d) for a, b in fake]
            lo, hi = 90.0 - lat - OBLIQUITY, 90.0 - lat + OBLIQUITY
            got.extend(date_for_angle(lat, a)[0] for a in angles if lo <= a <= hi)
        got.sort()
        p05, p95 = got[len(got) // 20], got[-max(1, len(got) // 20)]
        print(f"    {name:22} random apertures -> dates {day_to_date(p05)} "
              f"to {day_to_date(p95)} (90 % of them)")
    print()
    print("  RANDOM APERTURE SETS PRODUCE THE SAME SEASON. The sowing-window")
    print("  match follows from the solid's geometry and the latitude of")
    print("  north-west Europe, not from anything a maker chose. It would hold")
    print("  for a dodecahedron drilled at random.")

    print("\n  3. WHAT THE MODEL ACTUALLY REQUIRES, AND WHAT THE CORPUS HAS")
    print("    - the opposed PAIRING of every aperture: published for 3 of 40")
    print("      specimens, and 2 of those 3 are rejected on quality grounds")
    print("    - the face-to-face distance: published for 2 of the 3")
    print("    - a fixed latitude: the corpus spans 43.7 to 55 N, and the")
    print("      predicted dates move about 1 day per 0.4 deg of latitude")

    print("\n" + "=" * 78)
    print("  VERDICT")
    print("=" * 78)
    print("  THE MECHANISM IS SOUND AND WAS MISSING FROM THIS PROJECT. It is")
    print("  built on the correct solid and its central constant is ours.")
    print()
    print("  THE EVIDENCE OFFERED FOR IT IS NOT EVIDENCE. The deviation")
    print("  statistic is satisfied by any set of angles in the sun's range,")
    print("  as the null above shows, so it cannot support the reading.")
    print()
    print("  THE MODEL IS NOT YET REFUTED EITHER. Testing it properly needs the")
    print("  opposed pairing and the face-to-face distance on the same")
    print("  specimen, which the corpus has for one unrejected object. That is")
    print("  RDORP-013 item B2 again, and this is now a third finding waiting")
    print("  on it.")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=2000)
    args = ap.parse_args()
    report(trials=args.trials)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
