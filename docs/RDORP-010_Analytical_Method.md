---
Document ID: RDORP-010
Title: Analytical Method
Version: 0.4.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-07
Last Updated: 2026-08-07
Related Documents:
  - RDORP-001 Project Charter
  - RDORP-003 Research Method
  - RDORP-009 Decision Model
---

# Analytical Method

## 1. Purpose

This document defines the complete operational procedure for evaluating competing
functional hypotheses for Roman dodecahedra using the RDORP evidence base.

It operationalises the decision pipeline defined in RDORP-009 and governs the
four analytical datasets:

| Dataset               | Table in rdorp.sqlite     | Purpose                                     |
| --------------------- | ------------------------- | ------------------------------------------- |
| Evidence variables    | `evidence_variables`      | What to observe on each specimen            |
| Prediction matrix     | `hpm`                     | What each hypothesis predicts we will find  |
| Observations          | `artifact_observations`   | What is actually observed, per specimen     |
| Corpus observations   | `corpus_observations`     | What is observed across the corpus          |
| Discrimination matrix | `hdm_scores`              | How well each hypothesis explains the data  |
| Ranking               | `results`                 | Ranked output and robustness verdict        |
| Published conclusions | `evidence_register`       | Author interpretations, held apart, never scored |

---

## 2. Research Question

> **Which functional hypothesis is best supported by the complete body of
> archaeological, geometrical, engineering, and experimental evidence
> currently available for Roman dodecahedra?**

Secondary questions:

- Are there measurable geometric patterns across the corpus?
- Does archaeological context support or weaken specific hypotheses?
- Can engineering analysis eliminate proposed functions?
- Can experimental archaeology reproduce expected wear and behaviour?

Hypothesis evaluation is the **final stage** of the workflow. It is only
performed after the evidence base is sufficiently populated.

---

## 3. Hypotheses

Eight functional hypotheses are under evaluation.

| ID   | Name                                |
| ---- | ----------------------------------- |
| H001 | Structural connector / modular node |
| H002 | Measuring instrument / rangefinder  |
| H003 | Ritual object                       |
| H004 | Candlestick / lamp support          |
| H005 | Textile / knitting tool             |
| H006 | Astronomical instrument             |
| H007 | Military equipment                  |
| H008 | Portable shrine component           |

No hypothesis is treated as established fact before evaluation.

New hypotheses may be added by appending a row to `hypotheses.csv` and
re-running `database/build_db.py`.

---

## 4. Evidence Variables

Forty evidence variables (EV001–EV040) cover six categories:

| Category               | Variables          |
| ---------------------- | ------------------ |
| Geometry               | EV001–EV010        |
| Manufacturing          | EV011–EV016        |
| Wear                   | EV017–EV024        |
| Archaeological Context | EV025–EV032        |
| Engineering            | EV033–EV038        |
| Comparative            | EV039–EV040        |

Each variable has a **discriminatory power** rating (Very High / High / Medium)
that indicates how useful it is for distinguishing between hypotheses.
Variables rated Very High should be prioritised during data collection.

The full variable definitions are in `database/Evidence_Master_List_v1.csv`
and the `evidence_variables` table.

---

## 5. Analytical Pipeline

The analysis proceeds in six sequential steps.

```
STEP 1  Populate hpm            Prior predictions per hypothesis
STEP 2  Collect specimens       Specimen records in specimens table
STEP 3  Record observations     Artifact_observations per specimen × variable
STEP 4  Aggregate observations  Corpus-level summary per evidence variable
STEP 5  Score hdm_scores        Agreement of corpus observations with hpm
STEP 6  Rank hypotheses         Sum scores; sensitivity analysis; output
```

Each step depends on the previous one. Steps 1 and 2 are independent and
can proceed in parallel.

---

## 6. Step 1 — Hypothesis Prediction Matrix (HPM)

### Purpose

The HPM encodes the **prior expectation** for each evidence variable if a
given hypothesis is correct. It is filled in once, before artifact data is
examined, and must not be revised in response to artifact observations.

### Table

`hpm(hypothesis_id, ev_id, prediction, rationale)`

### Rating scale

