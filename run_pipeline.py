#!/usr/bin/env python3
"""RDORP - run the whole pipeline in the one order that is correct.

    build_db.py    rebuild the master database from seed data
    score_hdm.py   score the HDM and write hdm_scores and results
    validate.py    check the datasets and write the validation report
    reports.py     write the analytical reports
    export.py      regenerate every CSV and JSON export

Order matters and used not to be enforced anywhere. ``build_db.py`` drops and
recreates ``hdm_scores``, so running it without re-scoring afterwards leaves the
analysis empty; and exporting before scoring writes empty score files. Running
this module is the only supported way to refresh the repository.

Every run appends to ``logs/import_log.md``. The pipeline stops if validation
reports an error.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "database"))

import build_db          # noqa: E402
import export            # noqa: E402
import reports           # noqa: E402
import score_hdm         # noqa: E402
import validate          # noqa: E402

LOG = logging.getLogger("rdorp.pipeline")
DB_PATH = os.path.join(ROOT, "database", "rdorp.sqlite")
LOG_PATH = os.path.join(ROOT, "logs", "import_log.md")


def table_counts(db_path: str) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {t: conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                for t in tables}
    finally:
        conn.close()


def append_log(entry: list[str]) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        if new:
            fh.write(
                "# Import Log\n\n"
                "Appended to by `run_pipeline.py`. One section per run. This is "
                "the only file in the repository that is written cumulatively "
                "rather than regenerated.\n"
            )
        fh.write("\n" + "\n".join(entry) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full RDORP pipeline.")
    parser.add_argument("--skip-validation-gate", action="store_true",
                        help="continue to export even if validation reports errors")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    started = datetime.now()
    entry = [f"## Run {started.isoformat(timespec='seconds')}", ""]

    LOG.info("step 1/5 build")
    build_db.build_database()

    LOG.info("step 2/5 score")
    report = score_hdm.run(DB_PATH)
    base = report["baseline"]

    LOG.info("step 3/5 validate")
    findings = validate.run(DB_PATH)
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARNING"]

    if errors and not args.skip_validation_gate:
        entry += [
            f"- **HALTED**: validation reported {len(errors)} errors.",
            "- Exports were NOT regenerated, so they still reflect the last "
            "clean run.",
            "",
        ]
        for f in errors[:20]:
            entry.append(f"  - `{f.rule}` {f.entity}: {f.detail}")
        append_log(entry)
        for f in errors:
            print(f"ERROR [{f.rule}] {f.entity}: {f.detail}")
        return 1

    LOG.info("step 4/5 reports")
    reports.run(DB_PATH)

    LOG.info("step 5/5 export")
    export.run(DB_PATH)

    counts = table_counts(DB_PATH)
    elapsed = (datetime.now() - started).total_seconds()

    entry += [
        f"- Completed in {elapsed:.1f} s",
        f"- Validation: {len(errors)} errors, {len(warnings)} warnings, "
        f"{len(findings) - len(errors) - len(warnings)} notes",
        f"- Scored {len(base.variables_used)} of {len(report['variables'])} "
        f"evidence variables; {len(report['unscored'])} have no corpus evidence",
        "- Ranking (weighted): "
        + "  >  ".join(f"{h} ({base.totals[h]:+.1f})" for h in base.ranking),
        "- Leader across all scenarios: "
        + ", ".join(sorted({s.leader for s in report["scenarios"]})),
        "",
        "| Table | Rows |",
        "| ----- | ---- |",
    ]
    entry += [f"| `{t}` | {n} |" for t, n in counts.items()]
    append_log(entry)

    print(f"\nPipeline complete in {elapsed:.1f} s")
    print(f"  validation : {len(errors)} errors, {len(warnings)} warnings")
    print(f"  scored     : {len(base.variables_used)}/{len(report['variables'])} variables")
    print("  ranking    : "
          + "  >  ".join(f"{h} ({base.totals[h]:+.1f})" for h in base.ranking))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
