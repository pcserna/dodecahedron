#!/usr/bin/env python3
"""RDORP - regenerate the derived tables inside the prose documents.

Why this exists
---------------
``reports/`` is generated from the database on every run and is always current.
``docs/RDORP-012_Results_Summary.md`` was not: its two hundred-odd figures were
typed by hand, and every rework of that document found stale ones. The worst
case reached publication - after the cluster tie-break was corrected, five
hypotheses in the results table still carried their pre-correction scores,
because the fix was applied to two rows by hand and the other five were missed.

This module removes that class of error. Each derived table in the document
sits between a pair of sentinel comments::

    <!-- RDORP:BEGIN bands -->
    ...generated content, overwritten on every run...
    <!-- RDORP:END bands -->

Everything outside the sentinels is prose and is never touched. Everything
inside is computed from the database and can be regenerated or verified.

Two modes
---------
``render``  rewrite each managed block from the database (the default).
``check``   verify without writing, and exit non-zero on any drift. The
            pipeline runs this so a hand-edit inside a managed block is caught
            rather than silently overwritten later.

What is NOT generated
---------------------
Band membership. Which band a hypothesis belongs in is a judgement about
evidential quality, not a number: H013 outscores H003 on clustered evidence and
still sits a band lower, because it staked 53 points to their 22. That
judgement is declared in ``BANDS`` below with its reasoning, and the renderer
reports any score inversion it creates so the judgement stays visible rather
than quietly decaying as scores move.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import score_hdm as S  # noqa: E402
import reports as R  # noqa: E402

#: The denominator for every coverage figure, defined once. reports/ and
#: RDORP-012 used to carry 134 and 129 respectively, so the same corpus was
#: 45 per cent covered in one file and 47 per cent in the other.
KNOWN_CORPUS = R.KNOWN_CORPUS

LOG = logging.getLogger("rdorp.render")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")
DOC_DEFAULT = os.path.join(ROOT, "docs", "RDORP-012_Results_Summary.md")

BEGIN = "<!-- RDORP:BEGIN {name} -->"
END = "<!-- RDORP:END {name} -->"

#: The tie rule used for every clustered figure the document reports. Stated
#: here rather than left to the default so the document and the reports cannot
#: drift apart silently (RDORP-013 A16).
TIE_RULE = "conservative"

#: Band membership - a judgement, not a computation. See the module docstring.
#: Order is the order the document presents them in.
BANDS: list[tuple[str, list[str]]] = [
    ("**Leading pair**", ["H012", "H014"]),
    ("**Consistent but weakly testable**", ["H003", "H008"]),
    ("**Partly supported**", ["H013", "H005"]),
    ("**Unsupported**", ["H001", "H004", "H002", "H006", "H007"]),
    ("**Refuted**", ["H010", "H011"]),
    ("**Eliminated**", ["H009"]),
]

#: Hypotheses whose row is emphasised in the results table.
EMPHASISE = {"H012", "H014", "H009"}

#: Rows shown in the clustering table of section 2.7. The full fourteen are in
#: reports/hdm_analysis.md; this table exists to show where the correction
#: falls, so it shows the leaders and the largest movers in both directions.
CLUSTER_TABLE_ROWS = ["H012", "H014", "H013", "H005", "H002", "H010", "H009"]

MINUS = "−"  # the document uses a true minus sign, not a hyphen


def sgn(x: float, dp: int = 1) -> str:
    return f"{x:+.{dp}f}".replace("-", MINUS)


def short_name(name: str) -> str:
    """First clause of a hypothesis name, for a narrow table column."""
    return name.split("/")[0].split("(")[0].strip()


class Facts:
    """Everything the managed blocks need, computed once."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        conn.row_factory = sqlite3.Row
        self.conn = conn
        (self.hypotheses, self.variables, self.hpm, self.corpus,
         self.readings, self.clusters) = S.load(conn)
        self.names = {r["hypothesis_id"]: r["name"]
                      for r in conn.execute("SELECT * FROM hypotheses")}
        self.cells = S.score_all(self.hypotheses, self.variables, self.hpm,
                                 self.corpus, self.readings)
        self.unclustered = S.totals(self.cells, self.hypotheses)
        self.clustered = S.totals(self.cells, self.hypotheses,
                                  clusters=self.clusters, tie_rule=TIE_RULE)
        self.scored = S.scorable(self.corpus, self.readings, self.hypotheses)
        self.commitment = S.commitment(self.hypotheses, self.variables, self.hpm,
                                       self.corpus, self.readings,
                                       sorted(self.scored))
        self.value = {r["subject_id"]: (r["product_value"] or 0)
                      + (r["craft_value"] or 0) + (r["experience_value"] or 0)
                      for r in conn.execute(
                          "SELECT * FROM utility_assessments "
                          "WHERE subject_type = 'hypothesis'")}

    def one(self, sql: str) -> int:
        return self.conn.execute(sql).fetchone()[0]

    def rank(self, clustered: bool = True) -> dict[str, int]:
        t = self.clustered if clustered else self.unclustered
        return {h: i + 1 for i, h in enumerate(sorted(t, key=lambda x: -t[x]))}