| Symbol | Meaning                                           |
| ------ | ------------------------------------------------- |
| `++`   | Strongly expected if hypothesis is true           |
| `+`    | Expected if hypothesis is true                    |
| `0`    | Neutral — non-discriminatory for this variable    |
| `-`    | Unlikely if hypothesis is true                    |
| `--`   | Strongly contradictory — would falsify hypothesis |

### Status

The HPM is seeded with 320 entries (8 hypotheses × 40 variables) in
`rdorp.sqlite`. Review and revise entries before proceeding to Step 5.

---

## 7. Step 2 — Specimen Collection

### Purpose

Each artifact receives one row in the `specimens` table.

### Minimum required fields

- `rd_id` (permanent identifier, format `RD-0001`)
- `findspot`
- `country`
- `primary_source_id`
- `confidence` (A–E per RDORP source evaluation scale)

### Source priority

| Grade | Source type                                      |
| ----- | ------------------------------------------------ |
| A     | Direct archaeological measurement from excavation |
| B     | Museum documentation or authoritative catalogue  |
| C     | Peer-reviewed secondary publication              |
| D     | Estimated from published photographs or drawings |
| E     | Unverified claim                                 |

Unknown values are left NULL. Never estimate or infer measurements.

---

## 8. Step 3 — Artifact Observations

### Purpose

For each specimen × evidence variable combination where data exists, record
one row in `artifact_observations`.

### Table

```
artifact_observations(
    observation_id,   -- autoincrement
    rd_id,            -- foreign key to specimens
    ev_id,            -- foreign key to evidence_variables
    observed_value,   -- text; include units where applicable
    confidence,       -- A–E
    source_id,        -- foreign key to sources
    page,
    figure,
    extraction_date,
    notes
)
```

### Rules

- One row per specimen × variable × source.
- If two sources disagree, preserve both as separate rows.
- Never overwrite an existing observation. Add a new row and note the conflict.
- `observed_value` must reflect what the source states, not an interpretation.

---

## 9. Step 4 - Corpus-Level Aggregation

Before scoring, observations are aggregated across all specimens for each
evidence variable and stored as one row in `corpus_observations`.

```
corpus_observations(
    ev_id,            -- primary key; one row per evidence variable
    statement,        -- the sourced fact, in the source's own terms
    direction,        -- this project's classification of that fact
    confidence,       -- A-E, quality of the underlying evidence
    evidence_class,   -- Observed | Derived | Experimental
    discriminating,   -- 0 if the HPM prediction cannot be tested by it
    source_id, page, figure, extraction_date, notes
)
```

Two rules govern this table.

**Nothing is scored without a row here.** `hdm_scores` is built only from
`corpus_observations`, and `database/validate.py` raises an error if a score
exists without one. Before v0.2.0 the scoring input was a dictionary inside the
scoring script, carrying no source references and open to no audit.

**`statement` is evidence; `direction` is judgement.** The statement records
what a source says. The direction records how this project reads that statement
against the HPM prediction. They sit in separate columns so that a reader can
accept the evidence and reject the reading.

### Direction scale

| Direction        | Factor | Meaning                                             |
| ---------------- | ------ | --------------------------------------------------- |
| `confirmed`      | +1.0   | The predicted property holds as a corpus-wide rule  |
| `weak_confirmed` | +0.5   | It holds, but only in a minority of cases           |
| `ambiguous`      |  0.0   | Evidence exists but does not decide                 |
| `weak_absent`    | -0.5   | It fails as a general rule but holds in some cases  |
| `absent`         | -1.0   | The predicted property is not present               |

The two half-weight levels were added in v0.2.0. Before then any partial result
collapsed to `ambiguous` and scored zero, which discarded real information: a
property present in a fifth of the corpus is not the same as no evidence.

### Non-discriminating variables

`discriminating = 0` marks a variable for which corpus evidence exists but the
HPM predictions are not specific enough to be confirmed or refuted by it. The
clearest case is EV025 Site type. It is the best-quantified variable in the
corpus, yet seven of the eight hypotheses predict a bare `+` without naming
which site type they expect, so no distribution can test them.

