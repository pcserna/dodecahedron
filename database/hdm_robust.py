"""
RDORP — Robust HDM Scoring
Addresses methodology weaknesses:
  1. Discriminatory-power weighting (Very High=3, High=2, Medium=1)
  2. Source confidence weighting (A/B=1.0, C=0.75, D=0.5, E=0.25)
  3. Sensitivity analysis: ±1 on contestable HPM predictions
  4. Uncertainty bounds: worst/best case for all unscored variables
  5. Writes formal partial scores to hdm_scores table
"""

import sqlite3
from collections import defaultdict

conn = sqlite3.connect("database/rdorp.sqlite")

# ── Reference data ────────────────────────────────────────────────────────────

hypotheses = {r[0]: r[1] for r in conn.execute(
    "SELECT hypothesis_id, name FROM hypotheses ORDER BY hypothesis_id")}
H_KEYS = sorted(hypotheses.keys())

ev_info = {r[0]: {"var": r[1], "power": r[2]} for r in conn.execute(
    "SELECT ev_id, variable, discriminatory_power FROM evidence_variables")}

hpm = {(r[0], r[1]): r[2] for r in conn.execute(
    "SELECT hypothesis_id, ev_id, prediction FROM hpm")}

DP_WEIGHT  = {"Very High": 3, "High": 2, "Medium": 1}
CONF_WEIGHT = {"A": 1.0, "B": 1.0, "C": 0.75, "D": 0.5, "E": 0.25}
PRED_NUM = {"++": 2, "+": 1, "0": 0, "-": -1, "--": -2}

def pred_score(pred, direction, conf="B"):
    """Convert HPM prediction + corpus observation direction to a raw score."""
    p = PRED_NUM.get(pred, 0)
    cw = CONF_WEIGHT.get(conf, 1.0)
    if direction == "confirmed":
        return p * cw
    elif direction == "absent":
        return -p * cw
    else:  # ambiguous
        return 0.0

def weighted_score(raw, ev_id):
    return raw * DP_WEIGHT.get(ev_info[ev_id]["power"], 1)

# ── Corpus observations (from hdm_analysis.py, keyed by ev_id) ───────────────
# Confidence represents minimum quality of underlying evidence.
# direction: 'confirmed' / 'absent' / 'ambiguous'

SCORED_OBS = {
    "EV001": ("confirmed", "B"),   # sizes confirmed across corpus
    "EV002": ("confirmed", "B"),   # masses measured
    "EV003": ("confirmed", "B"),   # wall thickness measured
    "EV004": ("confirmed", "B"),   # variable holes in all complete specimens
    "EV006": ("confirmed", "B"),   # hole profiles smooth/bevelled
    "EV008": ("confirmed", "B"),   # knob dimensions measured
    "EV011": ("confirmed", "C"),   # alloy from XRF (Norton Disney C, others)
    "EV012": ("confirmed", "B"),   # interior rough, exterior smooth
    "EV014": ("confirmed", "B"),   # concentric ring decoration confirmed
    "EV018": ("ambiguous", "B"),   # mixed wear evidence (3 with, 1 without)
    # EV025: 2 military (Corbridge, Arbeia) + 2 civilian baths (Jublains, Arles)
    #         + 1 near villa (Norton Disney) + 15 unknown/cultivated land
    # Overall still ambiguous but baths pattern (2/7 known) slightly informs
    "EV025": ("ambiguous", "A"),
    "EV033": ("confirmed", "C"),   # rod fit confirmed (derived)
    "EV034": ("confirmed", "C"),   # rope routing feasible (derived)
    "EV035": ("confirmed", "C"),   # structural stability (derived)
    "EV036": ("confirmed", "C"),   # load transfer feasible (derived)
    "EV037": ("absent",    "C"),   # assembly absent: 3x size range (derived)
    # EV039: within-specimen CV = 40% (highly variable); no arithmetic progression
    # between-specimen: only one ~18mm cluster (2 specimens); no common standard
    # → standardisation is ABSENT; contradicts H002 (measuring gauge)
    "EV039": ("absent",    "B"),
}

# ── Weighted partial scores ───────────────────────────────────────────────────

print("=" * 72)
print("WEIGHTED PARTIAL HDM SCORES  (dp_weight × conf_weight applied)")
print("Very High=3  High=2  Medium=1  |  A/B=1.0  C=0.75  D=0.5  E=0.25")
print("=" * 72)

unweighted = defaultdict(float)
weighted   = defaultdict(float)

ev_scores = {}
for ev_id, (direction, conf) in SCORED_OBS.items():
    row = {}
    for h in H_KEYS:
        pred = hpm.get((h, ev_id), "0")
        raw  = pred_score(pred, direction, conf)
        wt   = weighted_score(raw, ev_id)
        row[h] = (raw, wt)
        unweighted[h] += raw
        weighted[h]   += wt
    ev_scores[ev_id] = row

# Print table
header = f"  {'Variable':<30} {'Power':<10}"
for h in H_KEYS:
    header += f" {h[-3:]:>4}"
