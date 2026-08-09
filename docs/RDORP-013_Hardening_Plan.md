---
Document ID: RDORP-013
Title: Hardening Plan and Next Steps
Version: 1.6.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-08
Last Updated: 2026-08-09
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

**Six items are now closed and two of them changed the result.** Clustering
correlated evidence (A1) moved the leader; the weight sweep (A2) showed the
weights decide nothing. The blind protocols (A3, A5) were run and **measured**
the central validity threat rather than removing it. What they measured is bad
enough that the items they generated — A11, A12 and A13 — now sit above
everything else in this document, including the museum work. **A15 joins them**:
the scale does not say where indifference ends and prediction begins, and that
alone decides which of the two leading hypotheses is reported first.

---

## Summary

| # | Item | Kind | Effect if acted on |
| - | ---- | ---- | ------------------ |
| **A11** | Half the evidence variables do not state which pole is positive | Method | **Blocks everything below. Direction assignment is not reproducible until this is fixed** |
| **A15** | No rule separates *the mechanism forbids this* from *the mechanism does not care* | Method | **Decides which of the two leaders is first. Worth +4.1 to H012, the unclustered leader, and nothing to H014** |
| **A12** | The 84 blind predictions still need blind directions | Method | **Blocks A5 from being loaded. Without it a blind specification is scored by a contaminated scorer** |
| **A13** | The A3a prompt leaks which hypotheses lead | Method | **Blocks the remaining blind runs. Makes 52 % an optimistic figure and the prompt unusable as written** |
| **B1** | Rope wear and rotational wear never observed | Evidence | Decides four refutations |
| **B2** | Aperture and ring survey | Evidence | Cheapest decisive test in the project |
| **A4** | Three scored variables have no source | Method | Removes a rule violation; moves H001 by −2.6 |
| **B3** | Residue analysis | Evidence | Decides the two leading hypotheses |
| **C1** | Guggenberger 1999 read directly | Evidence | Underwrites most single-source variables at a stroke |
| **A14** | Reported figures are maintained by hand | Method | Every rework has found stale numbers; generating them would end a recurring class of error |
| A6 | Argument from silence has no rule | Method | Separates *examined and absent* from *never looked* |
| A7 | The screening threshold is crude | Method | The rule is known to produce false negatives |
| ~~A1~~ | Correlated evidence is scored as independent | Method | **DONE. Changed the leader: H014 first, H012 second, and the pair is inseparable** |
| ~~A2~~ | No sensitivity analysis over the weighting scheme | Method | **DONE. 45 combinations; the weights decide nothing, deduplication decides everything** |
| ~~A3~~ | Prediction matrices written and scored by the same party | Method | **RUN, on one hypothesis of three. 52 % cell agreement, 46 % direction agreement. The threat is real and measured** |
| ~~A5~~ | Eight variables carry evidence no hypothesis can be tested against | Method | **SPECIFIED. 84 blind predictions written, 51 changed. Cannot be scored until A11 and A12 are done** |
| ~~A9~~ | The two evidence layers cannot contradict each other | Method | **DONE.** Found four scored variables with no specimen beneath them |
| ~~A10~~ | Predictions do not see accumulating evidence | Method | **DONE.** Six of eleven open predictions are now testable |

Items below the threshold of moving the answer — A8 priors, B4 thermal
analysis, B5 experimental casting, and C2 to C4 corpus expansion — are set out
in their own sections and not listed here.

---

## Part A — Methodological hardening

### Blocking — nothing else should be done first

Three of the four were found by the blind protocols, and by the runners rather
than by this project; the fourth was found by a reader's objection. **None needs
a laboratory, a specimen or a collaborator**, and between them they decide which
hypothesis is reported first.

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

### A13. The A3a prompt leaks the answer — NEW

**The defect.** The blind-matrix prompt states that H012 and H014 are "the two
currently leading" hypotheses, and that H003 "is suspected of scoring well by
predicting almost nothing". A specifier told this knows, before writing a
single cell, that the hypothesis in front of them scores well and roughly why.

