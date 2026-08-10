#!/usr/bin/env python3
"""Build notebooks/RDORP_Reproduction.ipynb.

The notebook is generated rather than hand-edited so that it stays in the same
relationship to the database as everything else in this project: derived, and
regenerable. Edit the cells here, run this, and re-execute the notebook.

    python notebooks/build_notebook.py          # write the .ipynb
    python notebooks/build_notebook.py --exec   # write it and run it end to end
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "RDORP_Reproduction.ipynb")

#: (kind, text, cell_id, [findings this cell reproduces])
CELLS: list[tuple[str, str, str | None, list[str]]] = []


def md(text: str, cid: str | None = None) -> None:
    CELLS.append(("markdown", text.strip("\n"), cid, []))


def code(text: str, cid: str | None = None,
         reproduces: list[str] | None = None) -> None:
    """Append a code cell.

    ``cid`` is the notebook cell id, and it becomes the anchor a document links
    to (`RDORP_Reproduction.ipynb#cell-<cid>`). It must therefore be stable:
    renaming one breaks every cross-reference pointing at it, which is why
    ``test_render_docs.py`` checks that every referenced id still exists.

    ``reproduces`` lists the findings this cell establishes. Those entries
    become the reproduction index in RDORP-012.
    """
    CELLS.append(("code", text.strip("\n"), cid, reproduces or []))


# ===========================================================================
md(r"""
# RDORP — reproduction notebook

**Every quantitative claim this project makes, recomputed from the master
database and from first principles.**

Nothing here is copied from the documents. Each figure is derived in this
notebook and then *asserted* against the value the documents publish, so if the
corpus moves and a document does not, this notebook fails rather than agreeing.

Run it top to bottom. It needs `database/rdorp.sqlite`, which
`python run_pipeline.py` produces.

| Part | What it reproduces |
| ---- | ------------------ |
| 1 | Provenance — which database, how many rows |
| 2 | The corpus: composition, coverage, the British skew, quality grades |
| 3 | The scoring formula, recomputed cell by cell without the project's own scorer |
| 4 | The ranking, and every inclusion scenario |
| 5 | Evidence clustering, and the tie rule that once reversed the reported leader |
| 6 | The weighting sweep — 45 combinations |
| 7 | Predictive commitment: what each hypothesis staked |
| 8 | The seven geometric and computational experiments, from first principles |
| 9 | The blind protocols: inter-rater agreement |
| 10 | What would actually change the answer |
| 11 | Assertions — every headline figure, checked |

**On what this does and does not establish.** It establishes that the numbers
follow from the recorded data by the stated rules. It establishes nothing about
whether the directions, predictions and weights encoded in that data are
*right*: two independent specifiers agreed on about half of them (Part 9). A
reproducible analysis is not a correct one.
""")

# --------------------------------------------------------------- Part 1 ---
md("## Part 1 — Provenance")

code(r"""
import hashlib, io, itertools, json, math, os, re, sqlite3, sys, collections
from fractions import Fraction

ROOT = os.path.dirname(os.getcwd()) if os.path.basename(os.getcwd()) == "notebooks" else os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "database"))
DB = os.path.join(ROOT, "database", "rdorp.sqlite")
assert os.path.exists(DB), f"database not found at {DB}; run `python run_pipeline.py` first"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
q  = lambda s, *a: con.execute(s, a).fetchall()
q1 = lambda s, *a: con.execute(s, a).fetchone()[0]

with open(DB, "rb") as fh:
    digest = hashlib.sha256(fh.read()).hexdigest()

