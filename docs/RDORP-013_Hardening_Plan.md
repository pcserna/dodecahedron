---
Document ID: RDORP-013
Title: Hardening Plan and Next Steps
Version: 1.4.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-08
Last Updated: 2026-08-08
Related Documents:
  - RDORP-010 Analytical Method
  - RDORP-011 Geometry Specification
  - RDORP-012 Results Summary
---

# Hardening Plan and Next Steps

What is wrong with the current analysis, what would fix it, and in what order.

The project's results are stated in RDORP-012. This document is the adversarial
companion: it assumes the results are wrong and asks what would show it.

Items are ranked by **how much they would move the answer**, not by effort. Four
of the top six require no laboratory and no new specimens.

---

## Summary

| # | Item | Kind | Effect if acted on |
| - | ---- | ---- | ------------------ |
| ~~A1~~ | Correlated evidence is scored as independent | Method | **DONE. Changed the leader: H014 now first, H012 second, and the pair is inseparable** |
| ~~A2~~ | No sensitivity analysis over the weighting scheme | Method | **DONE. 45 combinations; the weights decide nothing, deduplication decides everything** |
| **B1** | Rope wear and rotational wear never observed | Evidence | Decides four refutations |
| ~~A3~~ | Prediction matrices written and scored by the same party | Method | **RUN. 52 % cell agreement, 46 % direction agreement. The threat is real and measured** |
| **A11** | Half the evidence variables do not state which pole is positive | Method | **New, found by A3. Causes spurious disagreement and blocks A5 from being loaded** |
| **B2** | Aperture and ring survey | Evidence | Cheapest decisive test in the project |
| **A4** | Three scored variables have no source | Method | Removes a rule violation; moves H001 by −2.6 |
| **B3** | Residue analysis | Evidence | Decides the two leading hypotheses |
| **C1** | Guggenberger 1999 read directly | Evidence | Underwrites most single-source variables at a stroke |
| ~~A5~~ | Eight variables carry good evidence no hypothesis can be tested against | Method | **SPECIFIED. 84 blind predictions written, 51 changed. Cannot be scored until A11 and A12 are done** |
| **A12** | The blind predictions still need blind directions | Method | **New. A5's predictions cannot be scored without directions only the contaminated party can currently assign** |
| A9 | The two evidence layers cannot contradict each other | Method | **Done.** Found four scored variables with no specimen beneath them |
| A10 | Predictions do not see accumulating evidence | Method | **Done.** Six of eleven open predictions are now testable |

---

## Part A — Methodological hardening

### A1. Correlated evidence is being scored as independent — DONE

**The defect.** The scoring sums weighted scores across 32 variables as though
each were an independent observation. Several are not. The clearest case is the
wear cluster: `EV017` internal hole wear, `EV018` external wear, `EV019` rope
wear and `EV020` rotational wear **all cite the same page of the same source**
(`PUB-0003`, 45), which in turn reports a single statement from Guggenberger
1999. One sentence is being scored four times, three of them at Very High power.

**The magnitude.** Collapsing the cluster to its single strongest contribution:

| Hypothesis | Current | Wear cluster | Collapsed | Revised |
| ---------- | ------- | ------------ | --------- | ------- |
| H013 Rope-laying top | +8.7 | −15.3 | −4.5 | **+19.5** |
| H005 Textile tool | −0.2 | −10.8 | −4.5 | **+6.2** |
| H001 Structural connector | +2.3 | −8.6 | −4.5 | **+6.4** |
| H010 Parasol crown | −9.2 | −10.8 | −4.5 | −2.9 |
| H009 Tent apex | −34.0 | −12.6 | −4.5 | −25.9 |
| H012 Cord frame *(leader)* | +24.0 | +0.4 | +2.2 | +25.8 |
| H014 Wax former *(leader)* | +21.0 | +0.4 | +2.2 | +22.8 |

**This is the largest known distortion in the analysis, and it inflates the
refutations rather than the leaders** — the same asymmetry the source-corroboration
audit found (RDORP-012 §2.8). Two independent checks now agree: the positive
result is robust, the negative result is overstated.

