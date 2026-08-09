# Task prompt — blind specification of a full prediction matrix (RDORP-013 item A3, part 1)

**Run this in a fresh session, ideally with a different person or model from
the one that built the project.**

---

## Why this exists

Every prediction in this project was written by the same party that assigned
the directions, computed the scores and wrote the conclusions. There is no
independent specification and no second rater. **That is the central validity
threat to the whole method**, and nothing in the analysis addresses it.

Six of the fourteen hypotheses are additionally contaminated: they were
proposed *after* the evidence was known, so their predictions were written by
someone who already knew what they would be scored against.

You are the control. You will specify a matrix without seeing the evidence.
The disagreement rate between your matrix and the existing one is the number
this exercise exists to produce.

---

## Do not look these up

**Do not open, read, grep or query any of the following before you have
finished:**

- `docs/RDORP-012_Results_Summary.md` — states the results
- `docs/RDORP-013_Hardening_Plan.md`
- `reports/` — all four files
- the `corpus_observations`, `artifact_observations`, `hdm_scores`, `results`,
  `hpm`, `hpm_readings`, `screening`, `experiments` tables, or their CSVs
- `database/build_db.py`
- any web search about Roman dodecahedron findspots, wear, dating or
  distribution

You do not need the repository. Everything required is below.

If you already know facts about Roman dodecahedra, do not go looking for more,
and derive each prediction from the mechanism rather than from recall.

---

## Background

A Roman dodecahedron is a hollow cast copper-alloy object: twelve pentagonal
faces, one aperture in the centre of each face, a knob at each of the twenty
vertices. Roughly 130 are known from the north-western Roman provinces. No
surviving Roman text mentions them.

The project tests hypotheses by writing down, **in advance**, what each would
predict for 48 evidence variables, then comparing that against the corpus.

---

## Your assignment

Specify the **complete matrix** for **one** hypothesis, chosen from:

| ID | Name | Mechanism |
| -- | ---- | --------- |
| H001 | Structural connector / modular node | Rods seat in the apertures; several objects assemble into a larger frame |
| H002 | Rangefinder / measuring instrument | Sighted through opposed apertures to estimate distance |
| H003 | Ritual object | Symbolic or cultic object; the form itself carries the meaning |
| H012 | Spool-knitting / cord-working frame | Yarn looped over the knobs around one face; the worked tube emerges through that aperture |
| H014 | Wax bulla / seal former | Soft wax pressed in the object around a knotted cord to form a sealing; the knobs act as spacers limiting compression |

**H012 and H014 are the most valuable**, because they are the two currently
leading and both were specified after the evidence was known. **H003 is the
next most valuable**, because it is suspected of scoring well by predicting
almost nothing, and an independent specification would show whether that is
the hypothesis or the specifier.

If you have time for more than one, do them in separate passes and do not look
back at the first while writing the second.

---

## The prediction scale

| Symbol | Meaning |
| ------ | ------- |
| `++` | Strongly expected if the hypothesis is true |
| `+`  | Expected |
| `0`  | The mechanism is genuinely indifferent |
| `-`  | Unexpected |
| `--` | Strongly contrary; would count heavily against |

`0` is legitimate where a mechanism truly does not care. But `0` scores nothing
either way, so a matrix full of zeros describes an untestable hypothesis.
**Count your zeros at the end and report the number.**

---

## The 48 variables