**This was found by the runner, not by this project.**

**Consequence.** The 52 % agreement figure is an **upper bound**. A specifier
who did not know H012 leads would plausibly agree less. The figure cannot be
quoted without the caveat, and the prompt cannot be reused as written.

**Fix.** Rewrite the prompt so it names the candidate hypotheses without
ranking them or hinting at their performance. Then re-run H012 as a control
alongside the outstanding H014 and H003, in three separate sessions, none of
which has read the first H012 result.

**Cost.** An hour to fix, three sessions to run. Must precede the remaining A3
work.

### A15. Indifference is being scored as prediction — NEW

**The defect.** The prediction scale defines `0` as *"the mechanism is genuinely
indifferent"* and `-` as *"unexpected"*. **Nothing states where one ends and the
other begins**, and the matrix does not draw the line consistently.

`EV039` standardisation is the clearest case. Five hypotheses make what is
recognisably the same claim, and two of them are paid for it:

| | Prediction | Rationale |
| - | ---------- | --------- |
| H012 Cord-working frame | `-` | "A personal craft tool **need not** conform to any standard" |
| H013 Rope-laying top | `-` | "A personal craft tool **need not** conform to any standard" |
| H003 Ritual object | `0` | "Ritual objects vary widely; standardisation **is not expected**" |
| H004 Candlestick | `0` | "Candle holders **are not required** to be standardised" |
| H008 Shrine component | `0` | "Shrine components **are not required** to be standardised" |

The corpus records `absent`, so the two `-` cells earn **+1.80** each and the
three `0` cells earn nothing. The distinction is drawn on the wording of the
rationale, not on any rule.

**There is a real distinction underneath, and it is not the one being drawn.**
A mechanism can *forbid* a feature or merely *not require* it, and only the
first is a prediction:

- `H012 / EV017` — *"nothing passes through the bore under load; the worked tube
  hangs free"*. The mechanism **forbids** internal wear. `-` is right, and the
  cell is doing exactly what the method is for.
- `H012 / EV039` — *"a personal craft tool need not conform to any standard"*.
  The mechanism **permits** variation. It also permits uniformity. Nothing is
  forbidden, and `0` is arguably right.

Both are written as "not expected", and both are scored `-`.

**The scope.** Across the 32 scored variables, **13 cells are scored `-` on
indifference language and 41 cells are scored `0` on language of the same kind**.
The weighted magnitude riding on the 13 is 20.6 points. The net effect:

| Hypothesis | Net from these cells |
| ---------- | -------------------- |
| **H012** | **+4.05** |
| H010 | +1.80 |
| H013 | +1.80 |
| H001 | +1.50 |
| H006 | +1.12 |
| H002 | +0.38 |
| H004 | +0.23 |
| **H014** | **0.00** |

Not all 13 are wrong — several, like `H012 / EV017`, are genuine
mechanism-forbids predictions. But **the largest beneficiary is the unclustered
leader, and the hypothesis it leads gains nothing**, so the defect points the
same way as the margin it decides.

**What it costs.** Repairing `EV039` either way shrinks H012's unclustered lead
over H014:

| | H012 | H014 | H003 | H008 |
| - | ---- | ---- | ---- | ---- |
| As recorded | **+24.0** | +21.0 | +12.2 | +11.4 |
| H012 and H013 set to `0` | **+22.2** | +21.0 | +12.2 | +11.4 |
| H003, H004 and H008 set to `-` | **+24.0** | +21.0 | +14.0 | +13.2 |

**Clustered, nothing moves at all.** `EV039` sits in the `corpus_size_range`
cluster and is not its strongest cell, so it contributes nothing once the
published size range stops being counted three times. The basis this project
already treats as primary is immune, which is a third independent argument for
preferring it.

**It also undermines the commitment metric.** A hypothesis that predicts *no
pattern* is rewarded when no pattern is found — but absence of pattern is the
default state of a hand-made object. That is a cheap point to earn, and the
staked-points figure counts it as though it had been risked.