# --- block builders ---------------------------------------------------------
# Each returns the markdown that replaces the body of its managed block.

def block_composition(f: Facts) -> str:
    specimens = f.one("SELECT COUNT(*) FROM specimens")
    observations = f.one("SELECT COUNT(*) FROM artifact_observations")
    consulted = f.one("SELECT COUNT(*) FROM sources WHERE confidence IN ('A','B')")
    rows = [
        ("Specimens recorded", str(specimens)),
        ("Known corpus", f"116 by 2016 (`PUB-0051`), 129 catalogued to 2021 "
                        f"(`PUB-0023`), c {KNOWN_CORPUS} by 2025 (`PUB-0003`)"),
        ("Coverage", f"{round(100 * specimens / KNOWN_CORPUS)} % of "
                     f"c {KNOWN_CORPUS}"),
        ("Sourced observations", str(observations)),
        ("Sources", f"{f.one('SELECT COUNT(*) FROM sources')}, of which "
                    f"{consulted} are graded A or B"),
        ("Evidence variables", str(f.one("SELECT COUNT(*) FROM evidence_variables"))),
        ("Hypotheses assessed", str(len(f.hypotheses))),
        ("Functional domains screened", str(f.one("SELECT COUNT(*) FROM screening_candidates"))),
        ("Experiments recorded", str(f.one("SELECT COUNT(*) FROM experiments"))),
        ("Pre-registered predictions", str(f.one("SELECT COUNT(*) FROM predictions"))),
        ("Countries represented", str(f.one(
            "SELECT COUNT(DISTINCT country) FROM specimens "
            "WHERE country IS NOT NULL AND country <> ''"))),
        ("Evidence variables scored", f"{len(f.scored)} of "
                                      f"{f.one('SELECT COUNT(*) FROM evidence_variables')}"),
    ]
    return "\n".join(f"| {k} | {v} |" for k, v in rows)


#: Provenance grades, in order, with the definition the document prints.
PROVENANCE_GRADES = [
    ("A", "Excavated from a stratified, dated deposit"),
    ("B", "Excavated or reported find, documented findspot, institutional custody"),
    ("C", "Findspot recorded, surface or detector find"),
    ("D", "Institutional custody, no findspot"),
    ("E", "Private hands, or no findspot and no independent publication"),
]

#: Admissibility rules, with the requirement text and the column that records it.
ADMISSIBILITY_RULES = [
    ("Mass", "completeness = complete", "admit_mass"),
    ("Geometry",
     "completeness ∈ {complete, incomplete} and measurement ∈ {direct, one remove}",
     "admit_geometry"),
    ("Context", "recorded findspot and provenance ≤ D", "admit_context"),
]


