---
Document ID: RDORP-012
Title: Results Summary
Version: 1.9.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-07
Last Updated: 2026-08-08
Related Documents:
  - RDORP-003 Research Method
  - RDORP-009 Decision Model
  - RDORP-010 Analytical Method
  - RDORP-011 Geometry Specification
  - RDORP-013 Hardening Plan
---

# Results Summary

A synthesis of the current state of the RDORP evidence base and of what it does
and does not support. Every figure is reproducible by running
`python run_pipeline.py`; the generated reports are `reports/hdm_analysis.md`,
`reports/corpus_coverage.md`, `reports/validation_report.md` and
`reports/batch_summary.md`.

---

## 1. Findings

### 1.1 How much of this can be trusted

**The method's reliability has been measured, and it is poor** ([recompute the agreement rates](../notebooks/RDORP_Reproduction.ipynb#cell-blind-a3b)). Three blind
protocols were run in separate sessions, each working only from a prompt and
forbidden the project's own files.

| Test | Agreement |
| ---- | --------- |
| An independent specifier writing H012's full prediction matrix, blind to the evidence | **52 %** of cells (22 of 42) |
| An independent rater assigning directions to the 28 scored corpus observations, blind to the hypotheses | **46 %** (13 of 28) |
| The same rater on confidence grades | 54 % (15 of 28) |
| Both direction and confidence | **25 %** (7 of 28) |

Scored against the corpus, the independently specified matrix gave H012 **six
points less** than the recorded one.

**Everything below inherits that uncertainty.** Scores are therefore reported
in bands rather than as a rank order, and differences of a few points should
not be read as differences at all.

### 1.2 What is nonetheless stable

