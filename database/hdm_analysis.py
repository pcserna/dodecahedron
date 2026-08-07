"""
Assess hypothesis discrimination readiness.
Computes: which variables CAN be scored now vs. which are blocked and why.
Also runs a partial HDM for scoreable variables to show the analytic value.
"""

import sqlite3

conn = sqlite3.connect("database/rdorp.sqlite")

hypotheses = {r[0]: r[1] for r in conn.execute("SELECT hypothesis_id, name FROM hypotheses")}
ev_vars = {r[0]: (r[1], r[2]) for r in conn.execute(
    "SELECT ev_id, variable, discriminatory_power FROM evidence_variables")}

# ── 1. Classify each variable by scorability ──────────────────────────────────

obs_counts = {r[0]: r[1] for r in conn.execute(
    "SELECT ev_id, COUNT(DISTINCT rd_id) FROM artifact_observations GROUP BY ev_id")}

ENGINEERING = {"EV033","EV034","EV035","EV036","EV037"}  # need desk assessment, not more specimens
DERIVED     = {"EV039","EV040"}                           # need corpus-level stats

scoreable   = []  # can score now from existing observations
needs_work  = []  # can score now if engineering/derived assessment done
blocked     = []  # needs physical examination or literature not yet found

for ev_id, (var, power) in ev_vars.items():
    n = obs_counts.get(ev_id, 0)
    if ev_id in ENGINEERING:
        needs_work.append((ev_id, var, power, n, "Engineering desk assessment needed"))
    elif ev_id in DERIVED:
        if n >= 3:
            needs_work.append((ev_id, var, power, n, "Corpus stats can be computed now"))
        else:
            blocked.append((ev_id, var, power, n, "Insufficient specimen measurements"))
    elif n >= 3:
        scoreable.append((ev_id, var, power, n, "Ready"))
    elif n >= 1:
        needs_work.append((ev_id, var, power, n, f"Only {n} specimen(s); acceptable for preliminary"))
    else:
        blocked.append((ev_id, var, power, n, "No observations — needs physical/literature access"))

print("=" * 70)
print(f"SCOREABLE NOW ({len(scoreable)} variables)")
print("=" * 70)
for ev, var, power, n, reason in sorted(scoreable, key=lambda x: (
        0 if x[2]=="Very High" else 1 if x[2]=="High" else 2, x[0])):
    print(f"  {ev}  {var[:30]:<30} [{power:<9}] n={n:>2}")

print()
print("=" * 70)
print(f"CAN SCORE WITH ADDITIONAL WORK ({len(needs_work)} variables)")
print("=" * 70)
for ev, var, power, n, reason in sorted(needs_work, key=lambda x: x[0]):
    print(f"  {ev}  {var[:30]:<30} [{power:<9}] n={n:>2}  → {reason}")

print()
print("=" * 70)
print(f"BLOCKED — CANNOT SCORE YET ({len(blocked)} variables)")
print("=" * 70)
for ev, var, power, n, reason in sorted(blocked, key=lambda x: (
        0 if x[2]=="Very High" else 1 if x[2]=="High" else 2, x[0])):
    print(f"  {ev}  {var[:30]:<30} [{power:<9}]  {reason}")

# ── 2. Partial HDM: score variables where we CAN score ────────────────────────
# Scoring rule: compare HPM prediction with corpus observation direction.
# We apply simple corpus-level aggregations manually for key scoreable variables.

print()
print("=" * 70)
print("PARTIAL HDM — PRELIMINARY SCORES FOR SCOREABLE VARIABLES")
print("Scale: +2 strongly confirms | +1 confirms | 0 neutral | -1 contradicts | -2 strongly contradicts")
print("=" * 70)

# Manual corpus-level observations for scoreable variables
# These derive directly from the artifact_observations data already in the database.