**Fix.** State the rule: `-` requires that the mechanism make the feature
*less likely than it would otherwise be*; permission is `0`. Then re-read all
13 cells against it, and record the reasoning for each as is done for
directions. **This is a judgement, and which repair is correct is not obvious**
— it should be made explicitly and visibly, not by silently re-scoring.

**Cost.** Half a day. Belongs with A11: both are defects in what the scale
*means* rather than in the evidence.

**Found by** a reader objecting that rope-making would not have needed
standardised tools in this period. The objection is correct, the matrix already
agreed with it — and checking why exposed this.

### Outstanding

Ordered by how much each would move the reported answer.

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

### A14. Reported figures are maintained by hand — NEW

**The defect.** RDORP-012 states some two hundred numbers — corpus counts,
scores, scenario results, coverage percentages, agreement rates. The files
under `reports/` are generated from the database on every run and are always
current. **The summary document is not**: its figures are typed in, and they go
stale the moment the corpus grows.

**Every rework of that document has found stale numbers.** The most recent pass
corrected seven, including the specimen count, the observation count and the
British share. That is not a lapse of care; it is what hand-maintained derived
figures do.

**Fix.** Generate the mechanical parts — composition table, band table,
scenario table, sensitivity figures — into a fragment the pipeline rewrites,
leaving only prose under hand. Failing that, add a validator check that reads
every tagged numeric claim in the prose and compares it against the database,
erroring on drift.

**Cost.** A day for the generated-fragment route. It pays for itself at the
second rework, and the project is already past that.

### A8. No priors

The framework scores likelihood of evidence given each hypothesis and never
asks how plausible each hypothesis was to begin with. That is defensible — priors
are where bias enters — but it should be stated as a choice rather than left
implicit, and the usage-value axis is already doing some of this work informally.

**Fix.** Document the choice in RDORP-010. Consider whether the usage-value axis
should be formalised as a prior rather than reported separately.

---

### Closed

Recorded in full because two of them changed the result, and because a method document that deletes its own history cannot be audited.

### A1. Correlated evidence is being scored as independent — DONE

**The defect.** The scoring sums weighted scores across 32 variables as though
each were an independent observation. Several are not. The clearest case is the
wear cluster: `EV017` internal hole wear, `EV018` external wear, `EV019` rope
wear and `EV020` rotational wear **all cite the same page of the same source**
(`PUB-0003`, 45), which in turn reports a single statement from Guggenberger
1999. One sentence is being scored four times, three of them at Very High power.

**The magnitude.** Collapsing the cluster to its single strongest contribution:

| Hypothesis | Unclustered | Clustered | Change |
| ---------- | ----------- | --------- | ------ |
| H013 Rope-laying top | +8.7 | **+17.1** | **+8.4** |
| H005 Textile tool | −0.2 | **+8.2** | **+8.3** |
| H010 Parasol crown | −9.2 | −5.0 | +4.2 |
| H014 Wax former | +21.0 | **+24.1** | +3.0 |
| H009 Tent apex | −34.0 | −31.4 | +2.6 |
| H001 Structural connector | +2.3 | +4.1 | +1.7 |
| H012 Cord frame | +24.0 | +23.5 | −0.6 |
| H003 Ritual object | +12.2 | +10.3 | −1.8 |
| H002 Rangefinder | +3.5 | −0.4 | −3.8 |

Five clusters were declared in the end, not one: wear, corpus size range,
aperture metrics, casting, and the derived engineering assessments. **Every
hypothesis that moved by more than four points moved upward**, which is the
asymmetry stated below.

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

### A3. Prediction matrices are written and scored by the same party — RUN

**The defect.** Every prediction in the matrix was authored by this project,
which also assigns every direction and computes every score. There is no
independent specification, no second rater, and no blind protocol. This is the
central validity threat for the whole method.

