#!/usr/bin/env python3
"""RDORP - regenerate every derived dataset from the master database.

MASTER_PROMPT requires CSV, SQLite and JSON to be generated from one master
and never edited by hand. Before this module existed there was no export step
at all: the CSV files under ``database/`` were empty stubs left over from an
earlier schema, two of them using an incompatible EV numbering scheme, and the
real data lived only inside the SQLite file.

Every file this module writes carries a ``_GENERATED.md`` marker alongside it
naming the generator, so that a file's status is unambiguous on disk.

Seed files are never overwritten. They are listed in ``SEED_FILES`` and are the
only CSV files under ``database/`` that may be edited by hand.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import shutil
import sqlite3
from datetime import date

LOG = logging.getLogger("rdorp.export")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")
EXPORT_DIR = os.path.join(ROOT, "exports")

#: Hand-maintained inputs to build_db.py. Never written by this module.
SEED_FILES = {
    "hypotheses.csv",
    "Evidence_Master_List_v1.csv",
    "evidence_register_v1.csv",
}

#: Tables exported in full, and the file name each one takes under database/.
#: The names on the left of the mapping are the ones MASTER_PROMPT and
#: DATA_DICTIONARY refer to, so those documented paths now hold real data.
TABLES = {
    "specimens": "specimens.csv",
    "artifact_observations": "artifact_observations.csv",
    "sources": "sources.csv",
    "evidence_register": "evidence_register.csv",
    "evidence_variables": "evidence_variables.csv",
    "evidence_sources": "evidence_sources.csv",
    "corpus_observations": "corpus_observations.csv",
    "hpm": "hpm.csv",
    "hdm_scores": "hdm_scores.csv",
    "results": "results.csv",
    "predictions": "predictions.csv",
    "experiments": "experiments.csv",
    "screening_candidates": "screening_candidates.csv",
    "screening": "screening.csv",
    "utility_assessments": "utility_assessments.csv",
    "specimen_quality": "specimen_quality.csv",
}


def _fetch(conn: sqlite3.Connection, table: str):
    cur = conn.execute(f'SELECT * FROM "{table}"')
    columns = [d[0] for d in cur.description]
    return columns, cur.fetchall()


def _write_csv(path: str, columns, rows) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def _write_json(path: str, columns, rows) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = [dict(zip(columns, row)) for row in rows]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def export_hdm_matrix(conn: sqlite3.Connection, paths: list[str]) -> None:
    """Write the discrimination matrix as one row per variable, one column per hypothesis."""
    hypotheses = [r[0] for r in conn.execute(
        "SELECT hypothesis_id FROM hypotheses ORDER BY hypothesis_id")]
    scores = {(r[0], r[1]): r[2] for r in conn.execute(
        "SELECT hypothesis_id, ev_id, weighted_score FROM hdm_scores")}
    variables = conn.execute(
        "SELECT ev_id, variable, category, discriminatory_power "
        "FROM evidence_variables ORDER BY ev_id"
    ).fetchall()
    directions = {r[0]: r[1] for r in conn.execute(
        "SELECT ev_id, direction FROM corpus_observations")}

    columns = ["ev_id", "variable", "category", "discriminatory_power",
               "corpus_direction"] + hypotheses
    rows = []
    for ev_id, name, category, power in variables:
        row = [ev_id, name, category, power, directions.get(ev_id, "")]
        row += [scores.get((h, ev_id), "") for h in hypotheses]
        rows.append(row)
    for path in paths:
        _write_csv(path, columns, rows)


def write_marker(directory: str, generator: str, files: list[str]) -> None:
    os.makedirs(directory, exist_ok=True)
    listing = "\n".join(f"- `{f}`" for f in sorted(files))
    text = (
        "# Generated files\n\n"
        f"Generated on {date.today().isoformat()} by `{generator}` from "
        "`database/rdorp.sqlite`.\n\n"
        "Do not edit these files. Change the master data in "
        "`database/build_db.py`, then re-run `python run_pipeline.py`.\n\n"
        f"{listing}\n"
    )
    with open(os.path.join(directory, "_GENERATED.md"), "w", encoding="utf-8") as fh:
        fh.write(text)


def run(db_path: str = DB_DEFAULT) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    written: dict[str, int] = {}
    try:
        csv_dir = os.path.join(EXPORT_DIR, "csv")
        json_dir = os.path.join(EXPORT_DIR, "json")
        sqlite_dir = os.path.join(EXPORT_DIR, "sqlite")

        for table, filename in TABLES.items():
            if filename in SEED_FILES:
                raise RuntimeError(
                    f"refusing to overwrite seed file {filename}"
                )
            columns, rows = _fetch(conn, table)
            _write_csv(os.path.join(HERE, filename), columns, rows)
            _write_csv(os.path.join(csv_dir, filename), columns, rows)
            _write_json(os.path.join(json_dir, f"{table}.json"), columns, rows)
            written[table] = len(rows)

        export_hdm_matrix(conn, [
            os.path.join(HERE, "hdm_matrix.csv"),
            os.path.join(csv_dir, "hdm_matrix.csv"),
        ])

        os.makedirs(sqlite_dir, exist_ok=True)
        shutil.copyfile(db_path, os.path.join(sqlite_dir, "rdorp.sqlite"))

        generated = list(TABLES.values()) + ["hdm_matrix.csv"]
        write_marker(csv_dir, "database/export.py", generated)
        write_marker(json_dir, "database/export.py",
                     [f"{t}.json" for t in TABLES])
        write_marker(sqlite_dir, "database/export.py", ["rdorp.sqlite"])
    finally:
        conn.close()
    LOG.info("exported %d tables", len(written))
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate RDORP exports.")
    parser.add_argument("--db", default=DB_DEFAULT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for table, count in run(args.db).items():
        print(f"  {table:25s} {count:5d} rows")


if __name__ == "__main__":
    main()