def block_quality(f: Facts) -> str:
    counts = {r["provenance_grade"]: r["c"] for r in f.conn.execute(
        "SELECT provenance_grade, COUNT(*) c FROM specimen_quality GROUP BY 1")}
    out = ["| Provenance grade | Meaning | Count |",
           "| ---------------- | ------- | ----- |"]
    for grade, meaning in PROVENANCE_GRADES:
        out.append(f"| {grade} | {meaning} | {counts.get(grade, 0)} |")
    return "\n".join(out)


def block_admissibility(f: Facts) -> str:
    total = f.one("SELECT COUNT(*) FROM specimens")
    out = ["| Rule | Requirement | Admissible |",
           "| ---- | ----------- | ---------- |"]
    for label, requirement, col in ADMISSIBILITY_RULES:
        n = f.one(f"SELECT COUNT(*) FROM specimen_quality WHERE {col} = 1")
        out.append(f"| **{label}** | {requirement} | **{n} of {total}** |")
    return "\n".join(out)


def block_concentration(f: Facts) -> str:
    total = f.one("SELECT COUNT(*) FROM artifact_observations")
    rows = f.conn.execute(
        "SELECT source_id, COUNT(*) c FROM artifact_observations "
        "GROUP BY 1 ORDER BY c DESC LIMIT 2").fetchall()
    top, second = rows[0], rows[1]
    two = round(100 * (top["c"] + second["c"]) / total)
    return (f"**Source concentration.** {round(100 * top['c'] / total)} % of all "
            f"{total} observations come from a single source, `{top['source_id']}`, "
            f"the British Portable Antiquities Scheme database of metal-detector "
            f"surface finds. Together with `{second['source_id']}`, two sources "
            f"account for {two} %.")


def block_bands(f: Facts) -> str:
    out = ["| Band | Hypothesis | Clustered | Unclustered | Staked | Value |",
           "| ---- | ---------- | --------- | ----------- | ------ | ----- |"]
    for label, members in BANDS:
        for i, h in enumerate(members):
            b = "**" if h in EMPHASISE else ""
            out.append(
                f"| {label if i == 0 else ''} | {h} {f.names[h]} | "
                f"{b}{sgn(f.clustered[h], 0)}{b} | {sgn(f.unclustered[h], 0)} | "
                f"{f.commitment[h]['max_possible']:.0f} | "
                f"{sgn(f.value.get(h, 0), 0)} |")
    return "\n".join(out)


def block_clustering(f: Facts) -> str:
    ru, rc = f.rank(clustered=False), f.rank(clustered=True)
    out = ["| Hypothesis | Unclustered | Clustered | Shift |",
           "| ---------- | ----------- | --------- | ----- |"]
    for h in CLUSTER_TABLE_ROWS:
        b = "**" if h in ("H012", "H014") else ""
        shift = f.clustered[h] - f.unclustered[h]
        out.append(f"| {b}{h} {short_name(f.names[h])}{b} | "
                   f"{sgn(f.unclustered[h])} ({ru[h]}) | "
                   f"{b}{sgn(f.clustered[h])} ({rc[h]}){b} | {sgn(shift)} |")
    return "\n".join(out)


#: The finding -> notebook-cell map, written by notebooks/build_notebook.py.
CELL_INDEX = os.path.join(ROOT, "notebooks", "cell_index.json")
NOTEBOOK_REL = "../notebooks/RDORP_Reproduction.ipynb"