**Other suspected clusters, unquantified:**

| Cluster | Variables | Shared basis |
| ------- | --------- | ------------ |
| Aperture dimensions | EV004, EV005, EV039, EV043 | The same measured diameters |
| Size range | EV037, EV039 | The published 4–10 cm range |
| Casting artefacts | EV013, EV046 | The production-hole pair *(already caught; EV046 set non-discriminating)* |
| Geometric irregularity | EV010, EV012, EV013 | The same manufacturing evidence |

**Fix.** Add an `evidence_cluster` column to `corpus_observations`. Variables
sharing a cluster share a budget: the cluster contributes its single strongest
cell, or its mean, rather than the sum. Report both the clustered and unclustered
totals. Declaring clusters is a judgement and must be recorded with reasoning,
like directions.

**Implemented** as `corpus_observations.evidence_cluster` and the `clustered`
scenario. Five clusters declared on shared evidential basis. **The correction
changed the leader**: H014 +24.1 against H012 +23.5, where unclustered H012 led
by three points. H013 rose 8.4 and H005 8.3. The two leaders are now separated
by less than one point under every weighting and must be reported as a tied
pair.

### A2. No sensitivity analysis over the weighting scheme — DONE

**The defect.** Discriminatory power is weighted 3 / 2 / 1, source confidence
1.0 / 0.9 / 0.75 / 0.5 / 0.25, evidence class 1.0 / 0.75 / 0.5. **These numbers
were invented and never tested.** The analysis runs seven scenarios over which
*variables* are included and none over the weights themselves.

**Fix.** Sweep the weight schemes and report the ranking's stability:

- Power: 3/2/1, 5/3/1, 4/2/1, 2/1.5/1, and flat 1/1/1
- Confidence: as now, linear, and flat
- Class: 1/0.75/0.5, 1/0.5/0.25, and excluded entirely

Report the fraction of the 45 combinations in which each hypothesis leads. A
result that survives one weighting and not the rest is a result about the
weighting.

**Implemented** as `weight_sweep`, reported in `reports/hdm_analysis.md`.
**Result: the weighting scheme decides nothing.** Unclustered, the same
hypothesis leads in all 45 combinations. Clustered, H014 leads in 36 and H012
in 9, with the margin never exceeding one point. The suspicion that the
ranking was an artefact of invented weights is not supported; the real
sensitivity was to correlated evidence, which A1 has now corrected.

### A3. Prediction matrices are written and scored by the same party

**The defect.** Every prediction in the matrix was authored by this project,
which also assigns every direction and computes every score. There is no
independent specification, no second rater, and no blind protocol. This is the
central validity threat for the whole method, and it is unaddressed.

Six of fourteen hypotheses are additionally declared contaminated: H009 to H014
were specified after the evidence was known.

**Fix, in order of strength.**

1. **Blind specification.** Give a collaborator the hypothesis, the variable
   list with definitions, and *no observations*. Have them write the 48
   predictions. Compare against ours and report the disagreement rate.
2. **Inter-rater reliability on directions.** Have a second person assign
   directions from the `statement` field alone, without seeing the hypotheses or
   the scores. Report Cohen's κ.
3. **Re-specify the six contaminated matrices** blind, by someone who has not
   read RDORP-012.

**Cost.** Needs one collaborator and perhaps two days of their time. **This is
the highest-value thing an outside contributor could do.**

**Prompts are written and ready to run**, each self-contained so the runner
never needs to touch the repository:

| Prompt | Task | Blindfold |
| ------ | ---- | --------- |
| `docs/A3a_BLIND_MATRIX_PROMPT.md` | Specify all 48 predictions for one hypothesis | Blind to the observations |
| `docs/A3b_DIRECTION_RATING_PROMPT.md` | Rate the direction and confidence of all 28 scored corpus observations | Blind to the hypotheses and scores |
| `docs/A5_BLIND_SPECIFICATION_PROMPT.md` | Respecify six vague variables across all 14 hypotheses | Blind to the observations |

Note that A3b's blindfold points the **opposite way** to the other two: the
rater sees the evidence and must not see the hypotheses. Running A3a and A3b
in the same session would defeat both.

