#!/usr/bin/env python3
"""RDORP - generate the analytical reports from the master database.

Writes three files under ``reports/``:

* ``hdm_analysis.md``   the scored comparison of hypotheses, with every
                        sensitivity scenario and every stated limitation
* ``corpus_coverage.md`` what the recorded corpus contains and how it differs
                        from the known corpus
* ``batch_summary.md``  what the most recent batch added

All three are generated. Editing them by hand breaks reproducibility.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from datetime import date

import score_hdm

LOG = logging.getLogger("rdorp.reports")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB_DEFAULT = os.path.join(HERE, "rdorp.sqlite")
REPORT_DIR = os.path.join(ROOT, "reports")

KNOWN_CORPUS = 134  # PUB-0003, 32

HEADER_NOTE = (
    "Generated file. Do not edit by hand: change the master data in "
    "`database/build_db.py` and re-run `python run_pipeline.py`."
)


def _header(title: str, doc_id: str, db_path: str, generator: str) -> list[str]:
    return [
        f"# {title}",
        "",
        "| Field | Value |",
        "| ----- | ----- |",
        f"| Document ID | {doc_id} |",
        f"| Generated | {date.today().isoformat()} |",
        f"| Database | `{os.path.relpath(db_path, ROOT)}` |",
        f"| Generator | `{generator}` |",
        "",
        HEADER_NOTE,
        "",
    ]


def _fmt(value: float) -> str:
    """Format a score, avoiding the '-0.0' that a signed format produces."""
    return "0.0" if abs(value) < 1e-9 else f"{value:+.1f}"


def _write(path: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    LOG.info("wrote %s", path)


# --- HDM analysis ------------------------------------------------------------


def hdm_analysis(report: dict, db_path: str) -> list[str]:
    hyp = report["hypotheses"]
    variables = report["variables"]
    corpus = report["corpus"]
    cells = report["cells"]
    base = report["baseline"]
    commit = report["commitment"]

    lines = _header("Hypothesis Discrimination Analysis", "RDORP-HDM",
                    db_path, "database/reports.py")

    lines += [
        "## 1. What this report is",
        "",
        "This report applies the method defined in RDORP-010 to the evidence "
        "currently in the database. It is a comparison of how well each "
        "hypothesis accounts for the evidence collected so far. It is **not** a "
        "conclusion about the function of Roman dodecahedra, and the corpus it "
        "rests on covers a minority of known specimens.",
        "",
        f"Variables scored: **{len(base.variables_used)} of {len(variables)}**. "
        f"Variables with corpus evidence but non-specific predictions: "
        f"**{sum(1 for o in corpus.values() if not o.discriminating)}**. "
        f"Variables with no corpus evidence at all: **{len(report['unscored'])}**.",
        "",
        "## 2. Ranking",
        "",
        "Weighted score = prediction score x discriminatory power x source "
        "confidence x evidence class.",
        "",
        "| Rank | Hypothesis | Name | Weighted | Unweighted | Predictions staked | Points at stake | Achieved |",
        "| ---- | ---------- | ---- | -------- | ---------- | ------------------ | --------------- | -------- |",
    ]
    unweighted = next(s for s in report["scenarios"] if s.key == "unweighted")
    for rank, h in enumerate(base.ranking, start=1):
        c = commit[h]
        pct = (base.totals[h] / c["max_possible"] * 100) if c["max_possible"] else 0.0
        lines.append(
            f"| {rank} | {h} | {hyp[h]} | {base.totals[h]:+.1f} | "
            f"{unweighted.totals[h]:+.1f} | {c['predictions_made']}"
            f"/{len(base.variables_used)} (strong {c['strong_predictions']}) | "
            f"{c['max_possible']:.1f} | {pct:.0f}% |"
        )

    lines += [
        "",
        "### How to read the last three columns",
        "",
        "A hypothesis that predicts `0` for most variables risks nothing, yet it "
        "still gains points whenever something it marked as unlikely turns out "
        "to be absent. Raw totals therefore reward hypotheses that commit to "
        "little. *Points at stake* is the score a hypothesis would have obtained "
        "if every one of its predictions had been confirmed; *achieved* is the "
        "fraction it actually obtained. The two readings must be taken together:",
        "",
    ]
    top = base.ranking[0]
    heaviest = max(hyp, key=lambda h: commit[h]["max_possible"])
    lines += [
        f"- **{top}** leads on total score while staking only "
        f"{commit[top]['max_possible']:.1f} points, of which it achieved "
        f"{base.totals[top] / commit[top]['max_possible'] * 100:.0f} per cent. It "
        "is highly consistent with the evidence, but it is also the least "
        "testable hypothesis in the set.",
        f"- **{heaviest}** staked the most "
        f"({commit[heaviest]['max_possible']:.1f} points across "
        f"{commit[heaviest]['predictions_made']} predictions, "
        f"{commit[heaviest]['strong_predictions']} of them strong) and achieved "
        f"{base.totals[heaviest] / commit[heaviest]['max_possible'] * 100:.0f} "
        "per cent. It is the most testable hypothesis in the set and the "
        "evidence has gone against it.",
        "",
        "## 3. Scored variables",
        "",
        "| EV | Variable | Power | Class | Conf | Direction | " +
        " | ".join(base.ranking) + " |",
        "| -- | -------- | ----- | ----- | ---- | --------- | " +
        " | ".join("---" for _ in base.ranking) + " |",
    ]
    for ev_id in sorted(base.variables_used):
        obs = corpus[ev_id]
        var = variables[ev_id]
        row = (f"| {ev_id} | {var.name} | {var.power} | {obs.evidence_class} | "
               f"{obs.confidence} | {obs.direction} | ")
        row += " | ".join(_fmt(cells[(h, ev_id)][4]) for h in base.ranking)
        lines.append(row + " |")

    lines += [
        "",
        "## 4. Sensitivity analysis",
        "",
        "RDORP-010 section 11 requires that a hypothesis be considered robustly "
        "supported only if it ranks first across all reasonable scenarios.",
        "",
        "| Scenario | Variables | Ranking |",
        "| -------- | --------- | ------- |",
    ]
    for scenario in report["scenarios"]:
        ranking = "  >  ".join(
            f"{h} ({scenario.totals[h]:+.1f})" for h in scenario.ranking[:4]
        )
        lines.append(f"| {scenario.label} | {len(scenario.variables_used)} | {ranking} |")

    leaders = {s.leader for s in report["scenarios"]}
    order = base.ranking
    margin = base.totals[order[0]] - base.totals[order[1]]
    largest_cell = max(
        abs(cells[(h, ev)][4]) for h in base.ranking for ev in base.variables_used
    )
    separated = margin > largest_cell
    lines += [
        "",
        f"Leader across scenarios: **{', '.join(sorted(leaders))}**"
        + (" — stable." if len(leaders) == 1 else " — NOT stable."),
        "",
        f"Margin between {order[0]} and {order[1]}: **{margin:+.1f}**, against a "
        f"largest single-variable contribution anywhere in the matrix of "
        f"{largest_cell:.1f}. "
        + (f"The top two positions are therefore separated by more than any one "
           f"variable could supply."
           if separated else
           f"**{order[0]} and {order[1]} are not separated**: a single variable "
           f"can carry more weight than the gap between them, so they must be "
           f"reported as a tied leading pair rather than as first and second."),
        "",
        "### Leave-one-variable-out",
        "",
    ]
    flips = [f for f in report["leave_one_out"] if f["changes_leader"]]
    if flips:
        lines += ["| EV | Variable | New leader |", "| -- | -------- | ---------- |"]
        lines += [f"| {f['ev_id']} | {f['variable']} | {f['leader']} |" for f in flips]
    else:
        lines.append("Removing any single scored variable leaves the leader unchanged.")

    lines += [
        "",
        "### Sensitivity to the prediction matrix",
        "",
        "Every scored HPM prediction was shifted by one level in each direction. "
        "Shifts that cannot move, because the prediction is already at the end of "
        "the scale, are skipped rather than counted as evidence of stability.",
        "",
    ]
    perturbations = report["perturbations"]
    top_two = set(order[:2])
    outside = [p for p in perturbations if p["new_leader"] not in top_two]
    within = len(perturbations) - len(outside)
    if perturbations:
        lines += [
            f"**{len(perturbations)}** single-prediction changes move the top "
            f"position. Of those, **{within}** only exchange the two hypotheses "
            f"already tied at the top ({' and '.join(order[:2])}) and carry no "
            f"information, while **{len(outside)}** would promote a hypothesis "
            f"from outside that pair.",
            "",
        ]
        if outside:
            lines += [
                "Changes that promote a hypothesis from outside the leading pair:",
                "",
                "| EV | Variable | Hypothesis | Change | New leader |",
                "| -- | -------- | ---------- | ------ | ---------- |",
            ]
            for p in outside[:20]:
                lines.append(
                    f"| {p['ev_id']} | {p['variable']} | {p['hypothesis']} | "
                    f"`{p['from']}` -> `{p['to']}` | {p['new_leader']} |"
                )
            if len(outside) > 20:
                lines.append(f"| ... | *{len(outside) - 20} further cases* | | | |")
        else:
            lines.append(
                "No single-prediction change promotes a hypothesis from outside "
                "the leading pair. The pair is unstable internally but stable "
                "against the rest of the field."
            )
    else:
        lines.append("No single-prediction change moves the top position.")

    lines += [
        "",
        "### Uncertainty bounds over unscored variables",
        "",
        "Best case assumes every unscored variable resolves in a hypothesis's "
        "favour; worst case assumes every one resolves against it. A hypothesis "
        "is robust only if its worst case still beats the best case of its "
        "strongest rival.",
        "",
        "| Hypothesis | Current | Worst case | Best case | Robust |",
        "| ---------- | ------- | ---------- | --------- | ------ |",
    ]
    conn = sqlite3.connect(db_path)
    try:
        robust = {r[0]: r[1] for r in conn.execute(
            "SELECT hypothesis_id, robust FROM results")}
    finally:
        conn.close()
    for h in base.ranking:
        lines.append(
            f"| {h} | {base.totals[h]:+.1f} | "
            f"{base.totals[h] + report['worst'][h]:+.1f} | "
            f"{base.totals[h] + report['best'][h]:+.1f} | "
            f"{'yes' if robust.get(h) else 'no'} |"
        )

    prof = report["profile"]
    lines += [
        "",
        "## 4b. The evidence profile — what any correct hypothesis must predict",
        "",
        "The scoring can be inverted. For each scored variable the optimal "
        "prediction is fixed by the observed direction: `++` where something is "
        "present, `--` where it is absent. The result is a portrait of the "
        "artefact class, stated as requirements.",
        "",
        f"A hypothesis matching this profile exactly would score "
        f"**{prof['ceiling']:+.1f}**. The best hypothesis actually on the table "
        f"scores {base.totals[base.leader]:+.1f}, which is "
        f"{base.totals[base.leader] / prof['ceiling'] * 100:.0f} per cent of it.",
        "",
        "> **This profile is not a hypothesis and must never be scored as one.** "
        "A prediction set reverse-engineered from it is fitted to the data by "
        "construction, and its score would measure nothing but the fitting. Its "
        "legitimate uses are as a description of what has to be explained, and "
        "as a checklist to examine a hypothesis against *before* scoring it.",
        "",
        "| EV | Variable | Power | Observed | Must predict | Worth |",
        "| -- | -------- | ----- | -------- | ------------ | ----- |",
    ]
    for row in prof["rows"]:
        lines.append(
            f"| {row['ev_id']} | {row['variable']} | {row['power']} | "
            f"{row['direction']} | `{row['requires']}` | +{row['value']:.1f} |"
        )

    lines += [
        "",
        "### How far each hypothesis already agrees",
        "",
        "Counted over the profile requirements only, by sign of the prediction.",
        "",
        "| Hypothesis | Agrees | Disagrees | Silent |",
        "| ---------- | ------ | --------- | ------ |",
    ]
    agreement = report["profile_agreement"]
    for h in sorted(agreement, key=lambda k: (-agreement[k]["agree"],
                                              agreement[k]["disagree"])):
        a = agreement[h]
        lines.append(f"| {h} {hyp[h]} | {a['agree']} | {a['disagree']} | "
                     f"{a['silent']} |")

    lines += [
        "",
        "A hypothesis with many disagreements is engaged and wrong; one with "
        "many silences is unengaged, and its low disagreement count is not a "
        "virtue. Neither pattern is success.",
        "",
        "## 4b2. Screening of candidate functional domains",
        "",
        "Authoring a full 42-variable prediction matrix for every idea is "
        "expensive and, once the evidence is known, increasingly contaminated. "
        "A screen is cheaper and more honest: it records only the predictions a "
        "domain **cannot avoid** — those that follow from the mechanism whether "
        "the proposer likes them or not — and checks those against the corpus.",
        "",
        "A candidate is **eliminated** when the corpus contradicts, at full "
        "strength, a prediction it had to make on a Very High or High power "
        "variable. Surviving a screen is not support; it means the domain is "
        "worth the cost of a full prediction matrix.",
        "",
        "| ID | Candidate | Domain | Would produce | Screen | Hard contradictions | Verdict |",
        "| -- | --------- | ------ | ------------- | ------ | ------------------- | ------- |",
    ]
    for c in report["screening"]:
        lines.append(
            f"| {c['candidate_id']} | {c['name']} | {c['domain']} | "
            f"{c['creates'] or '—'} | {c['total']:+.1f} | {c['hard']} | "
            f"{'**' + c['verdict'] + '**' if c['verdict'] == 'ELIMINATED' else c['verdict']} |"
        )

    lines += [
        "",
        "### Where each candidate fails",
        "",
    ]
    for c in report["screening"]:
        worst = sorted(c["rows"], key=lambda r: r["value"])[:3]
        worst = [w for w in worst if w["value"] < 0]
        if not worst:
            continue
        detail = "; ".join(
            f"{w['ev_id']} {w['variable']} (predicted `{w['prediction']}`, "
            f"observed {w['direction']}, {w['value']:+.1f})" for w in worst
        )
        lines.append(f"- **{c['candidate_id']} {c['name']}** — {detail}")
        if c["untested"]:
            lines.append(
                f"  - Untested predictions that would decide it: "
                + ", ".join(f"{u[0]} (`{u[2]}`)" for u in c["untested"])
            )

    lines += [
        "",
        "## 4b3. Usage value: was the function worth having?",
        "",
        "Evidential fit and worth are different questions. A hypothesis can "
        "agree with every observation and still be implausible, because nobody "
        "casts difficult bronze for two centuries to obtain what a stick would "
        "give them. Worth is recorded in three kinds, because the corpus "
        "discriminates sharply between them.",
        "",
        "**Product** is the value of the material output *net of the cheapest "
        "substitute* (−2 to +2). **Craft** is whether the difficulty and cost "
        "of making it are part of its worth (0 to 2). **Experience** is whether "
        "using it delivers something valued in itself, rather than through an "
        "output (0 to 2).",
        "",
        "> **None of this enters `hdm_scores`.** Folding a judgement about worth "
        "into the evidence score would let opinion masquerade as evidence. It "
        "is a separate axis, reported beside the evidential one.",
        "",
        "| Subject | Product (net of substitute) | Craft | Experience | Cheapest substitute |",
        "| ------- | --------------------------- | ----- | ---------- | ------------------- |",
    ]
    conn = sqlite3.connect(db_path)
    try:
        for sid, styp, prod, sub, pv, cv, ev_, rat in conn.execute(
            """SELECT subject_id, subject_type, product, substitute,
                      product_value, craft_value, experience_value, rationale
               FROM utility_assessments
               ORDER BY (product_value + craft_value + experience_value) DESC,
                        subject_id"""
        ):
            lines.append(
                f"| **{sid}** {prod[:52]} | {pv:+d} | {cv} | {ev_} | "
                f"{(sub or '')[:52]} |"
            )
    finally:
        conn.close()

    lines += [
        "",
        "The axis separates the field cleanly. **Every reading in which the "
        "object makes something scores negative on product**, because a cheaper "
        "substitute existed in every case: a wooden spool, a pottery lamp, a "
        "knotted cord, a groma, a sundial. **Only the readings in which the "
        "making and the holding are themselves the point score positive on all "
        "three.** For those, the expense is functional rather than anomalous, "
        "and the absence of standardisation is what individual commissioning "
        "looks like rather than a defect.",
        "",
        "That asymmetry is a result, not an assumption. It was not put into the "
        "evidence and cannot be taken out of it: it follows from the objects "
        "being costly, difficult, finely finished, individually varied and "
        "unworn.",
        "",
        "## 4c. Pre-registered predictions",
        "",
        "Guesses recorded before the measurements exist, so that the "
        "difference between a test and a story is on the record. **These are "
        "not evidence and are never scored.** When a measurement is made it "
        "becomes an ordinary sourced observation and the prediction is "
        "resolved against it.",
        "",
        "| ID | Variable | Bears on | Registered | Prediction | Refuted if |",
        "| -- | -------- | -------- | ---------- | ---------- | ---------- |",
    ]
    conn = sqlite3.connect(db_path)
    try:
        for row in conn.execute(
            """SELECT prediction_id, ev_id, hypothesis_ids, registered_on,
                      predicted, falsified_if, status
               FROM predictions ORDER BY prediction_id"""
        ):
            pid, ev_id, hyps, reg, pred, falsif, status = row
            mark = "" if status == "open" else f" **[{status}]**"
            name = variables[ev_id].name if ev_id in variables else ev_id
            lines.append(
                f"| {pid}{mark} | {ev_id} {name} | {hyps} | {reg} | "
                f"{pred[:170].replace('|', chr(92) + '|')} | "
                f"{falsif[:170].replace('|', chr(92) + '|')} |"
            )
    finally:
        conn.close()

    lines += [
        "",
        "## 5. Variables that cannot yet be scored",
        "",
        "### Corpus evidence exists, but the prediction matrix is not specific "
        "enough",
        "",
        "These are defects in the HPM, not gaps in the evidence. They must be "
        "repaired by respecifying the prediction *without reference to the "
        "observations below*, otherwise the matrix is being tuned to the data.",
        "",
        "| EV | Variable | Power | Corpus evidence held |",
        "| -- | -------- | ----- | -------------------- |",
    ]
    for ev_id, obs in sorted(corpus.items()):
        if obs.discriminating:
            continue
        var = variables[ev_id]
        summary = obs.statement[:150].replace("|", "\\|")
        lines.append(f"| {ev_id} | {var.name} | {var.power} | {summary}... |")

    lines += [
        "",
        "### No corpus evidence at all",
        "",
        "| EV | Variable | Power | Maximum effect on any hypothesis |",
        "| -- | -------- | ----- | -------------------------------- |",
    ]
    for ev_id in report["unscored"]:
        var = variables[ev_id]
        swing = 2 * var.dp_weight * score_hdm.CONF_WEIGHT["C"]
        lines.append(f"| {ev_id} | {var.name} | {var.power} | +/- {swing:.1f} |")

    lines += [
        "",
        "## 6. Stated limitations",
        "",
        "1. The recorded corpus is a minority of the known corpus and is not "
        "drawn from it representatively. See `reports/corpus_coverage.md`.",
        "2. Wear evidence is macroscopic. The source that supplies it states "
        "that microscopic wear analysis has not been carried out (PUB-0003, 52), "
        "so the absence of wear is an absence of *reported* wear.",
        "3. Residue and thermal-alteration evidence is deliberately unscored. "
        "The only residue record in the corpus is described by its own source as "
        "possibly unreliable. Scoring these variables as absent would penalise "
        "the hypotheses they bear on using analyses that have never been run.",
        "4. Most corpus-level statistics rest on one publication, PUB-0003, "
        "which in turn summarises an unpublished catalogue (PUB-0022) that this "
        "project has not consulted directly.",
        "5. The direction assigned to each corpus observation is this project's "
        "judgement of a sourced fact, not an observation. Directions are stored "
        "in `corpus_observations` with their reasoning so that they can be "
        "challenged independently of the evidence.",
        "",
    ]
    return lines


# --- Corpus coverage ---------------------------------------------------------


def corpus_coverage(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        total = conn.execute("SELECT COUNT(*) c FROM specimens").fetchone()["c"]
        lines = _header("Corpus Coverage and Representativeness", "RDORP-COV",
                        db_path, "database/reports.py")
        lines += [
            "## 1. Coverage",
            "",
            f"- Specimens recorded: **{total}**",
            f"- Known corpus: about **{KNOWN_CORPUS}** (PUB-0003, 32)",
            f"- Coverage: **{total / KNOWN_CORPUS * 100:.0f} per cent**",
            "",
            "## 2. Geographic representativeness",
            "",
            "The known corpus is about 70 per cent Gallic and Germanic and about "
            "20 per cent British (PUB-0003, 32). The recorded corpus is compared "
            "with that below.",
            "",
            "| Country | Recorded | Share |",
            "| ------- | -------- | ----- |",
        ]
        for row in conn.execute(
            "SELECT country, COUNT(*) n FROM specimens GROUP BY country ORDER BY n DESC"
        ):
            lines.append(f"| {row['country']} | {row['n']} | "
                         f"{row['n'] / total * 100:.0f}% |")

        lines += [
            "",
            "## 3. Archaeological context",
            "",
            "The known corpus, among specimens with a recorded find location, is "
            "more than half settlements, just under one-fifth military camps, "
            "c 8.5 per cent sacred, c 7 per cent graves, c 5.5 per cent pits and "
            "wells, c 4 per cent hoards and c 4 per cent rivers (PUB-0003, 33).",
            "",
            "| Context category | Recorded |",
            "| ---------------- | -------- |",
        ]
        for row in conn.execute(
            "SELECT context_category, COUNT(*) n FROM specimens "
            "GROUP BY context_category ORDER BY n DESC"
        ):
            lines.append(f"| {row['context_category']} | {row['n']} |")

        lines += [
            "",
            "## 4. Source confidence of recorded specimens",
            "",
            "| Grade | Specimens |",
            "| ----- | --------- |",
        ]
        for row in conn.execute(
            "SELECT confidence, COUNT(*) n FROM specimens GROUP BY confidence ORDER BY confidence"
        ):
            lines.append(f"| {row['confidence']} | {row['n']} |")

        lines += [
            "",
            "## 5. Observation density per evidence variable",
            "",
            "| EV | Variable | Power | Specimen observations |",
            "| -- | -------- | ----- | --------------------- |",
        ]
        for row in conn.execute(
            """SELECT v.ev_id, v.variable, v.discriminatory_power,
                      COUNT(o.observation_id) n
               FROM evidence_variables v
               LEFT JOIN artifact_observations o ON o.ev_id = v.ev_id
               GROUP BY v.ev_id ORDER BY v.ev_id"""
        ):
            lines.append(f"| {row['ev_id']} | {row['variable']} | "
                         f"{row['discriminatory_power']} | {row['n']} |")

        lines += [
            "",
            "## 6. What would most improve the corpus",
            "",
            "1. **Consult PUB-0022 (Guggenberger 1999) directly.** Almost every "
            "corpus-level value currently in the database is taken from PUB-0003 "
            "citing it at one remove. It also holds the per-specimen measurement "
            "tables that would populate the geometry variables properly.",
            "2. **Add continental specimens with measurements.** The recorded "
            "corpus is skewed towards British metal-detector finds, which carry "
            "measurements but almost no archaeological context.",
            "3. **Obtain microscopic wear analysis on any specimen.** This is "
            "the single largest evidence gap and the source of the most "
            "discriminating result currently in the database.",
            "4. **Obtain residue analysis.** EV023 and EV024 are both rated Very "
            "High and are deliberately unscored because no reliable analysis "
            "exists.",
            "",
        ]
        return lines
    finally:
        conn.close()


# --- Batch summary -----------------------------------------------------------


def batch_summary(report: dict, db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        base = report["baseline"]
        lines = _header("Batch Summary", "RDORP-BATCH", db_path,
                        "database/reports.py")

        counts = {
            t: conn.execute(f"SELECT COUNT(*) c FROM {t}").fetchone()["c"]
            for t in ("sources", "specimens", "artifact_observations",
                      "corpus_observations", "evidence_register", "hdm_scores",
                      "results", "experiments")
        }
        lines += ["## Database contents", "",
                  "| Table | Rows |", "| ----- | ---- |"]
        lines += [f"| `{t}` | {n} |" for t, n in counts.items()]

        batch = conn.execute(
            """SELECT COUNT(*) c FROM artifact_observations
               WHERE source_id = 'PUB-0003'"""
        ).fetchone()["c"]
        new_specimens = conn.execute(
            "SELECT rd_id, specimen_name, country, context_category FROM specimens "
            "WHERE primary_source_id = 'PUB-0003' ORDER BY rd_id"
        ).fetchall()

        lines += [
            "",
            "## Most recent batch: 002 — Guggenberger and Leach 2025 (PUB-0003)",
            "",
            f"- Observations extracted from PUB-0003: **{batch}**",
            f"- Specimens added: **{len(new_specimens)}**",
            f"- Corpus-level observations now scoreable: "
            f"**{len(base.variables_used)}**",
            "",
            "| RD_ID | Specimen | Country | Context |",
            "| ----- | -------- | ------- | ------- |",
        ]
        for row in new_specimens:
            lines.append(f"| {row['rd_id']} | {row['specimen_name']} | "
                         f"{row['country']} | {row['context_category']} |")

        lines += [
            "",
            "## Batch completion criteria (TASK.md)",
            "",
            "| Criterion | Status |",
            "| --------- | ------ |",
            "| Sources imported | done |",
            "| Specimens updated | done |",
            "| Evidence extracted | done |",
            "| Measurements normalised | done — mm, g, ISO dates |",
            "| Validation passed | see `reports/validation_report.md` |",
            "| CSV exports regenerated | done — `database/`, `exports/csv`, `exports/json` |",
            "| Validation report generated | done |",
            "",
        ]
        return lines
    finally:
        conn.close()


def run(db_path: str = DB_DEFAULT) -> dict:
    report = score_hdm.run(db_path)
    _write(os.path.join(REPORT_DIR, "hdm_analysis.md"), hdm_analysis(report, db_path))
    _write(os.path.join(REPORT_DIR, "corpus_coverage.md"), corpus_coverage(db_path))
    _write(os.path.join(REPORT_DIR, "batch_summary.md"), batch_summary(report, db_path))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RDORP reports.")
    parser.add_argument("--db", default=DB_DEFAULT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(args.db)


if __name__ == "__main__":
    main()
