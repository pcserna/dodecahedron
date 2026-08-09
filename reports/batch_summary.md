# Batch Summary

| Field | Value |
| ----- | ----- |
| Document ID | RDORP-BATCH |
| Generated | 2026-08-09 |
| Database | `database\rdorp.sqlite` |
| Generator | `database/reports.py` |

Generated file. Do not edit by hand: change the master data in `database/build_db.py` and re-run `python run_pipeline.py`.

## Database contents

| Table | Rows |
| ----- | ---- |
| `sources` | 49 |
| `specimens` | 40 |
| `artifact_observations` | 224 |
| `corpus_observations` | 37 |
| `evidence_register` | 47 |
| `hdm_scores` | 448 |
| `results` | 14 |
| `experiments` | 8 |

## Most recent batch: 002 — Guggenberger and Leach 2025 (PUB-0003)

- Observations extracted from PUB-0003: **37**
- Specimens added: **12**
- Corpus-level observations now scoreable: **32**

| RD_ID | Specimen | Country | Context |
| ----- | -------- | ------- | ------- |
| RD-0022 | Mainz 3 dodecahedron | Unknown | Unknown |
| RD-0023 | Gelduba (Gellep) grave dodecahedron | Germany | Grave |
| RD-0024 | Pfofeld dodecahedron | Germany | Military |
| RD-0025 | Schwarzenacker dodecahedron | Germany | Temple |
| RD-0026 | Lydney dodecahedron fragment | United Kingdom | Temple |
| RD-0027 | Severn estuary (Gloucester) dodecahedron fragment | United Kingdom | Hoard |
| RD-0028 | Paris-region dodecahedron | France | Civilian |
| RD-0029 | Carmarthenshire dodecahedron | United Kingdom | Hoard |
| RD-0030 | Bachem grave dodecahedron | Germany | Grave |
| RD-0031 | Feldberg dodecahedron | Germany | Military |
| RD-0032 | Brigetio dodecahedron | Hungary | Unknown |
| RD-0033 | Deonica dodecahedron | Serbia | Unknown |

## Batch completion criteria (TASK.md)

| Criterion | Status |
| --------- | ------ |
| Sources imported | done |
| Specimens updated | done |
| Evidence extracted | done |
| Measurements normalised | done — mm, g, ISO dates |
| Validation passed | see `reports/validation_report.md` |
| CSV exports regenerated | done — `database/`, `exports/csv`, `exports/json` |
| Validation report generated | done |