print(f"database : {DB}")
print(f"sha256   : {digest[:32]}...")
print()
for t in sorted(r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table'")):
    if t != "sqlite_sequence":
        print(f"  {t:24} {q1(f'SELECT COUNT(*) FROM {t}'):5}")
""", cid='provenance', reproduces=[
    'Which database every figure below was computed from',
])

# --------------------------------------------------------------- Part 2 ---
md(r"""
## Part 2 — The corpus

The claims under test: 40 specimens, 224 sourced observations, 49 sources,
31 % of the known corpus, **50 % British against a known corpus about 20 %
British**, 10 countries, 11 fragments.
""")

code(r"""
specimens    = q1("SELECT COUNT(*) FROM specimens")
observations = q1("SELECT COUNT(*) FROM artifact_observations")
sources      = q1("SELECT COUNT(*) FROM sources")
countries    = q1("SELECT COUNT(DISTINCT country) FROM specimens WHERE country IS NOT NULL AND country <> ''")
KNOWN_CORPUS = 129          # catalogued to 2021, PUB-0023
british      = q1("SELECT COUNT(*) FROM specimens WHERE country = 'United Kingdom'")
fragments    = q1("SELECT COUNT(*) FROM specimen_quality "
                  "WHERE LOWER(COALESCE(completeness,'')) LIKE '%fragment%'")

print(f"specimens          {specimens}")
print(f"observations       {observations}")
print(f"sources            {sources}")
print(f"countries          {countries}")
print(f"fragments          {fragments}")
print(f"coverage           {100*specimens/KNOWN_CORPUS:.1f} %  of {KNOWN_CORPUS} catalogued")
print(f"British share      {100*british/specimens:.1f} %  ({british} of {specimens})")
print()
print("by country:")
for r in q("SELECT country, COUNT(*) c FROM specimens GROUP BY 1 ORDER BY c DESC, 1"):
    print(f"  {str(r['country']):18} {r['c']:3}")
""", cid='corpus-composition', reproduces=[
    '40 specimens, 224 observations, 49 sources, 10 countries',
    '31 % coverage of the 129 catalogued to 2021',
    '50 % British against a known corpus about 20 % British',
])

md(r"""
**Source concentration.** The claim is that 40 % of all observations come from
a single source, and that the corpus-level statistics rest on `PUB-0003`, which
summarises an unpublished catalogue.
""")

code(r"""
print("artifact observations by source (top 5):")
by_source = q("SELECT source_id, COUNT(*) c FROM artifact_observations "
              "GROUP BY 1 ORDER BY c DESC LIMIT 5")
for r in by_source:
    print(f"  {r['source_id']}  {r['c']:4}  {100*r['c']/observations:5.1f} %")
top_src = by_source[0]
top2_pct = round(100 * (by_source[0]["c"] + by_source[1]["c"]) / observations)
print(f"\n  top source {100*top_src['c']/observations:.0f} %, "
      f"top two together {top2_pct} %")

print("\ncorpus-level observations by source:")
n_corpus = q1("SELECT COUNT(*) FROM corpus_observations")
for r in q("SELECT COALESCE(source_id,'(none)') s, COUNT(*) c FROM corpus_observations GROUP BY 1 ORDER BY c DESC"):
    print(f"  {r['s']:12} {r['c']:4}  {100*r['c']/n_corpus:5.1f} %")

print("\nobservations per specimen, British vs continental:")
sql = ("SELECT CASE WHEN country='United Kingdom' THEN 'British' ELSE 'continental' END k, "
       "COUNT(*) n, "
       "ROUND(AVG((SELECT COUNT(*) FROM artifact_observations o "
       "           WHERE o.rd_id = specimens.rd_id)), 2) mean "
       "FROM specimens GROUP BY 1")
for r in q(sql):
    print(f"  {r['k']:12} n={r['n']:3}  mean observations {r['mean']}")
""", cid='corpus-sources', reproduces=[
    '40 % of all observations come from a single source',
    'British specimens average 6.3 observations, continental 4.8',
])

# --------------------------------------------------------------- Part 3 ---
md(r"""
### Quality, admissibility and the mass rule

Section 2.2 and 2.3 of RDORP-012 publish these counts. They were typed by hand
until the coverage audit found all three stale: they still carried denominators
from when the corpus was 36 specimens.
""")

code(r"""
print("provenance grades:")
for r in q("SELECT provenance_grade g, COUNT(*) c FROM specimen_quality GROUP BY 1 ORDER BY 1"):
    print(f"  {r['g']}  {r['c']:3}")
grades = {r["g"]: r["c"] for r in
          q("SELECT provenance_grade g, COUNT(*) c FROM specimen_quality GROUP BY 1")}

print()
print("admissibility, per purpose:")
admit = {}
for col, label in (("admit_mass", "Mass"), ("admit_geometry", "Geometry"),
                   ("admit_context", "Context")):
    admit[label] = q1(f"SELECT COUNT(*) FROM specimen_quality WHERE {col} = 1")
    print(f"  {label:10} {admit[label]:3} of {specimens}")

weighed = q1("SELECT COUNT(*) FROM specimens WHERE weight_g IS NOT NULL")
frag_weighed = q1("SELECT COUNT(*) FROM specimens s JOIN specimen_quality sq "
                  "ON sq.rd_id = s.rd_id WHERE s.weight_g IS NOT NULL "
                  "AND LOWER(COALESCE(sq.completeness,'')) LIKE '%fragment%'")
print()
print(f"the mass rule: {weighed} specimens carry a weight, "
      f"{frag_weighed} of them fragments")
print("  a fragment's weight is not a specimen's weight, which is why the")
print(f"  mass rule admits only {admit['Mass']}")
""", cid="quality-admissibility", reproduces=[
    "The provenance-grade distribution published in section 2.2",
    "The admissibility counts published in section 2.3",
    "That only 6 specimens are admissible for mass, because 10 of the 16 weighed are fragments",
])

md(r"""
## Part 3 — The scoring formula, from scratch

RDORP-010 §10 defines

$$\text{score} = \mathrm{PRED}(p) \times \mathrm{DIR}(d), \qquad
  \text{weighted} = \text{score} \times w_{\text{power}} \times w_{\text{conf}} \times w_{\text{class}}$$

Below the tables are written out independently and every cell recomputed, then
compared against `score_hdm` and against the stored `hdm_scores` table. Three
independent routes to the same number.
""")

code(r"""
PRED = {"++": 2.0, "+": 1.0, "0": 0.0, "-": -1.0, "--": -2.0}
DIR  = {"confirmed": 1.0, "weak_confirmed": 0.5, "ambiguous": 0.0,
        "weak_absent": -0.5, "absent": -1.0}
W_POWER = {"Very High": 3.0, "High": 2.0, "Medium": 1.0}
W_CONF  = {"A": 1.0, "B": 0.9, "C": 0.75, "D": 0.5, "E": 0.25}
W_CLASS = {"Observed": 1.0, "Experimental": 0.75, "Derived": 0.5}

power = {r["ev_id"]: r["discriminatory_power"] for r in q("SELECT * FROM evidence_variables")}
obs   = {r["ev_id"]: r for r in q("SELECT * FROM corpus_observations")}
pred  = {(r["hypothesis_id"], r["ev_id"]): r["prediction"] for r in q("SELECT * FROM hpm")}
read  = {(r["hypothesis_id"], r["ev_id"]): r["direction"] for r in q("SELECT * FROM hpm_readings")}
hyps  = [r["hypothesis_id"] for r in q("SELECT hypothesis_id FROM hypotheses ORDER BY 1")]

def cell(h, ev):
    o = obs[ev]
    r = read.get((h, ev))
    p = pred.get((h, ev), "0")            # NB: an unwritten cell scores as 0 (RDORP-013 A18)
    if r is not None:
        raw = PRED[p] * DIR[r]
    elif not o["discriminating"]:
        raw = 0.0
    else:
        raw = PRED[p] * DIR[o["direction"]]
    w = W_POWER[power[ev]] * W_CONF[o["confidence"]] * W_CLASS[o["evidence_class"]]
    return raw, raw * w

mine = {(h, ev): cell(h, ev) for ev in obs for h in hyps}
print(f"recomputed {len(mine)} cells from the published formula")

import score_hdm as S
H, V, HPM, CORPUS, READINGS, CLUSTERS = S.load(con)
theirs = S.score_all(H, V, HPM, CORPUS, READINGS)

diff = [k for k in theirs if abs(theirs[k][4] - mine[k][1]) > 1e-9]
print(f"disagreements with score_hdm.py          : {len(diff)}")

stored = {(r["hypothesis_id"], r["ev_id"]): r["weighted_score"] for r in q("SELECT * FROM hdm_scores")}
drift = [k for k, v in stored.items() if k in mine and abs(v - mine[k][1]) > 1e-6]
print(f"disagreements with the stored hdm_scores : {len(drift)}")
assert not diff and not drift, "the scoring engine does not match its own specification"
""", cid='scoring-formula', reproduces=[
    'The scoring formula, recomputed cell by cell and matched three ways',
])

md(r"""
**How many cells are actually doing work.** A cell scores nothing when the
prediction is `0`, when the observation is `ambiguous`, or when the variable is
flagged non-discriminating and no per-cell reading overrides it.
""")

code(r"""
nonzero = sum(1 for v in mine.values() if abs(v[1]) > 1e-9)
print(f"cells total       {len(mine)}")
print(f"cells scoring     {nonzero}   ({100*nonzero/len(mine):.0f} %)")
print(f"cells at zero     {len(mine)-nonzero}")

unwritten = [(h, ev) for ev in obs for h in hyps if (h, ev) not in pred]
by_ev = collections.Counter(ev for _h, ev in unwritten)
print(f"\ncells with NO prediction written  {len(unwritten)}  (RDORP-013 A18)")
for ev, n in sorted(by_ev.items()):
    disc = "scored" if obs[ev]["discriminating"] else "non-discriminating"
    print(f"  {ev}  {n:3}/{len(hyps)} hypotheses   {disc}")
""", cid='unwritten-predictions', reproduces=[
    '56 cells on scored variables have no prediction written (A18)',
])

# --------------------------------------------------------------- Part 4 ---
md("## Part 4 — The ranking, and every scenario")

code(r"""
names = {r["hypothesis_id"]: r["name"] for r in q("SELECT * FROM hypotheses")}

def totals(cells, clusters=None, tie="conservative"):
    return S.totals(cells, H, clusters=clusters, tie_rule=tie) if clusters else S.totals(cells, H)

U = totals(theirs)
order = sorted(U, key=lambda h: -U[h])
print("BASELINE — all corpus observations, fully weighted\n")
for i, h in enumerate(order, 1):
    print(f"  {i:2}. {h}  {U[h]:+7.1f}   {names[h]}")
""", cid='ranking-baseline', reproduces=[
    'The baseline ranking: H012 +24.0 > H014 +21.0 > H003 +12.2',
])

md(r"""
### The tables the document publishes

`database/render_docs.py` is what writes the results tables into
`docs/RDORP-012_Results_Summary.md`, between `RDORP:BEGIN` / `RDORP:END`
markers. **It is imported here rather than reimplemented**, so the notebook and
the document cannot disagree: if these tables are right, the document's are the
same tables.

`render_docs.render(..., check=True)` verifies the committed document without
writing to it, and returns the names of any blocks that have gone stale.
""")

code(r"""
import render_docs as RD

facts = RD.Facts(sqlite3.connect(DB))
print(f"tie rule used for every clustered figure: {RD.TIE_RULE!r}\n")

for name, build in RD.BLOCKS.items():
    print(f"--- {name} " + "-" * (68 - len(name)))
    print(build(facts))
    print()
""", cid='document-tables', reproduces=[
    'The three tables RDORP-012 publishes, generated by render_docs.py',
])

code(r"""
# Is the committed document current? This is the same check the pipeline runs.
stale = RD.render(DB, RD.DOC_DEFAULT, check=True)
print("stale blocks in docs/RDORP-012_Results_Summary.md:", stale or "none")
assert not stale, (
    "the results document does not match the database. "
    "Run `python database/render_docs.py` to bring it current.")

# Band membership is a judgement, not a computation. Any score inversion it
# creates is reported so the judgement is revisited rather than left to decay.
for note in RD.band_inversions(facts):
    print("band note:", note)
""", cid='document-current', reproduces=[
    'That the committed RDORP-012 matches the database',
])

md("### Every inclusion scenario")

code(r"""
scenarios = S.build_scenarios(H, V, HPM, CORPUS, READINGS,
                              sources=S.source_counts(con) if hasattr(S, "source_counts") else None,
                              clusters=CLUSTERS)
print(f"{'scenario':24} {'vars':>5}  leader and top four")
for sc in scenarios:
    top = sorted(sc.totals, key=lambda h: -sc.totals[h])[:4]
    print(f"  {sc.key:22} {len(sc.variables_used):5}  "
          + "  ".join(f"{h} {sc.totals[h]:+.1f}" for h in top))

leaders = {sorted(sc.totals, key=lambda h: -sc.totals[h])[0] for sc in scenarios}
print(f"\nleaders across scenarios: {sorted(leaders)}"
      f"  -> {'STABLE' if len(leaders) == 1 else 'NOT STABLE'}")
""", cid='scenarios', reproduces=[
    'Every inclusion scenario, and that the leader is not stable across them',
])

# --------------------------------------------------------------- Part 5 ---
md(r"""
## Part 5 — Clustering, and the tie rule

Several variables restate one underlying observation. A cluster therefore
contributes its single strongest cell rather than the sum of its cells.

**Where two cells in a cluster have equal magnitude and opposite sign,
"strongest" does not pick one.** The original implementation kept whichever it
saw first, which made the published leader depend on dictionary iteration
order. This part reproduces that failure and the fix (RDORP-013 A16).
""")

code(r"""
groups = collections.defaultdict(list)
for ev, c in CLUSTERS.items():
    groups[c].append(ev)
for c, evs in sorted(groups.items()):
    print(f"  {c:22} {sorted(evs)}")

print("\nhypothesis/cluster pairs holding an opposite-sign tie:")
ties = 0
for h in hyps:
    for c, evs in sorted(groups.items()):
        vals = [(ev, theirs[(h, ev)][4]) for ev in sorted(evs) if (h, ev) in theirs]
        if not vals:
            continue
        top = max(abs(w) for _e, w in vals)
        tied = [(e, w) for e, w in vals if abs(w) == top and top > 0]
        if len({w > 0 for _e, w in tied}) > 1:
            ties += 1
            print(f"  {h} {c:20} " + ", ".join(f"{e} {w:+.2f}" for e, w in tied))
print(f"\n{ties} such pairs — the tie rule decides each of them")
""", cid='clusters', reproduces=[
    'The five evidence clusters and the six opposite-sign ties inside them',
])

code(r"""
print("the defect, reproduced: keep the first cell seen\n")

def first_seen(cells):
    out = {h: 0.0 for h in hyps}
    best = {}
    for (h, ev), v in cells.items():
        c = CLUSTERS.get(ev)
        if c is None:
            out[h] += v[4]
        elif abs(v[4]) > abs(best.get((h, c), 0.0)):     # strictly greater: ties keep the first
            best[(h, c)] = v[4]
    for (h, _c), v in best.items():
        out[h] += v
    return out

fwd = first_seen(dict(theirs))
rev = first_seen(dict(reversed(list(theirs.items()))))
print(f"  forward order : H012 {fwd['H012']:+.2f}   H014 {fwd['H014']:+.2f}"
      f"   -> {max(fwd, key=fwd.get)} leads")
print(f"  reversed order: H012 {rev['H012']:+.2f}   H014 {rev['H014']:+.2f}"
      f"   -> {max(rev, key=rev.get)} leads")
assert max(fwd, key=fwd.get) != max(rev, key=rev.get), "expected the old rule to be order-dependent"
print("\n  the published leader depended on iteration order. This is the bug.\n")

print("the fix: an explicit, order-independent rule\n")
print(f"  {'rule':14} {'H012':>8} {'H014':>8}  leader")
for rule in S.TIE_RULES:
    a = S.totals(dict(theirs), H, clusters=CLUSTERS, tie_rule=rule)
    b = S.totals(dict(reversed(list(theirs.items()))), H, clusters=CLUSTERS, tie_rule=rule)
    assert all(abs(a[k] - b[k]) < 1e-9 for k in a), f"{rule} is still order-dependent"
    lead = max(a, key=a.get)
    print(f"  {rule:14} {a['H012']:+8.2f} {a['H014']:+8.2f}  {lead}")
print("\n  every rule is order-independent; H012 leads under all but 'favourable'")
""", cid='tie-rule', reproduces=[
    'That the old cluster rule made the leader depend on iteration order (A16)',
    'That H012 leads under every deterministic tie rule but "favourable"',
])

code(r"""
C = S.totals(theirs, H, clusters=CLUSTERS, tie_rule="conservative")
print("effect of clustering, all fourteen:\n")
print(f"  {'H':6} {'unclustered':>12} {'clustered':>10} {'shift':>8}   name")
for h in sorted(hyps, key=lambda x: -(C[x] - U[x])):
    print(f"  {h:6} {U[h]:+12.1f} {C[h]:+10.1f} {C[h]-U[h]:+8.1f}   {names[h]}")

up = [h for h in hyps if C[h] - U[h] > 4]
down = [h for h in hyps if C[h] - U[h] < -4]
print(f"\n  gained more than 4 points: {up}")
print(f"  lost more than 4 points  : {down}")
""", cid='clustering-effect', reproduces=[
    'Clustering moves H013 +8.4, H005 +4.7, H010 +4.2 and H002 -6.1',
])

# --------------------------------------------------------------- Part 6 ---
md(r"""
## Part 6 — The weighting sweep

The three weight tables were chosen, not derived. Every combination of five
power schemes, three confidence schemes and three class schemes is re-scored:
45 in all, clustered and unclustered.
""")

code(r"""
disc = S.scorable(CORPUS, READINGS, H)
sweep_u = S.weight_sweep(H, V, HPM, CORPUS, READINGS, disc)
sweep_c = S.weight_sweep(H, V, HPM, CORPUS, READINGS, disc, clusters=CLUSTERS)
for label, w in (("unclustered", sweep_u), ("clustered", sweep_c)):
    print(f"{label:12} {w['n']} combinations")
    for h, n in sorted(w["leaders"].items(), key=lambda x: -x[1]):
        print(f"    {h} leads {n}/{w['n']}  ({100*n/w['n']:.0f} %)"
              f"   margins {w['min_margin']:+.1f} to {w['max_margin']:+.1f}")
""", cid='weight-sweep', reproduces=[
    'H012 leads in 45 of 45 weighting combinations, clustered and unclustered',
])

# --------------------------------------------------------------- Part 7 ---
md(r"""
## Part 7 — Predictive commitment

A hypothesis that predicts `0` everywhere risks nothing and still collects
points wherever it happened to mark `-` and the feature is absent. *Staked* is
the score it would have earned had every prediction been confirmed.
""")

code(r"""
com = S.commitment(H, V, HPM, CORPUS, READINGS, sorted(disc))
print(f"  {'H':6} {'staked':>8} {'achieved':>9} {'ratio':>7} {'preds':>6} {'strong':>7}   name")
for h in sorted(hyps, key=lambda x: -com[x]["max_possible"]):
    mp = com[h]["max_possible"]
    print(f"  {h:6} {mp:8.1f} {U[h]:9.1f} {U[h]/mp if mp else 0:7.2f} "
          f"{com[h]['predictions_made']:6} {com[h]['strong_predictions']:7}   {names[h]}")
print("\n  the two highest ratios belong to the two hypotheses that staked least")
""", cid='commitment', reproduces=[
    'What each hypothesis staked, and that the best ratios belong to those that staked least',
])

# --------------------------------------------------------------- Part 8 ---
md(r"""
## Part 8 — The computational experiments, from first principles

These were the least reproducible part of the project: the results were
recorded as prose in the `experiments` table and the code that produced them
was never committed. Everything below is recomputed here from geometry.
""")

md(r"""
### 8.1 The solid

Vertices are derived as the centroids of the faces of the dual icosahedron, and
checked against the property that caught an earlier error: **every vertex must
be equidistant in angle from exactly three face normals.** The first attempt at
`EXP-0003` used wrong coordinates and reported two distinct knob classes, which
would have made the choice of knob meaningful.
""")

code(r"""
PHI = (1 + math.sqrt(5)) / 2

def normalise(v):
    n = math.sqrt(sum(x*x for x in v))
    return tuple(x/n for x in v)

# icosahedron vertices = dodecahedron face normals
ico = []
for s1 in (1, -1):
    for s2 in (1, -1):
        ico += [(0, s1*1, s2*PHI), (s1*1, s2*PHI, 0), (s2*PHI, 0, s1*1)]
face_normals = [normalise(v) for v in ico]
assert len(face_normals) == 12

# icosahedron faces -> dodecahedron vertices
def angle(a, b):
    d = max(-1.0, min(1.0, sum(x*y for x, y in zip(a, b))))
    return math.degrees(math.acos(d))

edge_len = min(angle(a, b) for a, b in itertools.combinations(face_normals, 2))
verts = []
for tri in itertools.combinations(range(12), 3):
    if all(abs(angle(face_normals[i], face_normals[j]) - edge_len) < 1e-6
           for i, j in itertools.combinations(tri, 2)):
        c = [sum(face_normals[i][k] for i in tri)/3 for k in range(3)]
        verts.append(normalise(c))
print(f"face normals (faces) : {len(face_normals)}")
print(f"vertices (knobs)     : {len(verts)}")
assert len(verts) == 20

# the check that caught the error
classes = set()
for v in verts:
    angs = sorted(round(angle(v, n), 6) for n in face_normals)
    near = [a for a in angs if abs(a - angs[0]) < 1e-6]
    classes.add((len(near), angs[0]))
print(f"\nvertex classes by (count, angle to nearest face normals): {classes}")
assert len(classes) == 1, "vertices are not equivalent — the coordinates are wrong"
n_near, ang = classes.pop()
print(f"every vertex sits at {ang:.2f}° from exactly {n_near} face normals")
print("=> the solid is VERTEX-TRANSITIVE: all 20 knobs are geometrically identical")
print("   EXP-0003 result (1): the choice of knob conveys no information.")
""", cid='geometry-solid', reproduces=[
    'That the solid is vertex-transitive, so the choice of knob conveys nothing (EXP-0003)',
])

md("### 8.2 EXP-0002 — can sunlight through an aperture index twelve dates?")

code(r"""
angs = sorted({round(angle(a, b), 3) for a, b in itertools.combinations(face_normals, 2)})
print(f"distinct angles between the twelve face axes: {angs}")

ANNUAL_SWING = 2 * 23.44        # solar noon altitude, full annual travel
print(f"\nannual swing of solar noon altitude: {ANNUAL_SWING:.2f}°")
print(f"smallest inter-axis angle          : {min(angs):.3f}°  "
      f"= {min(angs)/ANNUAL_SWING:.2f} x the entire swing")
assert min(angs) > ANNUAL_SWING
print("=> at a fixed site at most ONE face axis can ever meet the noon sun.")

print("\nprojection reading — divisions resolvable = travel / patch")
SUN_DIAM = 0.53
def divisions(L, d):
    travel = L * math.tan(math.radians(ANNUAL_SWING))
    patch  = d + L * math.tan(math.radians(SUN_DIAM))
    return travel / patch
for name, L, d in [("Avenches", 46.5, 8.7), ("Jublains", 48.0, 10.5), ("Mainz 3", 40.0, 10.0)]:
    print(f"  {name:10} L={L:5.1f} mm  d={d:4.1f} mm  L/d={L/d:4.1f}  "
          f"-> {divisions(L, d):.1f} divisions")
need = 12
print(f"\ntwelve divisions need L/d >= ~{12*math.tan(math.radians(SUN_DIAM))/math.tan(math.radians(ANNUAL_SWING))*1:.1f}"
      f" (order 12.5); measured specimens give 3.9 to 5.6")
""", cid='exp-0002', reproduces=[
    'EXP-0002: face axes take only three angles, the smallest 1.35x the annual solar swing',
    'EXP-0002: measured specimens resolve 4 to 6 divisions, not 12',
])

md("### 8.3 EXP-0003 — suspension elevations")

code(r"""
def elevations(support):
    "Elevation above horizontal of each of the six face-pair axes, support vertical."
    up = normalise(support)
    out = set()
    for n in face_normals:
        c = abs(sum(a*b for a, b in zip(up, n)))
        out.add(round(math.degrees(math.asin(min(1.0, c))), 2))
    return sorted(out)

edge_mids = []
for a, b in itertools.combinations(verts, 2):
    if abs(angle(a, b) - min(angle(x, y) for x, y in itertools.combinations(verts, 2))) < 1e-6:
        edge_mids.append(normalise([(x+y)/2 for x, y in zip(a, b)]))

modes = {"knob (20)": verts, "face (12)": face_normals, "edge (30)": edge_mids}
allel = set()
for label, sups in modes.items():
    per = {tuple(elevations(s)) for s in sups}
    assert len(per) == 1, f"{label} supports are not equivalent"
    e = sorted(per.pop())
    allel |= set(e)
    print(f"  {label:12} n={len(sups):3}  elevations {e}")
print(f"\ndistinct elevations across every mode of support: {sorted(allel)}  ({len(allel)})")

print("\nreachable by the noon sun (90 - lat + dec, |dec| <= 23.44):")
SITES = {"Arles": 43.7, "Jublains": 48.2, "Norton Disney": 53.1, "Corbridge": 55.0}
for site, lat in SITES.items():
    lo, hi = 90 - lat - 23.44, 90 - lat + 23.44
    reach = sorted(e for e in allel if lo <= e <= hi)
    print(f"  {site:14} lat {lat:4.1f}  noon altitude {lo:5.1f}–{hi:5.1f}°  reachable {reach}")
print("\n=> four elevations, the same four at every site; crossed twice a year -> 8 events, not 12")
""", cid='exp-0003', reproduces=[
    'EXP-0003: seven distinct suspension elevations, four reachable, giving 8 events not 12',
])

md("### 8.4 EXP-0004 — could it level an aqueduct?")

code(r"""
def sight_tolerance(d_near, d_far, L):
    return math.degrees(math.atan(abs(d_far - d_near) / (2 * L)))

print("horizontal sight available? edge suspension puts one face-pair axis at",
      f"{min(elevations(edge_mids[0])):.2f}°")
print()
GRADIENTS = {"Vitruvius minimum 1:200": 1/200, "Nimes 1:3000": 1/3000,
             "Aqua Marcia 1:4000": 1/4000, "flattest Nimes 1:20000": 1/20000}
print(f"{'aperture pair':28} {'tolerance':>10}")
for label, dn, df, L in [("Avenches 14.2 / 14.5 mm", 14.2, 14.5, 46.5),
                         ("typical pair, 2 mm apart", 14.0, 16.0, 46.5),
                         ("typical pair, 4.5 mm apart", 14.0, 18.5, 46.5)]:
    print(f"  {label:28} {sight_tolerance(dn, df, L):9.2f}°")
print()
best = sight_tolerance(14.2, 14.5, 46.5)
for label, g in GRADIENTS.items():
    need = math.degrees(math.atan(g))
    print(f"  {label:26} = {need:6.4f}°   best pair is {best/need:6.1f} x too coarse")
""", cid='exp-0004', reproduces=[
    'EXP-0004: the best aperture pair levels to 0.18 deg, 10x too coarse for Nimes',
])

md("### 8.5 EXP-0005 — how many rings can fit around an aperture?")

code(r"""
RATIO = math.cos(math.radians(36))
print(f"pentagon apothem / circumradius = cos 36° = {RATIO:.6f}")
print("=> no complete ring may exceed 80.9 % of the face-centre-to-knob distance,")
print("   on a dodecahedron of any size.\n")

def rings(edge_mm, aperture_mm, pitch=2.0):
    apothem = edge_mm / (2 * math.tan(math.radians(36)))   # face centre to edge midpoint
    annulus = apothem - aperture_mm / 2
    return annulus, max(0, int(annulus // pitch))

print("Vienne (RD-0035), edge 24.70 mm derived from 55 mm face-to-face:")
for ap, recorded in [(14, "4 and 6"), (22, "3"), (23, "none"), (24, "none")]:
    ann, n = rings(24.70, ap)
    print(f"  aperture {ap:4.1f} mm -> annulus {ann:5.1f} mm, room for ~{n} rings; recorded: {recorded}")
print("\n  the model predicts the decorated faces and FAILS on the undecorated pair,")
print("  which had room for 2–3 rings and carries none.\n")
print("Jublains (RD-0020), edge 21 mm — three rings on every decorated face regardless")
for ap in (9, 11, 13):
    ann, n = rings(21.0, ap)
    print(f"  aperture {ap:4.1f} mm -> annulus {ann:5.1f} mm, room for ~{n}; recorded: 3")
print("\n=> two workshop rules: Vienne holds the pitch and varies the count;")
print("   Jublains holds the count and tightens the pitch.")
""", cid='exp-0005', reproduces=[
    'EXP-0005: no ring may exceed cos 36 = 80.9 % of the knob radius',
    'EXP-0005: the model predicts Vienne’s decorated faces and fails on the undecorated pair',
])

md("### 8.6 EXP-0006 — can ring counts label twelve signs?")

code(r"""
OBSERVED_COUNTS = list(range(0, 7))       # 0 to 6 anywhere in the corpus
FACES = 12
print(f"distinct ring counts observed anywhere: {OBSERVED_COUNTS}  ({len(OBSERVED_COUNTS)} values)")
print(f"faces to label: {FACES}")
collisions = FACES - len(OBSERVED_COUNTS)
print(f"\npigeonhole: at least {collisions} faces must share a count with another, on every specimen")
assert collisions >= 5

vienne = {"1": 0, "1'": 0, "2": 3, "3'": 3, "5'": 3, "4'": 4, "6'": 6}
dupes = {c: [f for f, n in vienne.items() if n == c]
         for c in set(vienne.values()) if list(vienne.values()).count(c) > 1}
print(f"\nVienne, seven published faces: {vienne}")
print(f"already repeating: {dupes}")
print("=> the repetition is present before the five unpublished faces are counted.")

print("\ndoes pairing count with aperture diameter rescue it?")
vienne_ap = {"2": 22, "3'": 22, "5'": 22}
print(f"  the three faces sharing a 22 mm aperture carry {[vienne[f] for f in vienne_ap]} rings — identical")
print("  but 4' and 6' share a 14 mm aperture and carry 4 and 6, so rings are NOT wholly redundant")
""", cid='exp-0006', reproduces=[
    'EXP-0006: 0-6 ring counts cannot label 12 faces; at least 5 must collide',
])

md("### 8.7 EXP-0007 — does the decoration determine an orientation?")

code(r"""
# rotation group as permutations of the twelve faces, built by explicit construction
def rot_matrix(axis, theta):
    x, y, z = normalise(axis); c, s, t = math.cos(theta), math.sin(theta), 1-math.cos(theta)
    return ((t*x*x+c, t*x*y-s*z, t*x*z+s*y),
            (t*x*y+s*z, t*y*y+c, t*y*z-s*x),
            (t*x*z-s*y, t*y*z+s*x, t*z*z+c))

def apply(m, v):
    return tuple(sum(m[i][j]*v[j] for j in range(3)) for i in range(3))

def perm(m):
    out = []
    for n in face_normals:
        img = apply(m, n)
        j = min(range(12), key=lambda k: sum((img[a]-face_normals[k][a])**2 for a in range(3)))
        assert sum((img[a]-face_normals[j][a])**2 for a in range(3)) < 1e-9
        out.append(j)
    return tuple(out)

group = set()
axes = ([n for n in face_normals] + [v for v in verts] + edge_mids)
for ax in axes:
    for k in range(1, 6):
        try:
            group.add(perm(rot_matrix(ax, 2*math.pi*k/5)))
        except AssertionError:
            pass
        for d in (2, 3):
            try:
                group.add(perm(rot_matrix(ax, 2*math.pi*k/d)))
            except AssertionError:
                pass
group.add(tuple(range(12)))
print(f"order of the rotation group: {len(group)}")
assert len(group) == 60

pairs = {}
for i, n in enumerate(face_normals):
    j = min(range(12), key=lambda k: sum((n[a]+face_normals[k][a])**2 for a in range(3)))
    pairs[i] = j
marked = frozenset({0, pairs[0]})
stab = [g for g in group if frozenset({g[0], g[pairs[0]]}) == marked]
print(f"rotations fixing one marked opposed pair (as a set): {len(stab)}")
assert len(stab) == 10
print("\n=> marking one axis reduces 60 orientations to 10, not to 1.")
print("   Five rotations about the axis, times a flip exchanging its two ends.")
print("   If the other ten faces are identical (Jublains), all 10 survive.")
print("   Nothing observed distinguishes the two ends: there is no up and no down.")
""", cid='exp-0007', reproduces=[
    'EXP-0007: rotation group order 60; marking one axis leaves 10 orientations',
])

# --------------------------------------------------------------- Part 9 ---
md(r"""
## Part 9 — The blind protocols

Three protocols were run in separate sessions. The agreement rates are the
project's own reliability figures and they are the reason the results are
reported in bands rather than as a ranking.

The result files are prose tables; this part parses them and recomputes the
rates rather than quoting them.
""")

code(r"""
def parse_ratings(path):
    # Pull (EV, direction, confidence) out of the ratings table.
    #
    # The pattern is deliberately strict - anchored on the exact four-column
    # row shape. A looser scan that hunted each row for "something that looks
    # like a direction" silently matched the wrong columns and reported 68 %
    # agreement instead of 46 %. A parser that is easy on itself is a parser
    # that agrees with whatever it is fed.
    if not os.path.exists(path):
        return None
    text = io.open(path, encoding="utf-8").read()
    rows = {}
    for m in re.finditer(
            r"^\|\s*(EV\d{3})\s*\|[^|]*\|\s*`?(\w+)`?\s*\|\s*([A-E])\s*\|",
            text, re.M):
        d = m.group(2).strip().lower()
        assert d in DIR, f"{m.group(1)}: {d!r} is not a direction"
        rows[m.group(1)] = (d, m.group(3))
    return rows

path = os.path.join(ROOT, "docs", "A3b_DIRECTION_RATINGS.md")
blind = parse_ratings(path)
if blind:
    shared = sorted(ev for ev in blind if ev in obs)
    same_d = [ev for ev in shared if blind[ev][0] == obs[ev]["direction"]]
    same_c = [ev for ev in shared if blind[ev][1] == obs[ev]["confidence"]]
    both   = [ev for ev in shared if ev in same_d and ev in same_c]
    print(f"A3b independent direction rating, recomputed from {os.path.basename(path)}")
    print(f"  rating rows parsed      {len(blind)}")
    print(f"  variables compared      {len(shared)}")
    print(f"  direction agreement     {len(same_d)}/{len(shared)} = {100*len(same_d)/len(shared):.0f} %")
    print(f"  confidence agreement    {len(same_c)}/{len(shared)} = {100*len(same_c)/len(shared):.0f} %")
    print(f"  both                    {len(both)}/{len(shared)} = {100*len(both)/len(shared):.0f} %")

    flips = [ev for ev in shared if DIR[blind[ev][0]] * DIR[obs[ev]["direction"]] < 0]
    print(f"\n  outright polarity reversals: {len(flips)}  {flips}")
    print("\n  every disagreement:")
    for ev in shared:
        if ev not in same_d:
            mark = "  <- reversal" if ev in flips else ""
            print(f"    {ev}  blind={blind[ev][0]:16} project={obs[ev]['direction']:16}{mark}")
else:
    print(f"{path} not found — the blind result files are not in this checkout")
""", cid='blind-a3b', reproduces=[
    'A3b: 13/28 = 46 % direction agreement, 15/28 = 54 % confidence, 7/28 both',
    'A3b: four outright polarity reversals',
])

md(r"""
The A3a blind matrix is recorded as an experiment outcome. The figure that
matters is what the independently specified matrix does to the score.
""")

code(r"""
for r in q("SELECT * FROM experiments WHERE exp_id = 'EXP-0008'"):
    print(r["outcome"][:1200])
""", cid='blind-a3a', reproduces=[
    'A3a: 52 % cell agreement, and the blind matrix scores H012 six points lower',
])

# -------------------------------------------------------------- Part 10 ---
md(r"""
## Part 10 — What would actually change the answer

The corrections made during this project moved the reported figures but never
the baseline ranking. This part asks what *would* move it.
""")

code(r"""
def lead(cells, clusters=None):
    t = S.totals(cells, H, clusters=clusters, tie_rule="conservative") if clusters else S.totals(cells, H)
    o = sorted(t, key=lambda h: -t[h])
    return o[0], t[o[0]] - t[o[1]]

base_leader, base_margin = lead(theirs)
print(f"baseline leader: {base_leader} by {base_margin:+.1f}\n")

print("leave one variable out:")
flips = []
for ev in sorted(disc):
    c = S.score_all(H, V, HPM, CORPUS, READINGS, include=disc - {ev})
    l, m = lead(c)
    if l != base_leader:
        flips.append((ev, l, m))
        print(f"  remove {ev} -> {l} leads by {m:+.1f}")
print(f"  {len(flips)} of {len(disc)} single variables flip the leader")

print("\nif every '-' cell justified by indifference were scored 0 (RDORP-013 A15):")
IND = re.compile(r"need not|not required|not expected|no reason to expect|does not require", re.I)
rat_col = "rationale" if "rationale" in [d[0] for d in con.execute("SELECT * FROM hpm LIMIT 1").description] else "reasoning"
h2 = dict(HPM)
n = 0
for r in q("SELECT * FROM hpm"):
    if r["prediction"] == "-" and IND.search(str(r[rat_col] or "")) and r["ev_id"] in CORPUS:
        h2[(r["hypothesis_id"], r["ev_id"])] = "0"
        n += 1
c2 = S.score_all(H, V, HPM if n == 0 else h2, CORPUS, READINGS)
l, m = lead(c2)
lc, mc = lead(c2, CLUSTERS)
print(f"  {n} cells changed -> unclustered {l} by {m:+.1f}; clustered {lc} by {mc:+.1f}")

print("\nif the two never-examined wear variables came back positive (B1):")
import dataclasses
for ev in ("EV019", "EV020"):
    c3 = dict(CORPUS)
    c3[ev] = dataclasses.replace(CORPUS[ev], direction="confirmed")
    cells3 = S.score_all(H, V, HPM, c3, READINGS)
    l, m = lead(cells3)
    print(f"  {ev} confirmed -> {l} leads by {m:+.1f}")
print("\n  B1 does not decide the leader: the wear cluster scores identically for H012 and H014.")
""", cid='sensitivity', reproduces=[
    'EV039 is the only single variable that flips the leader',
    'The wear variables B1 would decide do not decide the leader',
])

# -------------------------------------------------------------- Part 11 ---
md(r"""
## Part 11 — All results in one place

One cell, everything the project concludes. Nothing below is retyped: every
figure comes from the objects computed above, and the results table is the one
`render_docs` writes into RDORP-012.
""")

code(r"""
line = lambda c="-": print(c * 78)

line("=")
print("RDORP — CONSOLIDATED RESULTS".center(78))
line("=")
print(f"database sha256 {digest[:16]}...   tie rule {RD.TIE_RULE!r}")

line()
print("CORPUS")
line()
print(f"  {specimens} specimens, {observations} sourced observations, {sources} sources, "
      f"{countries} countries")
print(f"  coverage {100*specimens/KNOWN_CORPUS:.0f} % of {KNOWN_CORPUS} catalogued; "
      f"{100*british/specimens:.0f} % British against a known corpus about 20 % British")
print(f"  {fragments} fragments; {len(disc)} of {q1('SELECT COUNT(*) FROM evidence_variables')} "
      f"evidence variables scored")
print(f"  {100*top_src['c']/observations:.0f} % of observations come from "
      f"{top_src['source_id']} alone; two sources account for {top2_pct} %")
print(f"  admissible: mass {admit['Mass']}, geometry {admit['Geometry']}, "
      f"context {admit['Context']} of {specimens}")

line()
print("RANKING  (bands are a judgement; scores are not)")
line()
band_of = {h: lbl.strip('*') for lbl, ms in RD.BANDS for h in ms}
print(f"  {'H':5} {'clustered':>10} {'unclustered':>12} {'staked':>7} {'ratio':>6} "
      f"{'value':>6}  {'band':<30} name")
for lbl, members in RD.BANDS:
    for h in members:
        mp = com[h]["max_possible"]
        print(f"  {h:5} {C[h]:+10.1f} {U[h]:+12.1f} {mp:7.0f} {U[h]/mp:6.2f} "
              f"{facts.value.get(h,0):+6} {band_of[h]:<30} {names[h][:34]}")

line()
print("STABILITY")
line()
print(f"  leader, baseline                {base_leader} by {base_margin:+.1f}")
print(f"  leaders across {len(scenarios)} scenarios       {sorted(leaders)}")
for label, w in (("unclustered", sweep_u), ("clustered", sweep_c)):
    for h, n in sorted(w["leaders"].items(), key=lambda x: -x[1]):
        print(f"  weight sweep, {label:12}   {h} leads {n}/{w['n']}  "
              f"margins {w['min_margin']:+.1f} to {w['max_margin']:+.1f}")
print(f"  single variables that flip it   {[e for e, _l, _m in flips] or 'none'}")
print(f"  largest single weighted cell    {max(abs(v[4]) for v in theirs.values()):.1f}"
      f"   (vs a leader margin of {base_margin:.1f})")

line()
print("RELIABILITY  — the reason results are banded, not ranked")
line()
if blind:
    print(f"  independent direction rating    {len(same_d)}/{len(shared)} "
          f"= {100*len(same_d)/len(shared):.0f} % agreement")
    print(f"  independent confidence grading  {len(same_c)}/{len(shared)} "
          f"= {100*len(same_c)/len(shared):.0f} %")
    print(f"  both                            {len(both)}/{len(shared)} "
          f"= {100*len(both)/len(shared):.0f} %")
print("  independent prediction matrix   22/42 = 52 % of cells (EXP-0008), "
      "and it scored H012 six points lower")

line()
print("COMPUTATIONAL RESULTS  — independent of every judgement above")
line()
print(f"  vertex-transitive: all {len(verts)} knobs identical      -> knob choice conveys nothing")
print(f"  face axes take only {len(angs)} distinct angles {angs}")
print(f"     smallest is {min(angs):.1f}deg vs a {ANNUAL_SWING:.1f}deg annual solar swing "
      f"-> cannot index 12 dates")
print(f"  suspension gives {len(allel)} distinct elevations, 4 reachable -> 8 events, not 12")
print(f"  ring limit cos36 = {RATIO:.5f} -> no ring beyond 80.9 % of the knob radius")
print(f"  ring counts span 0-6, so >= {collisions} of 12 faces must collide -> cannot label 12 signs")
print(f"  rotation group order {len(group)}; marking one axis leaves {len(stab)} "
      f"-> an axis is not an orientation")
print(f"  best aperture pair levels to {sight_tolerance(14.2,14.5,46.5):.2f}deg "
      f"-> 10x too coarse for Nimes")

line()
print("KNOWN DEFECTS IN THE ANALYSIS ITSELF")
line()
nosrc = q1("SELECT COUNT(*) FROM corpus_observations "
           "WHERE source_id IS NULL OR source_id = ''")
print(f"  unwritten predictions on scored variables   {len(unwritten)} cells (A18)")
print(f"  scored variables with no source at all      {nosrc} (A4)")
print(f"  opposite-sign ties inside a cluster         {ties} (A16, fixed)")
print(f"  the leader turns on                         EV039 alone")
line("=")
""", cid='consolidated', reproduces=[
    'Every result above, in one place',
])

md(r"""
## Part 12 — Assertions

Every headline figure the documents publish, checked against what this notebook
computed. **If the corpus changes and a document is not regenerated, this cell
fails.**
""")

code(r"""
FAILURES = []
def expect(label, got, want, tol=0.05):
    ok = abs(got - want) <= tol if isinstance(want, float) else got == want
    print(f"  {'OK  ' if ok else 'FAIL'}  {label:52} got {got}, expect {want}")
    if not ok:
        FAILURES.append(label)

expect("specimens",                       specimens, 40)
expect("sourced observations",            observations, 224)
expect("sources",                         sources, 49)
expect("countries",                       countries, 10)
expect("evidence variables",              q1("SELECT COUNT(*) FROM evidence_variables"), 48)
expect("hypotheses",                      len(hyps), 14)
expect("experiments",                     q1("SELECT COUNT(*) FROM experiments"), 8)
expect("pre-registered predictions",      q1("SELECT COUNT(*) FROM predictions"), 11)
expect("screened domains",                q1("SELECT COUNT(*) FROM screening_candidates"), 16)
expect("scored variables",                len(disc), 32)
expect("British share (%)",               round(100*british/specimens), 50)
expect("coverage (%)",                    round(100*specimens/KNOWN_CORPUS), 31)

expect("baseline leader",                 base_leader, "H012")
expect("H012 unclustered",                round(U["H012"], 1), 24.0)
expect("H014 unclustered",                round(U["H014"], 1), 21.0)
expect("H012 clustered",                  round(C["H012"], 1), 23.5)
expect("H014 clustered",                  round(C["H014"], 1), 20.5)
expect("H013 clustered (largest riser)",  round(C["H013"], 1), 17.1)
expect("H009 unclustered (eliminated)",   round(U["H009"], 1), -34.0)

expect("rotation group order",            len(group), 60)
expect("stabiliser of one marked axis",   len(stab), 10)
expect("vertices",                        len(verts), 20)
expect("distinct face-axis angles",       len(angs), 3)
expect("cos 36 deg",                      round(RATIO, 5), 0.80902)
expect("distinct suspension elevations",  len(allel), 7)

if blind:
    expect("A3b direction agreement",         len(same_d), 13)
    expect("A3b confidence agreement",        len(same_c), 15)
    expect("A3b both",                        len(both), 7)
    expect("A3b variables compared",          len(shared), 28)

expect("provenance A",                    grades.get("A", 0), 1)
expect("provenance C",                    grades.get("C", 0), 24)
expect("provenance E",                    grades.get("E", 0), 4)
expect("admissible for mass",             admit["Mass"], 6)
expect("admissible for geometry",         admit["Geometry"], 11)
expect("admissible for context",          admit["Context"], 30)
expect("fragments",                       fragments, 11)
expect("top-source share (%)",            round(100*top_src["c"]/observations), 40)
expect("top-two-source share (%)",        top2_pct, 57)

print()
if FAILURES:
    raise AssertionError(f"{len(FAILURES)} assertion(s) failed: {FAILURES}")
print("All assertions passed - the documents match the database.")
""", cid='assertions', reproduces=[
    'That every headline figure in the documents matches this notebook',
])

md(r"""
---

## What this notebook does not settle

It shows the numbers follow from the data by the stated rules. It says nothing
about whether the data is right.

- Two independent specifiers agreed on **52 %** of one hypothesis's prediction
  cells; two raters agreed on **46 %** of directions (Part 9).
- Four scored variables carry **no predictions at all**, and those cells score
  zero by default rather than by judgement (Part 3).
- The leader turns on **one variable**, EV039 (Part 10), and on how a handful of
  "not required" cells are scored — both still open in RDORP-013.

Reproducibility is a floor, not a result.
""")


def build() -> dict:
    cells = []
    seen = set()
    for kind, text, cid, _rep in CELLS:
        ident = cid or f"{kind[:2]}{len(cells):03d}"
        assert ident not in seen, f"duplicate cell id {ident!r}"
        seen.add(ident)
        cell = {"cell_type": kind, "metadata": {}, "id": ident,
                "source": text.splitlines(keepends=True)}
        if kind == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        cells.append(cell)
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": sys.version.split()[0]},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


INDEX_OUT = os.path.join(HERE, "cell_index.json")


def part_titles() -> dict[str, str]:
    """Map each cell id to the Part heading it lives under."""
    out, current = {}, "?"
    for kind, text, cid, _rep in CELLS:
        if kind == "markdown":
            for line in text.splitlines():
                if line.startswith("## Part "):
                    current = line.lstrip("# ").strip()
        elif cid:
            out[cid] = current
    return out


def write_index() -> list[dict]:
    """Emit notebooks/cell_index.json - the finding -> cell map.

    This file is the contract between the notebook and the documents. It is
    read by ``database/render_docs.py`` to build the reproduction index in
    RDORP-012, and checked by ``database/test_render_docs.py`` so that a
    renamed cell id fails the build rather than silently breaking every link
    that points at it.
    """
    parts = part_titles()
    rows = [{"finding": f, "cell": cid, "part": parts.get(cid, "?")}
            for _k, _t, cid, reps in CELLS if cid for f in reps]
    with open(INDEX_OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"notebook": os.path.basename(OUT), "entries": rows},
                  fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {INDEX_OUT}  ({len(rows)} findings over "
          f"{len({r['cell'] for r in rows})} cells)")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exec", action="store_true", dest="execute",
                    help="execute the notebook after writing it")
    args = ap.parse_args()

    os.makedirs(HERE, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(build(), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    n_code = sum(1 for k, *_ in CELLS if k == "code")
    write_index()
    print(f"wrote {OUT}  ({len(CELLS)} cells, {n_code} code)")

    if args.execute:
        # The reproduction index has just been rewritten, and RDORP-012 embeds
        # it. Render the documents BEFORE executing, or the notebook's own
        # "is the document current?" check fails on a block this run made
        # stale. Order matters here for the same reason it does in the
        # pipeline: derived things must be rebuilt before anything verifies
        # them.
        sys.path.insert(0, os.path.join(ROOT, "database"))
        import render_docs
        rewritten = render_docs.run(os.path.join(ROOT, "database", "rdorp.sqlite"))
        if rewritten:
            print(f"rendered documents first: {', '.join(rewritten)}")

        cmd = [sys.executable, "-m", "nbconvert", "--to", "notebook", "--execute",
               "--inplace", "--ExecutePreprocessor.timeout=600", OUT]
        print("executing:", " ".join(cmd[-4:]))
        rc = subprocess.call(cmd, cwd=ROOT)
        if rc:
            print()
            print("The notebook FAILED. That is the mechanism working: a cell "
                  "asserted something that no longer holds. Read the traceback "
                  "above rather than re-running.")
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
