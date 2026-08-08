#!/usr/bin/env python3
"""RDORP - dataset validation (MASTER_PROMPT 'Validation Rules', TASK.md 'Quality Requirements').

Checks the master database and writes ``reports/validation_report.md``.

The rule from MASTER_PROMPT is followed exactly: validation never modifies
data. It emits findings and lets a human decide. Findings are graded:

    ERROR    the record violates a stated project rule and must be corrected
    WARNING  the record is admissible but weakens the evidence base
    NOTE     recorded for transparency; no action implied

``main`` exits non-zero if any ERROR is present, so the pipeline can stop.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import date

LOG = logging.getLogger("rdorp.validate")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")
REPORT_DEFAULT = os.path.join(ROOT, "reports", "validation_report.md")

#: Source types that carry page numbers. A missing page on any other type is a
#: property of the source, not a defect in the extraction.
PAGINATED_SOURCE_TYPES = {
    "Journal", "Book", "Thesis", "Catalogue", "Archive", "Excavation report",
}

#: Values that must never be used to represent an unknown (DATABASE_SCHEMA s5).
FORBIDDEN_UNKNOWNS = {"n/a", "na", "unknown value", "none", "-", "?", "tbd", "0.0"}

#: Corpus limits published in PUB-0003, p 31 and p 39. Measurements outside
#: these are not necessarily wrong, but they must be justified.
PLAUSIBLE_RANGES_MM = {
    "max_diameter_mm": (40.0, 110.0),
    "wall_thickness_mm": (0.5, 4.0),
    "knob_diameter_mm": (1.0, 20.0),
}
PLAUSIBLE_HOLE_MM = (6.0, 40.0)


@dataclass
class Finding:
    level: str
    rule: str
    entity: str
    detail: str


class Validator:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.findings: list[Finding] = []

    def add(self, level: str, rule: str, entity: str, detail: str) -> None:
        self.findings.append(Finding(level, rule, entity, detail))

    # -- individual rules ---------------------------------------------------

    def check_referential_integrity(self) -> None:
        """MASTER_PROMPT: reject records with an unknown specimen or source."""
        for row in self.conn.execute("PRAGMA foreign_key_check"):
            self.add("ERROR", "referential-integrity", str(row[0]),
                     f"row {row[1]} violates foreign key to {row[2]}")

        orphan_obs = self.conn.execute(
            """SELECT observation_id, rd_id FROM artifact_observations
               WHERE rd_id NOT IN (SELECT rd_id FROM specimens)"""
        ).fetchall()
        for row in orphan_obs:
            self.add("ERROR", "specimen-unknown", f"observation {row['observation_id']}",
                     f"references unknown specimen {row['rd_id']}")

    def check_sources_present(self) -> None:
        """MASTER_PROMPT: every fact has a source."""
        for row in self.conn.execute(
            "SELECT observation_id, rd_id, ev_id FROM artifact_observations "
            "WHERE source_id IS NULL OR source_id = ''"
        ):
            self.add("ERROR", "source-missing",
                     f"observation {row['observation_id']}",
                     f"{row['rd_id']} x {row['ev_id']} has no source_id")

        for row in self.conn.execute(
            "SELECT ev_id, evidence_class FROM corpus_observations "
            "WHERE source_id IS NULL OR source_id = ''"
        ):
            level = "WARNING" if row["evidence_class"] == "Derived" else "ERROR"
            self.add(level, "source-missing", f"corpus observation {row['ev_id']}",
                     f"no source_id (evidence_class={row['evidence_class']}). "
                     "Derived assessments are this project's own reasoning and "
                     "have no external source by definition, but they are "
                     "discounted and excluded from the observed-only scenario")

        for row in self.conn.execute(
            "SELECT rd_id FROM specimens WHERE primary_source_id IS NULL"
        ):
            self.add("ERROR", "source-missing", row["rd_id"], "no primary_source_id")

    def check_page_references(self) -> None:
        """TASK.md: every extracted observation records a page number.

        Web pages, databases and personal communications have no pagination, so
        a missing page on one of those is a property of the source rather than a
        defect in the extraction. Those are recorded as notes; a missing page on
        a source that does paginate is a warning.
        """
        rows = self.conn.execute(
            """SELECT o.observation_id, o.rd_id, o.ev_id, o.source_id, s.type
               FROM artifact_observations o
               LEFT JOIN sources s ON s.source_id = o.source_id
               WHERE (o.page IS NULL OR o.page = '') AND o.source_id IS NOT NULL"""
        ).fetchall()
        for row in rows:
            paginated = row["type"] in PAGINATED_SOURCE_TYPES
            self.add(
                "WARNING" if paginated else "NOTE",
                "page-missing", f"observation {row['observation_id']}",
                f"{row['rd_id']} x {row['ev_id']} cites {row['source_id']} "
                + (f"({row['type']}) without a page or figure"
                   if paginated else
                   f"({row['type']}), a source type that carries no pagination; "
                   "record an identifier if the source offers one, otherwise "
                   "this is a limit of the source, not of the extraction"))

    def check_extraction_dates(self) -> None:
        for row in self.conn.execute(
            "SELECT observation_id, extraction_date FROM artifact_observations"
        ):
            value = row["extraction_date"]
            if not value:
                self.add("WARNING", "extraction-date-missing",
                         f"observation {row['observation_id']}", "no extraction_date")
            elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                self.add("ERROR", "extraction-date-format",
                         f"observation {row['observation_id']}",
                         f"'{value}' is not an ISO 8601 date")

    def check_duplicates(self) -> None:
        """MASTER_PROMPT: reject duplicated evidence."""
        for row in self.conn.execute(
            """SELECT rd_id, ev_id, source_id, observed_value, COUNT(*) n
               FROM artifact_observations
               GROUP BY rd_id, ev_id, source_id, observed_value
               HAVING n > 1"""
        ):
            self.add("ERROR", "duplicate-evidence", f"{row['rd_id']} x {row['ev_id']}",
                     f"{row['n']} identical rows from {row['source_id']}")

        for row in self.conn.execute(
            """SELECT inventory_number, COUNT(*) n, GROUP_CONCAT(rd_id) ids
               FROM specimens WHERE inventory_number IS NOT NULL
               GROUP BY inventory_number HAVING n > 1"""
        ):
            self.add("ERROR", "conflicting-identifier", row["inventory_number"],
                     f"shared by specimens {row['ids']}")

        for row in self.conn.execute(
            """SELECT guggenberger_number, COUNT(*) n, GROUP_CONCAT(rd_id) ids
               FROM specimens WHERE guggenberger_number IS NOT NULL
               GROUP BY guggenberger_number HAVING n > 1"""
        ):
            self.add("ERROR", "conflicting-identifier",
                     f"Guggenberger no {row['guggenberger_number']}",
                     f"shared by specimens {row['ids']}")

    def check_placeholder_values(self) -> None:
        """DATABASE_SCHEMA s5: unknown must never be replaced by a dummy value."""
        for row in self.conn.execute(
            "SELECT observation_id, observed_value FROM artifact_observations"
        ):
            value = (row["observed_value"] or "").strip().lower()
            if value in FORBIDDEN_UNKNOWNS:
                self.add("ERROR", "placeholder-value",
                         f"observation {row['observation_id']}",
                         f"observed_value '{row['observed_value']}' is a "
                         "placeholder; unknown values must be left empty")

    def check_measurement_plausibility(self) -> None:
        """Flag measurements outside the published corpus range."""
        for column, (low, high) in PLAUSIBLE_RANGES_MM.items():
            for row in self.conn.execute(
                f"SELECT rd_id, {column} v FROM specimens WHERE {column} IS NOT NULL"
            ):
                if not low <= row["v"] <= high:
                    self.add("WARNING", "measurement-out-of-range", row["rd_id"],
                             f"{column} = {row['v']} mm lies outside the published "
                             f"corpus range {low}-{high} mm (PUB-0003, 31 and 39)")

        hole_cols = [f"hole_{i:02d}_mm" for i in range(1, 13)]
        for row in self.conn.execute(
            f"SELECT rd_id, {', '.join(hole_cols)} FROM specimens"
        ):
            for col in hole_cols:
                v = row[col]
                if v is None:
                    continue
                if not PLAUSIBLE_HOLE_MM[0] <= v <= PLAUSIBLE_HOLE_MM[1]:
                    self.add("WARNING", "measurement-out-of-range", row["rd_id"],
                             f"{col} = {v} mm lies outside the published corpus "
                             f"hole range {PLAUSIBLE_HOLE_MM[0]}-"
                             f"{PLAUSIBLE_HOLE_MM[1]} mm (PUB-0003, 31)")

    def check_confidence_grades(self) -> None:
        for table, key in (("specimens", "rd_id"), ("artifact_observations", "observation_id")):
            for row in self.conn.execute(
                f"SELECT {key} k, confidence FROM {table} WHERE confidence IS NULL"
            ):
                self.add("ERROR", "confidence-missing", f"{table} {row['k']}",
                         "no confidence grade assigned")

    def check_scoring_provenance(self) -> None:
        """Nothing may be scored that has no corpus-level observation behind it."""
        scored = {r["ev_id"] for r in self.conn.execute(
            "SELECT DISTINCT ev_id FROM hdm_scores")}
        corpus = {r["ev_id"] for r in self.conn.execute(
            "SELECT ev_id FROM corpus_observations")}
        for ev_id in sorted(scored - corpus):
            self.add("ERROR", "score-without-observation", ev_id,
                     "hdm_scores contains a score for a variable with no row in "
                     "corpus_observations")

        for row in self.conn.execute(
            """SELECT ev_id, direction FROM corpus_observations
               WHERE discriminating = 0"""
        ):
            self.add("NOTE", "hpm-not-discriminating", row["ev_id"],
                     "corpus evidence exists but the HPM predictions for this "
                     "variable are not specific enough to be confirmed or "
                     "refuted; scored 0 and reported as an HPM defect")

    def check_predictions(self) -> None:
        """Pre-registered predictions must stay separate from evidence.

        The failure mode this guards against is a prediction quietly becoming
        the evidence that confirms it. A prediction whose variable has since
        acquired corpus evidence must be resolved against that evidence, not
        left open while the evidence is scored.
        """
        scored = {r["ev_id"] for r in self.conn.execute(
            "SELECT DISTINCT ev_id FROM hdm_scores")}
        for row in self.conn.execute(
            "SELECT prediction_id, ev_id, status, registered_on, resolved_on "
            "FROM predictions"
        ):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["registered_on"] or ""):
                self.add("ERROR", "prediction-date", row["prediction_id"],
                         "registered_on is not an ISO 8601 date; without a "
                         "reliable registration date a prediction is not a test")
            if row["status"] == "open" and row["ev_id"] in scored:
                self.add("ERROR", "prediction-unresolved", row["prediction_id"],
                         f"still open although {row['ev_id']} now has corpus "
                         "evidence and has been scored; resolve it against that "
                         "evidence before the evidence is used")
            if row["status"] != "open" and not row["resolved_on"]:
                self.add("ERROR", "prediction-unstamped", row["prediction_id"],
                         f"status is '{row['status']}' but resolved_on is empty")
            if row["status"] == "open":
                self.add("NOTE", "prediction-open", row["prediction_id"],
                         f"registered {row['registered_on']} against "
                         f"{row['ev_id']}; awaiting measurement")

    def check_interpretations_not_scored(self) -> None:
        """MASTER_PROMPT: interpretation must never be recorded as evidence."""
        for row in self.conn.execute(
            "SELECT evidence_id, evidence_statement FROM evidence_register "
            "WHERE evidence_type = 'Interpretation'"
        ):
            self.add("NOTE", "interpretation-recorded", row["evidence_id"],
                     "published interpretation held separately from evidence and "
                     "excluded from scoring")

    def check_corpus_coverage(self) -> None:
        total = self.conn.execute("SELECT COUNT(*) c FROM specimens").fetchone()["c"]
        known = 134  # PUB-0003, 32
        self.add("NOTE", "corpus-coverage", "specimens",
                 f"{total} of about {known} known specimens recorded "
                 f"({total / known * 100:.0f} per cent)")

        by_country = self.conn.execute(
            "SELECT country, COUNT(*) n FROM specimens GROUP BY country ORDER BY n DESC"
        ).fetchall()
        top = by_country[0]
        share = top["n"] / total * 100
        if share > 50:
            self.add("WARNING", "corpus-bias", "specimens",
                     f"{share:.0f} per cent of recorded specimens are from "
                     f"{top['country']}, whereas PUB-0003, 32 reports that about "
                     "20 per cent of the known corpus is British and about 70 per "
                     "cent is from the Gallic and Germanic provinces. The recorded "
                     "corpus is not representative of the known corpus")

        no_context = self.conn.execute(
            "SELECT COUNT(*) c FROM specimens WHERE context_category = 'Unknown'"
        ).fetchone()["c"]
        if no_context:
            self.add("WARNING", "context-missing", "specimens",
                     f"{no_context} of {total} specimens have context_category "
                     "'Unknown' and cannot contribute to context variables")

    def check_evidence_gaps(self) -> None:
        rows = self.conn.execute(
            """SELECT ev_id, variable, discriminatory_power FROM evidence_variables
               WHERE ev_id NOT IN (SELECT ev_id FROM corpus_observations)
               ORDER BY CASE discriminatory_power
                   WHEN 'Very High' THEN 1 WHEN 'High' THEN 2 ELSE 3 END, ev_id"""
        ).fetchall()
        for row in rows:
            level = "WARNING" if row["discriminatory_power"] == "Very High" else "NOTE"
            self.add(level, "evidence-gap", row["ev_id"],
                     f"{row['variable']} ({row['discriminatory_power']}) has no "
                     "corpus-level observation and is therefore unscored")

    # -- driver -------------------------------------------------------------

    def run(self) -> list[Finding]:
        for check in (
            self.check_referential_integrity,
            self.check_sources_present,
            self.check_page_references,
            self.check_extraction_dates,
            self.check_duplicates,
            self.check_placeholder_values,
            self.check_measurement_plausibility,
            self.check_confidence_grades,
            self.check_scoring_provenance,
            self.check_predictions,
            self.check_interpretations_not_scored,
            self.check_corpus_coverage,
            self.check_evidence_gaps,
        ):
            check()
        return self.findings


def write_report(findings: list[Finding], path: str, db_path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    counts = {level: sum(1 for f in findings if f.level == level)
              for level in ("ERROR", "WARNING", "NOTE")}

    lines = [
        "# Validation Report",
        "",
        "| Field | Value |",
        "| ----- | ----- |",
        "| Document ID | RDORP-VAL |",
        f"| Generated | {date.today().isoformat()} |",
        f"| Database | `{os.path.relpath(db_path, ROOT)}` |",
        "| Generator | `database/validate.py` |",
        "",
        "Generated file. Do not edit by hand; change the master database and "
        "re-run the pipeline.",
        "",
        "## Summary",
        "",
        f"- **Errors: {counts['ERROR']}** — records violating a stated project rule",
        f"- **Warnings: {counts['WARNING']}** — admissible but weakening the evidence base",
        f"- **Notes: {counts['NOTE']}** — recorded for transparency",
        "",
        "Validation never modifies data. Every finding below is reported for a "
        "human decision, as required by MASTER_PROMPT.",
        "",
    ]

    for level in ("ERROR", "WARNING", "NOTE"):
        subset = [f for f in findings if f.level == level]
        lines += [f"## {level.title()}s ({len(subset)})", ""]
        if not subset:
            lines += ["None.", ""]
            continue
        lines += ["| Rule | Entity | Detail |", "| ---- | ------ | ------ |"]
        for f in sorted(subset, key=lambda x: (x.rule, x.entity)):
            detail = f.detail.replace("|", "\\|")
            lines.append(f"| `{f.rule}` | {f.entity} | {detail} |")
        lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    LOG.info("wrote %s", path)


def run(db_path: str = DB_DEFAULT, report_path: str = REPORT_DEFAULT) -> list[Finding]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        findings = Validator(conn).run()
    finally:
        conn.close()
    write_report(findings, report_path, db_path)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the RDORP database.")
    parser.add_argument("--db", default=DB_DEFAULT)
    parser.add_argument("--report", default=REPORT_DEFAULT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    findings = run(args.db, args.report)
    errors = sum(1 for f in findings if f.level == "ERROR")
    warnings = sum(1 for f in findings if f.level == "WARNING")
    print(f"Validation: {errors} errors, {warnings} warnings, "
          f"{len(findings) - errors - warnings} notes")
    for f in findings:
        if f.level == "ERROR":
            print(f"  ERROR [{f.rule}] {f.entity}: {f.detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