| ID | Variable | Definition |
| -- | -------- | ---------- |
| EV001 | Overall dimensions | Overall height, width and bounding dimensions |
| EV002 | Mass | Artefact weight |
| EV003 | Wall thickness | Thickness of the cast shell |
| EV004 | Hole diameter distribution | Distribution of aperture diameters |
| EV005 | Opposite-hole relationships | Pairing and correspondence of opposite apertures |
| EV006 | Hole profile | Cross-sectional form of the apertures |
| EV007 | Hole edge radius | Chamfers and edge finishing |
| EV008 | Knob diameter | Size of the vertex knobs |
| EV009 | Knob symmetry | Regularity of knob placement |
| EV010 | Face symmetry | Deviation from regular geometry |
| EV011 | Alloy composition | Metallurgical composition |
| EV012 | Casting quality | Quality of the casting |
| EV013 | Casting defects | Voids, seams, miscasts |
| EV014 | Surface finishing | Decoration and surface treatment |
| EV015 | Repair evidence | Ancient repairs |
| EV016 | Tool marks | Secondary machining traces |
| EV017 | Internal hole wear | Wear inside the apertures |
| EV018 | External wear | Wear on external surfaces |
| EV019 | Rope wear | Grooves or polish from rope |
| EV020 | Rotational wear | Evidence of repeated rotation |
| EV021 | Impact damage | Chips, dents, breaks |
| EV022 | Abrasion | Abrasive surface loss |
| EV023 | Thermal alteration | Heat damage, soot, wax |
| EV024 | Residues | Organic or inorganic residues |
| EV025 | Site type | Military, villa, town, temple, etc. |
| EV026 | Roman province | Roman administrative region |
| EV027 | Associated finds | Objects found together |
| EV028 | Stratigraphy | Stratigraphic context |
| EV029 | Dating | Chronological range |
| EV030 | Number at site | Single or multiple specimens at one site |
| EV031 | Military association | Direct military evidence |
| EV032 | Ritual association | Direct ritual evidence |
| EV033 | Rod compatibility | Whether rods can be seated in the apertures |
| EV034 | Rope compatibility | Whether cord can be routed through or over |
| EV035 | Structural stability | Resistance to deformation under load |
| EV036 | Load transfer | Plausible force paths through the object |
| EV037 | Assembly potential | Whether several could combine into a larger structure |
| EV038 | Orientation dependence | Whether the function requires a fixed orientation |
| EV039 | Standardisation | Conformity to a metrological standard |
| EV040 | Regional variation | Geographic patterning in form |
| EV041 | Knob wear | Wear, polish or abrasion on the knobs and knob necks |
| EV042 | Microwear location | Microscopic wear inside the bore versus on the outer lip |
| EV043 | Aperture distinguishability | Whether every aperture on one object can be told from every other |
| EV044 | Interior finish and marking | Whether the interior is finished, marked or graduated |
| EV045 | Manufacturing difficulty | How hard the object was to produce |
| EV046 | Marked axis | Whether a visual marking singles out one axis or face |
| EV047 | Authenticity and provenance | Security of a specimen as an authentic ancient object |
| EV048 | Within-type standardisation | Whether one typological group is more uniform than the corpus |

---

## What to produce

For **every one of the 48 variables**: a symbol and a one-sentence
**mechanical reason** — why the mechanism requires it. Not "this seems
plausible", but a physical or behavioural consequence: *"poles are withdrawn
every time camp is struck, so the sockets must wear."*

### Constraints

- **Specify the hypothesis as its strongest proponent would.** You are not
  refuting it. A strawman matrix is worse than no matrix.
- Do not skip variables that feel irrelevant. Deciding they are irrelevant *is*
  the prediction — write `0` and say why.
- Where the mechanism implies a threshold or a named expectation, give it:
  a mass range, a site type, a period, an alloy.
- Work straight through EV001 to EV048 in order. Do not revise earlier entries
  after later ones suggest a pattern.

---

## Output format

```
# Blind prediction matrix — H0XX <name>
Specified by: <who / which model>
Date:
Consulted forbidden sources: yes / no

| EV | Prediction | Mechanical reason |
| -- | ---------- | ----------------- |
| EV001 | + | ... |
...
| EV048 | 0 | ... |

## Declaration
- Zeros: __ of 48
- Strong predictions (++ or --): __ of 48
- Which variables were hardest to specify, and why?
- Which three predictions do you consider most decisive for this hypothesis?
- Before any evidence is consulted: how well do you expect this hypothesis to do?
```

The last question matters. It is recorded before the answer is known, and it
can be wrong. That is the point.

---

## What happens next

Your matrix is compared cell by cell against the one already in the project,
and the disagreement rate is reported. Cells where an independent specifier
disagrees are cells where the score depends on who wrote it.

Then your matrix is scored against the corpus, and the two rankings are
compared.

**Disagreement is the useful outcome.** If your matrix matches the existing one
everywhere, the exercise has shown only that two specifiers share a bias.
