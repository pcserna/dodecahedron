"""
RDORP — EV039 Standardisation Test
Tests whether hole diameters cluster at common values across specimens,
which would support H002 (measuring gauge) over H001 (connector) and H005 (textile).
"""

import sqlite3
import statistics
import math

conn = sqlite3.connect("database/rdorp.sqlite")

# ── Collect all hole diameter data from observations ─────────────────────────
# We have two types of data:
#   1. Per-specimen ranges (min/max from EV004 observations)
#   2. Structured columns hole_01_mm…hole_12_mm in specimens table (currently empty)

print("=" * 68)
print("EV039 STANDARDISATION TEST — HOLE DIAMETER ANALYSIS")
print("=" * 68)

# Extract hole range data from EV004 observations
hole_data = {}  # rd_id → {min, max, individual_vals}

for r in conn.execute("""
    SELECT s.rd_id, s.specimen_name, s.max_diameter_mm,
           o.ev_id, o.observed_value, o.confidence
    FROM artifact_observations o
    JOIN specimens s ON s.rd_id = o.rd_id
    WHERE o.ev_id IN ('EV004','EV005')
    ORDER BY s.rd_id, o.ev_id
"""):
    rd_id, name, overall, ev_id, val, conf = r
    if rd_id not in hole_data:
        hole_data[rd_id] = {"name": name[:30], "overall_mm": overall,
                             "conf": conf, "ranges": [], "ev005": None}
    if ev_id == "EV004":
        hole_data[rd_id]["ranges"].append(val or "")
    elif ev_id == "EV005":
        hole_data[rd_id]["ev005"] = val

# Parse numeric values from descriptions
import re

def extract_numbers(text):
    """Pull all mm values from a text observation."""
    return [float(x) for x in re.findall(r'\b(\d+\.?\d*)\s*mm\b', text or "")]

# Build per-specimen hole diameter datasets
specimens_with_holes = {}
for rd_id, d in hole_data.items():
    nums = []
    for desc in d["ranges"]:
        nums.extend(extract_numbers(desc))
    if nums:
        specimens_with_holes[rd_id] = {
            "name":      d["name"],
            "overall":   d["overall_mm"],
            "holes":     sorted(nums),
            "conf":      d["conf"],
            "ev005":     d["ev005"],
        }

print("\n=== PER-SPECIMEN HOLE DIAMETER DATA ===\n")
print(f"  {'ID':<8} {'Name':<30} {'Overall':>8} {'HoleMM (parsed from obs)'}")
print("  " + "-" * 72)
for rd_id in sorted(specimens_with_holes):
    d = specimens_with_holes[rd_id]
    holes_str = ", ".join(f"{h:.1f}" for h in d["holes"])
    print(f"  {rd_id:<8} {d['name']:<30} {str(d['overall'] or '?'):>8}mm  [{holes_str}]  conf={d['conf']}")

# ── Within-specimen analysis ──────────────────────────────────────────────────
print("\n=== WITHIN-SPECIMEN VARIATION ===")
print("  (CV = coefficient of variation = std/mean × 100)")
print(f"\n  {'ID':<8} {'n holes':>7} {'min':>6} {'max':>6} {'range':>7} {'mean':>6} {'CV%':>6}  Interpretation")
print("  " + "-" * 72)

cv_values = []
for rd_id in sorted(specimens_with_holes):
    d = specimens_with_holes[rd_id]
    h = d["holes"]
    if len(h) < 2:
        continue
    mn   = min(h)
    mx   = max(h)
    rng  = mx - mn
    mean = statistics.mean(h)
    std  = statistics.stdev(h) if len(h) > 1 else 0
    cv   = (std / mean * 100) if mean else 0
    # Interpretation: high CV = lots of variation (supports H001/H005)
    #                  low CV = standardised (supports H002)
    interp = "highly variable" if cv > 20 else ("moderate" if cv > 10 else "standardised")
    cv_values.append((rd_id, cv, mean, rng))
    note = " ← FRAGMENT only" if d["overall"] is None else ""
    print(f"  {rd_id:<8} {len(h):>7} {mn:>6.1f} {mx:>6.1f} {rng:>7.1f} {mean:>6.1f} {cv:>6.1f}%  {interp}{note}")