### A3 — RESULTS

All three protocols were run in separate sessions, each working only from its
prompt.

| Protocol | Measure | Result |
| -------- | ------- | ------ |
| **A3a** blind matrix for H012 | Cell agreement with the existing matrix | **22 of 42 — 52 %**, with six disagreements of two levels or more |
| **A3a** scored | H012 under the blind matrix | **+16.4** unclustered, **+17.7** clustered, against +22.7 and +22.1 |
| **A3b** direction rating | Direction agreement | **13 of 28 — 46 %** |
| **A3b** | Confidence agreement | 15 of 28 — 54 % |
| **A3b** | Both agreeing | **7 of 28 — 25 %** |
| **A5** | Vague predictions changed once made specific | **51 of 84 — 61 %** |

**The central validity threat is confirmed and quantified.** Two specifiers
working from the same hypothesis definitions agree on barely half the cells,
and two raters reading the same sourced statements agree on the direction less
than half the time.

**Where the loss falls is the finding.** The blind matrix costs H012 most on
EV017 internal hole wear (−4.5), EV003 wall thickness (−3.6) and EV019 rope
wear (−2.2). On each of the three, the existing matrix predicts the *absence*
that the corpus records, while the independent specifier, working from the
mechanism alone, predicted the *presence*. **That is the signature of a matrix
written by someone who already knew the answer**, and it is exactly what the
exercise was built to detect.

**Three caveats, all raised by the runners themselves and none by this
project:**

1. **Partial independence.** All three runs used the same model family as the
   original. The A3a runner flagged this unprompted: a second specifier sharing
   the project's priors, not an independent discipline.
2. **The A3a prompt leaked.** It stated that H012 and H014 are "the two
   currently leading" hypotheses, so the specifier knew before writing a cell
   that this hypothesis scores well. That is a fault in the prompt. **It makes
   52 % an optimistic figure**, and the prompt must be corrected before reuse.
3. The A5 runner grepped the hardening plan for its own item name and saw two
   lines stating these variables carry good evidence.

**Still outstanding under A3:** H014 and H003 have not been blind-specified,
and must be done in sessions that have not read the H012 result.

### A11. Half the variables do not state which pole is positive — NEW

Found by A3, and it explains a large share of the disagreement.

The direction scale runs `confirmed` to `absent`, which is unambiguous for a
variable naming a feature whose presence is at issue — *rope wear*, *repair
evidence*. It is ambiguous for a variable naming a **quantity**:

| Variable | The question it does not answer |
| -------- | ------------------------------- |
| EV002 Mass | Does `confirmed` mean mass is recorded, or that it is high? |
| EV003 Wall thickness | Thin walls present, or thick walls present? |
| EV010 Face symmetry | Symmetry present, or deviation present? |
| EV012 Casting quality | Quality good, or quality poor? |
| EV035 Structural stability | Stable, or unstable? |
| EV042 Microwear location | Bore wear, or lip wear? |
| EV044 Interior finish | Finished, or unfinished? |

The independent rater named EV012 explicitly: *"whether the variable means
'quality is good' or 'quality is poor'."* Four of the twenty-one A3b
disagreements are outright polarity reversals on such variables — EV003, EV010,
EV012, EV044 — and one of the two three-level disagreements in A3a is EV042,
where both specifiers described **the same physical expectation** and assigned
opposite signs.

**So the reliability figures above are pessimistic in one direction and
optimistic in the other**: some disagreement is spurious and would vanish with
clearer definitions, while the prompt leak inflates agreement.

**Fix.** Restate every ambiguous variable so the positive pole is explicit —
*Wall thickness: substantial (over 3 mm)* rather than *Wall thickness* — then
re-run A3b against the corrected definitions. Until then, direction assignment
is not reproducible, and no reliability figure from it should be published.

**Cost.** Half a day. Must precede any further direction work.

### A12. Blind predictions still need blind directions — NEW

A5 produced 84 specific predictions for the six variables that currently score
nothing. **They cannot be loaded yet**, and the reason is structural.