print(header)
print("  " + "-" * 70)

for ev_id, (direction, conf) in SCORED_OBS.items():
    var  = ev_info[ev_id]["var"][:28]
    power = ev_info[ev_id]["power"]
    flag = "??" if direction == "ambiguous" else ("OK" if direction == "confirmed" else "NO")
    line = f"  {var:<30} {power[:8]:<10}"
    for h in H_KEYS:
        raw, wt = ev_scores[ev_id][h]
        line += f" {wt:>+4.0f}"
    print(f"{line}  [{flag} conf={conf}]")

print("  " + "-" * 70)
print(f"  {'UNWEIGHTED TOTAL':<40}", end="")
for h in H_KEYS:
    print(f" {unweighted[h]:>+4.0f}", end="")
print()
print(f"  {'WEIGHTED TOTAL':<40}", end="")
for h in H_KEYS:
    print(f" {weighted[h]:>+4.0f}", end="")
print()
print(f"  {'(16 of 40 variables scored)':<40}")
print()
print(f"  {'':30} ", end="")
for h in H_KEYS:
    print(f" {h[-3:]}", end="")
print()
w_rank = sorted(H_KEYS, key=lambda h: weighted[h], reverse=True)
print(f"  Weighted rank: " + " > ".join(
    f"{h[-3:]}({weighted[h]:+.0f})" for h in w_rank))

# ── Sensitivity analysis: ±1 on HPM for top 5 contestable predictions ─────────
print()
print("=" * 72)
print("SENSITIVITY ANALYSIS — ±1 VARIATION ON CONTESTABLE HPM PREDICTIONS")
print("Does the weighted ranking change if a prediction shifts one level?")
print("=" * 72)

contestable_hpm = [
    ("EV004", "H001", "How variable holes support H001 vs H002 equally"),
    ("EV004", "H005", "Textile tool also predicts ++ for variable holes"),
    ("EV033", "H001", "Rod fit: prerequisite for H001 but also H004/H005"),
    ("EV034", "H001", "Rope routing: core for H001 but also H005"),
    ("EV037", "H001", "Assembly absent: directly contradicts H001 core claim"),
    ("EV012", "H002", "Precision casting: equally expected for H003 and H006"),
    ("EV012", "H006", "Astronomical also requires precision — perhaps ++?"),
]

baseline_w = dict(weighted)

for ev_id, h_id, reason in contestable_hpm:
    current_pred = hpm.get((h_id, ev_id), "0")
    direction, conf = SCORED_OBS.get(ev_id, ("ambiguous", "B"))
    current_score = pred_score(current_pred, direction, conf)
    current_wt = weighted_score(current_score, ev_id)

    # Shift +1
    p_num = PRED_NUM.get(current_pred, 0)
    p_up = {v: k for k, v in PRED_NUM.items()}.get(min(2, p_num + 1), current_pred)
    # Shift -1
    p_dn = {v: k for k, v in PRED_NUM.items()}.get(max(-2, p_num - 1), current_pred)

    s_up = weighted_score(pred_score(p_up, direction, conf), ev_id)
    s_dn = weighted_score(pred_score(p_dn, direction, conf), ev_id)

    delta_up = s_up - current_wt
    delta_dn = s_dn - current_wt

    new_h_up = baseline_w[h_id] + delta_up
    new_h_dn = baseline_w[h_id] + delta_dn

    rank_up = sorted(H_KEYS, key=lambda h: (baseline_w[h] + (delta_up if h==h_id else 0)), reverse=True)
    rank_dn = sorted(H_KEYS, key=lambda h: (baseline_w[h] + (delta_dn if h==h_id else 0)), reverse=True)

    change_up = "RANK CHANGES" if rank_up[0] != w_rank[0] else "rank stable"
    change_dn = "RANK CHANGES" if rank_dn[0] != w_rank[0] else "rank stable"

    print(f"  {ev_id} × {h_id}  current={current_pred}")
    print(f"    Reason: {reason}")
    print(f"    If {current_pred}→{p_up}: {h_id} score {baseline_w[h_id]:+.0f}→{new_h_up:+.0f}  [{change_up}]")
    print(f"    If {current_pred}→{p_dn}: {h_id} score {baseline_w[h_id]:+.0f}→{new_h_dn:+.0f}  [{change_dn}]")
    print()

# ── Uncertainty bounds: worst/best case for unscored variables ────────────────
print("=" * 72)
print("UNCERTAINTY BOUNDS — UNSCORED VARIABLES")
print("Best case: assume all unscored variables confirm each hypothesis's predictions")
print("Worst case: assume all unscored variables contradict each hypothesis's predictions")
print("(Using discriminatory-power weights; confidence C for unscored/derived)")
print("=" * 72)

all_scored_evs = set(SCORED_OBS.keys())
max_add  = defaultdict(float)   # best-case additional points
max_lose = defaultdict(float)   # worst-case additional points (negative)

