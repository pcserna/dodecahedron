# TASK.md

# RDORP Current Task

## Project

Roman Dodecahedron Open Research Project (RDORP)

This document defines the **current work package** for Codex.

Unlike `MASTER_PROMPT.md`, this file is expected to change throughout the project.

---

# Current Objective

Build the first complete, traceable evidence corpus for Roman dodecahedra.

The objective is **not** to evaluate hypotheses.

The objective is to extract, validate, normalize, and store evidence.

---

# Current Work Package

## WP-001

### Title

Corpus Construction

---

# Goal

Create the first complete version of the research corpus.

The corpus consists of:

- specimens.csv
- evidence_register.csv
- artifact_observations.csv
- sources.csv

Every dataset must remain internally consistent.

---

# Priority Order

Always work in this order.

## 1.

Collect source material.

Priority:

- Primary excavation reports
- Museum catalogues
- Peer-reviewed publications
- Academic catalogues
- Secondary publications

---

## 2.

Identify every specimen discussed.

If the specimen does not already exist

create a new RD_ID.

Otherwise update the existing record.

---

## 3.

Extract every evidence statement.

Each evidence statement must:

- be directly supported by the source;
- contain the original meaning;
- avoid interpretation;
- reference the exact page or figure whenever available.

---

## 4.

Extract measurements.

Examples include:

- dimensions
- weight
- wall thickness
- hole diameters
- decoration
- manufacturing details
- wear
- residues
- archaeological context

---

## 5.

Normalize measurements.

Use SI units.

Millimetres.

Grams.

ISO dates.

Decimal degrees.

Never estimate missing values.

---

## 6.

Update datasets.

Every completed batch updates:

- specimens.csv
- evidence_register.csv
- artifact_observations.csv
- sources.csv

No exceptions.

---

# Evidence Extraction Rules

Extract only:

- observations
- measurements
- archaeological facts
- excavation information
- documented analyses

Do NOT extract:

- speculation
- unsupported conclusions
- personal opinions
- inferred functions

Interpretation belongs to later project stages.

---

# Source Recording

Every extracted observation must include:

- SourceID
- page number
- figure number (if available)
- confidence level
- extraction date

---

# Conflict Resolution

If two sources disagree:

- preserve both observations;
- record separate evidence entries;
- never overwrite existing evidence;
- mark the disagreement in the Notes field.

---

# Batch Completion Criteria

A batch is complete only when:

✓ Sources imported

✓ Specimens updated

✓ Evidence extracted

✓ Measurements normalized

✓ Validation passed

✓ CSV exports regenerated

✓ Validation report generated

---

# Expected Deliverables

For every completed batch produce:

database/

- specimens.csv
- evidence_register.csv
- artifact_observations.csv
- sources.csv

reports/

- validation_report.md
- batch_summary.md

logs/

- import_log.md

---

# Coding Rules

Never edit generated CSV files manually.

Always modify the master database.

Always regenerate exports.

Every script must be idempotent.

Running the same import twice must never create duplicate records.

---

# Quality Requirements

Every observation must satisfy:

- Traceable
- Verifiable
- Reproducible
- Source-linked
- Scientifically neutral

If any requirement cannot be met,

leave the field empty and record the issue in the validation report.

---

# Immediate Next Task

## Batch 001

Process the highest-quality and best-documented sources first.

Priority sequence:

1. Build `sources.csv` from the core bibliography.
2. Create the initial `specimens.csv` index from authoritative catalogues and museum records.
3. Extract all evidence for the first 10 verified specimens.
4. Populate `artifact_observations.csv`.
5. Extend `evidence_register.csv`.
6. Generate validation and completeness reports.

The batch is finished only when all linked datasets have been regenerated and validated successfully.