Scoring a prediction requires a **direction** for its variable. For
distribution variables such as site type and associated finds, a single
corpus-wide direction cannot serve every hypothesis — that is why
`hpm_readings` exists, holding a direction per hypothesis per variable. Those
readings would have to be written by this project, which knows the evidence.

**Loading A5 without blind readings would reintroduce, at the direction step,
exactly the contamination A5 removed at the prediction step.** The blind
predictions would be scored by a contaminated scorer, and the exercise would
be worth nothing.

**Fix.** A fourth prompt: give a blind runner the 84 predictions and the corpus
statements for those six variables, and have them assign the per-cell readings
without seeing the scores or the ranking. Only then can A5 be loaded.

### A4. Three scored variables have no source

`EV034` rope compatibility, `EV035` structural stability and `EV036` load
transfer are this project's own geometric reasoning with **no source at all**, in
a database whose first rule is that every fact has one. They are discounted to
half weight and excluded from the observed-only scenario, but they remain in the
baseline, and removing them drops H001 from +2.3 to −0.3.

**Fix.** Either source them — a published engineering assessment of the form
would do — or reclassify them as Derived-unsourced and exclude them from the
baseline, leaving them visible in a separate scenario. Promote the validator
finding from warning to error.

**Cost.** An hour.

### A5. Eight variables carry evidence no hypothesis can be tested against

Site type, associated finds, dating, province, mass, stratigraphy and two others
carry corpus evidence and score zero, because the predictions are not specific
enough to be confirmed or refuted. `EV025` site type is the best-quantified
variable in the corpus and contributes nothing.

**Fix.** Respecify those predictions to name what each hypothesis expects — which
site type, which associated finds, which period. **The respecification must be
written before the observation is consulted**, or the matrix is being tuned to
the data. Ideally by someone who has not read §3 of RDORP-012.

**Cost.** A day, plus the discipline to do it in the right order. **Prompt
ready at `docs/A5_BLIND_SPECIFICATION_PROMPT.md`.**

### A6. Argument from silence has no rule

`EV019` and `EV020` are scored `absent` because no report exists, not because
anyone looked. This was handled by dropping confidence to C, but by judgement
rather than by rule.

**Fix.** Add an `observation_basis` field distinguishing *examined and absent*
from *not reported*. Cap the confidence of not-reported observations, and exclude
them from a scenario by default.

**Cost.** Two hours.

### A7. The screening threshold is crude

The screen eliminated C-10 on one hard contradiction; promoted to a full
hypothesis it scored +21.0 and second place. The verdict rule is therefore known
to produce false negatives.

**Fix.** Replace the binary rule with a reported band — eliminated, marginal,
promote — and treat any candidate with a positive total as marginal regardless of
hard contradictions.

**Cost.** An hour.

### A9. The two evidence layers cannot contradict each other — DONE

**The defect.** Scoring reads only `corpus_observations`. Specimen evidence never
propagates upward, so a corpus observation can stand indefinitely while the
specimens beneath it say something else, and nothing notices. This was found by
adding three specimens and eighteen observations and watching **every score stay
byte-identical**.

**Fix, implemented in `validate.py`.** Three checks:

- `corpus-without-specimen` — a corpus observation that scores but rests on no
  specimen at all. **Four found**, and they are not minor: `EV019` rope wear and
  `EV020` rotational wear score `absent` at Very High power, `EV038` and `EV044`
  at High power, and nothing in the corpus can currently contradict any of them.
- `specimen-without-corpus` — specimen evidence on a variable the corpus does
  not cover, so none of it reaches the scoring. **Seven found.**
- `recorded-conflict` — conflicts recorded in prose are surfaced rather than
  buried in a notes field. **Nine found.**

**Still outstanding.** The checks report the asymmetry; they do not resolve it.
A corpus observation contradicted by its own specimens still scores unchanged.

### A10. Predictions do not see accumulating evidence — DONE

**The defect.** `check_predictions` errors only when a prediction's variable
acquires a *corpus* observation. Specimen evidence can accumulate indefinitely
without anyone noticing that a registered prediction has become testable.

