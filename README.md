# RDORP — Roman Dodecahedron Open Research Project

An open, reproducible evidence base for testing what Roman dodecahedra were
for.

About 134 of these hollow, knobbed, twelve-faced bronze objects are known. They
come almost entirely from the north-western Roman provinces, were made between
roughly AD 200 and 400, and **no surviving Roman text mentions them**. Dozens of
explanations have been proposed. Almost none has ever been tested against the
whole body of evidence in a way anyone else could check.

This project does not argue for an answer. It builds the evidence base and the
machinery to evaluate hypotheses against it — including yours.

**Everything here is reproducible.** Clone the repository, run one command, and
you get the same database, the same scores and the same reports.

---

## Current state

| | |
| --- | --- |
| Specimens | 36 of c 134 known (27 %) |
| Sourced observations | 203 |
| Sources | 43, of which 21 read directly |
| Evidence variables | 48 |
| Hypotheses assessed | 14 |
| Functional domains screened | 17 |
| Pre-registered predictions | 11 |

**Headline result: no hypothesis is both well supported by the evidence and
obviously worth doing.** Every reading in which the object bears load, is used in
the field, or is issued as standard equipment has been tested and refuted.
Fifteen of seventeen screened everyday uses are eliminated. The leaders on
evidential fit are among the weakest on functional plausibility, and none is
robust.

The full picture, with all caveats, is in
**[docs/RDORP-012_Results_Summary.md](docs/RDORP-012_Results_Summary.md)**.

---

## How to run it

Requires Python 3.12+. No dependencies beyond the standard library.

```bash
git clone <repository-url>
cd dodecahedron
python run_pipeline.py
```

That rebuilds the database from source data, scores every hypothesis, validates
the datasets, regenerates the reports and regenerates every export — in that
order, which is not optional. It stops before touching the exports if validation
finds an error.

Read the output in `reports/`:

| File | Contents |
| ---- | -------- |
| `hdm_analysis.md` | Full scoring matrix, every sensitivity scenario, the evidence profile, the screen |
| `corpus_coverage.md` | What the corpus contains and how it is skewed |
| `validation_report.md` | Every rule violation and warning |
| `batch_summary.md` | What the most recent batch added |

---

## The rules

These are not style preferences. They are what makes the corpus usable by
someone who disagrees with us.

1. **Every fact has a source.** Source, page, figure where available, and an
   extraction date. If you have not read the publication yourself, say so and
   cite what you did read.
2. **Unknown stays unknown.** Never estimate, interpolate or average a missing
   measurement. Leave the field empty and record the range in a note.
3. **Observation and interpretation never mix.** What a source *reports* is
   evidence. What its author *concludes* goes in the evidence register, marked
   as interpretation, and is never scored.
4. **Conflicts are preserved, not resolved.** If two sources disagree, both
   entries stay and the conflict is recorded. Nothing is ever overwritten.
5. **Predictions come before observations.** A hypothesis states what it expects
   *before* the evidence is consulted. Predictions written after the fact are
   marked contaminated and reported as such — six of the fourteen currently are.
6. **Generated files are never edited by hand.** Change the source data and
   re-run the pipeline.

---

## Contributing a specimen

The single most useful contribution. The corpus covers 27 % of known specimens
and is 56 % British against a known corpus that is about 20 % British.

**You need:** an identifier, a findspot, a source, and whatever measurements
exist. That is enough — partial records are welcome and normal.

1. Add the publication or record to `SOURCES` in
   [database/build_db.py](database/build_db.py), with a confidence grade A–E.
2. Add the specimen to `SPECIMENS`, with the next free `RD_ID`.
3. Add one row to `OBSERVATIONS` per specimen × variable × source, with page and
   extraction date.
4. Add a row to `SPECIMEN_QUALITY` recording completeness, provenance grade and
   measurement grade.
5. Run `python run_pipeline.py` and read `reports/validation_report.md`.

Open a pull request with the diff. If you would rather not write Python, **open
an issue with the information and a citation** and someone will enter it.

**Especially wanted:** continental specimens; anything with a stratified
context; complete sets of twelve aperture diameters; and any specimen with an
excavated findspot. Only one dodecahedron in the entire corpus has ever come
from a sealed, dated deposit.

---

## Testing your own hypothesis

There are two routes. Take the cheap one first.

### Route 1 — screening (minutes)

A screen records only the predictions your mechanism **cannot avoid** — those
that follow whether you like them or not — and checks those against the corpus.

1. Add an entry to `SCREENING_CANDIDATES` in `build_db.py`: what it is, what it
   would produce, and how it works.
2. Add 5–10 rows to `SCREENING`, one per unavoidable prediction, each with a
   rationale stating the *mechanical* reason.
3. Run the pipeline and read section 4b2 of `reports/hdm_analysis.md`.

A candidate is eliminated when the corpus contradicts, at full strength, a
prediction it had to make on a high-power variable. Surviving is not support —
it means your idea earns a full test.

### Route 2 — full assessment

1. Add a row to [database/hypotheses.csv](database/hypotheses.csv).
2. Write a prediction for **every** evidence variable in a new `HPM_Hxxx` block
   in `build_db.py`, using `++ + 0 - --`, each with a rationale.
   **Write all of them before you look at the observations.** This is the whole
   point; if you cannot, declare it.
