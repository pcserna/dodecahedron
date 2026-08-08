# `database/` — what is master data and what is generated

Before this file existed, the CSV files in this directory looked like master
data and were not. Two of them used an evidence-variable numbering scheme
incompatible with the database, and four were empty headers. Anyone reading
them got wrong answers silently.

The rule now is explicit.

## Master data — edit these

| File | Role |
| ---- | ---- |
| `build_db.py` | **The master dataset.** Sources, specimens, observations, corpus observations, the prediction matrix and published interpretations are Python literals inside it. Everything else in the repository is derived from it. |
| `hypotheses.csv` | Seed: hypothesis list. |
| `Evidence_Master_List_v1.csv` | Seed: the 40 evidence variables. |
| `evidence_register_v1.csv` | Seed: initial evidence register. |

Nothing else in this directory may be edited by hand.

## Generated — never edit these

| File | Generator |
| ---- | --------- |
| `rdorp.sqlite` | `build_db.py`, then `score_hdm.py` |
| `specimens.csv`, `artifact_observations.csv`, `sources.csv`, `evidence_register.csv`, `evidence_variables.csv`, `evidence_sources.csv`, `corpus_observations.csv`, `hpm.csv`, `hdm_scores.csv`, `results.csv`, `experiments.csv`, `hdm_matrix.csv` | `export.py` |
| everything under `../exports/` | `export.py` |
| everything under `../reports/` | `validate.py`, `reports.py` |
| `../logs/import_log.md` | `run_pipeline.py` (appended, not regenerated) |

The generated CSV files carry the names that MASTER_PROMPT and
`docs/DATA_DICTIONARY.md` refer to, so the documented paths now hold real,
current data.

## How to run it

```
python run_pipeline.py
```

from the repository root. That is the only supported entry point. The order is
not optional: `build_db.py` drops and recreates `hdm_scores`, so building
without re-scoring leaves the analysis empty, and exporting before scoring
writes empty score files. `run_pipeline.py` enforces the order and stops before
touching the exports if validation reports an error.

Individual modules can be run for inspection:

```
python database/build_db.py     # rebuild only
python database/score_hdm.py    # score and print the ranking
python database/validate.py     # validate; exit code 1 if any error
python database/reports.py      # regenerate the analytical reports
python database/export.py       # regenerate CSV and JSON
```

## Why master data lives in Python rather than CSV

Every observation carries a long prose `notes` field recording provenance,
conflicts with other sources, and the reason for its confidence grade. That is
where most of the scientific value sits, and it survives review far better in
source form than in a CSV cell. The trade-off is deliberate; the CSV exports
exist so that the data is usable without reading Python.

## Adding evidence

1. Add the source to `SOURCES` in `build_db.py`. If it has not been read
   directly, say so in its `notes` and never use it as an observation's
   `source_id`.
2. Add or update the specimen in `SPECIMENS`.
3. Add rows to `OBSERVATIONS`, one per specimen × variable × source, with page
   and extraction date. Never overwrite an existing row: conflicting sources
   both stay, and the conflict goes in `notes`.
4. If the new evidence changes what can be said at corpus level, update
   `CORPUS_OBSERVATIONS` — and say in its `notes` what changed and why.
5. If the source draws a conclusion, put that in `INTERPRETATIONS`, not in
   `OBSERVATIONS`. Interpretations are never scored.
6. Run `python run_pipeline.py` and read `reports/validation_report.md`.