**It has now been measured rather than removed**, and the measurement is below.
The defect stands: every prediction still in the database was written by this
project, and one blind matrix has been produced for one hypothesis.

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
still the highest-value thing an outside contributor could do**: one hypothesis
of three has been specified blind, by the same model family as the original.

**Three prompts were written**, each self-contained so the runner never needs to
touch the repository, and each has been run once:

| Prompt | Task | Blindfold | Status |
| ------ | ---- | --------- | ------ |
| `docs/A3a_BLIND_MATRIX_PROMPT.md` | Specify all 48 predictions for one hypothesis | Blind to the observations | Run for H012. **Leaks; must be fixed (A13)** before H014 and H003 |
| `docs/A3b_DIRECTION_RATING_PROMPT.md` | Rate the direction and confidence of all 28 scored corpus observations | Blind to the hypotheses and scores | Run. **Must be re-run after A11** |
| `docs/A5_BLIND_SPECIFICATION_PROMPT.md` | Respecify six vague variables across all 14 hypotheses | Blind to the observations | Run. **Blocked on A12** before it can be loaded |

Note that A3b's blindfold points the **opposite way** to the other two: the
rater sees the evidence and must not see the hypotheses. Running A3a and A3b
in the same session would defeat both.

#### What the protocols found

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

### A5. Eight variables carry evidence no hypothesis can be tested against — SPECIFIED, NOT YET LOADED

Site type, associated finds, dating, province, mass, stratigraphy and two others
carry corpus evidence and score zero, because the predictions are not specific
enough to be confirmed or refuted. `EV025` site type is the best-quantified
variable in the corpus and contributes nothing.

**Fix.** Respecify those predictions to name what each hypothesis expects — which
site type, which associated finds, which period. **The respecification must be
written before the observation is consulted**, or the matrix is being tuned to
the data. Ideally by someone who has not read §3 of RDORP-012.

**Run, and not yet usable.** The blind specification was carried out and
produced 84 predictions across six variables, of which **51 — 61 % — differ
from what this project had written**. The result is held at
`docs/A5_BLIND_SPECIFICATION.md` and **cannot be loaded until A12 supplies
blind directions**, because scoring it with directions written here would
reintroduce, one step later, exactly the contamination the exercise removed.

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

The recorded corpus is 50 % British against a known corpus about 20 % British.
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
   results. One hypothesis of three is done; **H014 and H003 remain**, and the
   prompt must be de-leaked first (A13).
2. **Independent direction assignment** (A3) — needs a second rater. Done once,
   at 46 % agreement, and **must be repeated after A11** because a share of that
   disagreement is an artefact of the variable definitions rather than a real
   difference of judgement.
3. **Specimen access** (Part B) — needs someone with museum contacts.
4. **The specialist literature** (C1) — needs library access and German and
   French.
5. **Adversarial review of the deductions** in RDORP-012 §7. Those are reasoning,
   not observation, and have had no external scrutiny.
6. **A blind run by a different model family or a human specialist.** All three
   protocols so far used the same model family as the original. The runners
   flagged this themselves: a second specifier sharing the project's priors is
   not an independent discipline, and the agreement rates are therefore an upper
   bound on what genuine independence would produce.

**What we should stop doing.** Proposing further hypotheses from inside the
project. Six of fourteen are already contaminated, and each new one is authored
by a party that knows the answers better than the last. New hypotheses should
come from outside, or from the literature.

---

## Part E — Publication gates

| Route | Blocked by |
| ----- | ---------- |
| Data paper — corpus, pipeline, provenance model | **Nothing.** A4 should be fixed first |
| Short note — the computational refutations (`EXP-0002` to `EXP-0007`) | **Nothing.** Self-contained, checkable, and independent of every judgement in the matrix |
| Methods paper — the framework, with its measured reliability as the result | **A11 and A13.** A1 and A2 are done; A3 has been run once and its figure is not yet quotable without the leak caveat |
| Archaeology paper — a claim about what the object was for | Primary data (Part B), C1, and human verification of every judgement recorded here |

