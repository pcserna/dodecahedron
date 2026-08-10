# Validation Report

| Field | Value |
| ----- | ----- |
| Document ID | RDORP-VAL |
| Generated | 2026-08-10 |
| Database | `database\rdorp.sqlite` |
| Generator | `database/validate.py` |

Generated file. Do not edit by hand; change the master database and re-run the pipeline.

## Summary

- **Errors: 0** — records violating a stated project rule
- **Warnings: 22** — admissible but weakening the evidence base
- **Notes: 71** — recorded for transparency

Validation never modifies data. Every finding below is reported for a human decision, as required by MASTER_PROMPT.

## Errors (0)

None.

## Warnings (22)

| Rule | Entity | Detail |
| ---- | ------ | ------ |
| `context-missing` | specimens | 43 of 57 specimens have context_category 'Unknown' and cannot contribute to context variables |
| `corpus-without-specimen` | EV019 | scores 'absent' at Very High power on a corpus statement alone, with no specimen observation anywhere beneath it. Nothing in the corpus can currently contradict it |
| `corpus-without-specimen` | EV020 | scores 'absent' at Very High power on a corpus statement alone, with no specimen observation anywhere beneath it. Nothing in the corpus can currently contradict it |
| `corpus-without-specimen` | EV038 | scores 'weak_absent' at High power on a corpus statement alone, with no specimen observation anywhere beneath it. Nothing in the corpus can currently contradict it |
| `corpus-without-specimen` | EV044 | scores 'absent' at High power on a corpus statement alone, with no specimen observation anywhere beneath it. Nothing in the corpus can currently contradict it |
| `evidence-gap` | EV023 | Thermal alteration (Very High) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV024 | Residues (Very High) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV041 | Knob wear (Very High) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV042 | Microwear location (Very High) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV043 | Aperture distinguishability (Very High) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV045 | Manufacturing difficulty (Very High) has no corpus-level observation and is therefore unscored |
| `measurement-out-of-range` | RD-0017 | max_diameter_mm = 127.71 mm lies outside the published corpus range 40.0-110.0 mm (PUB-0003, 31 and 39) |
| `prediction-testable` | P-0001 | 6 specimen observation(s) now exist on EV041 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `prediction-testable` | P-0002 | 1 specimen observation(s) now exist on EV024 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `prediction-testable` | P-0005 | 1 specimen observation(s) now exist on EV007 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `prediction-testable` | P-0006 | 2 specimen observation(s) now exist on EV015 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `prediction-testable` | P-0007 | 1 specimen observation(s) now exist on EV030 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `prediction-testable` | P-0009 | 3 specimen observation(s) now exist on EV043 while the prediction is still open. It may be resolvable, or the evidence may be too thin to resolve it; either way the position should be stated rather than left implicit |
| `source-missing` | corpus observation EV034 | no source_id (evidence_class=Derived). Derived assessments are this project's own reasoning and have no external source by definition, but they are discounted and excluded from the observed-only scenario |
| `source-missing` | corpus observation EV035 | no source_id (evidence_class=Derived). Derived assessments are this project's own reasoning and have no external source by definition, but they are discounted and excluded from the observed-only scenario |
| `source-missing` | corpus observation EV036 | no source_id (evidence_class=Derived). Derived assessments are this project's own reasoning and have no external source by definition, but they are discounted and excluded from the observed-only scenario |
| `unwritten-prediction` | EV044 | carries scored corpus evidence but no hypothesis has a prediction for it. All 14 cells default to '0', so it is counted among the scored variables and discriminates nothing |

## Notes (71)

