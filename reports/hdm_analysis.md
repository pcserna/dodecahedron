# Hypothesis Discrimination Analysis

| Field | Value |
| ----- | ----- |
| Document ID | RDORP-HDM |
| Generated | 2026-08-09 |
| Database | `database\rdorp.sqlite` |
| Generator | `database/reports.py` |

Generated file. Do not edit by hand: change the master data in `database/build_db.py` and re-run `python run_pipeline.py`.

## 1. What this report is

This report applies the method defined in RDORP-010 to the evidence currently in the database. It is a comparison of how well each hypothesis accounts for the evidence collected so far. It is **not** a conclusion about the function of Roman dodecahedra, and the corpus it rests on covers a minority of known specimens.

Variables scored: **32 of 48**. Variables with corpus evidence but non-specific predictions: **9**. Variables with no corpus evidence at all: **11**.

## 2. Ranking

Weighted score = prediction score x discriminatory power x source confidence x evidence class.

| Rank | Hypothesis | Name | Weighted | Unweighted | Predictions staked | Points at stake | Achieved |
| ---- | ---------- | ---- | -------- | ---------- | ------------------ | --------------- | -------- |
| 1 | H012 | Spool-knitting / cord-working frame (knob-based) | +24.0 | +15.5 | 19/32 (strong 3) | 35.8 | 67% |
| 2 | H014 | Wax bulla / seal former | +21.0 | +14.0 | 21/32 (strong 7) | 46.8 | 45% |
| 3 | H003 | Ritual object | +12.2 | +8.5 | 11/32 (strong 2) | 21.8 | 56% |
| 4 | H008 | Portable shrine component | +11.4 | +8.0 | 12/32 (strong 2) | 23.2 | 49% |
| 5 | H013 | Rope-laying top (rotated | +8.7 | +9.0 | 23/32 (strong 8) | 53.3 | 16% |
| 6 | H002 | Rangefinder / measuring instrument | +3.5 | +1.5 | 20/32 (strong 8) | 50.6 | 7% |
| 7 | H001 | Structural connector / modular node | +2.3 | +6.0 | 28/32 (strong 12) | 68.2 | 3% |
| 8 | H005 | Textile / knitting tool | -0.2 | +2.0 | 18/32 (strong 3) | 39.4 | -0% |
| 9 | H006 | Astronomical instrument | -0.5 | +0.0 | 17/32 (strong 7) | 42.5 | -1% |
| 10 | H004 | Candlestick / lamp support | -0.6 | +1.5 | 15/32 (strong 1) | 28.1 | -2% |
| 11 | H007 | Military equipment | -1.5 | -0.5 | 12/32 (strong 3) | 29.1 | -5% |
| 12 | H011 | Archery targeting / ranging aid | -8.8 | -4.0 | 23/32 (strong 14) | 68.0 | -13% |
| 13 | H010 | Parasol / umbrella crown fitting | -9.2 | -1.5 | 26/32 (strong 11) | 66.5 | -14% |
| 14 | H009 | Tent apex / crown fitting (mobile shelter node) | -34.0 | -14.0 | 25/32 (strong 20) | 77.8 | -44% |

### How to read the last three columns

A hypothesis that predicts `0` for most variables risks nothing, yet it still gains points whenever something it marked as unlikely turns out to be absent. Raw totals therefore reward hypotheses that commit to little. *Points at stake* is the score a hypothesis would have obtained if every one of its predictions had been confirmed; *achieved* is the fraction it actually obtained. The two readings must be taken together:

- **H012** leads on total score while staking only 35.8 points, of which it achieved 67 per cent. It is highly consistent with the evidence, but it is also the least testable hypothesis in the set.
- **H009** staked the most (77.8 points across 25 predictions, 20 of them strong) and achieved -44 per cent. It is the most testable hypothesis in the set and the evidence has gone against it.

## 3. Scored variables

| EV | Variable | Power | Class | Conf | Direction | H012 | H014 | H003 | H008 | H013 | H002 | H001 | H005 | H006 | H004 | H007 | H011 | H010 | H009 |
| -- | -------- | ----- | ----- | ---- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EV001 | Overall dimensions | High | Observed | B | confirmed | +1.8 | +1.8 | 0.0 | 0.0 | +1.8 | 0.0 | +1.8 | +1.8 | 0.0 | +1.8 | 0.0 | +1.8 | +1.8 | +1.8 |
| EV003 | Wall thickness | High | Observed | B | absent | +1.8 | +1.8 | 0.0 | 0.0 | +1.8 | 0.0 | -1.8 | 0.0 | 0.0 | 0.0 | -1.8 | +1.8 | +1.8 | -3.6 |
| EV004 | Hole diameter distribution | Very High | Observed | B | confirmed | +5.4 | +5.4 | 0.0 | 0.0 | +5.4 | +5.4 | +5.4 | +5.4 | +2.7 | -2.7 | 0.0 | +5.4 | -5.4 | -2.7 |
| EV005 | Opposite-hole relationships | Very High | Observed | B | weak_absent | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -1.4 | -2.7 | -1.4 | -1.4 | +1.4 | 0.0 | -2.7 | -2.7 | -1.4 |
| EV006 | Hole profile | High | Observed | B | confirmed | +1.8 | +1.8 | 0.0 | 0.0 | +3.6 | +3.6 | +3.6 | +1.8 | +1.8 | +1.8 | 0.0 | +3.6 | +3.6 | +3.6 |
| EV008 | Knob diameter | Medium | Observed | B | confirmed | +1.8 | +1.8 | +0.9 | +0.9 | +1.8 | 0.0 | +1.8 | +0.9 | 0.0 | +0.9 | 0.0 | +0.9 | -0.9 | 0.0 |
| EV009 | Knob symmetry | Medium | Observed | B | confirmed | +1.8 | +1.8 | +0.9 | +0.9 | +1.8 | +0.9 | +1.8 | 0.0 | +1.8 | +0.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| EV010 | Face symmetry | High | Observed | B | absent | 0.0 | -1.8 | 0.0 | 0.0 | -1.8 | -3.6 | -1.8 | 0.0 | -3.6 | 0.0 | 0.0 | -3.6 | -3.6 | -3.6 |
| EV011 | Alloy composition | High | Observed | C | confirmed | 0.0 | 0.0 | +1.5 | +1.5 | 0.0 | 0.0 | +1.5 | 0.0 | 0.0 | 0.0 | +1.5 | 0.0 | 0.0 | +3.0 |
| EV012 | Casting quality | High | Observed | B | weak_confirmed | +0.9 | +0.9 | +0.9 | +0.9 | +0.9 | +1.8 | +0.9 | 0.0 | +1.8 | 0.0 | +0.9 | +1.8 | +0.9 | +0.9 |
| EV013 | Casting defects | High | Observed | B | confirmed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -3.6 | -1.8 | 0.0 | -3.6 | 0.0 | -1.8 | -3.6 | -1.8 | -3.6 |
| EV014 | Surface finishing | Medium | Observed | B | confirmed | +0.9 | +1.8 | +0.9 | +0.9 | +0.9 | +0.9 | 0.0 | +0.9 | +0.9 | 0.0 | 0.0 | +0.9 | +1.8 | 0.0 |
| EV016 | Tool marks | High | Observed | B | confirmed | +1.8 | +3.6 | 0.0 | 0.0 | +1.8 | +3.6 | +1.8 | 0.0 | +3.6 | 0.0 | 0.0 | +3.6 | +1.8 | 0.0 |
| EV017 | Internal hole wear | Very High | Observed | C | absent | +2.2 | +2.2 | +2.2 | +2.2 | -4.5 | -2.2 | -4.5 | -4.5 | 0.0 | -2.2 | 0.0 | +2.2 | -4.5 | -4.5 |
| EV018 | External wear | High | Observed | B | absent | -1.8 | -1.8 | +1.8 | +1.8 | -1.8 | 0.0 | -1.8 | -1.8 | 0.0 | 0.0 | -1.8 | -1.8 | -1.8 | -3.6 |
| EV019 | Rope wear | Very High | Observed | C | absent | 0.0 | 0.0 | 0.0 | 0.0 | -4.5 | +2.2 | -4.5 | -2.2 | +2.2 | 0.0 | 0.0 | -2.2 | -2.2 | -4.5 |
| EV020 | Rotational wear | Very High | Observed | C | absent | 0.0 | 0.0 | 0.0 | 0.0 | -4.5 | +2.2 | +2.2 | -2.2 | 0.0 | -2.2 | 0.0 | 0.0 | -2.2 | 0.0 |
| EV025 | Site type | Very High | Observed | B | ambiguous | +2.7 | +5.4 | 0.0 | 0.0 | +2.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -5.4 | +5.4 | -5.4 |
| EV026 | Roman province | Medium | Observed | B | ambiguous | +0.9 | +0.9 | 0.0 | 0.0 | +0.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -1.8 | -0.9 | -1.8 |
| EV027 | Associated finds | Very High | Observed | C | ambiguous | -2.2 | -4.5 | 0.0 | 0.0 | -2.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -4.5 | -4.5 | -4.5 |
| EV029 | Dating | Very High | Observed | B | ambiguous | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -2.7 |
| EV031 | Military association | High | Observed | B | weak_confirmed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | +0.9 | +0.9 | 0.0 | +0.9 | 0.0 | +1.8 | +1.8 | -1.8 | +1.8 |
| EV032 | Ritual association | High | Observed | C | weak_confirmed | -0.8 | -0.8 | +1.5 | +1.5 | -0.8 | -0.8 | -0.8 | -0.8 | 0.0 | +0.8 | 0.0 | -1.5 | 0.0 | -1.5 |
| EV033 | Rod compatibility | Very High | Derived | C | confirmed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | +1.1 | +2.2 | +1.1 | 0.0 | +1.1 | 0.0 | 0.0 | +2.2 | +2.2 |
| EV034 | Rope compatibility | Very High | Derived | C | confirmed | +1.1 | +1.1 | 0.0 | 0.0 | +2.2 | -1.1 | +2.2 | +1.1 | -1.1 | -1.1 | 0.0 | +1.1 | +1.1 | +2.2 |
| EV035 | Structural stability | Very High | Derived | C | weak_confirmed | +0.6 | +0.6 | 0.0 | 0.0 | +0.6 | 0.0 | +1.1 | 0.0 | 0.0 | +0.6 | 0.0 | 0.0 | +0.6 | +1.1 |
| EV036 | Load transfer | High | Derived | C | weak_confirmed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | +0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | +0.4 | +0.8 |
| EV037 | Assembly potential | High | Observed | B | absent | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | -3.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| EV038 | Orientation dependence | High | Observed | C | weak_absent | 0.0 | -0.8 | 0.0 | -0.8 | -0.8 | -1.5 | +0.8 | 0.0 | -1.5 | -1.5 | 0.0 | -1.5 | -1.5 | -1.5 |
| EV039 | Standardisation | High | Observed | B | absent | +1.8 | -1.8 | 0.0 | 0.0 | +1.8 | -3.6 | -1.8 | -1.8 | -3.6 | 0.0 | -1.8 | -3.6 | +1.8 | -3.6 |
| EV040 | Regional variation | High | Observed | C | confirmed | +1.5 | +1.5 | +1.5 | +1.5 | +1.5 | -1.5 | -1.5 | +1.5 | -1.5 | 0.0 | +1.5 | -1.5 | +1.5 | -3.0 |
| EV044 | Interior finish and marking | High | Observed | B | absent | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## 4. Sensitivity analysis

RDORP-010 section 11 requires that a hypothesis be considered robustly supported only if it ranks first across all reasonable scenarios.

| Scenario | Variables | Ranking |
| -------- | --------- | ------- |
| All corpus observations, fully weighted | 32 | H012 (+24.0)  >  H014 (+21.0)  >  H003 (+12.2)  >  H008 (+11.4) |
| Archaeological observations only (this project's derived engineering assessments excluded) | 28 | H012 (+22.4)  >  H014 (+19.3)  >  H003 (+12.2)  >  H008 (+11.4) |
| Confidence A-C only (low-confidence observations excluded) | 32 | H012 (+24.0)  >  H014 (+21.0)  >  H003 (+12.2)  >  H008 (+11.4) |
| Very High discriminatory-power variables only | 11 | H014 (+10.2)  >  H012 (+9.8)  >  H002 (+6.3)  >  H006 (+2.5) |
| Correlated variables share a budget: a cluster contributes its strongest cell, not the sum of its cells; a tie in magnitude is resolved against the hypothesis | 32 | H012 (+23.5)  >  H014 (+20.5)  >  H013 (+17.1)  >  H003 (+10.3) |
| As clustered, but a tie in magnitude is resolved in the hypothesis's favour - the upper bound of the clustering judgement | 32 | H014 (+24.1)  >  H012 (+23.5)  >  H013 (+17.1)  >  H003 (+10.3) |
| All corpus observations, no weighting applied | 32 | H012 (+15.5)  >  H014 (+14.0)  >  H013 (+9.0)  >  H003 (+8.5) |
| Corroborated variables only: at least two independent sources stand behind the observation | 25 | H012 (+22.4)  >  H014 (+20.1)  >  H013 (+15.6)  >  H003 (+12.2) |
| Per-cell readings ignored, so every hypothesis is judged only on the variables all of them can be judged on | 28 | H012 (+22.7)  >  H014 (+19.2)  >  H003 (+12.2)  >  H008 (+11.4) |

Leader across scenarios: **H012, H014** — NOT stable.

Margin between H012 and H014: **+3.0**, against a largest single-variable contribution anywhere in the matrix of 5.4. **H012 and H014 are not separated**: a single variable can carry more weight than the gap between them, so they must be reported as a tied leading pair rather than as first and second.

### Leave-one-variable-out

| EV | Variable | New leader |
| -- | -------- | ---------- |
| EV039 | Standardisation | H014 |

### Sensitivity to the prediction matrix

Every scored HPM prediction was shifted by one level in each direction. Shifts that cannot move, because the prediction is already at the end of the scale, are skipped rather than counted as evidence of stability.

No single-prediction change moves the top position.

### Sensitivity to the weighting scheme

The weights were chosen, not derived. Every combination of five discriminatory-power schemes, three source-confidence schemes and three evidence-class schemes was re-scored: 45 in all.

| Basis | Leader | Frequency | Margin over 2nd |
| ----- | ------ | --------- | --------------- |
| Unclustered | H012 | 45/45 (100%) | +0.9 to +6.5 |
| Clustered | H012 | 45/45 (100%) | +0.1 to +6.5 |

**The weighting scheme is not what decides the result.**
Unclustered, **H012 leads under all 45 combinations**, by +0.9 to +6.5.
Clustered, **H012 leads under all 45 combinations**, by +0.1 to +6.5.

Where clustering is applied, note that the **tie rule** is a separate judgement from the weights: six hypothesis/cluster pairs hold two cells of equal magnitude and opposite sign, and the `clustered_favourable` scenario above is the upper bound of that judgement. See RDORP-013 item A16.

### Uncertainty bounds over unscored variables

Best case assumes every unscored variable resolves in a hypothesis's favour; worst case assumes every one resolves against it. A hypothesis is robust only if its worst case still beats the best case of its strongest rival.

| Hypothesis | Current | Worst case | Best case | Robust |
| ---------- | ------- | ---------- | --------- | ------ |
| H012 | +24.0 | +6.8 | +41.3 | no |
| H014 | +21.0 | +10.5 | +31.5 | no |
| H003 | +12.2 | +5.4 | +18.9 | no |
| H008 | +11.4 | +4.7 | +18.1 | no |
| H013 | +8.7 | -8.6 | +25.9 | no |
| H002 | +3.5 | -4.0 | +11.0 | no |
| H001 | +2.3 | -6.7 | +11.3 | no |
| H005 | -0.2 | -10.7 | +10.3 | no |
| H006 | -0.5 | -6.5 | +5.5 | no |
| H004 | -0.6 | -10.4 | +9.1 | no |
| H007 | -1.5 | -6.8 | +3.8 | no |
| H011 | -8.8 | -22.3 | +4.7 | no |
| H010 | -9.2 | -19.7 | +1.3 | no |
| H009 | -34.0 | -41.5 | -26.5 | no |

## 4b. The evidence profile — what any correct hypothesis must predict

The scoring can be inverted. For each scored variable the optimal prediction is fixed by the observed direction: `++` where something is present, `--` where it is absent. The result is a portrait of the artefact class, stated as requirements.

A hypothesis matching this profile exactly would score **+82.0**. The best hypothesis actually on the table scores +24.0, which is 29 per cent of it.

> **This profile is not a hypothesis and must never be scored as one.** A prediction set reverse-engineered from it is fitted to the data by construction, and its score would measure nothing but the fitting. Its legitimate uses are as a description of what has to be explained, and as a checklist to examine a hypothesis against *before* scoring it.

| EV | Variable | Power | Observed | Must predict | Worth |
| -- | -------- | ----- | -------- | ------------ | ----- |
| EV004 | Hole diameter distribution | Very High | confirmed | `++` | +5.4 |
| EV017 | Internal hole wear | Very High | absent | `--` | +4.5 |
| EV019 | Rope wear | Very High | absent | `--` | +4.5 |
| EV020 | Rotational wear | Very High | absent | `--` | +4.5 |
| EV001 | Overall dimensions | High | confirmed | `++` | +3.6 |
| EV003 | Wall thickness | High | absent | `--` | +3.6 |
| EV006 | Hole profile | High | confirmed | `++` | +3.6 |
| EV010 | Face symmetry | High | absent | `--` | +3.6 |
| EV013 | Casting defects | High | confirmed | `++` | +3.6 |
| EV016 | Tool marks | High | confirmed | `++` | +3.6 |
| EV018 | External wear | High | absent | `--` | +3.6 |
| EV037 | Assembly potential | High | absent | `--` | +3.6 |
| EV039 | Standardisation | High | absent | `--` | +3.6 |
| EV044 | Interior finish and marking | High | absent | `--` | +3.6 |
| EV011 | Alloy composition | High | confirmed | `++` | +3.0 |
| EV040 | Regional variation | High | confirmed | `++` | +3.0 |
| EV005 | Opposite-hole relationships | Very High | weak_absent | `--` | +2.7 |
| EV033 | Rod compatibility | Very High | confirmed | `++` | +2.2 |
| EV034 | Rope compatibility | Very High | confirmed | `++` | +2.2 |
| EV008 | Knob diameter | Medium | confirmed | `++` | +1.8 |
| EV009 | Knob symmetry | Medium | confirmed | `++` | +1.8 |
| EV012 | Casting quality | High | weak_confirmed | `++` | +1.8 |
| EV014 | Surface finishing | Medium | confirmed | `++` | +1.8 |
| EV031 | Military association | High | weak_confirmed | `++` | +1.8 |
| EV032 | Ritual association | High | weak_confirmed | `++` | +1.5 |
| EV038 | Orientation dependence | High | weak_absent | `--` | +1.5 |
| EV035 | Structural stability | Very High | weak_confirmed | `++` | +1.1 |
| EV036 | Load transfer | High | weak_confirmed | `++` | +0.8 |

### How far each hypothesis already agrees

Counted over the profile requirements only, by sign of the prediction.

| Hypothesis | Agrees | Disagrees | Silent |
| ---------- | ------ | --------- | ------ |
| H001 Structural connector / modular node | 15 | 11 | 2 |
| H012 Spool-knitting / cord-working frame (knob-based) | 14 | 2 | 12 |
| H014 Wax bulla / seal former | 13 | 5 | 10 |
| H013 Rope-laying top (rotated | 13 | 7 | 8 |
| H010 Parasol / umbrella crown fitting | 12 | 11 | 5 |
| H011 Archery targeting / ranging aid | 11 | 9 | 8 |
| H002 Rangefinder / measuring instrument | 10 | 9 | 9 |
| H003 Ritual object | 9 | 0 | 19 |
| H008 Portable shrine component | 9 | 1 | 18 |
| H009 Tent apex / crown fitting (mobile shelter node) | 9 | 12 | 7 |
| H004 Candlestick / lamp support | 8 | 5 | 15 |
| H005 Textile / knitting tool | 8 | 7 | 13 |
| H006 Astronomical instrument | 8 | 7 | 13 |
| H007 Military equipment | 4 | 4 | 20 |

A hypothesis with many disagreements is engaged and wrong; one with many silences is unengaged, and its low disagreement count is not a virtue. Neither pattern is success.

## 4b2. Screening of candidate functional domains

Authoring a full 42-variable prediction matrix for every idea is expensive and, once the evidence is known, increasingly contaminated. A screen is cheaper and more honest: it records only the predictions a domain **cannot avoid** — those that follow from the mechanism whether the proposer likes them or not — and checks those against the corpus.

A candidate is **eliminated** when the corpus contradicts, at full strength, a prediction it had to make on a Very High or High power variable. Surviving a screen is not support; it means the domain is worth the cost of a full prediction matrix.

| ID | Candidate | Domain | Would produce | Screen | Hard contradictions | Verdict |
| -- | --------- | ------ | ------------- | ------ | ------------------- | ------- |
| C-12 | Soft-material forming and handling tool | Craft | Formed pieces of leather, wax, foil or soft metal | +29.4 | 1 | **ELIMINATED** |
| C-13 | Garment or tailoring size gauge | Craft / Textile | Garment parts made to a repeatable size | +11.8 | 3 | **ELIMINATED** |
| C-10 | Wax bulla or seal former | Administrative | Standardised wax bullae securing cords on documents | +8.5 | 2 | **ELIMINATED** |
| C-15 | Suspended solar altitude sight | Astronomical | A reading of solar altitude, and hence of the date | -1.8 | 3 | **ELIMINATED** |
| C-14 | Zodiac sundial by internal light projection | Astronomical | A reading of the date or zodiac sign | -1.9 | 5 | **ELIMINATED** |
| C-09 | Byre or beehive fumigation holder | Animal husbandry | Smoke | -4.2 | 2 | **ELIMINATED** |
| C-17 | Levelling sight for water engineering | Engineering / Surveying | A levelled line or a set gradient | -7.6 | 4 | **ELIMINATED** |
| C-11 | Knob-based dividers or angle gauge | Metrology / Surveying | Marked-out distances and angles | -8.6 | 4 | **ELIMINATED** |
| C-06 | Seed-sowing or dibbing gauge | Farming | Evenly spaced sowing | -16.2 | 4 | **ELIMINATED** |
| C-08 | Tether or hobble ring | Animal husbandry | — | -16.9 | 4 | **ELIMINATED** |
| C-05 | Volumetric grain or liquid measure | Farming / Commerce | A measured quantity of grain, seed or liquid | -18.0 | 4 | **ELIMINATED** |
| C-04 | Rigging fairlead or lead block | Maritime | — | -19.1 | 4 | **ELIMINATED** |
| C-07 | Livestock bell or rattle | Animal husbandry | Sound | -19.5 | 5 | **ELIMINATED** |
| C-03 | Net-making mesh gauge | Maritime | Fishing or fowling net of standard mesh | -19.8 | 4 | **ELIMINATED** |
| C-02 | Harness or yoke junction fitting | Military / Farming | — | -25.0 | 6 | **ELIMINATED** |
| C-01 | Artillery shot gauge | Military | Calibrated ammunition of consistent weight | -27.0 | 6 | **ELIMINATED** |

### Where each candidate fails

- **C-12 Soft-material forming and handling tool** — EV027 Associated finds (predicted `++`, observed absent, -4.5)
  - Untested predictions that would decide it: EV024 (`++`)
- **C-13 Garment or tailoring size gauge** — EV027 Associated finds (predicted `++`, observed absent, -4.5); EV013 Casting defects (predicted `-`, observed confirmed, -1.8); EV039 Standardisation (predicted `+`, observed absent, -1.8)
  - Untested predictions that would decide it: EV007 (`++`), EV024 (`+`)
- **C-10 Wax bulla or seal former** — EV027 Associated finds (predicted `++`, observed absent, -4.5); EV039 Standardisation (predicted `+`, observed absent, -1.8)
  - Untested predictions that would decide it: EV023 (`-`), EV024 (`++`)
- **C-15 Suspended solar altitude sight** — EV019 Rope wear (predicted `++`, observed absent, -4.5); EV027 Associated finds (predicted `++`, observed absent, -4.5); EV010 Face symmetry (predicted `++`, observed absent, -3.6)
  - Untested predictions that would decide it: EV041 (`++`)
- **C-14 Zodiac sundial by internal light projection** — EV027 Associated finds (predicted `++`, observed absent, -4.5); EV010 Face symmetry (predicted `++`, observed absent, -3.6); EV039 Standardisation (predicted `++`, observed absent, -3.6)
- **C-09 Byre or beehive fumigation holder** — EV025 Site type (predicted `++`, observed absent, -5.4); EV018 External wear (predicted `+`, observed absent, -1.8)
  - Untested predictions that would decide it: EV023 (`++`), EV024 (`++`)
- **C-17 Levelling sight for water engineering** — EV019 Rope wear (predicted `++`, observed absent, -4.5); EV027 Associated finds (predicted `++`, observed absent, -4.5); EV010 Face symmetry (predicted `++`, observed absent, -3.6)
- **C-11 Knob-based dividers or angle gauge** — EV027 Associated finds (predicted `++`, observed absent, -4.5); EV010 Face symmetry (predicted `++`, observed absent, -3.6); EV013 Casting defects (predicted `--`, observed confirmed, -3.6)
- **C-06 Seed-sowing or dibbing gauge** — EV025 Site type (predicted `++`, observed absent, -5.4); EV003 Wall thickness (predicted `++`, observed absent, -3.6); EV018 External wear (predicted `++`, observed absent, -3.6)
  - Untested predictions that would decide it: EV021 (`++`)
- **C-08 Tether or hobble ring** — EV025 Site type (predicted `++`, observed absent, -5.4); EV017 Internal hole wear (predicted `++`, observed absent, -4.5); EV019 Rope wear (predicted `++`, observed absent, -4.5)
- **C-05 Volumetric grain or liquid measure** — EV004 Hole diameter distribution (predicted `--`, observed confirmed, -5.4); EV010 Face symmetry (predicted `++`, observed absent, -3.6); EV013 Casting defects (predicted `--`, observed confirmed, -3.6)
- **C-04 Rigging fairlead or lead block** — EV025 Site type (predicted `++`, observed absent, -5.4); EV017 Internal hole wear (predicted `++`, observed absent, -4.5); EV019 Rope wear (predicted `++`, observed absent, -4.5)
- **C-07 Livestock bell or rattle** — EV025 Site type (predicted `++`, observed absent, -5.4); EV017 Internal hole wear (predicted `++`, observed absent, -4.5); EV019 Rope wear (predicted `++`, observed absent, -4.5)
  - Untested predictions that would decide it: EV021 (`++`)
- **C-03 Net-making mesh gauge** — EV025 Site type (predicted `++`, observed absent, -5.4); EV019 Rope wear (predicted `++`, observed absent, -4.5); EV027 Associated finds (predicted `++`, observed absent, -4.5)
  - Untested predictions that would decide it: EV041 (`++`)
- **C-02 Harness or yoke junction fitting** — EV025 Site type (predicted `++`, observed absent, -5.4); EV017 Internal hole wear (predicted `++`, observed absent, -4.5); EV019 Rope wear (predicted `++`, observed absent, -4.5)
- **C-01 Artillery shot gauge** — EV025 Site type (predicted `++`, observed absent, -5.4); EV017 Internal hole wear (predicted `++`, observed absent, -4.5); EV027 Associated finds (predicted `++`, observed absent, -4.5)

## 4b3. Usage value: was the function worth having?

Evidential fit and worth are different questions. A hypothesis can agree with every observation and still be implausible, because nobody casts difficult bronze for two centuries to obtain what a stick would give them. Worth is recorded in three kinds, because the corpus discriminates sharply between them.

**Product** is the value of the material output *net of the cheapest substitute* (−2 to +2). **Craft** is whether the difficulty and cost of making it are part of its worth (0 to 2). **Experience** is whether using it delivers something valued in itself, rather than through an output (0 to 2).

> **None of this enters `hdm_scores`.** Folding a judgement about worth into the evidence score would let opinion masquerade as evidence. It is a separate axis, reported beside the evidential one.

| Subject | Product (net of substitute) | Craft | Experience | Cheapest substitute |
| ------- | --------------------------- | ----- | ---------- | ------------------- |
| **H003** Symbolic or ritual efficacy, and standing | +2 | 2 | 2 | None: the object IS the product |
| **H008** A focus for domestic or personal cult | +2 | 2 | 2 | None: the object IS the product |
| **C-16** The making itself: a demonstration of mastery, and a | +0 | 2 | 2 | None: no cheaper object demonstrates the same master |
| **H014** Standardised wax sealings for documents | +0 | 1 | 1 | A simple mould, or forming the wax freehand |
| **C-12** Formed leather, wax, foil or soft metal | +0 | 1 | 0 | Wooden or bone formers, and simple moulds |
| **H010** Shade or rain cover | -1 | 0 | 1 | A turned wooden crown |
| **C-13** Garment parts made to a repeatable size | -1 | 0 | 0 | A knotted cord or a marked stick, effectively free |
| **C-14** A reading of the date or zodiac sign | -2 | 0 | 1 | Sundials, surviving in their hundreds and described  |
| **C-15** A reading of solar altitude, hence the season | -2 | 0 | 1 | Sundials, the public fasti, and the agricultural cal |
| **H001** A modular structure assembled from rods | -1 | 0 | 0 | Carpentry joints and iron fittings, cheaper and far  |
| **H004** Light | -2 | 0 | 1 | A pottery lamp, near-free and in every house |
| **H005** Looped or knitted fabric | -1 | 0 | 0 | A wooden or bone spool, effectively free |
| **H006** Celestial measurement | -2 | 0 | 1 | Documented instruments; and see EXP-0002 and EXP-000 |
| **H007** Unspecified military function | -1 | 0 | 0 | Unclear, because the product is unclear |
| **H012** Looped cord tubes, gloves or hose | -1 | 0 | 0 | A wooden or bone spool, effectively free |
| **H013** Laid cord or rope | -1 | 0 | 0 | Hand-laying, or a wooden laying top |
| **H002** An estimate of distance | -2 | 0 | 0 | The groma and the dioptra, both documented, plus tra |
| **H009** A pitched shelter | -2 | 0 | 0 | Rope lashing or a turned wooden hub, trivially cheap |
| **H011** A range estimate for shooting | -2 | 0 | 0 | Trained instinct, which is how archers actually shoo |

The axis separates the field cleanly. **Every reading in which the object makes something scores negative on product**, because a cheaper substitute existed in every case: a wooden spool, a pottery lamp, a knotted cord, a groma, a sundial. **Only the readings in which the making and the holding are themselves the point score positive on all three.** For those, the expense is functional rather than anomalous, and the absence of standardisation is what individual commissioning looks like rather than a defect.

That asymmetry is a result, not an assumption. It was not put into the evidence and cannot be taken out of it: it follows from the objects being costly, difficult, finely finished, individually varied and unworn.

## 4c. Pre-registered predictions

Guesses recorded before the measurements exist, so that the difference between a test and a story is on the record. **These are not evidence and are never scored.** When a measurement is made it becomes an ordinary sourced observation and the prediction is resolved against it.

| ID | Variable | Bears on | Registered | Prediction | Refuted if |
| -- | -------- | -------- | ---------- | ---------- | ---------- |
| P-0001 | EV041 Knob wear | H012; H005 | 2026-08-08 | NEGATIVE. Examination of the knobs and knob necks of well-preserved specimens will NOT show directional use-polish or grooving. Any abrasion found will be non-directional | Refuted if directional polish or grooving is found running over the knob and down the neck, in the same orientation on the five knobs around one or more faces, on an obje |
| P-0002 | EV024 Residues | H003; H004; H008; H012 | 2026-08-08 | POSITIVE IN A MINORITY. Organic residues will be recoverable from the interior and from the aperture rims of a minority of well-preserved, unconserved specimens. | Refuted if a systematic study of several well-preserved specimens recovers no organic residue at all. |
| P-0003 | EV023 Thermal alteration | H004; H003 | 2026-08-08 | NEGATIVE. No soot, scorching or heat alteration will be found on the interior of specimens. | Refuted if soot or thermal alteration is found on the interior of any well-preserved specimen. |
| P-0004 | EV042 Microwear location | H001; H005; H011; H012 | 2026-08-08 | RIM, NOT BORE. Microwear analysis will find, at most, light contact wear on the outer lip of the apertures, and will NOT find wear inside the bores. | Refuted if bore wear is found. Bore wear would revive H001 and H005 directly and would falsify the reading of the object as something that held contents rather than passe |
| P-0005 | EV007 Hole edge radius | H005; H012; H011 | 2026-08-08 | BEVELLED. Aperture lips will prove to be bevelled or rounded rather than square-cut, across most of the corpus. | Refuted if lips are predominantly square-cut and sharp, which would favour the optical reading (H011) over the cord-work reading (H012). |
| P-0006 | EV015 Repair evidence | All | 2026-08-08 | RARE. Ancient repairs will prove rare across the corpus. | Refuted if a systematic survey finds ancient repairs on a substantial share of specimens, which would imply real working use and would revive the tool hypotheses generall |
| P-0007 | EV030 Number at site | H001; H009; H011 | 2026-08-08 | SINGLETONS. Sites will overwhelmingly yield one dodecahedron each. | Refuted if several sites yield multiple specimens, which would revive H001 (a system using many nodes) and H009 (a camp holding many tents) at once. |
| P-0008 | EV021 Impact damage | All | 2026-08-08 | POST-DEPOSITIONAL. Impact damage, where present, will correlate with agricultural disturbance rather than with use. | Refuted if impact damage clusters on functionally significant surfaces such as aperture rims or knob crowns on stratified specimens. |
| P-0009 | EV043 Aperture distinguishability | H003; H008 | 2026-08-08 | DISTINGUISHABLE. On complete, well-preserved specimens, every aperture will prove distinguishable from every other on the same object, by diameter or by the number of eng | Refuted if complete specimens are found on which two or more apertures are indistinguishable by both diameter and ring count. Already partly refuted by RD-0035, where thr |
| P-0010 | EV045 Manufacturing difficulty | H003; H008; C-16 | 2026-08-08 | DIFFICULT. Attempts to reproduce a dodecahedron by lost-wax casting to the standard of the better specimens will prove demanding, with a substantial failure rate, and wil | Refuted if experimental casting shows the form to be routine for a competent Roman founder. That would remove the foundation of the craft-value reading (C-16) and of the  |
| P-0011 | EV048 Within-type standardisation | H002; H006; H011; C-01; C-03; C-05; C-13 | 2026-08-08 | NO BETTER WITHIN TYPE. Standardisation measured within a single Greiner/Guggenberger type will prove no better than standardisation measured across the pooled corpus. The | Refuted if specimens of one type prove substantially more uniform in overall diameter, aperture set or wall thickness than the corpus as a whole. That would mean the pool |

## 5. Variables that cannot yet be scored

### Corpus evidence exists, but the prediction matrix is not specific enough

These are defects in the HPM, not gaps in the evidence. They must be repaired by respecifying the prediction *without reference to the observations below*, otherwise the matrix is being tuned to the data.

| EV | Variable | Power | Corpus evidence held |
| -- | -------- | ----- | -------------------- |
| EV002 | Mass | High | The reference catalogue gives the corpus weight range as 35-580 g, with one specimen over 1000 g (PUB-0023). Complete specimens in this database fall ... |
| EV025 | Site type | Very High | Of the dodecahedra with a recorded find location: more than half come from cities or other settlements; just under one-fifth from military camps; c 8.... |
| EV026 | Roman province | Medium | c 70 per cent of finds come from the Gallic and Germanic provinces, especially the territory of the former Gallia Comata, and c 20 per cent from Brita... |
| EV027 | Associated finds | Very High | Documented associations include a bronze statuette of a goddess one metre away (Guggenberger no 110), a bronze statuette of Mercury as Hermes-Thoth in... |
| EV028 | Stratigraphy | High | Only one dodecahedron has ever been recovered from a sealed, dated, stratified deposit: RD-0020, from destruction layer F1058 of a small drystone buil... |
| EV029 | Dating | Very High | Dodecahedra were used from around AD 200 to the late fourth century AD; the stratified Jublains specimen was deposited in the first half of the 3rd ce... |
| EV046 | Marked axis | Very High | A single axis is marked out on the great majority of specimens, by the ABSENCE of decoration rather than its presence. The commonest type engraves cir... |
| EV047 | Authenticity and provenance security | Very High | No dodecahedron in this database has been authenticated by metallurgical or technical analysis against forgery, and none of the sources read raises th... |
| EV048 | Within-type standardisation | Very High | Type attributions are now known for the whole reference corpus: of 129 catalogued specimens, 82 are type 1a, 17 are untyped, 6 are 2a, 4 each are 3a a... |

### No corpus evidence at all

| EV | Variable | Power | Maximum effect on any hypothesis |
| -- | -------- | ----- | -------------------------------- |
| EV007 | Hole edge radius | Medium | +/- 1.5 |
| EV015 | Repair evidence | Medium | +/- 1.5 |
| EV021 | Impact damage | Medium | +/- 1.5 |
| EV022 | Abrasion | Medium | +/- 1.5 |
| EV023 | Thermal alteration | Very High | +/- 4.5 |
| EV024 | Residues | Very High | +/- 4.5 |
| EV030 | Number at site | Medium | +/- 1.5 |
| EV041 | Knob wear | Very High | +/- 4.5 |
| EV042 | Microwear location | Very High | +/- 4.5 |
| EV043 | Aperture distinguishability | Very High | +/- 4.5 |
| EV045 | Manufacturing difficulty | Very High | +/- 4.5 |

## 6. Stated limitations

1. The recorded corpus is a minority of the known corpus and is not drawn from it representatively. See `reports/corpus_coverage.md`.
2. Wear evidence is macroscopic. The source that supplies it states that microscopic wear analysis has not been carried out (PUB-0003, 52), so the absence of wear is an absence of *reported* wear.
3. Residue and thermal-alteration evidence is deliberately unscored. The only residue record in the corpus is described by its own source as possibly unreliable. Scoring these variables as absent would penalise the hypotheses they bear on using analyses that have never been run.
4. Most corpus-level statistics rest on one publication, PUB-0003, which in turn summarises an unpublished catalogue (PUB-0022) that this project has not consulted directly.
5. The direction assigned to each corpus observation is this project's judgement of a sourced fact, not an observation. Directions are stored in `corpus_observations` with their reasoning so that they can be challenged independently of the evidence.