Such variables score 0 and are reported as **HPM specification defects**, not as
evidence gaps. The distinction matters: an evidence gap is closed by collecting
data, an HPM defect is closed by respecifying a prediction - and that
respecification **must be written without reference to the observation that
exposed it**, or the matrix is being tuned to the data after the fact.

### Per-cell readings

`discriminating` is a property of a variable, shared by every hypothesis. That
is right where the evidence means the same thing whoever is asking - wear is
either there or it is not. It is wrong for distribution variables, where the
same distribution confirms one hypothesis and refutes another: a corpus that is
four-fifths civilian refutes a hypothesis that predicted military dominance and
says nothing about one that predicted nothing.

`hpm_readings(hypothesis_id, ev_id, direction, rationale)` records how a
*specific* prediction reads against such evidence. A cell with a reading is
scored using it; a cell without falls back to the shared direction and scores
zero where the variable is non-discriminating.

Two rules apply.

1. **A reading may only be written from a prediction that was specified
   independently of the observation**, and the rationale must record the basis.
   Without that constraint this table is a mechanism for retrofitting.
2. **Readings make the test harsher for the hypothesis that carries them**, by
   exposing it to variables its rivals are not exposed to. That is the intended
   behaviour, not a bias: a hypothesis that says what it expects can be wrong,
   and the predictive-commitment figures record how much it staked. The
   `same_footing` scenario re-runs the comparison with all readings ignored, and
   any conclusion must hold in both.

---

## 10. Step 5 - HDM Scoring

### Table

```
hdm_scores(hypothesis_id, ev_id, score, confidence,
           dp_weight, conf_weight, class_weight, weighted_score, notes)
```

### Scoring rule

```
score          = PRED_NUM(prediction) x DIRECTION_FACTOR(direction)
weighted_score = score x dp_weight x conf_weight x class_weight
```

where `PRED_NUM` maps `++ + 0 - --` to `+2 +1 0 -1 -2`.

`score` is the pure prediction-versus-observation value in the range -2 to +2
and nothing else is folded into it. Each weight occupies its own column so that
any of them can be inspected, recomputed, or disagreed with. Before v0.2.0 the
stored `score` had the confidence multiplier already applied, which made it
incomparable with the scale documented here.

### Weights

| Weight | Source | Values |
| ------ | ------ | ------ |
| `dp_weight` | `evidence_variables.discriminatory_power` | Very High 3, High 2, Medium 1 |
| `conf_weight` | `corpus_observations.confidence` | A 1.0, B 0.9, C 0.75, D 0.5, E 0.25 |
| `class_weight` | `corpus_observations.evidence_class` | Observed 1.0, Experimental 0.75, Derived 0.5 |

`class_weight` exists because one group of evidence variables - the engineering
assessments EV033 to EV036 - are not observations of artefacts at all. They are
this project's own reasoning about published measurements. Scoring them
alongside excavation records allowed the project's own inferences to carry the
ranking. They are now discounted by half and excluded entirely from the
observed-only scenario.

A and B no longer share a weight. Before v0.2.0 both were 1.0, so an archival
record and a museum record could not be told apart.

---

## 11. Step 6 - Hypothesis Ranking

### Score

S(H_i) = sum over j of weighted_score(H_i, EV_j), taken over the variables that
have a discriminating corpus observation.

### Predictive commitment

A total score alone is misleading. A hypothesis that predicts `0` for most
variables stakes nothing, yet still collects points whenever something it marked
`-` turns out to be absent. Ranking on totals therefore rewards hypotheses that
commit to little.

Each hypothesis is reported with:

- `predictions_made` - non-neutral predictions among the scored variables
- `strong_predictions` - how many of those are `++` or `--`
- `max_possible` - the score it would have obtained had every prediction been
  confirmed
- the fraction of `max_possible` actually achieved

**A ranking must never be quoted without these figures.** "Leads on total score"
and "accounts for the evidence" are different claims, and only the second is
supported by a high achieved fraction on a large stake.

### Outputs

`results(hypothesis_id, scenario, raw_score, weighted_score, rank,
scored_variables, evidence_gaps, worst_case, best_case, robust, notes)`

### Sensitivity analysis

