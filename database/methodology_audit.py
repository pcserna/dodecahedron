"""
RDORP — Methodological audit of the current partial HDM.
Identifies every assumption and structural weakness before we harden the scoring.
"""

import sqlite3

conn = sqlite3.connect("database/rdorp.sqlite")

# ── 1. Corpus representativeness ────────────────────────────────────────────
print("=" * 68)
print("1. CORPUS REPRESENTATIVENESS")
print("=" * 68)

total = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
by_country = conn.execute(
    "SELECT country, COUNT(*) n FROM specimens GROUP BY country ORDER BY n DESC"
).fetchall()
by_context = conn.execute("""
    SELECT context_category, COUNT(*) n FROM specimens
    GROUP BY context_category ORDER BY n DESC
""").fetchall()
by_conf = conn.execute(
    "SELECT confidence, COUNT(*) n FROM specimens GROUP BY confidence ORDER BY n"
).fetchall()

print(f"  Total specimens: {total}")
print(f"  Known corpus ~130 specimens → coverage: {total/130*100:.0f}%")
print()
print("  By country:")
for r in by_country:
    print(f"    {r[0]:<20} {r[1]:>3}  ({r[1]/total*100:.0f}%)")
print()
print("  By context_category (in specimens table):")
for r in by_context:
    print(f"    {str(r[0]):<20} {r[1]:>3}")
print()
print("  By source confidence:")
for r in by_conf:
    print(f"    {r[0]}: {r[1]}")

# ── 2. EV025 site-type quality audit ─────────────────────────────────────────
print()
print("=" * 68)
print("2. EV025 SITE TYPE — DATA QUALITY AUDIT")
print("=" * 68)
informative = 0
unknown = 0
for r in conn.execute(
    "SELECT observed_value FROM artifact_observations WHERE ev_id='EV025'"
):
    v = (r[0] or "").lower()
    if "cultivated" in v or "unknown" in v or "purchased" in v or "not specified" in v:
        unknown += 1
    else:
        informative += 1
print(f"  EV025 observations: {informative + unknown}")
print(f"    Informative (known context): {informative}")
print(f"    Uninformative (cultivated/unknown): {unknown}")
print(f"  → Only {informative}/{informative+unknown} ({informative/(informative+unknown)*100:.0f}%) of EV025 "
      f"observations carry discriminatory value")

# ── 3. HPM prediction uncertainty ────────────────────────────────────────────
print()
print("=" * 68)
print("3. HPM PREDICTION UNCERTAINTY — CONTESTABLE PREDICTIONS")
print("=" * 68)
print("  These predictions could legitimately be debated by archaeologists:")
contestable = [
    ("EV004", "H001", "++",
     "Varying holes support connector — but a gauge tool ALSO needs varied holes (H002 also ++)"),
    ("EV012", "H002", "++",
     "High casting quality for measuring — but ritual (H003) equally requires prestige quality"),
    ("EV033", "H001", "++",
     "Rods fit is a prerequisite for H001 — but also compatible with H004 (candles=rods) and H005"),
    ("EV037", "H001", "++",
     "Modular assembly is H001 core claim — but the corpus size variation now contradicts this"),
    ("EV025", "H007", "++",
     "Military context is only 2/20 specimens — but all other hypotheses also predict mixed contexts"),
]
for ev, h, pred, comment in contestable:
    print(f"  {ev} × {h} [{pred}]: {comment}")

# ── 4. Scoring function weaknesses ───────────────────────────────────────────
print()
print("=" * 68)
print("4. SCORING FUNCTION WEAKNESSES")
print("=" * 68)
weaknesses = [
    "Unweighted: a Very High variable counts the same as a Medium variable",
    "Confidence-blind: A-grade archival evidence counts same as E-grade Wikipedia",
    "Binary direction: 'ambiguous' collapses all uncertainty to 0 rather than a partial score",
    "No sensitivity analysis: scores not tested against ±1 HPM variation",
    "No uncertainty bounds: final score is a point estimate with no confidence interval",
    "Corpus bias: 85% British specimens, ~0% German/Dutch/Luxembourgish specimens",
    "Fragment vs. complete: fragment observations (incomplete specimens) weighted equally",
]
for i, w in enumerate(weaknesses, 1):
    print(f"  {i}. {w}")

# ── 5. Maximum possible score per variable ────────────────────────────────────
print()
print("=" * 68)
print("5. UNSCORED VARIABLES — MAXIMUM DISCRIMINATORY IMPACT")
print("   (what the ranking could change by if each were scored)")
print("=" * 68)

scored_evs = {
    "EV001","EV002","EV003","EV004","EV006","EV008",
    "EV011","EV012","EV014","EV018","EV025",
    "EV033","EV034","EV035","EV036","EV037",
}

dp_weight = {"Very High": 3, "High": 2, "Medium": 1}

rows = conn.execute("""
    SELECT ev_id, variable, discriminatory_power
    FROM evidence_variables
    ORDER BY CASE discriminatory_power
        WHEN 'Very High' THEN 1 WHEN 'High' THEN 2 ELSE 3 END, ev_id
""").fetchall()

print(f"  {'EV':<6} {'Variable':<32} {'Power':<12} {'Max impact':>10}  {'Note'}")
print("  " + "-" * 68)
for ev_id, var, power in rows:
    if ev_id not in scored_evs:
        w = dp_weight.get(power, 1)
        # max impact: could change score ±(weight × 2) for each hypothesis
        max_change = w * 2
        note = "physical access needed" if ev_id in {
            "EV019","EV020","EV023","EV024","EV027","EV007","EV021"
        } else "desk/literature work possible"
        print(f"  {ev_id:<6} {var[:32]:<32} {(power or ''):<12} {max_change:>+4}/hyp  {note}")

conn.close()