def load_cell_index() -> list[dict]:
    if not os.path.exists(CELL_INDEX):
        return []
    with open(CELL_INDEX, encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def block_reproduction(f: Facts) -> str:
    """The cross-reference table: every finding, and the cell that recomputes it.

    Links are anchors into the executed notebook. GitHub and nbviewer render
    `<file>.ipynb#cell-<id>` as a jump to that cell, so a reader can go from a
    claim in this document to the code that produced it in one click.
    """
    entries = load_cell_index()
    if not entries:
        return ("*No reproduction index found. Run "
                "`python notebooks/build_notebook.py` to generate it.*")
    out = ["| Finding | Reproduced in | Cell |",
           "| ------- | ------------- | ---- |"]
    last_part = None
    for e in entries:
        part = e["part"]
        shown = part if part != last_part else ""
        last_part = part
        out.append(f"| {e['finding']} | {shown} | "
                   f"[`{e['cell']}`]({NOTEBOOK_REL}#cell-{e['cell']}) |")
    return "\n".join(out)



# --- blocks added by the coverage audit -------------------------------------

#: Short labels for the scenario keys. The scenario definitions carry a full
#: sentence, which is right in the generated report and too long for a table.
SCENARIO_LABELS = {
    "baseline": "Baseline, fully weighted",
    "observed_only": "Archaeological observations only",
    "high_confidence": "Confidence A-C only",
    "very_high_power": "Very High power variables only",
    "clustered": "Clustered, ties resolved against the hypothesis",
    "clustered_favourable": "Clustered, ties resolved in its favour",
    "unweighted": "Unweighted",
    "multi_source": "Corroborated variables only",
    "same_footing": "Per-cell readings ignored",
}

#: What the screen DID with each candidate, as against what its score alone
#: would imply. These are decisions, not computations: C-10 was promoted to a
#: full hypothesis despite two hard contradictions, and C-12 was held back
#: despite the highest score in the screen because it is the generalisation of
#: a hypothesis already under test. The rule that produced the raw verdict is
#: known to be crude (RDORP-013 A7).
SCREEN_DECISIONS = {
    "C-10": "promoted to H014",
    "C-12": "held back - see 6.2",
    "C-15": "eliminated by computation",
    "C-14": "eliminated by computation",
    "C-17": "eliminated by precision",
    "C-05": "eliminated by computation",
    "C-01": "eliminated by computation",
}

def block_scenarios(f: Facts) -> str:
    """Every inclusion scenario and its leader (section 5.4)."""
    scs = S.build_scenarios(f.hypotheses, f.variables, f.hpm, f.corpus,
                            f.readings, sources=S.source_counts(f.conn),
                            clusters=f.clusters)
    out = ["| Scenario | Leader |", "| -------- | ------ |"]
    for sc in scs:
        lead = max(sc.totals, key=lambda h: sc.totals[h])
        emph = "**" if lead != "H012" else ""
        label = SCENARIO_LABELS.get(sc.key, sc.label)
        out.append(f"| {emph}{label}{emph} | {emph}{lead} "
                   f"({sgn(sc.totals[lead])}){emph} |")
    return "\n".join(out)


def block_multi_source(f: Facts) -> str:
    """Baseline vs corroborated-only (section 2.8)."""
    srcs = S.source_counts(f.conn)
    multi = {e for e in f.scored if srcs.get(e, 0) >= 2}
    cells = S.score_all(f.hypotheses, f.variables, f.hpm, f.corpus,
                        f.readings, include=multi)
    t = S.totals(cells, f.hypotheses)
    ru = f.rank(clustered=False)
    rm = {h: i + 1 for i, h in enumerate(sorted(t, key=lambda x: -t[x]))}
    rows = sorted(f.hypotheses, key=lambda h: -(t[h] - f.unclustered[h]))[:8]
    out = [f"| Hypothesis | Baseline | Corroborated only ({len(multi)} variables) | Shift |",
           "| ---------- | -------- | ----------------- | ----- |"]
    for h in rows:
        d = t[h] - f.unclustered[h]
        b = "**" if abs(d) >= 2.5 else ""
        out.append(f"| {b}{h} {short_name(f.names[h])}{b} | "
                   f"{sgn(f.unclustered[h])} ({ru[h]}) | "
                   f"{b}{sgn(t[h])} ({rm[h]}){b} | {b}{sgn(d)}{b} |")
    return "\n".join(out)


def block_tie_rules(f: Facts) -> str:
    """What each tie rule gives the leading pair (section 2.7)."""
    order = ["conservative", "mean_tied", "mean_all", "favourable"]
    label = {"conservative": "Conservative *(adopted)*",
             "mean_tied": "Mean of the tied cells",
             "mean_all": "Mean of all cells in the cluster",
             "favourable": "Favourable *(the accidental behaviour)*"}
    out = ["| Tie rule | H012 | H014 | Leader |",
           "| -------- | ---- | ---- | ------ |"]
    for rule in order:
        t = S.totals(f.cells, f.hypotheses, clusters=f.clusters, tie_rule=rule)
        lead = max(t, key=lambda h: t[h])
        b = "**" if rule == "conservative" else ""
        out.append(f"| {label[rule]} | {b}{sgn(t['H012'])}{b} | "
                   f"{b}{sgn(t['H014'])}{b} | {b}{lead}{b} |")
    return "\n".join(out)


def block_screening(f: Facts) -> str:
    """The sixteen screened functional domains (section 6.1)."""
    rows = S.screen(f.conn, f.variables, f.corpus)
    rows.sort(key=lambda r: -r["total"])
    out = ["| ID | Candidate | Domain | Score | Hard contradictions | Verdict |",
           "| -- | --------- | ------ | ----- | ------------------- | ------- |"]
    for r in rows:
        b = "**" if r["total"] > 0 else ""
        decision = SCREEN_DECISIONS.get(r["candidate_id"], r["verdict"].lower())
        out.append(f"| {r['candidate_id']} | {r['name']} | {r['domain']} | "
                   f"{b}{sgn(r['total'])}{b} | {r['hard']} | {decision} |")
    return "\n".join(out)


def block_bounds(f: Facts) -> str:
    """Best and worst case over the unscored variables (section 5.5)."""
    bnd = S.bounds(f.hypotheses, f.variables, f.hpm, f.corpus)
    rows = bnd[0] if isinstance(bnd, tuple) else bnd
    out = ["| Hypothesis | Current | Worst case | Best case | Robust |",
           "| ---------- | ------- | ---------- | --------- | ------ |"]
    for h in sorted(f.hypotheses, key=lambda x: -f.unclustered[x])[:6]:
        r = rows[h] if isinstance(rows, dict) else None
        if r is None:
            continue
        worst = r["worst"] if isinstance(r, dict) else r[0]
        best = r["best"] if isinstance(r, dict) else r[1]
        out.append(f"| {h} {short_name(f.names[h])} | {sgn(f.unclustered[h])} | "
                   f"{sgn(worst)} | {sgn(best)} | no |")
    return "\n".join(out)


def block_rejections(f: Facts) -> str:
    """What the rejections did to the measured ranges (section 2.5)."""
    def rng(col, admit):
        rows = [r[0] for r in f.conn.execute(
            f"SELECT s.{col} FROM specimens s JOIN specimen_quality q "
            f"ON q.rd_id = s.rd_id WHERE s.{col} IS NOT NULL"
            + (f" AND q.{admit} = 1" if admit else ""))]
        return (min(rows), max(rows), len(rows)) if rows else None

    out = ["| Statistic | All recorded | Admissible only |",
           "| --------- | ------------ | --------------- |"]
    lo, hi, n = rng("max_diameter_mm", None)
    alo, ahi, an = rng("max_diameter_mm", "admit_geometry")
    out.append(f"| Overall diameter | {lo:.1f}–{hi:.1f} mm, ratio "
               f"{hi/lo:.2f}:1 (n = {n}) | **{alo:.1f}–{ahi:.1f} mm, ratio "
               f"{ahi/alo:.2f}:1** (n = {an}) |")
    lo, hi, n = rng("weight_g", None)
    alo, ahi, an = rng("weight_g", "admit_mass")
    out.append(f"| Mass | {lo:.1f}–{hi:.1f} g (n = {n}) | "
               f"**{alo:.1f}–{ahi:.1f} g** (n = {an}) |")
    lo, hi, n = rng("wall_thickness_mm", None)
    out.append(f"| Wall thickness | {lo:.1f}–{hi:.1f} mm (n = {n}) | "
               f"not separately restricted |")
    return "\n".join(out)


BLOCKS = {
    "composition": block_composition,
    "quality": block_quality,
    "admissibility": block_admissibility,
    "concentration": block_concentration,
    "bands": block_bands,
    "clustering": block_clustering,
    "reproduction": block_reproduction,
    "scenarios": block_scenarios,
    "multi_source": block_multi_source,
    "tie_rules": block_tie_rules,
    "screening": block_screening,
    "rejections": block_rejections,
}


# --- band consistency -------------------------------------------------------

def band_inversions(f: Facts) -> list[str]:
    """Report hypotheses that outscore one placed in a higher band.

    Not an error - H013 does this deliberately, on the grounds that a score
    earned by predicting a great deal is not the same result as one earned by
    predicting almost nothing. It is reported so that the judgement is
    revisited when the scores move rather than decaying unnoticed.
    """
    order = [(label, h) for label, members in BANDS for h in members]
    out = []
    for i, (label_a, a) in enumerate(order):
        for label_b, b in order[i + 1:]:
            if label_a != label_b and f.clustered[b] > f.clustered[a] + 1e-9:
                out.append(f"{b} ({sgn(f.clustered[b])}, {label_b.strip('*')}) "
                           f"outscores {a} ({sgn(f.clustered[a])}, "
                           f"{label_a.strip('*')})")
    return out


# --- the renderer -----------------------------------------------------------

def _span(text: str, name: str) -> tuple[int, int]:
    b, e = BEGIN.format(name=name), END.format(name=name)
    if text.count(b) != 1 or text.count(e) != 1:
        raise ValueError(
            f"document must contain exactly one {b} and one {e}; "
            f"found {text.count(b)} and {text.count(e)}")
    start = text.index(b) + len(b)
    end = text.index(e)
    if end < start:
        raise ValueError(f"{e} appears before {b}")
    return start, end


def render(db_path: str = DB_DEFAULT, doc_path: str = DOC_DEFAULT,
           check: bool = False) -> list[str]:
    """Rewrite (or verify) every managed block. Returns the names that drifted."""
    conn = sqlite3.connect(db_path)
    try:
        facts = Facts(conn)

        with open(doc_path, encoding="utf-8") as fh:
            text = fh.read()

        drifted = []
        for name, build in BLOCKS.items():
            start, end = _span(text, name)
            wanted = "\n" + build(facts).strip() + "\n"
            if text[start:end] != wanted:
                drifted.append(name)
                text = text[:start] + wanted + text[end:]

        for note in band_inversions(facts):
            LOG.info("band note: %s", note)
    finally:
        conn.close()

    if drifted and not check:
        with open(doc_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        LOG.info("rewrote %d block(s): %s", len(drifted), ", ".join(drifted))
    elif drifted:
        LOG.warning("%d block(s) differ from the database: %s",
                    len(drifted), ", ".join(drifted))
    else:
        LOG.info("all %d managed block(s) already current", len(BLOCKS))
    return drifted


def run(db_path: str = DB_DEFAULT, doc_path: str = DOC_DEFAULT) -> list[str]:
    return render(db_path, doc_path, check=False)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate the derived tables inside RDORP-012.")
    ap.add_argument("--db", default=DB_DEFAULT)
    ap.add_argument("--doc", default=DOC_DEFAULT)
    ap.add_argument("--check", action="store_true",
                    help="verify without writing; exit 1 on drift")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    drifted = render(args.db, args.doc, check=args.check)
    if args.check and drifted:
        print("STALE: " + ", ".join(drifted))
        print("Run `python database/render_docs.py` to bring the document current.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