| Rule | Entity | Detail |
| ---- | ------ | ------ |
| `corpus-coverage` | specimens | 57 of about 134 known specimens recorded (43 per cent) |
| `evidence-gap` | EV007 | Hole edge radius (Medium) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV015 | Repair evidence (Medium) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV021 | Impact damage (Medium) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV022 | Abrasion (Medium) has no corpus-level observation and is therefore unscored |
| `evidence-gap` | EV030 | Number at site (Medium) has no corpus-level observation and is therefore unscored |
| `hpm-not-discriminating` | EV002 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV025 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV026 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV027 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV028 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV029 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV046 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV047 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `hpm-not-discriminating` | EV048 | corpus evidence exists but the HPM predictions for this variable are not specific enough to be confirmed or refuted; scored 0 and reported as an HPM defect |
| `interpretation-recorded` | EI-0001 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0002 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0003 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0004 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0005 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0006 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0007 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0009 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0010 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0011 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0012 | published interpretation held separately from evidence and excluded from scoring |
| `interpretation-recorded` | EI-0014 | published interpretation held separately from evidence and excluded from scoring |
| `page-missing` | observation 206 | RD-0038 x EV001 cites PUB-0045 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 207 | RD-0038 x EV025 cites PUB-0045 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 208 | RD-0038 x EV029 cites PUB-0045 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 209 | RD-0039 x EV025 cites PUB-0046 (Online), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 210 | RD-0039 x EV030 cites PUB-0046 (Online), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 216 | RD-0038 x EV004 cites PUB-0045 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 218 | RD-0040 x EV014 cites PUB-0048 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 219 | RD-0040 x EV041 cites PUB-0048 (Database), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 35 | RD-0005 x EV001 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 36 | RD-0005 x EV002 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 37 | RD-0005 x EV011 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 38 | RD-0005 x EV017 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 39 | RD-0005 x EV018 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 40 | RD-0005 x EV025 cites PUB-0008 (Article), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 41 | RD-0006 x EV025 cites PUB-0004 (Online), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 97 | RD-0018 x EV025 cites PUB-0013 (Online), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `page-missing` | observation 98 | RD-0018 x EV031 cites PUB-0013 (Online), a source type that carries no pagination; record an identifier if the source offers one, otherwise this is a limit of the source, not of the extraction |
| `prediction-open` | P-0001 | registered 2026-08-08 against EV041; awaiting measurement |
| `prediction-open` | P-0002 | registered 2026-08-08 against EV024; awaiting measurement |
| `prediction-open` | P-0003 | registered 2026-08-08 against EV023; awaiting measurement |
| `prediction-open` | P-0004 | registered 2026-08-08 against EV042; awaiting measurement |
| `prediction-open` | P-0005 | registered 2026-08-08 against EV007; awaiting measurement |
| `prediction-open` | P-0006 | registered 2026-08-08 against EV015; awaiting measurement |
| `prediction-open` | P-0007 | registered 2026-08-08 against EV030; awaiting measurement |
| `prediction-open` | P-0008 | registered 2026-08-08 against EV021; awaiting measurement |
| `prediction-open` | P-0009 | registered 2026-08-08 against EV043; awaiting measurement |
| `prediction-open` | P-0010 | registered 2026-08-08 against EV045; awaiting measurement |
| `prediction-open` | P-0011 | registered 2026-08-08 against EV048; awaiting measurement |
| `recorded-conflict` | RD-0005 x EV025 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0020 x EV006 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0020 x EV016 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0020 x EV032 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0029 x EV025 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0035 x EV017 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0035 x EV047 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0037 x EV016 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `recorded-conflict` | RD-0038 x EV029 | a conflict is recorded in this observation's notes; it is preserved rather than resolved, per the project rule, and is listed here so it is visible rather than buried |
| `specimen-without-corpus` | EV007 | 1 specimen observation(s) exist on a Medium power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV015 | 2 specimen observation(s) exist on a Medium power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV022 | 1 specimen observation(s) exist on a Medium power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV024 | 1 specimen observation(s) exist on a Very High power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV030 | 1 specimen observation(s) exist on a Medium power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV041 | 6 specimen observation(s) exist on a Very High power variable that carries no corpus observation, so none of it reaches the scoring |
| `specimen-without-corpus` | EV043 | 3 specimen observation(s) exist on a Very High power variable that carries no corpus observation, so none of it reaches the scoring |