**The negative result** ([notebook](../notebooks/RDORP_Reproduction.ipynb#cell-scenarios)). Every hypothesis in which the object bears load, is
used in the field, or is issued as standard equipment has been tested and
refuted. Sixteen further everyday uses across the military, maritime,
agricultural, pastoral, commercial, administrative, metrological and craft
domains were screened; fourteen were eliminated. Four properties of the corpus
defeat the utilitarian family as a class: contexts are predominantly urban and
civilian, nothing is standardised, walls are too thin to carry load, and no
functional equipment of any kind has ever been recovered alongside a
dodecahedron.

**The gauge–former asymmetry.** Every reading in which the object *gauges or
measures* is punished by the evidence; every reading in which it *forms or
holds material softer than itself* is rewarded. The cause is structural: a
gauge needs standardisation between examples and geometric fidelity within
them, and the corpus has neither.

**What computation settles** ([EXP-0002](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0002), [EXP-0006](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0006), [EXP-0007](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0007)). Three candidates are refuted by arithmetic rather
than by scoring, and those refutations do not depend on any judgement call: the
object cannot index the zodiac or any twelve-fold calendar by solar means; its
ring counts cannot encode twelve categories; and marking one opposed pair fixes
an axis but leaves ten orientations, so nothing determines a way up.

### 1.3 What is not stable

**Which hypothesis leads is stable; how far ahead is not** ([sweep](../notebooks/RDORP_Reproduction.ipynb#cell-weight-sweep), [sensitivity](../notebooks/RDORP_Reproduction.ipynb#cell-sensitivity)). H012 leads under
all 45 weighting schemes, clustered and unclustered. But the margin is small
and two identified defects both inflate it in the same direction: the
prediction scale pays H012 +4.1 for cells that state indifference rather than
expectation and pays H014 nothing (RDORP-013 A15), and the aperture and ring
survey — the cheapest outstanding test — bears directly on the variables that
separate them. **H012 and H014 should be read as a leading pair, with H012
ahead by less than the matrix currently says.**

*An earlier version of this document reported H014 as the clustered leader.
That was an artefact of an undeclared tie-break inside the clustering rule,
found and fixed as RDORP-013 item A16; see 2.7.*

**The refutations are less secure than the leaders.** Two independent checks
agree. Removing every variable that lacks two independent sources leaves the
leaders essentially unchanged and moves several refuted hypotheses
substantially. Deduplicating correlated evidence does the same. The refutations
resting on standardisation, context and distribution hold under both; those
resting on the absence of *wear* do not.

**And the wear evidence is the weakest load-bearing thing in the project.** It
is macroscopic only; two of its four variables have never been examined on any
specimen and are scored from the absence of a report; and all four cite one
page of one source.

### 1.4 What no hypothesis achieves

**None is robust.** Every one has a worst case over the unscored variables
below the best case of a rival. Only one — the tent-apex reading — is
decisively eliminated.

**None is both well supported and obviously worth doing.** On a separate
usage-value axis, every reading in which the object *makes* something scores
negative once the cheapest substitute is accounted for, because a wooden spool,
a pottery lamp, a knotted cord, a groma or a sundial existed in every case.
Only the readings in which the making and the holding are themselves the point
score positive — and those are the readings that predict least.

### 1.5 The corpus is not demonstrably one population

No specimen has been authenticated. Two of the three carrying usable aperture
data are unexcavated private-collection pieces. Ancient local imitation is
proposed in the literature and untested — and the absence of standardisation,
the project's most load-bearing finding, has only ever been measured by pooling
the whole corpus.

## 1A. Reproducing every finding

Everything in this document is recomputed, from the database and from first
principles, by
**[`notebooks/RDORP_Reproduction.ipynb`](../notebooks/RDORP_Reproduction.ipynb)**.

The notebook does not read this document. It derives each figure independently
and then *asserts* it against the value published here, so a corpus change that
is not carried into the prose makes the notebook **fail** rather than agree.

```
python run_pipeline.py                       # rebuild, score, validate, render
python notebooks/build_notebook.py --exec    # rebuild the notebook and run it
python database/render_docs.py --check       # fail if this document is stale
```

Three of the tables below are generated rather than typed: they sit between
`RDORP:BEGIN` / `RDORP:END` markers and are rewritten by
`database/render_docs.py` on every pipeline run. Editing one by hand achieves
nothing.

The index links each finding to the notebook cell that establishes it.

<!-- RDORP:BEGIN reproduction -->
| Finding | Reproduced in | Cell |
| ------- | ------------- | ---- |
| Which database every figure below was computed from | Part 1 — Provenance | [`provenance`](../notebooks/RDORP_Reproduction.ipynb#cell-provenance) |
| 40 specimens, 224 observations, 49 sources, 10 countries | Part 2 — The corpus | [`corpus-composition`](../notebooks/RDORP_Reproduction.ipynb#cell-corpus-composition) |
| 31 % coverage of the 129 catalogued to 2021 |  | [`corpus-composition`](../notebooks/RDORP_Reproduction.ipynb#cell-corpus-composition) |
| 50 % British against a known corpus about 20 % British |  | [`corpus-composition`](../notebooks/RDORP_Reproduction.ipynb#cell-corpus-composition) |
| 40 % of all observations come from a single source |  | [`corpus-sources`](../notebooks/RDORP_Reproduction.ipynb#cell-corpus-sources) |
| British specimens average 6.3 observations, continental 4.8 |  | [`corpus-sources`](../notebooks/RDORP_Reproduction.ipynb#cell-corpus-sources) |
| The provenance-grade distribution published in section 2.2 |  | [`quality-admissibility`](../notebooks/RDORP_Reproduction.ipynb#cell-quality-admissibility) |
| The admissibility counts published in section 2.3 |  | [`quality-admissibility`](../notebooks/RDORP_Reproduction.ipynb#cell-quality-admissibility) |
| That only 6 specimens are admissible for mass, because 10 of the 16 weighed are fragments |  | [`quality-admissibility`](../notebooks/RDORP_Reproduction.ipynb#cell-quality-admissibility) |
| The scoring formula, recomputed cell by cell and matched three ways | Part 3 — The scoring formula, from scratch | [`scoring-formula`](../notebooks/RDORP_Reproduction.ipynb#cell-scoring-formula) |
| 56 cells on scored variables have no prediction written (A18) |  | [`unwritten-predictions`](../notebooks/RDORP_Reproduction.ipynb#cell-unwritten-predictions) |
| The baseline ranking: H012 +24.0 > H014 +21.0 > H003 +12.2 | Part 4 — The ranking, and every scenario | [`ranking-baseline`](../notebooks/RDORP_Reproduction.ipynb#cell-ranking-baseline) |
| The three tables RDORP-012 publishes, generated by render_docs.py |  | [`document-tables`](../notebooks/RDORP_Reproduction.ipynb#cell-document-tables) |
| That the committed RDORP-012 matches the database |  | [`document-current`](../notebooks/RDORP_Reproduction.ipynb#cell-document-current) |
| Every inclusion scenario, and that the leader is not stable across them |  | [`scenarios`](../notebooks/RDORP_Reproduction.ipynb#cell-scenarios) |
| The five evidence clusters and the six opposite-sign ties inside them | Part 5 — Clustering, and the tie rule | [`clusters`](../notebooks/RDORP_Reproduction.ipynb#cell-clusters) |
| That the old cluster rule made the leader depend on iteration order (A16) |  | [`tie-rule`](../notebooks/RDORP_Reproduction.ipynb#cell-tie-rule) |
| That H012 leads under every deterministic tie rule but "favourable" |  | [`tie-rule`](../notebooks/RDORP_Reproduction.ipynb#cell-tie-rule) |
| Clustering moves H013 +8.4, H005 +4.7, H010 +4.2 and H002 -6.1 |  | [`clustering-effect`](../notebooks/RDORP_Reproduction.ipynb#cell-clustering-effect) |
| H012 leads in 45 of 45 weighting combinations, clustered and unclustered | Part 6 — The weighting sweep | [`weight-sweep`](../notebooks/RDORP_Reproduction.ipynb#cell-weight-sweep) |
| What each hypothesis staked, and that the best ratios belong to those that staked least | Part 7 — Predictive commitment | [`commitment`](../notebooks/RDORP_Reproduction.ipynb#cell-commitment) |
| That the solid is vertex-transitive, so the choice of knob conveys nothing (EXP-0003) | Part 8 — The computational experiments, from first principles | [`geometry-solid`](../notebooks/RDORP_Reproduction.ipynb#cell-geometry-solid) |
| EXP-0002: face axes take only three angles, the smallest 1.35x the annual solar swing |  | [`exp-0002`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0002) |
| EXP-0002: measured specimens resolve 4 to 6 divisions, not 12 |  | [`exp-0002`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0002) |
| EXP-0003: seven distinct suspension elevations, four reachable, giving 8 events not 12 |  | [`exp-0003`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0003) |
| EXP-0004: the best aperture pair levels to 0.18 deg, 10x too coarse for Nimes |  | [`exp-0004`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0004) |
| EXP-0005: no ring may exceed cos 36 = 80.9 % of the knob radius |  | [`exp-0005`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0005) |
| EXP-0005: the model predicts Vienne’s decorated faces and fails on the undecorated pair |  | [`exp-0005`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0005) |
| EXP-0006: 0-6 ring counts cannot label 12 faces; at least 5 must collide |  | [`exp-0006`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0006) |
| EXP-0007: rotation group order 60; marking one axis leaves 10 orientations |  | [`exp-0007`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0007) |
| EXP-0009: best zodiac fit 5.52 deg at 58.0 N, against 7.5 deg expected at random |  | [`exp-0009`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0009) |
| EXP-0009: 94 % of random elevation sets fit the zodiac at least as well |  | [`exp-0009`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0009) |
| EXP-0009: the statistic scores 0.0000 on a contrived on-boundary set, so it is sensitive |  | [`exp-0009`](../notebooks/RDORP_Reproduction.ipynb#cell-exp-0009) |
| A3b: 13/28 = 46 % direction agreement, 15/28 = 54 % confidence, 7/28 both | Part 9 — The blind protocols | [`blind-a3b`](../notebooks/RDORP_Reproduction.ipynb#cell-blind-a3b) |
| A3b: four outright polarity reversals |  | [`blind-a3b`](../notebooks/RDORP_Reproduction.ipynb#cell-blind-a3b) |
| A3a: 52 % cell agreement, and the blind matrix scores H012 six points lower |  | [`blind-a3a`](../notebooks/RDORP_Reproduction.ipynb#cell-blind-a3a) |
| EV039 is the only single variable that flips the leader | Part 10 — What would actually change the answer | [`sensitivity`](../notebooks/RDORP_Reproduction.ipynb#cell-sensitivity) |
| The wear variables B1 would decide do not decide the leader |  | [`sensitivity`](../notebooks/RDORP_Reproduction.ipynb#cell-sensitivity) |
| Every result above, in one place | Part 11 — All results in one place | [`consolidated`](../notebooks/RDORP_Reproduction.ipynb#cell-consolidated) |
| That every headline figure in the documents matches this notebook | Part 12 — Assertions | [`assertions`](../notebooks/RDORP_Reproduction.ipynb#cell-assertions) |
<!-- RDORP:END reproduction -->

---

## 2. The corpus: composition, quality and admissibility

### 2.1 Composition

**Tables between `RDORP:BEGIN` and `RDORP:END` markers are generated from the
database by `database/render_docs.py` and rewritten on every pipeline run.**
Editing one by hand achieves nothing: the next run overwrites it, and
`--check` fails the build in the meantime. Everything outside the markers is
prose and is written by hand.

<!-- RDORP:BEGIN composition -->
| Specimens recorded | 40 |
| Known corpus | 129 catalogued to 2021 (`PUB-0023`), c 134 by 2025 (`PUB-0003`) |
| Coverage | 31 % |
| Sourced observations | 224 |
| Sources | 49, of which 35 are graded A or B |
| Evidence variables | 48 |
| Hypotheses assessed | 14 |
| Functional domains screened | 16 |
| Experiments recorded | 9 |
| Pre-registered predictions | 11 |
| Countries represented | 10 |
| Evidence variables scored | 32 of 48 |
<!-- RDORP:END composition -->

Twenty specimens now carry a Greiner/Guggenberger catalogue number and type,
matched against the reference catalogue and assigned only where the catalogue
entry is unique for that findspot.

Geographic distribution of the recorded corpus is **50 % British**, against a
known corpus that is about 20 % British and about 70 % Gallic and Germanic. The
recorded corpus is therefore not representative, and the skew is an artefact of
accessibility: British Portable Antiquities Scheme records are online and carry
measurements, while the continental majority is catalogued in works this project
has not read directly.

### 2.2 Quality grading

Each specimen carries a completeness class, a provenance grade and a measurement
grade in `specimen_quality`.

<!-- RDORP:BEGIN quality -->
| Provenance grade | Meaning | Count |
| ---------------- | ------- | ----- |
| A | Excavated from a stratified, dated deposit | 1 |
| B | Excavated or reported find, documented findspot, institutional custody | 2 |
| C | Findspot recorded, surface or detector find | 24 |
| D | Institutional custody, no findspot | 9 |
| E | Private hands, or no findspot and no independent publication | 4 |
<!-- RDORP:END quality -->

**Eleven of the forty are fragments**, and one further specimen
(`RD-0002`) is substantially incomplete despite carrying no fragment label.

### 2.3 Admissibility rules

Fitness is assessed per purpose rather than admitting or excluding specimens
wholesale.

<!-- RDORP:BEGIN admissibility -->
| Rule | Requirement | Admissible |
| ---- | ----------- | ---------- |
| **Mass** | completeness = complete | **6 of 40** |
| **Geometry** | completeness ∈ {complete, incomplete} and measurement ∈ {direct, one remove} | **11 of 40** |
| **Context** | recorded findspot and provenance ≤ D | **30 of 40** |
<!-- RDORP:END admissibility -->

The mass rule is the most consequential. Sixteen specimens carry a recorded
weight, but ten of those are fragments: a fragment's weight is not a specimen's
weight, and pooling the two makes every mass statistic meaningless.

### 2.4 Rejections

| Specimen | Rejected from | Reason |
| -------- | ------------- | ------ |
| `RD-0017` Fishguard | **Geometry** | **Outlier.** Maximum diameter 127.71 mm exceeds the published corpus maximum of c 110 mm including knobs; 553.2 g is 2.2× the next heaviest complete specimen. Purchased, no excavation context. Either the measurement includes what the corpus figures exclude, or the object is atypical of the class |
| `RD-0006` Tongeren | **All scoring** | Sole source is a Wikipedia article, confidence E. The only E-confidence specimen |
| `RD-0036` Carnuntum | **Geometry** | Measurements arrive at two removes and no source in the chain states a tolerance |
| `RD-0002` Fridaythorpe | **Mass** | Six complete faces and half of five more; its 270 g is the weight of an incomplete object |
| 11 fragments | **Mass, geometry** | Whole-object dimensions cannot be taken from a fragment. Retained in full for decoration, context and aperture evidence |

### 2.5 Effect of the rejections

<!-- RDORP:BEGIN rejections -->
| Statistic | All recorded | Admissible only |
| --------- | ------------ | --------------- |
| Overall diameter | 44.0–127.7 mm, ratio 2.90:1 (n = 9) | **44.0–85.0 mm, ratio 1.93:1** (n = 8) |
| Mass | 1.7–553.2 g (n = 16) | **39.8–553.2 g** (n = 6) |
| Wall thickness | 1.1–3.7 mm (n = 5) | not separately restricted |
<!-- RDORP:END rejections -->

**The conclusions are unaffected.** The size-range findings that defeat the
modular-assembly and standardisation hypotheses rest on the *published* corpus
range of 4–10 cm (`PUB-0003`, 31), not on this project's own measured specimens,
and the spread among admissible specimens remains substantial. Mass was
already non-discriminating for want of a specified prediction, so no score
changes.

### 2.6 Authenticity

**No specimen in this database has been authenticated** by metallurgical or
technical analysis, and no source consulted raises the question.

Only `RD-0020` Jublains is secured by context: an object lifted from a sealed
burnt destruction layer by excavators cannot be a modern forgery.

**Two of the three specimens carrying usable aperture data are unexcavated
private-collection pieces.** `RD-0035` Vienne was published by its owner and has
no known archaeological context. `RD-0022` Mainz 3 has no findspot of any kind,
is privately held, and was unpublished until 2025. No source impugns either, and
this project does not; the point is that excavated context, independent
publication and institutional custody are all absent, so nothing corroborates
them.

**Ancient imitation is a live proposal in the literature.** `PUB-0003`, 32 n 10,
citing Greiner 1996, records that many British specimens have special features
and that *"some of which do not appear to be so skilfully designed. They may
point out to local imitations of 'classic' dodecahedra."*

If that is right the corpus is not one population, and the consequence falls on
the most load-bearing finding in the project. The absence of standardisation
defeats the artillery gauge, the volumetric measure, the net gauge, the
rangefinder, the astronomical instrument and the tailoring gauge alike — **and it
has only ever been measured by pooling the whole corpus.** Standardisation has
never been tested within a single Greiner/Guggenberger type. Until it has, that
finding carries an unquantified confound. See `EV048` and prediction `P-0011`.

### 2.7 Weaknesses of the evidence base

The corpus is thin in specific, identifiable ways, and they are not evenly
distributed across the conclusions.

**Two Very High variables score on silence.** `EV019` rope wear and `EV020`
rotational wear have **zero per-specimen observations**. No specimen has ever
been examined for either. They are scored `absent` because no report of them
exists anywhere — an argument from silence, recorded at confidence C, and still
contributing −4.5 apiece to the hypotheses that predict them.

<!-- RDORP:BEGIN concentration -->
**Source concentration.** 40 % of all 224 observations come from a single source, `PUB-0006`, the British Portable Antiquities Scheme database of metal-detector surface finds. Together with `PUB-0003`, two sources account for 57 %.
<!-- RDORP:END concentration -->

**Seven scored variables have no second voice.** Counting the corpus
observation's own source together with any per-specimen sources, seven of the
thirty-two scored variables rest on one source or none. (Thirty-two is itself
one too many: `EV044` is counted as scored but carries no prediction from any
hypothesis and discriminates nothing — see limit 11.)

| Variable | Power | Problem |
| -------- | ----- | ------- |
| `EV019` Rope wear | Very High | No specimen observation; argument from silence |
| `EV020` Rotational wear | Very High | No specimen observation; argument from silence |
| `EV034` Rope compatibility | Very High | **No source at all** — this project's own geometric reasoning |
| `EV035` Structural stability | Very High | **No source at all** |
| `EV036` Load transfer | High | **No source at all** |
| `EV038` Orientation dependence | High | Corpus statement only, no specimen backing |
| `EV044` Interior finish and marking | High | Corpus statement only, no specimen backing |

Three of them have **no source whatsoever**, in a database whose first rule is
that every fact has one. They are discounted to half weight as Derived evidence
and excluded from the observed-only scenario, but they are still in the
baseline.

**Thin specimens.** Median four observations per specimen; **13 of forty
have two or fewer**. A dozen entries amount to a findspot and a citation.

**Empty variables.** Twelve of forty-eight have no observation at all, five of
them Very High — including every variable that would decide the two leading
hypotheses.

**Confidence.** Only 10 % of observations are grade A, and almost all of those
come from a single specimen.

### 2.8 Consequence: what survives corroboration and independence

Two checks bear on this, and they agree. The first removes uncorroborated
variables; the second addresses variables that are not independent of one another.

**Correlated evidence — now implemented.** Variables that restate one
underlying observation share a budget in `corpus_observations.evidence_cluster`:
a cluster contributes its strongest single cell rather than the sum of its
cells. Five clusters are declared — wear, corpus size range, aperture metrics,
casting, and this project's own derived engineering assessments — each on
shared *evidential basis* rather than shared topic.

The wear cluster is the clearest case: `EV017`, `EV018`, `EV019` and `EV020`
all cite `PUB-0003`, 45 — one statement, reported from Guggenberger 1999,
scored four times, three of them at Very High power.

**The full clustered result — which does *not* change the leader:**

<!-- RDORP:BEGIN clustering -->
| Hypothesis | Unclustered | Clustered | Shift |
| ---------- | ----------- | --------- | ----- |
| **H012 Spool-knitting** | +24.0 (1) | **+23.5 (1)** | −0.6 |
| **H014 Wax bulla** | +21.0 (2) | **+20.5 (2)** | −0.6 |
| H013 Rope-laying top | +8.7 (5) | +17.1 (3) | +8.4 |
| H005 Textile | −0.2 (8) | +4.6 (6) | +4.7 |
| H002 Rangefinder | +3.5 (6) | −2.6 (11) | −6.1 |
| H010 Parasol | −9.2 (13) | −5.0 (12) | +4.2 |
| H009 Tent apex | −34.0 (14) | −31.4 (14) | +2.6 |
<!-- RDORP:END clustering -->

**Five clusters are declared, not one**: wear, corpus size range, aperture
metrics, casting, and this project's own derived engineering assessments. Each
is declared on shared evidential basis and recorded with its reasoning, so a
reader who disagrees can remove one and re-run.

**Where the correction falls is the finding.** Deduplication costs the leaders
almost nothing — each loses 0.6 — and returns **8.4 points to the rope-laying
top, 4.7 to the textile tool and 4.2 to the parasol crown**, all three of them
hypotheses the unclustered scoring had refuted or nearly refuted. **The
refutations were inflated by counting one source statement several times; the
leaders were not.** This is the same asymmetry the source-corroboration audit
finds below, reached by an independent route.

**One hypothesis moves the other way, and by more than any of them.** The
rangefinder falls 6.1 points, from +3.5 to −2.6, because its support came
partly from the four derived engineering variables that this project wrote
itself and that now share one budget. That is the correction working as
intended: the reading most dependent on our own reasoning is the one
deduplication punishes hardest.

**The tie-break inside the cluster rule was undefined, and it mattered** ([the failure and the fix, reproduced](../notebooks/RDORP_Reproduction.ipynb#cell-tie-rule)). A
cluster contributes its strongest single cell. Where two cells have equal
magnitude and opposite sign, "strongest" does not pick one — and the
implementation kept whichever it saw first, making the result depend on
dictionary iteration order. Six hypothesis/cluster pairs hold such a tie.
H014's `corpus_size_range` cluster holds `EV001` at +1.80 and `EV039` at
−1.80, so reversing the iteration order moved H014 by 3.6 points and reversed
the leadership.

The rule is now explicit and order-independent: **a tie is resolved against the
hypothesis**, the same discipline applied to argument from silence. The
favourable reading is reported alongside as `clustered_favourable`, the upper
bound of the judgement. A regression test asserts order-independence under
every rule (RDORP-013 A16).

<!-- RDORP:BEGIN tie_rules -->
| Tie rule | H012 | H014 | Leader |
| -------- | ---- | ---- | ------ |
| Conservative *(adopted)* | **+23.5** | **+20.5** | **H012** |
| Mean of the tied cells | +23.5 | +22.3 | H012 |
| Mean of all cells in the cluster | +16.9 | +16.3 | H012 |
| Favourable *(the accidental behaviour)* | +23.5 | +24.1 | H014 |
<!-- RDORP:END tie_rules -->

**Sensitivity to the weighting scheme.** All 45 combinations of five power
schemes, three confidence schemes and three class schemes were re-scored.
**H012 leads in 45 of 45 unclustered and 45 of 45 clustered.** Neither the
weights nor deduplication changes which hypothesis is first.

**Source corroboration.**

The `multi_source` scenario removes every variable lacking two independent
sources — the seven above — and rescores.

<!-- RDORP:BEGIN multi_source -->
| Hypothesis | Baseline | Corroborated only (25 variables) | Shift |
| ---------- | -------- | ----------------- | ----- |
| **H013 Rope-laying top** | +8.7 (5) | **+15.6 (3)** | **+6.9** |
| **H004 Candlestick** | −0.6 (10) | **+3.7 (6)** | **+4.3** |
| **H010 Parasol** | −9.2 (13) | **−5.3 (12)** | **+3.9** |
| **H005 Textile** | −0.2 (8) | **+3.2 (7)** | **+3.4** |
| **H011 Archery targeting** | −8.8 (12) | **−6.1 (13)** | **+2.6** |
| H009 Tent apex | −34.0 (14) | −32.1 (14) | +1.9 |
| H008 Portable shrine component | +11.4 (4) | +12.2 (5) | +0.8 |
| H006 Astronomical instrument | −0.5 (9) | −0.1 (9) | +0.4 |
<!-- RDORP:END multi_source -->

Three things follow from the corroboration check.

**The positive result is robust.** Both leaders move by less than two points and
neither changes rank. Nothing in the case for H012 or H014 depends on
uncorroborated evidence.

**Several refutations are not robust.** H013, the rope-laying top, rises nearly
seven points and two places, because its elimination rested substantially on
`EV019` and `EV020` — the two variables nobody has ever measured. The
candlestick, textile-tool and parasol readings recover similarly. **Every one of
these is a hypothesis refuted primarily by the absence of wear**, and that is
precisely where the evidence is weakest.

**H001 was being propped up by this project's own reasoning.** Removing the
three unsourced engineering variables drops it below zero and from seventh to
tenth. Its modest positive score in the baseline is partly an artefact of
scoring the project's own geometric assessments.

The refutations that rest on **standardisation, context, distribution and
casting defects** are unaffected, because those variables carry both a
corpus-level published statement and independent per-specimen observations.

**Both checks point the same way.** The case for the leading hypotheses does not
depend on weak or duplicated evidence; the case against the refuted ones partly
does. Clustering is now applied and is the primary basis for the bands in 5.1,
but it does not repair the underlying problem: **four hypotheses are still
refuted largely on wear that nobody has ever examined.** That is an evidence
gap, and only Part B of RDORP-013 closes it.

---

## 3. What the evidence shows

Thirty-two of forty-eight evidence variables carry a scoreable corpus
observation. The findings that carry the analysis are these.

### 3.1 The objects do not look used

The outer and inner surfaces "generally do not look worn, aside from a few
exceptions and later destruction and corrosion" (`PUB-0003`, 45). Four wear
variables score `absent`: internal hole wear, external wear, rope wear and
rotational wear — three of them rated Very High.

Any hypothesis in which the object is repeatedly handled, threaded, rotated or
assembled predicts wear, and it is not there.

Two qualifications are on the record. The observation is **macroscopic**;
`PUB-0003`, 52 lists microscopic wear analysis as an open question. And Duval
(`PUB-0017`, 200) reports that on the Vienne specimen the two largest opposed
openings look "less regularly cut … as if they had been worn by some friction,
due for example to a stick that passed through both simultaneously", where
Guggenberger explains the same feature across the corpus as production holes.
Both readings are preserved and internal hole wear is scored at confidence C
rather than B in consequence.

Two photographic observations were added, both at confidence D and both
recorded with their reasoning, because surface condition read from an image by
a non-specialist is the weakest evidence the project holds. The Hunt Museum
specimen shows **bright unpatinated metal on the crown of every knob** against
a fully patinated body; Much Hadham, an unpolished ploughsoil find, shows none.
**Patina forms during burial**, so bright metal indicates cleaning after
excavation rather than Roman use. What an image cannot settle is the *shape*
question — whether the crowns are flattened beyond their cast form, which would
survive burial and could not be produced by dusting.

The strongest single support is `RD-0005`: excavated, complete, undamaged, in
excellent condition, and unworn. Unlike the ploughsoil finds that dominate the
corpus, that cannot be explained as post-depositional surface loss.

### 3.2 Nothing is standardised

- Aperture diameters span 6–40 mm across the corpus and vary by a factor of 3
  within a single specimen.
- Overall diameter spans 40–100 mm.
- Wall thickness spans 0.5–4 mm.
- Opposite apertures differ by 2–4.5 mm on average; Avenches has no equal pair
  and two differing by more than 9 mm.
- The face-to-opposite-face distance varies *within one object*: Jublains
  measures 48–52 mm depending on the axis chosen.
- Decoration follows no consistent pattern between specimens.

Two corroborations carry particular weight because both come from authors
looking for a standard who did not find one. Duval devised his comparative
recording method precisely to detect regularity and concluded there is "no
evident regularity in the general distribution of the openings, either in their
juxtaposition or in their opposition". Sparavigna, arguing *for* the
measuring-instrument interpretation, concluded that "it does not seem that a
standard or rule for these instruments existed".

### 3.3 The mechanics do not support load

Walls of 0.5–4 mm, described in the source as "remarkably thin-walled", in an
alloy measured at 75 % copper, 7 % tin and **18 % lead** — a casting alloy chosen
for flow, not a structural bronze. Face symmetry departs measurably from regular
geometry, and about 70 % of specimens carry production holes arising from
casting.

### 3.4 Contexts are urban and civilian

Of dodecahedra with a recorded find location: **more than half from cities and
other settlements**; just under one-fifth from military camps; c 8.5 % from
contexts with plausible sacred connections; c 7 % from graves or necropolis
areas; c 5.5 % from well backfills and refuse pits; c 4 % from coin or bronze
hoards; c 4 % from rivers (`PUB-0003`, 33).

### 3.5 Nothing functional has ever been found alongside one

Across forty specimens the recorded associations are bronze statuettes of
deities, a bone object in a grave, a cache attributed to a temple, rich grave
goods, and a precision balance. There are no poles, pegs, cordage, nets, hooks,
floats, rigging, farm tools, harness, shot, arrowheads, seal boxes, styli,
needles, loom weights, awls, punches, offcuts or raw material.

There is also **no mould, casting waste, sprue, reject or workshop debris**
associated with any dodecahedron. We do not know where a single one was made.

### 3.6 The single best-evidenced context

One dodecahedron has been recovered from a sealed, dated, stratified deposit:
`RD-0020` Jublains, from burnt destruction layer F1058 of a small drystone
building over a cellar on Street 8, at the junction of Cardo A and Decumanus 8,
in use in the first half of the 3rd century.

It lay alongside **a complete precision balance**: a 225 mm beam weighing 20 g
with two pans, capacity not exceeding one Roman pound (327.45 g), of the kind
used to check the alloy of a coin or weigh precious materials.

The excavators read the building as either a merchant's or craftsman's shop —
money changer, goldsmith, bronzesmith, dealer in spices or precious materials —
**or** the den of a diviner or seer, "the two not being incompatible". That
reading is recorded as interpretation, not as evidence.

### 3.7 Decoration

Coverage is highly regular even though pattern is not. The commonest type
(Greiner/Guggenberger 1a) engraves circles around **ten of twelve** apertures and
leaves two bare — **and those two are opposite one another**. Ring counts of two
to six are recorded; three is typical. Type 2a is the exception: Mainz 3 carries
five ring-and-dot motifs on all twelve faces.

Within a specimen, ring count rises as aperture diameter falls, which Duval
judges probably empirical — a smaller aperture leaves more room on the face.
Between specimens there is no consistency at all.

---

## 4. Method

Assessment follows RDORP-010. Two independent axes are maintained and are never
combined.

### 4.1 Evidential axis

Each hypothesis carries a prediction for every evidence variable, fixed before
the corpus observation is read. Corpus observations live in
`corpus_observations`, carry a source reference, and are the sole input to
scoring: nothing is scored that lacks one.

```
score          = prediction value × direction factor        (−2 … +2)
weighted_score = score × discriminatory power × source confidence × evidence class
```

Evidence class discounts material this project produced itself. The engineering
assessments are reasoning about published measurements, not observations of
artefacts, and are weighted at half and excluded entirely from the observed-only
scenario.

**Predictive commitment is reported alongside every score and the score must
never be quoted without it.** A hypothesis predicting `0` for most variables
risks nothing yet still collects points whenever something it marked unlikely
proves absent. *Points at stake* is what a hypothesis would have scored had every
prediction been confirmed; *achieved* is the fraction obtained.

### 4.2 Usage-value axis

Evidential fit and functional worth are different questions. A hypothesis can
agree with every observation and remain implausible, because nobody casts
difficult bronze for two centuries to obtain what a stick would give them.

Three kinds of worth are recorded in `utility_assessments`. **Product** is the
value of the material output *net of the cheapest substitute*. **Craft** is
whether the difficulty and cost of making the object are part of its worth.
**Experience** is whether using it delivers something valued in itself rather
than through an output.

**This axis is deliberately excluded from the evidence score.** Folding a
judgement about worth into an evidence score would let opinion masquerade as
observation.

### 4.3 Screening

Authoring a full prediction matrix for every proposal is expensive and, once the
evidence is known, increasingly unsound. A screen records only the predictions a
mechanism *cannot avoid* and checks those against the corpus. A candidate is
eliminated when the corpus contradicts, at full strength, a prediction it had to
make on a Very High or High power variable. Surviving a screen is not support;
it means the domain merits a full matrix.

### 4.4 Pre-registration

Eleven predictions are registered in `predictions`, each stating what is
expected, what would refute it, and how to find out. They are never scored;
`validate.py` raises an error if one remains open after its variable acquires
corpus evidence. Several predict against the hypotheses this project's evidence
currently favours.

---

## 5. Hypothesis assessment

### 5.1 Results

**Reported in bands, not as a rank order.** An independent specification of one
matrix moved that hypothesis by six points, and two raters agree on directions
less than half the time (1.1). A ranking to one decimal place would be false
precision. Within a band, no ordering is claimed.

Evidence is given clustered — one observation counted once however many
variables express it — because that is the more defensible basis, and a tie
inside a cluster is resolved against the hypothesis (2.7). The unclustered
figure is shown for comparison. **The two now agree at the top**; they did not
in earlier versions of this document, and the disagreement was a defect rather
than a finding.

<!-- RDORP:BEGIN bands -->
| Band | Hypothesis | Clustered | Unclustered | Staked | Value |
| ---- | ---------- | --------- | ----------- | ------ | ----- |
| **Leading pair** | H012 Spool-knitting / cord-working frame (knob-based) | **+23** | +24 | 36 | −1 |
|  | H014 Wax bulla / seal former | **+20** | +21 | 47 | +2 |
| **Consistent but weakly testable** | H003 Ritual object | +10 | +12 | 22 | +6 |
|  | H008 Portable shrine component | +10 | +11 | 23 | +6 |
| **Partly supported** | H013 Rope-laying top (rotated, core through one aperture) | +17 | +9 | 53 | −1 |
|  | H005 Textile / knitting tool | +5 | −0 | 39 | −1 |
| **Unsupported** | H001 Structural connector / modular node | +4 | +2 | 68 | −1 |
|  | H004 Candlestick / lamp support | −1 | −1 | 28 | −1 |
|  | H002 Rangefinder / measuring instrument | −3 | +3 | 51 | −2 |
|  | H006 Astronomical instrument | −1 | −1 | 43 | −1 |
|  | H007 Military equipment | −2 | −2 | 29 | −1 |
| **Refuted** | H010 Parasol / umbrella crown fitting | −5 | −9 | 66 | +0 |
|  | H011 Archery targeting / ranging aid | −10 | −9 | 68 | −2 |
| **Eliminated** | H009 Tent apex / crown fitting (mobile shelter node) | **−31** | −34 | 78 | −2 |
<!-- RDORP:END bands -->

**The bands are not a rank order, and not ordered by score alone.** H013
scores above H003 and H008 on clustered evidence but sits in a lower band,
because it staked 53 points and recovered 17 while they staked 22 and 23 and
recovered 10. A high score earned by predicting almost nothing is not the same
result as a middling score earned by predicting a great deal, and collapsing
the two into one column would hide the difference.

*Staked* is the score a hypothesis would have obtained had every prediction
been confirmed; it measures how much each risked. *Value* is the usage-value
axis of section 10, and is judgement rather than evidence.

**H013 rope-laying is the largest mover.** It rises from +9 to +17 on
clustering, because its refutation rested almost entirely on the four wear
variables that restate one source statement.

### 5.2 Contamination status

RDORP-010 §6 requires prediction matrices to be fixed before artefact data is
examined. **Six hypotheses do not meet that condition and are declared
contaminated**: H009 to H014 were proposed after the evidence base existed and
after this project had read it. Their predictions were derived only from the
mechanics each mechanism requires, and each rationale states its mechanical
basis, which reduces the risk without removing it.

H014 carries the weakest form of the defect: the hypothesis is not this
project's — it was proposed and experimentally tested by Lamb (`PUB-0041`)
independently of this database — and only its prediction matrix was authored
here. It is also the only hypothesis in the set with any experimental work
behind it, and that work used 3D-printed replicas and observed no archaeological
specimen.

### 5.3 Reading the two axes together

**The hypothesis that leads on evidence fails hardest on worth, and the
hypotheses that lead on worth are mid-table on evidence.**

- **H012** is first on evidence and −1 on value. Peg-frames for looped cord work
  are made of scrap wood in every culture that does this; nothing about the task
  rewards leaded bronze, fine finishing or engraved rings. Twelve of its
  predictions are neutral, which inflates the score by stepping around some
  twenty points of penalty, and its decisive variable — knob wear — has never
  been measured.
- **H003 and H008** are joint first on value because for them expense is
  functional rather than anomalous. They score +2 on product by construction —
  the object *is* the product — which is close to unfalsifiable, and H003 makes
  only eleven predictions.
- **H014** is the only hypothesis without a disqualifying weakness on either
  axis: second on evidence with genuine commitment, and +2 on value. Its largest
  single loss is that no writing or sealing equipment has ever been found
  alongside a dodecahedron.

### 5.4 Robustness

<!-- RDORP:BEGIN scenarios -->
| Scenario | Leader |
| -------- | ------ |
| Baseline, fully weighted | H012 (+24.0) |
| Archaeological observations only | H012 (+22.4) |
| Confidence A-C only | H012 (+24.0) |
| **Very High power variables only** | **H014 (+10.2)** |
| Clustered, ties resolved against the hypothesis | H012 (+23.5) |
| **Clustered, ties resolved in its favour** | **H014 (+24.1)** |
| Unweighted | H012 (+15.5) |
| Corroborated variables only | H012 (+22.4) |
| Per-cell readings ignored | H012 (+22.7) |
<!-- RDORP:END scenarios -->

Two leaders across seven scenarios is not stability. **No hypothesis is robust**:
every one has a worst case over the unscored variables below the best case of a
rival. Removing any single scored variable leaves the leader unchanged, so the
result is not the artefact of one observation.

### 5.5 The one decisive elimination

**H009, tent apex**, is the only hypothesis the evidence eliminates. Its best
case, with every unscored variable resolving in its favour, is −26.5, still
below the worst case of every rival. It is also the most committed hypothesis in
the set: 25 predictions, 20 of them strong, 77.8 points staked.

Two arguments sink it independently of the scoring. **Distribution**: tents are
the most mobile artefact class in the Roman world, yet dodecahedra stop at the
north-western provinces — the argument `PUB-0003`, 33 deploys against a primary
military purpose. **Population**: a single legionary camp holds hundreds of
tents; about 134 dodecahedra are known in total.

---

## 6. Functional domains screened

<!-- RDORP:BEGIN screening -->
| ID | Candidate | Domain | Score | Hard contradictions | Verdict |
| -- | --------- | ------ | ----- | ------------------- | ------- |
| C-12 | Soft-material forming and handling tool | Craft | **+29.4** | 1 | held back - see 6.2 |
| C-13 | Garment or tailoring size gauge | Craft / Textile | **+11.8** | 3 | eliminated |
| C-10 | Wax bulla or seal former | Administrative | **+8.5** | 2 | promoted to H014 |
| C-15 | Suspended solar altitude sight | Astronomical | −1.8 | 3 | eliminated by computation |
| C-14 | Zodiac sundial by internal light projection | Astronomical | −1.9 | 5 | eliminated by computation |
| C-09 | Byre or beehive fumigation holder | Animal husbandry | −4.2 | 2 | eliminated |
| C-17 | Levelling sight for water engineering | Engineering / Surveying | −7.6 | 4 | eliminated by precision |
| C-11 | Knob-based dividers or angle gauge | Metrology / Surveying | −8.6 | 4 | eliminated |
| C-06 | Seed-sowing or dibbing gauge | Farming | −16.2 | 4 | eliminated |
| C-08 | Tether or hobble ring | Animal husbandry | −16.9 | 4 | eliminated |
| C-05 | Volumetric grain or liquid measure | Farming / Commerce | −18.0 | 4 | eliminated |
| C-04 | Rigging fairlead or lead block | Maritime | −19.1 | 4 | eliminated |
| C-07 | Livestock bell or rattle | Animal husbandry | −19.5 | 5 | eliminated |
| C-03 | Net-making mesh gauge | Maritime | −19.8 | 4 | eliminated |
| C-02 | Harness or yoke junction fitting | Military / Farming | −25.0 | 6 | eliminated |
| C-01 | Artillery shot gauge | Military | −27.0 | 6 | eliminated |
<!-- RDORP:END screening -->

### 6.1 The gauge–former asymmetry

| Reading | Best | Worst |
| ------- | ---- | ----- |
| Forms or holds soft material | C-12 **+29.4**, H014 +21.0, C-10 +8.5 | — |
| Gauges or measures | C-13 +11.8 | C-11 −8.6 … C-01 −27.0 |
| Bears load or is used in the field | — | C-06 −16.2 … C-02 −25.0 |

The asymmetry is structural and follows from the corpus rather than from any
mechanism, which is why adding a further utilitarian candidate would not change
it.

### 6.2 The strongest candidate, and why it is held back

**C-12** generalises H014 from a named material and product to the property that
matters mechanically: **everything the tool touched was softer than bronze.** It
screens at +29.4 with one hard contradiction, higher than any scored hypothesis,
and it resolves the central paradox — an object mechanically capable and never
mechanically used — with one physical premise rather than a special plea.

It is **not** promoted to a scored hypothesis. Its four wear predictions all
follow from that single premise, and the premise was chosen with knowledge of
the wear result. One act of fitting is better than twelve neutral predictions,
but it remains fitting.

Its entire testable content is residue analysis. If worked organic material —
beeswax, resin, leather dressing, fibre — is recovered, the soft-material family
becomes the strongest reading available. If a systematic study of well-preserved
specimens recovers nothing, it retains only the absence of contrary evidence.

Its one hard contradiction does not disappear by generalising: whether the tool
worked wax, leather or foil, no awls, punches, offcuts, scrap or raw material has
ever been recorded alongside a dodecahedron.

### 6.3 Candidates refuted by computation

**C-14, zodiac sundial by internal projection.** Twelve divisions require an
aperture-to-path ratio of L/d ≥ 12.5; measured specimens give 3.9 to 5.6, short
by a factor of two on every one. The projection surface is also rough, unmarked
and perforated by eleven further apertures, where every Roman zodiac dial carries
engraved declination curves on a finished surface.

**C-15, suspended solar altitude sight.** A dodecahedron is vertex-transitive, so
all twenty knobs are geometrically equivalent and the choice of knob conveys no
information. Across every possible support — 20 knobs, 12 faces, 30 edges — there
are seven distinct face-axis elevations, of which four are reachable by the noon
sun and identically so from 43.7° to 55° N. That yields eight calendar events,
not twelve.

**C-17, levelling for water engineering.** A horizontal sight line does exist —
hung from an edge, one face-pair axis lies at exactly 0°. But sight tolerance is
0.18° for the closest pair in the corpus and 1.15–2.58° for typical pairs,
against 0.2865° for the crudest gradient Vitruvius permits. Levelling accuracy
scales with baseline, and Vitruvius's chorobates is a bench of about twenty
Roman feet, far longer than any path through a dodecahedron.

**Three further computations bear on the object's own geometry rather than on
a candidate.**

`EXP-0005`, **the rings**: no complete ring can exceed cos 36° = **80.9 % of
the distance from face centre to knobs**, on any dodecahedron of any size. A
space-filling model at 2 mm pitch predicts the decorated faces of Vienne — 5
rings predicted where 4 and 6 are recorded, 3 where 3 are recorded — and fails
decisively on the undecorated opposed pair, which had room for two to three
rings and carries none. That is quantitative support for the production-hole
reading in 7.2. It also shows two workshop rules rather than one: Vienne holds
the pitch and varies the count, Jublains holds the count at three and tightens
the pitch.

`EXP-0006`, **ring counts cannot encode twelve categories**. Observed counts
span 0 to 6 — seven values for twelve faces — so by pigeonhole at least five
faces must share a count on every specimen. Vienne's published faces already
repeat: three carry three rings, two carry none.

`EXP-0007`, **orientation**. The rotation group has order 60. Distinguishing
one opposed pair reduces it to **10**, and if the remaining ten faces carry
identical decoration all 10 survive. Marking an axis is not determining an
orientation, and nothing distinguishes the two ends of the axis.

All eight computations are recorded in `experiments` and are reproducible from
the specimen measurements and standard geometry.

---

## 7. Deduction from the object's own properties

### 7.1 The topology is fixed; every measurement is free

| Fixed across the corpus | Free across the corpus |
| ----------------------- | ---------------------- |
| Twelve faces, one aperture each | Overall diameter, 2.5:1 |
| Twenty knobs, one per vertex; none without | Aperture diameter, 3:1 within one object |
| Hollow, thin-walled, cast | Wall thickness, 0.5–4 mm |
| Engraved rings around apertures | Knob diameter, ring count, decoration pattern |

**A function that survives a 2.5:1 change of scale cannot have depended on
measurement.** This is deductive, and it eliminates as a class every gauging,
calibrating and interchangeable-component reading. It is the formal statement of
the empirical asymmetry in 6.1.

### 7.2 What the marked axis marks

Ten faces are engraved and two are bare, **and the two bare faces are opposite
one another**, which defines a unique axis. On Jublains the same two faces also
carry oval openings, 21 × 26 mm against ten circular ones, and the excavators
record them as "placed in opposition on the object, possibly materialising a top
and a bottom".

Two explanations compete and they are not equally supported. About **70 % of
specimens carry production holes**, and the opposed pair without circles is "not
so perfectly round and often larger", which "in most cases can be explained by
the production process". Casting a hollow shell requires a core to be supported
and removed, and that is where the marks are.

**The manufacturing explanation subsumes the functional one.** The pair is
undecorated because it is not a proper face; oval and larger because a core
support was removed; opposed because that is how a core is supported through a
hollow solid. Every feature that makes the axis look deliberate follows from how
the object was made.

The consequence is that the one conspicuous asymmetry in a dodecahedron is most
probably a **by-product of casting, not a feature of use** — so hypotheses
requiring a working axis are drawing on a scar rather than an affordance.

A typological check could settle it: type 2a erases the distinction by engraving
all twelve faces while the size difference persists. A functional axis should not
be erasable by decoration; a manufacturing scar can be cosmetically covered.

### 7.3 Where silence is evidence and where it is not

There is no contemporaneous description of the object and not even a depiction.
That silence is not uniform, and the asymmetry is the finding rather than the
silence.

| Domain | Surviving technical literature | Silence counts |
| ------ | ------------------------------ | -------------- |
| Military equipment | Vegetius | heavily |
| Agriculture | Columella, Palladius, Varro | heavily |
| Architecture, surveying | Vitruvius; Corpus Agrimensorum | heavily |
| Water engineering | Frontinus; Vitruvius VIII | heavily |
| Traded goods and craft wages | Diocletian's Price Edict, AD 301, c 1,200 entries | heavily |
| Provincial craft practice | almost none | hardly at all |
| Gaulish religion | almost none, and hostile | hardly at all |
| Domestic and women's work | almost none | hardly at all |

The Price Edict is the sharpest instrument: a comprehensive schedule of everyday
commodities and wages from the middle of the dodecahedron window, covering the
relevant provinces, naming garments down to the *birrus Britannicus*. An object
made in the hundreds in expensive alloy for a utilitarian purpose with any
commercial standing should appear in it.

**Documentary silence therefore eliminates the utilitarian domains
differentially and leaves the craft, domestic and cultic ones untouched** — not
because those are better supported, but because Roman literature would not have
recorded them either way.

One comparandum sharpens it. Frontinus describes the Roman calibrated water-pipe
apertures, the *quinaria* system: a genuine Roman graded-aperture standard,
**named, standardised and written down**. We know what a real one looks like in
the record, and the dodecahedron is none of the three.

*This section is reasoning by this project. The individual absences are not
asserted from first-hand reading of those treatises.*

### 7.4 What the conjunction leaves

| Premise | Eliminates |
| ------- | ---------- |
| Fixed topology, free metrics | all measuring and interchangeable-component uses |
| Differential documentary silence | military, agricultural, surveying, commercial uses |
| No use wear, apertures salient | all uses involving repeated hard contact |
| No toolkit, singletons, c 134 total | trade equipment of any kind |
| Confined to the north-west, AD 200–400 | anything answering a universal or continuous need |

What survives is an object whose apertures mattered, whose dimensions did not,
used gently or visually, owned singly, belonging to no trade, and culturally
specific to the Gallo-Roman north-west for two centuries.

### 7.5 Verdict on the zodiac

| Route | Result |
| ----- | ------ |
| H006 Astronomical instrument | −0.5, 9th of 14; unsupported |
| C-14 Zodiac from projected light | −1.9, eliminated by computation |
| C-15 Zodiac from solar altitude | −1.8, eliminated by computation |
| Twelve apertures as twelve labelled categories | not refuted; the one live route |

**Determining the zodiac from the sun is refuted three times by calculation**
— by the face-axis separation, by the projection resolution, and by the fit
itself, all reproduced in Part 8 of the notebook.

The third is worth stating plainly, because it is the one that answers the
intuition behind the reading. If the object were a calendar, the sun reaching
one of its seven face-axis elevations at noon would mark a date; the zodiac
divides the year into twelve 30° arcs. **Do those dates fall on sign
boundaries?** Scanning latitude across the range the corpus covers, the best
mean distance to a boundary is **5.52° at 58.0 °N**, against 7.5° expected of
uniformly random dates.

That looks like a fit, and it is not one. The latitude scan is free, so it is a
maximisation over a nuisance parameter and will beat 7.5° for almost any set of
elevations. Against the controlling comparison — 20,000 *random* elevation sets
given the same free scan — **94 % do at least as well**, and the median random
set scores 3.51° against the real solid's 5.52°. The dodecahedron's elevations
are, if anything, unusually badly placed for marking sign boundaries. The
optimum also sits at the edge of the scanned range, a second sign that it is a
boundary artefact.

The computation is `EXP-0009`, at `database/exp_zodiac.py`, with tests at
`database/test_exp_zodiac.py` — including a sensitivity check: a contrived
elevation set placed deliberately on sign boundaries scores 0.0000°, so the
statistic does distinguish a real alignment from a random one.

What survives is the zodiac as a set of twelve *labels*, not as something read
off the sky. A Roman dodecahedron with a zodiac sign engraved on each face is
attested — the Geneva specimen, solid lead coated with silver — which establishes
that the twelve-category use existed, though that object is solid rather than
hollow and knobbed and so is not the same class.

**No hollow knobbed dodecahedron has ever been recorded with a zodiac sign, a
month name, a numeral or any inscription** — only concentric rings, whose count
appears to track aperture diameter rather than to label anything.

The labelling claim itself needs narrowing. If ring count is largely determined
by diameter it carries little independent information, and it cannot separate
apertures that diameter fails to separate — which is what happens on Vienne,
where three apertures share both a diameter and a ring count. And if opposite
pairs share decoration, as reported for Jublains, the marking distinguishes six
pairs rather than twelve apertures.

`EV043` tests it, and the two measurable specimens disagree: Avenches has all
twelve apertures distinct with a minimum separation exceeding the workshop
tolerance; Vienne does not.

---

## 8. Chronology and cultural setting

### 8.1 The window

| Evidence | Date |
| -------- | ---- |
| Corpus range in use | c AD 200 – late 4th century |
| Bachem, Feldberg, Zugmantel, Bad Cannstatt | 2nd century, uncertain |
| `RD-0020` Jublains, the only stratified specimen | first half of the 3rd century |
| `RD-0021` Arles | 3rd century |
| `RD-0005` Norton Disney | 4th-century pottery in association, 3rd-century in the fill |
| `RD-0023` Gelduba, grave of a woman | c AD 350 |
| Arloff icosahedron, the related comparandum | c AD 200 |

Roughly two centuries, with a possible 2nd-century tail that every source flags
as uncertain. There is no antecedent and no successor.

### 8.2 The zone

| Region | Share of the known corpus |
| ------ | ------------------------- |
| Gallic and Germanic provinces, especially former Gallia Comata | c 70 % |
| Britannia | c 20 % |
| Within territory that briefly formed the Gallic Empire (AD 260–74) | **c 90 %** |
| Italy, Spain, Africa, the eastern provinces | **none** |
| Outliers | Brigetio (Pannonia), Deonica (Moesia superior) |

The correlation with the Gallic Empire is real but must not be read as cause:
the objects begin around AD 200 and continue past AD 274, so both plausibly
reflect the same underlying regional coherence.

### 8.3 What the combination constrains

Six properties hold at once: bounded in time to about two centuries; bounded in
space to the Romanised Celtic north-west; expensive; never standardised; never
exported; never mentioned in any surviving text.

**Technologies do not behave like this.** A device that does a job spreads to
wherever the job exists, is copied to a standard, and is named. Something useful
for shipping reaches the Mediterranean; something useful for artillery reaches
every frontier; something useful for farming outlives the 4th century. This
object did none of those things, and the argument is independent of the wear,
standardisation and context evidence that refute the utilitarian hypotheses
individually.

One coincidence of setting is worth recording without being pressed. The *birrus
Britannicus* appears in Diocletian's Price Edict of AD 301 at 6,000 denarii, and
hooded garments are a style associated with Gaul and the north-west. A
distinctive, high-value, regionally branded textile industry existed in the same
provinces and the same window. No source connects the two; it is recorded only
because it is the one context in which regional confinement of a *utilitarian*
object would be unsurprising.

Hundreds of these objects were made, in expensive alloy, over two centuries, in a
literate province of a literate empire — and no Roman wrote down what they were.
Whatever the explanation, it has to account for that silence.

---

## 9. Limits of the evidence

1. **Coverage.** 31 % of the known corpus, skewed 50 % British against a known
   corpus of about 20 % British.
2. **Authenticity.** No specimen authenticated; two of the three with usable
   aperture data are unexcavated private-collection pieces; ancient imitation is
   proposed in the literature and untested.
3. **Single-source dependence.** Almost every corpus-level statistic rests on
   `PUB-0003`, which summarises an unpublished catalogue (`PUB-0022`) this
   project has not consulted directly.
4. **Wear is macroscopic, and two wear variables are not observed at all.**
   Microscopic analysis has never been performed, and rope wear and rotational
   wear are scored from the absence of any report rather than from examination
   (2.7).
5. **40 % of all 224 observations come from one source**, and seven scored
   variables have no second voice — three of them no source at all (2.7).
6. **Residues are unmeasured.** The only record in the corpus is described by its
   own source as possibly unreliable.
7. **Directions are judgements, and they are now known to be unreliable.** An
   independent rater, blind to the hypotheses and scores, agreed with the
   recorded direction on **13 of 28 observations (46 %)** and with the
   confidence grade on 15 of 28; both agreed on only 7. Four ratings were
   outright polarity reversals.
8. **The predictions depend on who wrote them.** An independent specification
   of H012's full matrix, blind to the evidence, agreed on **22 of 42 cells
   (52 %)** and scored the hypothesis **six points lower**. The loss falls on
   EV017, EV003 and EV019 — three variables where the recorded matrix predicts
   the absence that the corpus shows and the blind specifier predicted its
   presence. See RDORP-013 item A3.
9. **Roughly half the variables do not state which pole is positive**, which
   makes some of the disagreement above spurious and direction assignment
   irreproducible until it is fixed (RDORP-013 item A11).
10. **The scale does not say where indifference ends and prediction begins.**
   `0` means the mechanism does not care and `-` means the feature is
   unexpected, but no rule separates them, and the matrix does not draw the
   line consistently. Thirteen cells on scored variables are `-` on the strength
   of rationales reading *need not* or *not required*, while forty-one cells
   saying the same kind of thing are `0`. **The largest beneficiary is H012, at
   +4.1, and H014 gains nothing** — so it inflates the margin between the
   leading pair. It is inert under clustering (RDORP-013 item A15).
11. **One of the thirty-two scored variables carries no predictions at all.**
   `EV044` interior finish has a corpus observation at High power and is
   counted among the scored variables throughout this document, but no
   hypothesis has ever been given a prediction for it. All fourteen of its
   cells default to `0` and it discriminates nothing. Three further variables
   are in the same state and are at least flagged non-discriminating. **The
   headline "32 of 48 variables scored" is therefore one variable optimistic**,
   and every *staked* figure in 5.1 counts four unwritten cells as deliberate
   abstentions (RDORP-013 item A18).
12. **Six hypotheses are contaminated** (5.2).
13. **Eight variables carry corpus evidence that no hypothesis is specific enough
   to be tested against**, including site type and associated finds — the
   best-quantified evidence in the corpus. These are defects in the prediction
   matrix, not gaps in the evidence, and repairing them requires respecifying
   predictions *without reference to the observations that exposed them*.
14. **Twelve variables have no corpus evidence at all**, including three rated
   Very High.

---

## 10. What can and cannot be concluded

### Can be said

- The objects were not made to a standard at any level — size, wall, apertures,
  knobs or decoration.
- They show no macroscopic use wear.
- Their distribution is tightly restricted to the north-western provinces, with
  none from Italy, Spain, Africa or the eastern empire.
- They were in use from about AD 200 to the late 4th century.
- Contexts are predominantly civilian and predominantly settlements; military
  camps are a minority.
- No functional equipment of any kind has ever been recovered with one.
- The hypotheses making specific mechanical predictions — structural connector,
  rangefinder, astronomical instrument, textile tool, tent apex, parasol crown,
  archery aid, rope-laying top — have had those predictions tested and largely
  refuted.
- No reading is both well supported and obviously worth doing.

### Cannot be said

- **That the object was a ritual object.** H003 leads on value and sits third on
  evidence by not committing to anything the evidence could contradict.
- **That it was a frame for looped cord work.** H012 leads every evidential
  scenario, but twelve of its predictions are neutral, its matrix was authored
  with knowledge of the evidence, and its decisive variable has never been
  measured.
- **That it was a wax bulla former.** H014 is the best-balanced hypothesis and
  the only one with experimental work behind it, but that work used replicas, its
  decisive variable is unmeasured, and no sealing equipment has ever been found
  alongside a dodecahedron.
- **That it was a soft-material former of any kind.** C-12 outscores everything
  and is held back as a fitted construction.
- **That it served any screened utilitarian use.** Fourteen of sixteen are
  eliminated, as a class — but see the next point.
- **That the eliminations resting on absence of wear are secure.** H013, H005,
  H004 and H010 all recover substantially when uncorroborated variables are
  removed, and H013 rises to third place. Their refutation depends on two Very
  High variables that no one has ever measured (2.8).
- **That the zodiac can be determined from the object**, or that the object was
  labelled with it.
- **That the corpus is a single population of authentic originals.**
- Anything resting on residues, thermal alteration, microscopic wear, knob wear
  or manufacturing difficulty.

The primary research question remains open. What the project can now state
precisely is **which measurements would close it, and in what order**.

---

## 11. Priorities

| # | Action | Decides |
| - | ------ | ------- |
| 0 | **Restate every variable whose positive pole is undefined** (RDORP-013 A11), then re-run the direction rating | Direction assignment is not currently reproducible; roughly half the variables do not say whether `confirmed` means the property is high or low. No laboratory, half a day |
| 0b | **A fourth blind prompt: directions for the A5 predictions** (RDORP-013 A12) | 84 blind predictions are written and cannot be scored, because only the contaminated party can currently assign their directions |
| 1 | Measure every aperture **and** count its rings separately, on any complete specimen, recording which apertures are opposite which | `EV043`; the labelling and pair questions. A ruler, a lens and an afternoon in a museum store |
| 2 | **Examine one specimen for rope wear and rotational wear** | `EV019`, `EV020`; converts two Very High variables from silence into observation, and decides whether the refutations of H013, H005, H004 and H010 stand (2.8) |
| 2b | Microwear on knob necks and aperture lips of the same specimen | `EV041`, `EV042`; decides H012 and separates it from H013 |
| 3 | Residue analysis on unconserved specimens | `EV024`; decides H014 and C-12 |
| 4 | Consult `PUB-0022` (Guggenberger 1999) directly | Type attributions for `EV048`, which now gates the defence of the standardisation finding; and the per-specimen measurement tables |
| 5 | Standardisation measured **within** a single type | `EV048`, `P-0011`; whether the central finding survives the imitation confound |
| 6 | Experimental lost-wax reproduction; and a search for any mould, casting waste or reject | `EV045`, `P-0010`; whether the craft-value reading has a foundation |
| 7 | Respecify the prediction matrix for site type, associated finds and dating | Three Very High variables with good evidence contributing nothing |
| 8 | Thermal analysis | `EV023`; the only remaining route to the candlestick and fumigation readings |
| 9 | Add continental specimens with measurements and context | The 50 % British skew |
| 10 | A second source for the variables now resting on `PUB-0006` alone | Reduces the dependence of the whole analysis on one database of British surface finds; `PUB-0022` would underwrite most of them at a stroke |

Items 1 and 5 require no laboratory. Item 1 is the cheapest decisive test the
project has identified.

---

## 12. Revision History

| Version | Date | Description |
| ------- | ---- | ----------- |
| 1.9.0 | 2026-08-09 | Recorded in the limits that EV044 is counted among the scored variables while carrying no prediction from any hypothesis, so the 32-of-48 headline is one variable optimistic (RDORP-013 A18). |
| 1.8.0 | 2026-08-09 | Project-wide sanity check. Regenerated the 5.1 and 2.7 tables from the database after the A16 fix; five hypotheses still carried pre-fix clustered scores. Corrected H013's name, truncated in the source CSV. Stated that the bands are not ordered by score alone. |
| 1.7.0 | 2026-08-09 | Withdrew the finding that clustering changes the leader. It rested on an undeclared tie-break that depended on dictionary iteration order (RDORP-013 A16). H012 leads on every basis except very_high_power. |
| 1.6.0 | 2026-08-09 | Removed a superseded projection table from 2.7; recorded the indifference-scored-as-prediction defect in the limits (RDORP-013 A15); corrected the single-source share to 40 % and renumbered the limits list. |
| 1.5.0 | 2026-08-09 | Reworked: findings restructured to lead with the measured reliability of the method; results reported in bands rather than as a rank order; corpus figures brought current; clustered scoring made the primary basis. |
| 1.4.0 | 2026-08-09 | Recorded the blind-protocol results: 52 % cell agreement on predictions, 46 % on directions. The limits chapter now carries the reliability figures. |
| 1.3.0 | 2026-08-09 | Implemented evidence clustering (A1) and the weighting sweep (A2). *Reported that clustering changes the leader to H014 — withdrawn at 1.7.0; it was a tie-break artefact.* |
| 1.2.1 | 2026-08-08 | Merged the two findings on refutation security into one, renumbered the findings, and corrected the scoping of the conclusions in 2.8. |
| 1.2.0 | 2026-08-08 | Recorded the correlated-evidence inflation in 1.9 and 2.8, and referenced RDORP-013. |
| 1.1.0 | 2026-08-08 | Added the evidence-base weakness audit (2.7) and the corroborated-variables-only scenario (2.8), and corrected the finding in 1.1 that the refutations are uniformly secure. |
| 1.0.0 | 2026-08-08 | Restructured into comprehensive chapters, removing the record of the analysis's own development. Added the specimen quality and admissibility analysis with explicit rejection rules, and the resulting robustness check. |
| 0.1.0–0.19.0 | 2026-08-07 to 08 | Successive drafts. See git history. |
