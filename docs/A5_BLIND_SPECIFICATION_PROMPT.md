# Task prompt — blind respecification of six evidence variables (RDORP-013 item A5)

**Run this in a fresh session.** It is written to be self-contained: everything
needed is below, and the whole point of the exercise is that you complete it
*without* consulting the project's evidence.

---

## Do not look these up

You are specifying what each hypothesis **predicts**. You must do it without
knowing what was **found**. If you learn the observations first, the
specification is worthless — it becomes a description of the answer rather than
a test of it.

**Do not open, read, grep or query any of the following before you have
finished and written down all 84 predictions:**

- `docs/RDORP-012_Results_Summary.md` — states the results
- `reports/` — all four files contain scores or observations
- the `corpus_observations` table, or `database/corpus_observations.csv`
- the `artifact_observations` table, or its CSV
- the `hdm_scores`, `results`, `screening` or `hpm_readings` tables
- the `CORPUS_OBSERVATIONS`, `SCREENING` or `HPM_READINGS` blocks in
  `database/build_db.py`
- any web search about Roman dodecahedron findspots, dating or distribution

You do not need the repository at all. Everything required is in this file.

If you already know facts about Roman dodecahedra, that cannot be helped —
but do not go looking for more, and derive each prediction from the mechanism
rather than from recall.

---

## Background you do need

A Roman dodecahedron is a hollow cast copper-alloy object, twelve pentagonal
faces, an aperture in the centre of each face, a knob at each of the twenty
vertices. Roughly 130 are known. Fourteen hypotheses about their function are
under test.

The project scores each hypothesis by comparing what it **predicted** against
what the corpus **shows**. Six variables currently contribute nothing, because
the predictions recorded for them are too vague to be confirmed or refuted —
for example, most hypotheses predict a bare "+" for *site type* without naming
which site type they expect. A prediction that cannot be wrong is not a
prediction.

Your job is to replace those six with predictions specific enough to fail.

---

## The prediction scale

| Symbol | Meaning |
| ------ | ------- |
| `++` | Strongly expected if the hypothesis is true |
| `+`  | Expected |
| `0`  | The mechanism is genuinely indifferent |
| `-`  | Unexpected |
| `--` | Strongly contrary; would count heavily against |

`0` is legitimate and sometimes correct — a mechanism can be genuinely
indifferent to a variable. But `0` scores nothing either way, so a matrix full
of zeros is an untestable hypothesis. Use `0` only where the mechanism truly
does not care, and say why.

---

## The six variables

| ID | Variable | Definition | Unit | Power |
| -- | -------- | ---------- | ---- | ----- |
| EV002 | Mass | Artefact weight | g | High |
| EV025 | Site type | Military, villa, town, temple, etc. | Enum | **Very High** |
| EV026 | Roman province | Roman administrative region | Enum | Medium |
| EV027 | Associated finds | Objects found together | Text | **Very High** |
| EV028 | Stratigraphy | Stratigraphic context | Text | High |
| EV029 | Dating | Chronological range | Years | **Very High** |

---

## The fourteen hypotheses

| ID | Name | Mechanism |
| -- | ---- | --------- |
| H001 | Structural connector / modular node | Rods seat in the apertures; several objects assemble into a larger frame |
| H002 | Rangefinder / measuring instrument | Sighted through opposed apertures to estimate distance |
| H003 | Ritual object | Symbolic or cultic object; the form itself carries the meaning |
| H004 | Candlestick / lamp support | Holds a candle or lamp |
| H005 | Textile / knitting tool | Generic textile working; yarn passes through the apertures |
| H006 | Astronomical instrument | Sighting or measuring celestial positions |
| H007 | Military equipment | Unspecified military function |
| H008 | Portable shrine component | Focus for domestic or personal cult |
| H009 | Tent apex / crown fitting | Hub at the top of a tent; rafters seat in the apertures |
| H010 | Parasol / umbrella crown fitting | Crown of a hand-carried canopy; ribs seat in the apertures |
| H011 | Archery targeting / ranging aid | Sighted to judge range for shooting |
| H012 | Spool-knitting / cord-working frame | Yarn looped over the knobs around one face; worked tube emerges through that aperture |
| H013 | Rope-laying top | Core through one aperture, strands outside over the knobs, object turned to lay the rope |
| H014 | Wax bulla / seal former | Soft wax pressed in the object around a knotted cord to form a sealing; knobs act as spacers |

---

## What to produce

**84 predictions** — 14 hypotheses × 6 variables. For each, give:

1. the symbol,
2. **what specifically is expected** — name the site type, the associated
   objects, the period, the mass range, the region, the depositional context.
   "Military camps and marching camps" is a prediction. "+" is not.
3. the **mechanical reason** — why the mechanism requires it. Not "this seems
   likely", but "a tool used in X is lost where X is done".

### Worked examples of the specificity required

- **EV025, H007 military equipment** — `++`, *"Forts, marching camps and
  frontier installations should dominate; permanent civilian settlement should
  be marginal. Issued equipment is lost where it is issued and used."*
- **EV029, H004 candlestick** — a lamp is a universal domestic need, so name
  the period you expect and say whether a narrow window would count against.
- **EV002, H001 structural connector** — do not write "mass benefits a
  load-bearing node". Give a threshold: *"above X g, because below that the
  wall section cannot carry the load."* If you cannot name a threshold, the
  honest prediction is `0` and you should say so.

### Constraints

- Write all fourteen predictions for a variable **before** moving to the next
  variable. Do not go hypothesis by hypothesis — that invites tuning one
  against another.
- Apply the same standard to every hypothesis. Do not give a favoured
  hypothesis an easier target.
- Some of these hypotheses are weak. Specify them **as their proponent
  would**, not as someone refuting them would. A strawman prediction is worse
  than a vague one.
- Where a mechanism is genuinely indifferent, `0` with a stated reason is the
  correct answer.

---

## Output format

A single markdown file, grouped by variable:

```
## EV025 Site type

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 | ++ | ... | ... |
| H002 | 0  | ... | ... |
...
```

Then one closing section:

```
## Declaration
- Did you consult any of the forbidden sources? yes / no
- Which hypotheses did you find hardest to specify, and why?
- Which predictions would you expect to be most decisive, and why?
```

The last two answers are wanted **before** anyone checks the evidence. They are
the record of what was expected to matter, written while it could still be
wrong.

---

## What happens next

The predictions are loaded into the prediction matrix, replacing the vague
ones. Only then is the corpus evidence consulted, and a direction assigned per
hypothesis per variable. Six Very-High and High power variables that currently
contribute nothing — including the two best-quantified in the whole corpus —
become live.

If the result is that several hypotheses now fail on these variables, that is
the exercise working. Do not soften a prediction because you suspect it will
fail. **A prediction you would not be willing to lose is not a prediction.**