3. Optionally add a usage-value assessment: is the product worth more than the
   cheapest substitute? Is the difficulty of making it part of its worth?
4. Run the pipeline.

### Before you start, read this

The scoring will tell you things you may not expect.

- **Predicting `0` everywhere scores well and means nothing.** The reports show
  *points staked* beside every score for exactly this reason. A hypothesis that
  risks nothing is not supported, it is untested.
- **Four constraints defeat most utilitarian ideas** before mechanics are even
  considered: contexts are predominantly urban and civilian; nothing is
  standardised; walls are too thin for load; and no functional equipment of any
  kind has ever been found alongside a dodecahedron. Check yours against these
  first.
- **Some questions are settled by arithmetic, not scoring.** Three candidates
  have been eliminated by computation — see `experiments` and section 6.3 of the
  results summary. Check whether yours is one.
- The **evidence profile** in section 4b of `reports/hdm_analysis.md` states what
  any correct hypothesis must predict. Compare yours against it before scoring.

---

## Repository layout

```
run_pipeline.py            the only supported entry point
MASTER_PROMPT.md           governance rules the corpus is built under
TASK.md                    current work package

database/
  README.md                which files are source data and which are generated
  build_db.py              SOURCE DATA — specimens, observations, sources, predictions
  score_hdm.py             scoring, sensitivity analysis, evidence profile, screening
  validate.py              dataset validation
  reports.py               report generation
  export.py                CSV / JSON / SQLite export
  hypotheses.csv           source data — the hypothesis list
  Evidence_Master_List_v1.csv   source data — the 48 evidence variables
  evidence_register_v1.csv source data — initial evidence register
  rdorp.sqlite             generated database
  *.csv                    generated exports

docs/                      project documentation (see below)
reports/                   generated analytical reports
exports/                   generated csv/, json/, sqlite/
logs/import_log.md         appended once per pipeline run
```

| Document | |
| -------- | -- |
| [RDORP-012 Results Summary](docs/RDORP-012_Results_Summary.md) | **Start here.** What the evidence shows and what it does not |
| [RDORP-013 Hardening Plan](docs/RDORP-013_Hardening_Plan.md) | **What is wrong with the analysis and what would fix it.** Read this before trusting a number |
| [RDORP-010 Analytical Method](docs/RDORP-010_Analytical_Method.md) | How hypotheses are evaluated |
| [RDORP-011 Geometry Specification](docs/GEOMETRY_SPECIFICATION.md) | Face-numbering convention for recording apertures |
| [RDORP-004 Database Schema](docs/DATABASE_SCHEMA.md) | Record structure |
| [RDORP-005 Data Dictionary](docs/DATA_DICTIONARY.md) | Field definitions |
| [RDORP-003 Research Method](docs/RESEARCH_METHOD.md) | Methodology |
| [RDORP-009 Decision Model](docs/RDORP-009_Decision_Model.md) | Hypotheses and scoring concept |
| [RDORP-001 Project Charter](docs/PROJECT_CHARTER.md) | Scope and governance |
| [RDORP-002 Roadmap](docs/ROADMAP.md) | Planned stages |

---

## What would help most

Full plan with costs and consequences in
[RDORP-013 Hardening Plan](docs/RDORP-013_Hardening_Plan.md). The highest-value
contribution an outsider can make is **blind prediction specification** — writing
a hypothesis's predictions without seeing the observations — because nobody
inside the project can do it.

In order of how much each would settle:

1. **Measure every aperture and count its rings, on any complete specimen** —
   recording which apertures are opposite which. A ruler, a lens and an
   afternoon in a museum store. The cheapest decisive test identified.
2. **Microwear analysis** on the knob necks and aperture lips of one
   well-preserved specimen.
3. **Residue analysis** on an unconserved specimen.
4. **Guggenberger 1999** consulted directly — most corpus statistics currently
   rest on it at one remove.
5. **Standardisation measured within a single typological group** rather than
   across the pooled corpus.
6. **Experimental lost-wax reproduction**, and a search for any mould, casting
   waste or reject. No one knows where a single dodecahedron was made.

If you have museum access, items 1–3 are the ones to ask about.

---

## Sources and copyright

`database/sources.csv` lists every source with its DOI or URL. **The
publications themselves are not redistributed here** — most are under publisher
copyright. Obtain them from the publisher or via the DOI. Locally held copies
are excluded by `.gitignore`.

When contributing, cite sources properly and do not paste copyrighted text
beyond what is needed to record an observation.

---

## Licence

Project structure, database schema, code and original documentation are
available under the terms in [LICENSE](LICENSE). Museum, publisher and image
rights remain with their owners.

---

## Honest limitations

Stated plainly, because a corpus you cannot trust is worse than none:

- 27 % coverage, and not a representative 27 %.
- No specimen has been authenticated against forgery, and two of the three
  specimens carrying usable aperture data are unexcavated private-collection
  pieces.
- Ancient local imitation is proposed in the literature and untested. If real,
  it confounds the project's most load-bearing finding.
- Wear evidence is macroscopic only.
- Six of the fourteen hypotheses have prediction matrices written after the
  evidence was known, and are marked contaminated.
- The direction assigned to each corpus observation is a judgement about a
  sourced fact, not an observation. Every one is stored with its reasoning so it
  can be challenged separately from the evidence.

Disagreement is the point. If you think a direction is wrong, change it and
re-run — the number will move and you will be able to see exactly how much.