Required before any ranking is published, and generated in full by
`database/score_hdm.py`.

1. **Scenarios.** Baseline; observed-only, with Derived evidence excluded;
   high-confidence only, with D and E excluded; Very High power variables only;
   unweighted; and same-footing, with all per-cell readings ignored. The leader
   must hold across all of them.
2. **Leave-one-variable-out.** Each scored variable is removed in turn and the
   ranking recomputed.
3. **HPM perturbation.** Every scored prediction is shifted by one level in each
   direction and the effect on the top position recorded. Shifts that cannot
   move, because the prediction already sits at the end of the scale, are
   **skipped rather than counted as stability**. The v0.1.0 implementation
   mapped `++` upwards onto `++` and reported the resulting no-op as evidence
   that the ranking was robust.
4. **Uncertainty bounds.** Best and worst case over the unscored variables. A
   hypothesis is marked `robust` only if its worst case still exceeds the best
   case of its strongest rival.
5. **Separation.** The margin between first and second place is compared with
   the largest single-variable contribution anywhere in the matrix. If one
   variable outweighs the gap, the top two are reported as a tied leading pair
   rather than as first and second.

## 11a. Pre-registered predictions

A guess written down before the data exists is a test; the same guess written
down afterwards is a story. The `predictions` table keeps the difference on the
record.

```
predictions(prediction_id, ev_id, hypothesis_ids, registered_on,
            predicted, falsified_if, method, basis, confidence,
            status, outcome, resolved_on)
```

Rules.

1. **Predictions are never scored.** They are not evidence and never enter
   `hdm_scores`. When the measurement is made it becomes an ordinary sourced
   observation and the prediction is resolved against it.
2. **A prediction must state what would refute it.** `falsified_if` is
   mandatory, and a prediction that nothing could refute is not registered.
3. **A prediction must be resolved before its variable is used.**
   `validate.py` raises an error if a prediction is still `open` after its
   `ev_id` has acquired corpus evidence and been scored. This is the guard
   against a prediction quietly becoming the evidence that confirms it.
4. **Predictions should be registered against the hypotheses this project
   favours as well as against those it does not.** A prediction set that only
   ever supports the current leader tests nothing.

When a new evidence variable is created for a measurement not yet made, the HPM
predictions of the existing hypotheses for that variable **must be authored
before the measurement is read**. Existing hypotheses are otherwise left silent
on it, and silence scores zero, which is the honest default.

---

---

## 12. Evidence Gaps

Variables with NULL in `hdm_scores` represent evidence gaps. After initial
scoring, generate an ordered list of gaps weighted by:

1. Discriminatory power of the variable
2. Number of hypotheses it would distinguish

This list drives the priority for future data collection and experimental
archaeology (RDORP-007, RDORP-008).

---

## 13. Updating the Analysis

When new specimens or observations are added:

1. Insert rows into `specimens` and `artifact_observations`.
2. Re-run Step 4 (aggregation) for affected variables.
3. Re-run Step 5 (scoring) for affected hypothesis × variable pairs.
4. Re-run Step 6 (ranking).

Historical observations must never be deleted or overwritten.
Corrections are added as new rows with notes referencing the superseded entry.

---

## 14. Revision History

| Version | Date       | Description |
| ------- | ---------- | ----------- |
| 0.1.0   | 2026-08-07 | Initial analytical method definition. |
| 0.4.0   | 2026-08-08 | Added the `predictions` table and section 11a; added EV041 Knob wear and EV042 Microwear location; added H012. |
| 0.3.0   | 2026-08-08 | Added `hpm_readings` for per-cell readings of distribution variables, with the independence rule and the `same_footing` scenario that ignores them. Added H009. |
| 0.2.0   | 2026-08-07 | Corpus observations made an explicit, sourced table and the sole input to scoring. Direction scale extended with two half-weight levels. Non-discriminating variables separated from evidence gaps. Confidence removed from the stored `score` and split into named weight columns. Evidence-class weighting added. Predictive-commitment reporting made mandatory alongside any ranking. Sensitivity analysis extended with scenarios, leave-one-out, corrected HPM perturbation, and a separation test. |