# ── Between-specimen: do any hole values recur? ───────────────────────────────
print("\n=== BETWEEN-SPECIMEN: DO COMMON SIZES REPEAT? ===")
print("  (Would support H002 if specific diameters appear across specimens)")
print("  Tolerance: ±1.0mm for 'same size'\n")

all_holes = []
for rd_id, d in specimens_with_holes.items():
    for h in d["holes"]:
        all_holes.append((h, rd_id, d["name"][:20]))

# Cluster holes into bins of ±1.0mm
TOL = 1.0
bins = []  # list of (center, [rd_ids])
used = set()
for h, rid, _ in sorted(all_holes):
    if h in used:
        continue
    cluster = [(hh, rr) for hh, rr, _ in all_holes
               if abs(hh - h) <= TOL and rr != rid]
    if cluster:
        ids = [rid] + [rr for _, rr in cluster]
        sizes = [h] + [hh for hh, _ in cluster]
        bins.append((round(statistics.mean(sizes), 1), ids, sizes))
        used.update([h] + [hh for hh, _ in cluster])

if bins:
    print(f"  {'Size cluster':<14} {'Specimens sharing this size'}")
    for center, ids, sizes in sorted(bins, key=lambda x: -len(x[1])):
        if len(ids) > 1:
            print(f"  ~{center:.1f}mm          {', '.join(sorted(set(ids)))} "
                  f"(values: {', '.join(f'{s:.1f}' for s in sizes)})")
else:
    print("  No clusters found — no hole sizes repeat across specimens within ±1mm")

print("\n=== CROSS-SPECIMEN SIZE RATIO TEST ===")
print("  If H002 (measuring gauge): holes should be in simple integer ratios")
print("  (e.g., 10, 12, 14, 16mm = 2mm steps; or 10, 15, 20mm = ratio 1.5:1)")
print()

# Collect all unique hole values with their specimen
unique_holes = sorted(set(round(h, 1) for h, _, _ in all_holes))
print(f"  All unique hole values in corpus (rounded to 0.1mm):")
print(f"  {', '.join(str(h) for h in unique_holes)}")
print()

# Check for arithmetic progressions
if len(unique_holes) >= 3:
    steps = [round(unique_holes[i+1]-unique_holes[i], 1)
             for i in range(len(unique_holes)-1)]
    step_counts = {}
    for s in steps:
        step_counts[s] = step_counts.get(s, 0) + 1
    most_common_step = max(step_counts, key=step_counts.get)
    print(f"  Step sizes between consecutive values: {steps}")
    print(f"  Most common step: {most_common_step}mm (occurs {step_counts[most_common_step]}× "
          f"out of {len(steps)} intervals)")
    # A truly standardised gauge would have a dominant step size
    regularity = step_counts[most_common_step] / len(steps) * 100
    print(f"  Regularity of most common step: {regularity:.0f}% of intervals")
    if regularity > 60:
        print("  → PATTERN DETECTED: hole sizes show arithmetic progression")
    else:
        print("  → NO CLEAR PATTERN: hole sizes do not follow a common step")

# ── Statistical verdict ───────────────────────────────────────────────────────
print("\n=== EV039 VERDICT ===")
if cv_values:
    mean_cv = statistics.mean(v[1] for v in cv_values)
    print(f"  Mean within-specimen CV: {mean_cv:.1f}%")
    print(f"  (CV > 20% = highly variable; CV < 10% = standardised)")
    print()
    if mean_cv > 20:
        print("  FINDING: Hole diameters are HIGHLY VARIABLE within specimens (CV > 20%).")
        print("  This confirms corpus-level evidence E004 (variable holes).")
        print("  Contradicts H002 (measuring gauge) which predicts standardised sizes.")
        print("  Supports H001 (connector, different rods) and H005 (different yarn gauges).")
    elif mean_cv > 10:
        print("  FINDING: Hole diameters show MODERATE variation.")
        print("  Neither strongly standardised nor maximally variable.")
    else:
        print("  FINDING: Hole diameters are STANDARDISED (CV < 10%).")
        print("  Supports H002 (measuring gauge).")

print()
print("  DATA LIMITATION: Only min/max ranges available for most specimens.")
print("  Individual face-by-face measurements needed for robust statistics.")
print("  Full 12-face datasets would enable: Kolmogorov-Smirnov, ANOVA,")
print("  hierarchical clustering of size series.")

conn.close()