`P-0005` predicted bevelled aperture lips. A PAS record states that "all of the
apertures have slightly bevelled rounded edges" — the first `EV007` observation
in the project, bearing directly on an open prediction. Nothing noticed.

**Fix, implemented in `validate.py`.** `prediction-testable` reports every open
prediction that now has specimen evidence. **Six of eleven do:**

| Prediction | Variable | Specimen observations |
| ---------- | -------- | --------------------- |
| P-0001 | EV041 knob wear | 4 |
| P-0009 | EV043 aperture distinguishability | 3 |
| P-0006 | EV015 repair evidence | 2 |
| P-0002 | EV024 residues | 1 |
| P-0005 | EV007 hole edge radius | 1 |
| P-0007 | EV030 number at site | 1 |

Each should now be resolved, or explicitly declared still too thin to resolve.
Leaving the position implicit is what the check exists to prevent.

### A8. No priors

The framework scores likelihood of evidence given each hypothesis and never
asks how plausible each hypothesis was to begin with. That is defensible — priors
are where bias enters — but it should be stated as a choice rather than left
implicit, and the usage-value axis is already doing some of this work informally.

**Fix.** Document the choice in RDORP-010. Consider whether the usage-value axis
should be formalised as a prior rather than reported separately.

---

## Part B — Evidence acquisition

All three items below could be done in a single museum visit to one
well-preserved specimen. `RD-0005` Norton Disney is the best candidate:
excavated, complete, undamaged, institutionally held.

### B1. Rope wear and rotational wear — the two unobserved variables

Two Very High variables currently score from the absence of any report. Nobody
has ever examined a dodecahedron for either.

**Method.** Low-magnification then SEM examination of the knobs, knob necks,
aperture rims and interior for grooving, polish or directional striation
consistent with cord under tension or with rotation.

**Decides.** Whether the refutations of H013, H005, H004 and H010 stand. Those
four recover by +2.6 to +6.9 points when the uncorroborated wear variables are
removed (RDORP-012 §2.8), and by more again under A1.

### B2. The aperture and ring survey — cheapest decisive test

**Method.** Measure all twelve aperture diameters and count the engraved rings
around each **separately**, recording which apertures are opposite which. Follow
the face-numbering convention in RDORP-011. A ruler, a lens, and an afternoon.

**Decides.** `EV043`. Whether the apertures are individually distinguishable
(twelve categories), distinguishable only in opposed pairs (six), or not
systematically distinguishable at all. Recording rings and diameters separately
is essential because ring count appears to track diameter, and the two must be
disentangled before either can be said to label anything.

The two measurable specimens currently disagree — Avenches confirms, Vienne
partly refutes — and both are unexcavated.

### B3. Residue analysis

**Method.** GC-MS or FTIR on interior scrapings and aperture rims of specimens
that have **not** been cleaned or consolidated. Conservation history must be
established first; a conserved specimen is worthless for this.

**Decides.** `EV024`, and with it both leading hypotheses. Beeswax and resin
would support H014 and the soft-material family; a systematic negative would
remove their only positive evidence.

### B4. Thermal analysis

Interior examination for soot and combustion products. `EV023` is the only
remaining route to the candlestick and fumigation readings, and a positive result
would revive H004 almost single-handedly.

### B5. Experimental casting

Reproduce the hollow form by lost wax in an alloy of the recorded composition
(75 Cu / 7 Sn / 18 Pb), with integral or soldered knobs, and record the failure
rate. Separately, search museum and excavation records for **any** mould, casting
waste, sprue or reject.

**Decides.** `EV045` and prediction `P-0010`. The claim that these objects were
"difficult to cast and thus inherently valuable" is an assertion in the
literature, and the entire craft-value reading rests on it. No mould or casting
waste is known anywhere: we do not know where a single dodecahedron was made.

---

## Part C — Corpus expansion

### C1. Read Guggenberger 1999 directly

The single highest-value acquisition. It is the underlying source for the corpus
measurements, the typology, the knob data, the wear statement and the find-context
tallies — almost all of which currently reach this project at one remove through
`PUB-0003`. Reading it would:

- independently underwrite most of the variables now resting on `PUB-0006` alone;
- supply the per-specimen measurement tables that would populate the geometry
  variables properly;
- supply the type attributions needed for `EV048`, which gates the defence of the
  standardisation finding against the imitation confound.

Nouwen 1993 and Greiner 1996 follow for the same reasons.

### C2. Continental specimens

The recorded corpus is 56 % British against a known corpus about 20 % British.
Every additional continental specimen with measurements *and* context improves
representativeness directly.

### C3. Stratified contexts

One dodecahedron in the entire corpus comes from a sealed, dated deposit. Any
second would roughly double the project's grade-A evidence.

### C4. Authenticity screening

No specimen has been authenticated against forgery. XRF or isotope analysis on
the unprovenanced private-collection specimens — `RD-0022`, `RD-0035` — would
either secure or remove two of the three specimens carrying usable aperture data.

---

## Part D — Collaboration and review

The project is set up so that disagreement is cheap to express: change a
direction, re-run, and see exactly how much the number moves.

**What outside contributors can do that we cannot do ourselves:**

1. **Blind prediction specification** (A3) — needs someone who has not read the
   results.
2. **Independent direction assignment** (A3) — needs a second rater.
3. **Specimen access** (Part B) — needs someone with museum contacts.
4. **The specialist literature** (C1) — needs library access and German and
   French.
5. **Adversarial review of the deductions** in RDORP-012 §7. Those are reasoning,
   not observation, and have had no external scrutiny.

**What we should stop doing.** Proposing further hypotheses from inside the
project. Six of fourteen are already contaminated, and each new one is authored
by a party that knows the answers better than the last. New hypotheses should
come from outside, or from the literature.

---

## Part E — Publication gates

| Route | Blocked by |
| ----- | ---------- |
| Data paper — corpus, pipeline, provenance model | Nothing. A1 and A4 should be fixed first |
| Short note — the computational refutations (`EXP-0002` to `EXP-0004`) | Nothing. Self-contained and checkable |
| Methods paper — the framework | A1, A2, A3 |
| Archaeology paper | Primary data (Part B), C1, and human verification of every judgement recorded here |

---

## Sequencing

**Now, no new data required.** A1 clustering, A2 weight sweep, A4 unsourced
variables, A6 silence rule, A7 screening band. Together these change the reported
numbers and should precede any publication or wider circulation.

**Next, one museum visit.** B1, B2 and B3 on a single well-preserved specimen,
`RD-0005` for preference.

**In parallel, library work.** C1, and A5 respecification by someone who has not
read the results.

**Then, with a collaborator.** A3 blind specification and inter-rater reliability.

**Later.** B4, B5, C2, C3, C4.

---

## Definition of done

The analysis is hardened when:

1. No variable is scored more than once for the same underlying observation.
2. The ranking is reported with its stability across weighting schemes, not under
   one.
3. At least one prediction matrix has been specified blind and the disagreement
   rate reported.
4. No scored variable lacks a source.
5. Every corpus observation states whether its basis is examination or absence of
   report.
6. Rope wear, rotational wear, residues and aperture distinguishability have been
   measured on at least one specimen.
7. Guggenberger 1999 has been read.
8. Every pre-registered prediction has been resolved or is still genuinely open.

None of these requires the answer to be found. They require the analysis to be
worth trusting when it is.

---

## Revision History

| Version | Date | Description |
| ------- | ---- | ----------- |
| 1.4.0 | 2026-08-09 | All three blind protocols run and results recorded. Added A11 (variable polarity) and A12 (blind directions), both discovered by the exercise and both blocking A5 from being loaded. |
| 1.3.0 | 2026-08-09 | Wrote the three blind-protocol prompts for A3 and A5, each self-contained. |
| 1.2.0 | 2026-08-09 | A1 and A2 implemented. A1 changed the leader; A2 showed the weights decide nothing. |
| 1.1.0 | 2026-08-08 | Added A9 layer consistency and A10 prediction watch, both implemented in validate.py. |
| 1.0.0 | 2026-08-08 | Initial hardening plan. |