corpus_observations = {
    # (ev_id, observation_summary, direction_vs_expectation)
    # direction: 'confirmed' / 'absent' / 'ambiguous'
    "EV001": ("Sizes 44-128mm (mean ~75mm); range 4-11cm confirmed",    "confirmed"),
    "EV002": ("Weights 1.67g fragment to 553g; complete: 245-553g",     "confirmed"),
    "EV003": ("Wall thickness: 1.1-3.7mm; consistently thin",           "confirmed"),
    "EV004": ("All complete/near-complete specimens: variable hole sizes in same object",
              "confirmed"),
    "EV006": ("Bevelled/chamfered edges in BH-692011; raised rims in HAMP-CE1119",
              "confirmed"),
    "EV008": ("Knob diameters: 6.0-14.28mm across specimens; consistent within specimen",
              "confirmed"),
    "EV011": ("Alloys: Cu/Sn/Pb mixtures confirmed (Norton Disney XRF; Llandow XRF; Liege record)",
              "confirmed"),
    "EV012": ("Exterior smooth/finished; interior rough/crude in all specimens with data",
              "confirmed"),
    "EV014": ("Concentric circles/rings around holes in most decorated specimens",
              "confirmed"),
    "EV018": ("Mixed: no wear (RD-0005 Norton Disney); pitting/abrasion present in 3 others",
              "ambiguous"),
    "EV025": ("17/19 cultivated land (uninformative); 2 confirmed military (Corbridge, Arbeia)",
              "ambiguous"),
}

# Get HPM predictions
hpm = {}
for r in conn.execute("SELECT hypothesis_id, ev_id, prediction FROM hpm"):
    hpm[(r[0], r[1])] = r[2]

pred_to_num = {"++": 2, "+": 1, "0": 0, "-": -1, "--": -2}

# Score function: confirmed obs → prediction value as-is; absent → invert sign; ambiguous → 0
def score(pred, direction):
    p = pred_to_num.get(pred, 0)
    if direction == "confirmed":
        return p                   # prediction fulfilled
    elif direction == "absent":
        return -p                  # prediction not fulfilled → invert
    else:
        return 0                   # ambiguous → neutral

print(f"\n{'Variable':<32}", end="")
for h in sorted(hypotheses.keys()):
    print(f" {h[-3:]}", end="")
print()
print("-" * 70)

running_scores = {h: 0 for h in hypotheses}
scored_vars = 0

for ev_id, (obs_text, direction) in corpus_observations.items():
    var_name = ev_vars[ev_id][0][:30]
    power    = ev_vars[ev_id][1]
    row_scores = {}
    for h in sorted(hypotheses.keys()):
        pred = hpm.get((h, ev_id), "0")
        s = score(pred, direction)
        row_scores[h] = s
        running_scores[h] += s
    scored_vars += 1
    scores_str = "".join(f"{row_scores[h]:>+3}" if row_scores[h] != 0 else "  0"
                         for h in sorted(hypotheses.keys()))
    print(f"  {ev_id} {var_name:<30} {scores_str}")

print("-" * 70)
totals = "".join(f"{running_scores[h]:>+3}" for h in sorted(hypotheses.keys()))
print(f"  {'PARTIAL TOTAL':<36} {totals}")
print(f"  {'(from '+str(scored_vars)+' of 40 variables)':<36}")

print()
print("  H001=Structural connector  H002=Measuring instrument  H003=Ritual object")
print("  H004=Candlestick           H005=Textile tool          H006=Astronomical")
print("  H007=Military equipment    H008=Portable shrine")

print()
print("=" * 70)
print("VERDICT")
print("=" * 70)
max_h = max(running_scores, key=running_scores.get)
print(f"  Highest partial score: {max_h} ({hypotheses[max_h]}): {running_scores[max_h]:+d}")
print(f"  Scoreable variables: {scored_vars}/40")
print(f"  Missing Very High vars: {sum(1 for e,v,p,n,_ in blocked if p=='Very High')}")
print(f"  Missing High vars:      {sum(1 for e,v,p,n,_ in blocked if p=='High')}")

conn.close()
