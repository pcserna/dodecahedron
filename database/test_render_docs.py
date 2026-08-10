#!/usr/bin/env python3
"""Regression tests for the document renderer.

The renderer exists to stop a class of error that reached publication: a score
corrected in the database and not in the document. These tests prove it does.

Run: python database/test_render_docs.py
"""

from __future__ import annotations

import os
import shutil
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import render_docs as R  # noqa: E402

DB = R.DB_DEFAULT
DOC = R.DOC_DEFAULT
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def scratch_doc() -> str:
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    shutil.copyfile(DOC, path)
    return path


def test_idempotent() -> None:
    """Rendering twice must change nothing the second time."""
    doc = scratch_doc()
    try:
        R.render(DB, doc, check=False)
        again = R.render(DB, doc, check=False)
        check("rendering is idempotent", again == [], f"second pass rewrote {again}")
    finally:
        os.unlink(doc)


def test_check_is_clean_on_the_real_document() -> None:
    drifted = R.render(DB, DOC, check=True)
    check("the committed document is current", drifted == [],
          f"stale blocks: {drifted}")


def test_detects_a_hand_edit() -> None:
    """The whole point: a figure changed by hand must be caught."""
    doc = scratch_doc()
    try:
        R.render(DB, doc, check=False)
        with open(doc, encoding="utf-8") as fh:
            text = fh.read()
        start, end = R._span(text, "bands")
        body = text[start:end]
        # flip a score the way a careless hand-edit would
        tampered = body.replace("| **+23** |", "| **+99** |", 1)
        check("test set-up actually tampered with the table", tampered != body)
        with open(doc, "w", encoding="utf-8", newline="") as fh:
            fh.write(text[:start] + tampered + text[end:])

        drifted = R.render(DB, doc, check=True)
        check("check mode detects a hand-edited score", "bands" in drifted,
              f"drifted={drifted}")

        R.render(DB, doc, check=False)
        drifted = R.render(DB, doc, check=True)
        check("render mode repairs it", drifted == [])
    finally:
        os.unlink(doc)


def test_detects_a_changed_score() -> None:
    """A score that moves in the database must show up as document drift."""
    doc = scratch_doc()
    fd, db = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    shutil.copyfile(DB, db)
    try:
        R.render(DB, doc, check=False)
        con = sqlite3.connect(db)
        con.execute("UPDATE hpm SET prediction = '--' "
                    "WHERE hypothesis_id = 'H012' AND ev_id = 'EV004'")
        con.commit()
        con.close()
        drifted = R.render(db, doc, check=True)
        check("a changed prediction surfaces as document drift",
              "bands" in drifted, f"drifted={drifted}")
    finally:
        os.unlink(doc)
        os.unlink(db)


def test_prose_is_untouched() -> None:
    """Only the managed blocks may change."""
    doc = scratch_doc()
    try:
        with open(doc, encoding="utf-8") as fh:
            before = fh.read()
        R.render(DB, doc, check=False)
        with open(doc, encoding="utf-8") as fh:
            after = fh.read()

        def outside(text: str) -> str:
            for name in R.BLOCKS:
                s, e = R._span(text, name)
                text = text[:s] + "<<BLOCK>>" + text[e:]
            return text

        check("prose outside the markers is unchanged",
              outside(before) == outside(after))
    finally:
        os.unlink(doc)


def test_every_band_member_exists() -> None:
    con = sqlite3.connect(DB)
    known = {r[0] for r in con.execute("SELECT hypothesis_id FROM hypotheses")}
    con.close()
    declared = [h for _label, members in R.BANDS for h in members]
    check("every banded hypothesis exists", set(declared) <= known,
          f"unknown: {sorted(set(declared) - known)}")
    check("every hypothesis is banded exactly once",
          sorted(declared) == sorted(known),
          f"missing {sorted(known - set(declared))}, "
          f"duplicated {[h for h in set(declared) if declared.count(h) > 1]}")


def test_every_referenced_cell_exists() -> None:
    """The cross-references in RDORP-012 must point at cells that exist.

    A renamed cell id would otherwise leave every link in the reproduction
    index pointing at nothing, and a dead anchor in a markdown file is silent.
    """
    import json
    nb_path = os.path.join(os.path.dirname(R.CELL_INDEX), "RDORP_Reproduction.ipynb")
    if not (os.path.exists(R.CELL_INDEX) and os.path.exists(nb_path)):
        check("notebook and cell index exist", False,
              "run `python notebooks/build_notebook.py`")
        return
    with open(nb_path, encoding="utf-8") as fh:
        ids = {c.get("id") for c in json.load(fh)["cells"]}
    entries = R.load_cell_index()
    missing = sorted({e["cell"] for e in entries} - ids)
    check("every indexed cell exists in the notebook", not missing,
          f"missing: {missing}")
    check("the index is not empty", len(entries) > 0, f"{len(entries)} entries")

    with open(DOC, encoding="utf-8") as fh:
        doc = fh.read()
    linked = set(re.findall(r"RDORP_Reproduction\.ipynb#cell-([\w-]+)", doc))
    dead = sorted(linked - ids)
    check("every link in the document resolves to a cell", not dead,
          f"dead anchors: {dead}")


def test_notebook_was_executed() -> None:
    """A committed notebook with no outputs proves nothing."""
    import json
    nb_path = os.path.join(os.path.dirname(R.CELL_INDEX), "RDORP_Reproduction.ipynb")
    if not os.path.exists(nb_path):
        return
    with open(nb_path, encoding="utf-8") as fh:
        cells = [c for c in json.load(fh)["cells"] if c["cell_type"] == "code"]
    ran = [c for c in cells if c.get("outputs")]
    check("the committed notebook carries its outputs",
          len(ran) >= len(cells) - 1,
          f"{len(ran)} of {len(cells)} code cells have output")


def test_no_cell_errored() -> None:
    """No cell may have produced an error, and none may be silently empty.

    A cell whose source got mangled at build time can execute to nothing and
    look fine in a diff. That happened: an escaped newline became a real one,
    the cell raised, and the only symptom was an empty output.
    """
    import json
    nb_path = os.path.join(os.path.dirname(R.CELL_INDEX), "RDORP_Reproduction.ipynb")
    if not os.path.exists(nb_path):
        return
    with open(nb_path, encoding="utf-8") as fh:
        cells = [c for c in json.load(fh)["cells"] if c["cell_type"] == "code"]
    errored = [c.get("id") for c in cells
               if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
    check("no cell produced an error", not errored, f"errored: {errored}")

    empty = [c.get("id") for c in cells
             if "".join(c["source"]).strip() and not c.get("outputs")]
    check("no executed cell is silently empty", not empty, f"empty: {empty}")


def main() -> int:
    if not (os.path.exists(DB) and os.path.exists(DOC)):
        print("database or document missing; run run_pipeline.py first")
        return 2
    print("Document renderer regression tests\n")
    test_idempotent()
    test_check_is_clean_on_the_real_document()
    test_detects_a_hand_edit()
    test_detects_a_changed_score()
    test_prose_is_untouched()
    test_every_band_member_exists()
    test_every_referenced_cell_exists()
    test_notebook_was_executed()
    test_no_cell_errored()
    print(f"\n{len(FAILURES)} failure(s)"
          + (": " + ", ".join(FAILURES) if FAILURES else ""))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
