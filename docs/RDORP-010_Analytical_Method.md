---
Document ID: RDORP-010
Title: Analytical Method
Version: 0.1.0
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

| Dataset              | Table in rdorp.sqlite     | Purpose                                     |
| -------------------- | ------------------------- | ------------------------------------------- |
| Evidence variables   | `evidence_variables`      | What to observe on each specimen            |
| Prediction matrix    | `hpm`                     | What each hypothesis predicts we will find  |
| Observations         | `artifact_observations`   | What is actually observed                   |
| Discrimination matrix| `hdm_scores`              | How well each hypothesis explains the data  |

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

## 9. Step 4 — Corpus-Level Aggregation

Before scoring, aggregate observations across all specimens for each
evidence variable. This produces a **corpus summary** — a set of
empirical statements about the artifact population.

Example aggregation outputs:

| Variable                 | Corpus observation                                |
| ------------------------ | ------------------------------------------------- |
| EV004 Hole diameter dist | Hole diameters vary within specimens in N of M cases |
| EV023 Thermal alteration | Soot or wax residues present in N of M cases     |
| EV025 Site type          | Military: N%, Civilian: N%, Hoard: N%, Unknown: N% |

Aggregations are stored as evidence statements in `evidence_register` with
`evidence_type = 'Derived'`.

---

## 10. Step 5 — HDM Scoring

### Purpose

For each hypothesis × evidence variable pair, assign a score reflecting how
well the corpus observation agrees with the HPM prediction.

### Table

`hdm_scores(hypothesis_id, ev_id, score, confidence, notes)`

### Scoring rule

Compare the HPM prediction with the corpus observation:

| HPM prediction | Corpus agrees | Score |
| -------------- | ------------- | ----- |
| `++`           | Yes           | +2    |
| `++`           | No            | -2    |
| `+`            | Yes           | +1    |
| `+`            | No            | -1    |
| `0`            | Any           |  0    |
| `-`            | Absent        | +1    |
| `-`            | Present       | -1    |
| `--`           | Absent        | +2    |
| `--`           | Present       | -2    |

Confidence reflects the quality of the underlying evidence (A–E).

### Weighting (planned)

High-confidence observations may be weighted more heavily in the final
ranking. The weighting function will be defined in RDORP-011 when
sufficient data is available to calibrate it.

---

## 11. Step 6 — Hypothesis Ranking

### Raw score

$$
S(H_i) = \sum_{j=1}^{40} \text{hdm\_score}(H_i, EV_j)
$$

### Adjusted score (planned)

An adjusted score discounts scores derived from low-confidence observations
and applies discriminatory-power weights from `evidence_variables.discriminatory_power`.

### Outputs

Results are stored in the `results` table with columns:

- `hypothesis_id`
- `raw_score`
- `adjusted_score`
- `rank`
- `evidence_gaps` (count of NULL hdm_scores)
- `notes`

### Sensitivity analysis

Before publishing a ranking, a sensitivity analysis must assess how the
result changes when:

1. Low-confidence observations (D, E) are excluded.
2. Unscored variables (NULL) are assumed to be neutral (0) versus penalised (−1).
3. Individual high-weight variables are removed one at a time.

A hypothesis is only considered robustly supported if it ranks first across
all reasonable sensitivity scenarios.

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

| Version | Date       | Description                           |
| ------- | ---------- | ------------------------------------- |
| 0.1.0   | 2026-08-07 | Initial analytical method definition. |