for ev_id, info in ev_info.items():
    if ev_id in all_scored_evs:
        continue
    dp_w = DP_WEIGHT.get(info["power"], 1)
    for h in H_KEYS:
        pred = hpm.get((h, ev_id), "0")
        p = PRED_NUM.get(pred, 0)
        best  =  abs(p) * dp_w * CONF_WEIGHT["C"]   # best case
        worst = -abs(p) * dp_w * CONF_WEIGHT["C"]   # worst case
        max_add[h]  += best
        max_lose[h] += worst

print(f"\n  {'':35}", end="")
for h in H_KEYS:
    print(f" {h[-3:]}", end="")
print()
print(f"  {'Current weighted score':<35}", end="")
for h in H_KEYS:
    print(f" {weighted[h]:>+4.0f}", end="")
print()
print(f"  {'Best case (all unscored confirm)':<35}", end="")
for h in H_KEYS:
    print(f" {weighted[h]+max_add[h]:>+4.0f}", end="")
print()
print(f"  {'Worst case (all unscored contradict)':<35}", end="")
for h in H_KEYS:
    print(f" {weighted[h]+max_lose[h]:>+4.0f}", end="")
print()
print()
print("  Robustness: does the hypothesis lead even in its worst case?")
worst_scores = {h: weighted[h] + max_lose[h] for h in H_KEYS}
best_scores  = {h: weighted[h] + max_add[h]  for h in H_KEYS}
for h in w_rank:
    best_rivals = sorted([k for k in H_KEYS if k != h],
                         key=lambda k: best_scores[k], reverse=True)
    top_rival = best_rivals[0]
    robust = worst_scores[h] > best_scores[top_rival]
    print(f"  {h} ({hypotheses[h][:30]:<30}): "
          f"worst={worst_scores[h]:+.0f} vs best rival {top_rival}={best_scores[top_rival]:+.0f} "
          f"→ {'ROBUST' if robust else 'FRAGILE'}")

# ── Write partial scores to hdm_scores table ─────────────────────────────────
print()
print("=" * 72)
print("WRITING PARTIAL SCORES TO hdm_scores TABLE")
print("=" * 72)

conn.execute("DELETE FROM hdm_scores")
rows_written = 0
for ev_id, (direction, conf) in SCORED_OBS.items():
    dp_w = DP_WEIGHT.get(ev_info[ev_id]["power"], 1)
    for h in H_KEYS:
        pred  = hpm.get((h, ev_id), "0")
        raw   = pred_score(pred, direction, conf)
        score = round(raw)   # integer -2 to +2 for storage
        conn.execute(
            "INSERT OR REPLACE INTO hdm_scores(hypothesis_id, ev_id, score, confidence, notes) "
            "VALUES (?,?,?,?,?)",
            (h, ev_id, score, conf,
             f"direction={direction}; dp_weight={dp_w}; "
             f"pred={pred}; weighted={weighted_score(raw,ev_id):.2f}")
        )
        rows_written += 1

conn.commit()
print(f"  Written: {rows_written} hdm_scores rows")
n = conn.execute("SELECT COUNT(*) FROM hdm_scores").fetchone()[0]
print(f"  hdm_scores table now has {n} rows")

# ── Final recommendation ───────────────────────────────────────────────────────
print()
print("=" * 72)
print("SCIENTIFIC HARDENING PLAN — PRIORITISED")
print("=" * 72)
print("""
  TIER 1 — Do now (desk work, no new specimens needed)
  ─────────────────────────────────────────────────────
  A. Systematic literature review for wear/residue observations
     Target: Guggenberger & Leach 2025 (Antiquaries Journal) — likely contains
     wear and residue data from physical examination of specimens
     Impact: unlocks EV017, EV019, EV023, EV024 (all Very High, ±6 pts/hyp)

  B. EV005 (opposing-hole relationships) — re-examine Llandow (NMGW-063819)
     9.4mm vs 22.6mm on described 'opposing' faces
     Need: 3D scan or direct re-measurement to confirm geometric opposition
     Impact: ±6 pts/hyp; directly tests H001 (connector needs matching holes)

  C. EV039 (standardisation) — compute statistical metrics on measured hole
     diameters: coefficient of variation, Kolmogorov-Smirnov test for common
     distribution
     Impact: ±4 pts/hyp; directly tests H002 (measuring = standardised)

  TIER 2 — Expand corpus (literature/museum)
  ──────────────────────────────────────────
  D. Access Guggenberger 1999 catalogue (230-page master's thesis) for
     continental European specimens with measurements
     Impact: reduces 85% British bias; enables EV040 regional variation

  E. Add context data for Corbridge dodecahedron (military town vs. fort)
     Impact: strengthens EV031 military association scoring

  TIER 3 — Physical access (requires museum collaboration)
  ──────────────────────────────────────────────────────────
  F. EV023 (thermal alteration) and EV024 (residues) — request XRF/GCMS
     analysis on Tongeren or Musée Curtius specimen
     Impact: unlocks highest-discriminatory-power variables; could immediately
     confirm or eliminate H004 (candlestick) and H003 (ritual)
""")

conn.close()