**The methods paper is the nearest of the three that are blocked, and its
finding would be a negative one**: that a discrimination framework of this kind,
built carefully and documented completely, still agrees with an independent
specification of the same hypothesis on barely half its cells. That is worth
publishing, and it is worth publishing whether or not the object is ever
identified.

---

## Sequencing

**First, and blocking.** A11 variable polarity and A15 the prediction/indifference
boundary — both are defects in what the scale means and should be fixed together
— then A13 the leaked prompt, then A12 blind directions. None needs a laboratory, a specimen or a collaborator. Until
A11 is done, no direction assignment in this project is reproducible; until A13
is done, no further blind run is worth commissioning; until A12 is done, the 84
predictions already written cannot be scored.

**Then, re-run what those items invalidate.** A3b against the corrected
variable definitions, and A3a for H012, H014 and H003 against the corrected
prompt. The reliability figures currently in this document should be treated as
provisional until that is done.

**Then, no new data required.** A4 unsourced variables, A6 silence rule, A7
screening band, A14 generated figures.

**Then, one museum visit.** B1, B2 and B3 on a single well-preserved specimen,
`RD-0005` for preference.

**In parallel, library work.** C1 Guggenberger 1999, then Nouwen 1993 and
Greiner 1996.

**Later.** B4, B5, C2, C3, C4.

**Done, and not to be repeated.** A1, A2, A9, A10, and the first pass of A3 and
A5.


---

## Definition of done

The analysis is hardened when:

| | | Status |
| - | - | ------ |
| 1 | No variable is scored more than once for the same underlying observation | **Met.** Five clusters declared; both totals reported |
| 2 | The ranking is reported with its stability across weighting schemes, not under one | **Met.** 45 combinations swept; results now reported in bands |
| 3 | At least one prediction matrix has been specified blind and the disagreement rate reported | **Met once, and must be repeated.** The prompt leaked (A13) |
| 4 | Every variable states which pole is positive | **Not met.** A11 |
| 4b | The scale states where indifference ends and prediction begins | **Not met.** A15 |
| 5 | No scored variable lacks a source | **Not met.** Three remain (A4) |
| 6 | Every corpus observation states whether its basis is examination or absence of report | **Not met.** A6 |
| 7 | Rope wear, rotational wear, residues and aperture distinguishability measured on at least one specimen | **Not met.** Part B |
| 8 | Guggenberger 1999 has been read | **Not met.** C1 |
| 9 | Every pre-registered prediction has been resolved or is still genuinely open | **Not met.** Six of eleven are now testable and unresolved (A10) |
| 10 | Every reported figure is generated or checked against the database | **Not met.** A14 |


None of these requires the answer to be found. They require the analysis to be
worth trusting when it is.

---

## Revision History

| Version | Date | Description |
| ------- | ---- | ----------- |
| 1.6.0 | 2026-08-09 | Added A15: indifference scored as prediction. Worth +4.1 to H012 and nothing to H014, so it bears directly on which of the tied pair is reported first. Inert under clustering. |
| 1.5.0 | 2026-08-09 | Priorities reordered: A11, A12 and A13 now block everything else. Added A13 (the leaked prompt) and A14 (hand-maintained figures). A1 table replaced with the implemented clustered results. Sequencing, publication gates and definition of done rewritten against actual status. |
| 1.4.0 | 2026-08-09 | All three blind protocols run and results recorded. Added A11 (variable polarity) and A12 (blind directions), both discovered by the exercise and both blocking A5 from being loaded. |
| 1.3.0 | 2026-08-09 | Wrote the three blind-protocol prompts for A3 and A5, each self-contained. |
| 1.2.0 | 2026-08-09 | A1 and A2 implemented. A1 changed the leader; A2 showed the weights decide nothing. |
| 1.1.0 | 2026-08-08 | Added A9 layer consistency and A10 prediction watch, both implemented in validate.py. |
| 1.0.0 | 2026-08-08 | Initial hardening plan. |
