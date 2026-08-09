#!/usr/bin/env python3
"""RDORP - Hypothesis Discrimination Matrix scoring (RDORP-010 steps 5 and 6).

Replaces hdm_analysis.py, hdm_robust.py and methodology_audit.py.

What this module does
---------------------
1. Reads corpus-level observations from the ``corpus_observations`` table.
   Nothing is scored that does not have a row there, and every row there
   carries a source reference. The scoring input is no longer a dictionary
   embedded in the script.
2. Scores every hypothesis x evidence variable pair by comparing the HPM
   prediction with the corpus observation.
3. Applies three separate, independently inspectable weights:
   discriminatory power, source confidence, and evidence class.
4. Runs a sensitivity analysis over scenarios, HPM perturbations and
   leave-one-variable-out removals, and reports only perturbations that
   actually change something.
5. Computes best-case and worst-case bounds over the unscored variables.
6. Writes ``hdm_scores`` and ``results`` and returns a report structure.

Idempotent: running it twice produces identical table contents.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from dataclasses import dataclass, field
from typing import Iterable

LOG = logging.getLogger("rdorp.score")

DB_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rdorp.sqlite")

# --- Weighting tables --------------------------------------------------------

#: Discriminatory power of an evidence variable (evidence_variables table).
DP_WEIGHT: dict[str, float] = {"Very High": 3.0, "High": 2.0, "Medium": 1.0}

#: Source confidence of the corpus observation (RDORP source evaluation scale).
#: A and B are deliberately no longer equal; batch 001 gave both 1.0, which
#: meant an archival record and a museum record could not be told apart.
CONF_WEIGHT: dict[str, float] = {"A": 1.0, "B": 0.9, "C": 0.75, "D": 0.5, "E": 0.25}

#: Discount applied to evidence this project produced itself. Derived
#: engineering assessments are reasoning about measurements, not observations
#: of artefacts, and must not carry the same weight as excavation records.
CLASS_WEIGHT: dict[str, float] = {"Observed": 1.0, "Experimental": 0.75, "Derived": 0.5}

#: Numeric value of an HPM prediction symbol.
PRED_NUM: dict[str, int] = {"++": 2, "+": 1, "0": 0, "-": -1, "--": -2}
NUM_PRED: dict[int, str] = {v: k for k, v in PRED_NUM.items()}

#: How strongly the corpus observation confirms or refutes the prediction.
DIRECTION_FACTOR: dict[str, float] = {
    "confirmed": 1.0,
    "weak_confirmed": 0.5,
    "ambiguous": 0.0,
    "weak_absent": -0.5,
    "absent": -1.0,
}


@dataclass(frozen=True)
class CorpusObservation:
    """A corpus-level observation, as stored in ``corpus_observations``."""

    ev_id: str
    statement: str
    direction: str
    confidence: str
    evidence_class: str
    discriminating: bool
    source_id: str | None
    page: str | None
    notes: str | None


@dataclass(frozen=True)
class Variable:
    """An evidence variable and its discriminatory power."""

    ev_id: str
    name: str
    power: str

    @property
    def dp_weight(self) -> float:
        return DP_WEIGHT.get(self.power, 1.0)


@dataclass
class Scenario:
    """A scored view of the evidence under one set of inclusion rules."""

    key: str
    label: str
    totals: dict[str, float] = field(default_factory=dict)
    variables_used: list[str] = field(default_factory=list)

    @property
    def ranking(self) -> list[str]:
        return sorted(self.totals, key=lambda h: -self.totals[h])

    @property
    def leader(self) -> str:
        return self.ranking[0]

    @property
    def margin(self) -> float:
        order = self.ranking
        return self.totals[order[0]] - self.totals[order[1]]


# --- Data access -------------------------------------------------------------


def load(conn: sqlite3.Connection):
    """Load hypotheses, variables, the HPM and the corpus observations."""
    hypotheses = {
        r[0]: r[1]
        for r in conn.execute(
            "SELECT hypothesis_id, name FROM hypotheses ORDER BY hypothesis_id"
        )
    }
    variables = {
        r[0]: Variable(r[0], r[1], r[2])
        for r in conn.execute(
            "SELECT ev_id, variable, discriminatory_power FROM evidence_variables"
        )
    }
    hpm = {
        (r[0], r[1]): r[2]
        for r in conn.execute("SELECT hypothesis_id, ev_id, prediction FROM hpm")
    }
    readings = {
        (r[0], r[1]): r[2]
        for r in conn.execute(
            "SELECT hypothesis_id, ev_id, direction FROM hpm_readings")
    }
    clusters = {
        r[0]: r[1]
        for r in conn.execute(
            "SELECT ev_id, evidence_cluster FROM corpus_observations "
            "WHERE evidence_cluster IS NOT NULL")
    }
    corpus = {
        r[0]: CorpusObservation(
            ev_id=r[0],
            statement=r[1],
            direction=r[2],
            confidence=r[3],
            evidence_class=r[4],
            discriminating=bool(r[5]),
            source_id=r[6],
            page=r[7],
            notes=r[8],
        )
        for r in conn.execute(
            """SELECT ev_id, statement, direction, confidence, evidence_class,
                      discriminating, source_id, page, notes
               FROM corpus_observations"""
        )
    }
    return hypotheses, variables, hpm, corpus, readings, clusters


# --- Scoring -----------------------------------------------------------------


def raw_score(prediction: str, obs: CorpusObservation,
              reading: str | None = None) -> float:
    """Score one hypothesis x variable pair, before any weighting.

    Returns a value in [-2, +2] as specified by RDORP-010 section 10. The
    confidence of the observation is *not* folded in here; batch 001 stored a
    confidence-multiplied value in the ``score`` column, which made the stored
    score incomparable with the documented scale.

    ``reading`` is a per-cell direction from ``hpm_readings``, used where this
    hypothesis's prediction is specific enough to be read against evidence that
    the shared direction cannot serve. Where one exists it overrides both the
    shared direction and the non-discriminating flag.
    """
    if reading is not None:
        return PRED_NUM.get(prediction, 0) * DIRECTION_FACTOR[reading]
    if not obs.discriminating:
        return 0.0
    return PRED_NUM.get(prediction, 0) * DIRECTION_FACTOR[obs.direction]


def weights(obs: CorpusObservation, var: Variable) -> tuple[float, float, float]:
    return (
        var.dp_weight,
        CONF_WEIGHT.get(obs.confidence, 1.0),
        CLASS_WEIGHT.get(obs.evidence_class, 1.0),
    )


def score_all(hypotheses, variables, hpm, corpus, readings=None,
              include: Iterable[str] | None = None, use_readings: bool = True):
    """Score every hypothesis against every corpus observation.

    ``include`` optionally restricts scoring to a subset of ev_ids.
    ``use_readings=False`` ignores per-cell readings, which puts every
    hypothesis on the same footing regardless of how specific its predictions
    are.
    Returns ``{(hypothesis_id, ev_id): (score, dp_w, conf_w, class_w, weighted)}``.
    """
    readings = readings or {}
    selected = set(include) if include is not None else set(corpus)
    cells: dict[tuple[str, str], tuple[float, float, float, float, float]] = {}
    for ev_id, obs in corpus.items():
        if ev_id not in selected:
            continue
        var = variables[ev_id]
        dp_w, conf_w, class_w = weights(obs, var)
        for h in hypotheses:
            reading = readings.get((h, ev_id)) if use_readings else None
            s = raw_score(hpm.get((h, ev_id), "0"), obs, reading)
            cells[(h, ev_id)] = (s, dp_w, conf_w, class_w, s * dp_w * conf_w * class_w)
    return cells


def totals(cells, hypotheses, weighted: bool = True, clusters=None) -> dict[str, float]:
    """Sum the scored cells for each hypothesis.

    With ``clusters``, variables that restate one underlying observation share
    a budget: the cluster contributes its single strongest cell rather than the
    sum of its cells, so one fact counts once however many variables express
    it. Unclustered variables stand alone.
    """
    idx = 4 if weighted else 0
    if not clusters:
        out = {h: 0.0 for h in hypotheses}
        for (h, _ev), values in cells.items():
            out[h] += values[idx]
        return out

    out = {h: 0.0 for h in hypotheses}
    best: dict[tuple[str, str], float] = {}
    for (h, ev), values in cells.items():
        c = clusters.get(ev)
        if c is None:
            out[h] += values[idx]
        else:
            k = (h, c)
            if abs(values[idx]) > abs(best.get(k, 0.0)):
                best[k] = values[idx]
    for (h, _c), v in best.items():
        out[h] += v
    return out


# --- Scenarios ---------------------------------------------------------------


def scorable(corpus, readings, hypotheses) -> set[str]:
    """Variables that produce a non-zero cell for at least one hypothesis."""
    evs = {e for e, o in corpus.items() if o.discriminating}
    evs |= {ev for (_h, ev) in readings if ev in corpus}
    return evs


def source_counts(conn) -> dict[str, int]:
    """Distinct sources standing behind each variable.

    Counts the corpus observation's own source together with the sources of any
    per-specimen observations. A variable resting on one source, or on none, is
    an argument from a single voice however high its discriminatory power.
    """
    out: dict[str, set] = {}
    for ev_id, src in conn.execute(
        "SELECT ev_id, source_id FROM corpus_observations WHERE source_id IS NOT NULL"
    ):
        out.setdefault(ev_id, set()).add(src)
    for ev_id, src in conn.execute(
        "SELECT DISTINCT ev_id, source_id FROM artifact_observations "
        "WHERE source_id IS NOT NULL"
    ):
        out.setdefault(ev_id, set()).add(src)
    return {k: len(v) for k, v in out.items()}


def build_scenarios(hypotheses, variables, hpm, corpus, readings,
                    sources=None, clusters=None) -> list[Scenario]:
    """Score the evidence under each inclusion rule required by RDORP-010 s11."""
    discriminating = scorable(corpus, readings, hypotheses)
    sources = sources or {}
    clusters = clusters or {}

    definitions = [
        ("baseline", "All corpus observations, fully weighted", discriminating),
        (
            "observed_only",
            "Archaeological observations only (this project's derived "
            "engineering assessments excluded)",
            {e for e in discriminating if corpus[e].evidence_class == "Observed"},
        ),
        (
            "high_confidence",
            "Confidence A-C only (low-confidence observations excluded)",
            {e for e in discriminating if corpus[e].confidence in "ABC"},
        ),
        (
            "very_high_power",
            "Very High discriminatory-power variables only",
            {e for e in discriminating if variables[e].power == "Very High"},
        ),
    ]

    scenarios = []
    for key, label, evs in definitions:
        cells = score_all(hypotheses, variables, hpm, corpus, readings, include=evs)
        sc = Scenario(key, label)
        sc.totals = totals(cells, hypotheses)
        sc.variables_used = sorted(evs)
        scenarios.append(sc)

    if clusters:
        cells = score_all(hypotheses, variables, hpm, corpus, readings,
                          include=discriminating)
        sc = Scenario(
            "clustered",
            "Correlated variables share a budget: a cluster contributes its "
            "strongest cell, not the sum of its cells",
        )
        sc.totals = totals(cells, hypotheses, clusters=clusters)
        sc.variables_used = sorted(discriminating)
        scenarios.append(sc)

    if sources:
        multi = {e for e in discriminating if sources.get(e, 0) >= 2}
        cells = score_all(hypotheses, variables, hpm, corpus, readings, include=multi)
        sc = Scenario(
            "multi_source",
            "Corroborated variables only: at least two independent sources "
            "stand behind the observation",
        )
        sc.totals = totals(cells, hypotheses)
        sc.variables_used = sorted(multi)
        definitions_extra = sc
    else:
        definitions_extra = None

    unweighted_cells = score_all(hypotheses, variables, hpm, corpus, readings,
                                 include=discriminating)
    sc = Scenario("unweighted", "All corpus observations, no weighting applied")
    sc.totals = totals(unweighted_cells, hypotheses, weighted=False)
    sc.variables_used = sorted(discriminating)
    scenarios.append(sc)

    if definitions_extra is not None:
        scenarios.append(definitions_extra)

    if readings:
        shared_only = {e for e, o in corpus.items() if o.discriminating}
        cells = score_all(hypotheses, variables, hpm, corpus, readings,
                          include=shared_only, use_readings=False)
        sc = Scenario(
            "same_footing",
            "Per-cell readings ignored, so every hypothesis is judged only on "
            "the variables all of them can be judged on",
        )
        sc.totals = totals(cells, hypotheses)
        sc.variables_used = sorted(shared_only)
        scenarios.append(sc)

    return scenarios


def leave_one_out(hypotheses, variables, hpm, corpus, readings, baseline: Scenario):
    """Remove each scored variable in turn and report the effect on the ranking."""
    evs = set(baseline.variables_used)
    results = []
    for ev_id in sorted(evs):
        cells = score_all(hypotheses, variables, hpm, corpus, readings,
                          include=evs - {ev_id})
        t = totals(cells, hypotheses)
        order = sorted(t, key=lambda h: -t[h])
        results.append(
            {
                "ev_id": ev_id,
                "variable": variables[ev_id].name,
                "leader": order[0],
                "margin": t[order[0]] - t[order[1]],
                "changes_leader": order[0] != baseline.leader,
            }
        )
    return results


def hpm_perturbation(hypotheses, variables, hpm, corpus, readings, baseline: Scenario):
    """Shift every scored HPM prediction by +/-1 level and report real changes.

    Batch 001 attempted this but mapped ``++`` upwards onto ``++``, so five of
    its seven tests were no-ops that printed ``++ -> ++`` and reported the rank
    as stable. Shifts that cannot move are skipped here instead of counted as
    evidence of robustness.
    """
    evs = set(baseline.variables_used)
    findings = []
    for ev_id in sorted(evs):
        obs = corpus[ev_id]
        var = variables[ev_id]
        dp_w, conf_w, class_w = weights(obs, var)
        for h in hypotheses:
            current = hpm.get((h, ev_id), "0")
            reading = readings.get((h, ev_id))
            p = PRED_NUM.get(current, 0)
            for delta in (+1, -1):
                shifted = p + delta
                if shifted not in NUM_PRED:          # already at the end of the scale
                    continue
                new_pred = NUM_PRED[shifted]
                before = raw_score(current, obs, reading) * dp_w * conf_w * class_w
                after = raw_score(new_pred, obs, reading) * dp_w * conf_w * class_w
                change = after - before
                if change == 0:                      # non-discriminating variable
                    continue
                shifted_totals = dict(baseline.totals)
                shifted_totals[h] += change
                order = sorted(shifted_totals, key=lambda k: -shifted_totals[k])
                if order[0] != baseline.leader:
                    findings.append(
                        {
                            "ev_id": ev_id,
                            "variable": var.name,
                            "hypothesis": h,
                            "from": current,
                            "to": new_pred,
                            "delta": change,
                            "new_leader": order[0],
                        }
                    )
    return findings


def commitment(hypotheses, variables, hpm, corpus, readings, ev_ids) -> dict[str, dict]:
    """Measure how much each hypothesis actually staked on the scored evidence.

    A hypothesis that predicts ``0`` for most variables takes no risk, yet it
    still collects points whenever a variable it marked ``-`` turns out to be
    absent. Raw totals therefore favour hypotheses that commit to little. For
    each hypothesis this returns the number of non-neutral predictions, the
    largest weighted score it could possibly have obtained, and the fraction of
    that maximum actually achieved.
    """
    out = {}
    for h in hypotheses:
        max_possible = 0.0
        non_neutral = 0
        strong = 0
        for ev_id in ev_ids:
            obs = corpus[ev_id]
            dp_w, conf_w, class_w = weights(obs, variables[ev_id])
            p = abs(PRED_NUM.get(hpm.get((h, ev_id), "0"), 0))
            if p:
                non_neutral += 1
            if p == 2:
                strong += 1
            max_possible += p * dp_w * conf_w * class_w
        out[h] = {
            "predictions_made": non_neutral,
            "strong_predictions": strong,
            "max_possible": max_possible,
        }
    return out


def evidence_profile(variables, corpus, ev_ids):
    """Invert the scoring: what would a hypothesis have to predict to score best?

    For each scored variable the optimal prediction is fixed by the observed
    direction: ``++`` where something is present, ``--`` where it is absent. The
    result is a portrait of the artefact class, expressed as the requirements
    any correct hypothesis must satisfy, together with the ceiling score.

    THIS IS NOT A HYPOTHESIS AND MUST NEVER BE SCORED AS ONE. A prediction set
    reverse-engineered from this profile is fitted to the data by construction;
    its score would measure nothing but the fitting. The profile is a
    description of what has to be explained, and a checklist against which a
    hypothesis can be examined *before* it is scored.
    """
    rows = []
    ceiling = 0.0
    for ev_id in sorted(ev_ids):
        obs = corpus[ev_id]
        var = variables[ev_id]
        factor = DIRECTION_FACTOR[obs.direction]
        if factor == 0:
            continue
        dp_w, conf_w, class_w = weights(obs, var)
        best_pred = "++" if factor > 0 else "--"
        value = 2 * abs(factor) * dp_w * conf_w * class_w
        ceiling += value
        rows.append({
            "ev_id": ev_id,
            "variable": var.name,
            "power": var.power,
            "direction": obs.direction,
            "requires": best_pred,
            "value": value,
            "evidence_class": obs.evidence_class,
            "confidence": obs.confidence,
        })
    rows.sort(key=lambda r: -r["value"])
    return {"rows": rows, "ceiling": ceiling}


def profile_agreement(hypotheses, hpm, profile):
    """How far each hypothesis already agrees with the evidence profile."""
    out = {}
    for h in hypotheses:
        agree = disagree = silent = 0
        for row in profile["rows"]:
            p = PRED_NUM.get(hpm.get((h, row["ev_id"]), "0"), 0)
            want = PRED_NUM[row["requires"]]
            if p == 0:
                silent += 1
            elif (p > 0) == (want > 0):
                agree += 1
            else:
                disagree += 1
        out[h] = {"agree": agree, "disagree": disagree, "silent": silent}
    return out


def screen(conn, variables, corpus):
    """Screen candidate functional domains against their unavoidable predictions.

    A screen is not a score and produces no ranking. For each candidate it
    reports how many of the predictions the mechanism cannot avoid are
    contradicted by the corpus, and how heavily. The only verdicts are
    'eliminated' and 'promote to a full hypothesis'.

    A candidate is eliminated when the corpus contradicts a prediction it had
    to make on a Very High or High power variable at full strength. Surviving
    a screen is not support; it means the domain is worth the cost of a full
    prediction matrix.
    """
    cands = {r[0]: {"candidate_id": r[0], "name": r[1], "domain": r[2],
                    "description": r[3], "creates": r[4], "notes": r[5],
                    "rows": [], "total": 0.0, "hard": 0, "untested": []}
             for r in conn.execute("SELECT * FROM screening_candidates")}

    for cid, ev_id, pred, reading, rationale in conn.execute(
        "SELECT candidate_id, ev_id, prediction, reading, rationale "
        "FROM screening ORDER BY candidate_id, ev_id"
    ):
        c = cands[cid]
        var = variables[ev_id]
        obs = corpus.get(ev_id)
        if obs is None and reading is None:
            c["untested"].append((ev_id, var.name, pred, rationale))
            continue
        if obs is None:
            continue
        dp_w, conf_w, class_w = weights(obs, var)
        value = raw_score(pred, obs, reading) * dp_w * conf_w * class_w
        c["total"] += value
        contradicted = value < 0
        if contradicted and var.power in ("Very High", "High") and abs(value) >= 1.5:
            c["hard"] += 1
        c["rows"].append({"ev_id": ev_id, "variable": var.name,
                          "power": var.power, "prediction": pred,
                          "direction": reading or obs.direction,
                          "value": value, "rationale": rationale})

    for c in cands.values():
        c["verdict"] = "ELIMINATED" if c["hard"] else "promote"
    return sorted(cands.values(), key=lambda c: -c["total"])



#: Alternative weighting schemes for the sensitivity sweep (A2). The scheme in
#: use is the first of each list; the others test whether the ranking is a
#: property of the evidence or of the numbers chosen to weight it.
POWER_SCHEMES = {
    "3/2/1 (in use)": {"Very High": 3.0, "High": 2.0, "Medium": 1.0},
    "5/3/1":          {"Very High": 5.0, "High": 3.0, "Medium": 1.0},
    "4/2/1":          {"Very High": 4.0, "High": 2.0, "Medium": 1.0},
    "2/1.5/1":        {"Very High": 2.0, "High": 1.5, "Medium": 1.0},
    "flat":           {"Very High": 1.0, "High": 1.0, "Medium": 1.0},
}
CONF_SCHEMES = {
    "1/.9/.75/.5/.25 (in use)": {"A": 1.0, "B": 0.9, "C": 0.75, "D": 0.5, "E": 0.25},
    "linear":                   {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "E": 0.2},
    "flat":                     {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0},
}
CLASS_SCHEMES = {
    "1/.75/.5 (in use)": {"Observed": 1.0, "Experimental": 0.75, "Derived": 0.5},
    "1/.5/.25":          {"Observed": 1.0, "Experimental": 0.5, "Derived": 0.25},
    "flat":              {"Observed": 1.0, "Experimental": 1.0, "Derived": 1.0},
}


def weight_sweep(hypotheses, variables, hpm, corpus, readings, include,
                 clusters=None):
    """A2. Re-score under every combination of weighting scheme.

    The weights were chosen, not derived. A ranking that holds under one
    scheme and not the rest is a fact about the scheme. This reports how
    often each hypothesis leads across all combinations.
    """
    global DP_WEIGHT, CONF_WEIGHT, CLASS_WEIGHT
    keep = (DP_WEIGHT, CONF_WEIGHT, CLASS_WEIGHT)
    leaders, margins, rows = {}, [], []
    try:
        for pn, pw in POWER_SCHEMES.items():
            for cn, cw in CONF_SCHEMES.items():
                for kn, kw in CLASS_SCHEMES.items():
                    DP_WEIGHT, CONF_WEIGHT, CLASS_WEIGHT = pw, cw, kw
                    cells = score_all(hypotheses, variables, hpm, corpus,
                                      readings, include=include)
                    t = totals(cells, hypotheses, clusters=clusters)
                    order = sorted(t, key=lambda h: -t[h])
                    leaders[order[0]] = leaders.get(order[0], 0) + 1
                    margins.append(t[order[0]] - t[order[1]])
                    rows.append((pn, cn, kn, order[0], t[order[0]], order[1]))
    finally:
        DP_WEIGHT, CONF_WEIGHT, CLASS_WEIGHT = keep
    return {"leaders": leaders, "n": len(rows), "rows": rows,
            "min_margin": min(margins), "max_margin": max(margins)}


def bounds(hypotheses, variables, hpm, corpus):
    """Best and worst case contribution of the variables that are not scored."""
    scored = set(corpus)
    best = {h: 0.0 for h in hypotheses}
    worst = {h: 0.0 for h in hypotheses}
    unscored = []
    for ev_id, var in variables.items():
        if ev_id in scored:
            continue
        unscored.append(ev_id)
        # An unscored variable will eventually be observed at some confidence.
        # C is used as the neutral expectation for evidence not yet collected.
        swing = var.dp_weight * CONF_WEIGHT["C"]
        for h in hypotheses:
            magnitude = abs(PRED_NUM.get(hpm.get((h, ev_id), "0"), 0)) * swing
            best[h] += magnitude
            worst[h] -= magnitude
    return best, worst, sorted(unscored)


# --- Persistence -------------------------------------------------------------


def persist(conn, hypotheses, variables, corpus, cells, baseline, best, worst,
            unscored, commit):
    """Write hdm_scores and results. Rebuilt from scratch, so re-runs are safe."""
    conn.execute("DELETE FROM hdm_scores")
    conn.execute("DELETE FROM results")

    for (h, ev_id), (s, dp_w, conf_w, class_w, weighted) in sorted(cells.items()):
        obs = corpus[ev_id]
        conn.execute(
            """INSERT INTO hdm_scores
               (hypothesis_id, ev_id, score, confidence, dp_weight, conf_weight,
                class_weight, weighted_score, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                h, ev_id, s, obs.confidence, dp_w, conf_w, class_w, weighted,
                f"direction={obs.direction}; class={obs.evidence_class}; "
                f"source={obs.source_id or 'NONE'}"
                + (f" p{obs.page}" if obs.page else ""),
            ),
        )

    order = baseline.ranking
    for rank, h in enumerate(order, start=1):
        worst_h = baseline.totals[h] + worst[h]
        best_rival = max(
            (baseline.totals[k] + best[k] for k in hypotheses if k != h), default=0.0
        )
        conn.execute(
            """INSERT INTO results
               (hypothesis_id, scenario, raw_score, weighted_score, rank,
                scored_variables, evidence_gaps, worst_case, best_case, robust, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                h,
                baseline.key,
                sum(cells[(h, ev)][0] for ev in baseline.variables_used),
                baseline.totals[h],
                rank,
                len(baseline.variables_used),
                len(unscored),
                worst_h,
                baseline.totals[h] + best[h],
                int(worst_h > best_rival),
                f"{hypotheses[h]}; predictions_made="
                f"{commit[h]['predictions_made']}/{len(baseline.variables_used)} "
                f"(strong={commit[h]['strong_predictions']}); "
                f"achieved={baseline.totals[h]:+.1f} of a possible "
                f"{commit[h]['max_possible']:.1f}; robust means this hypothesis "
                f"still leads when every unscored variable resolves against it "
                f"and in favour of its strongest rival",
            ),
        )
    conn.commit()


# --- Entry point -------------------------------------------------------------


def run(db_path: str = DB_DEFAULT) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        hypotheses, variables, hpm, corpus, readings, clusters = load(conn)
        if not corpus:
            raise RuntimeError(
                "corpus_observations is empty - run build_db.py before scoring"
            )

        srccount = source_counts(conn)
        scenarios = build_scenarios(hypotheses, variables, hpm, corpus, readings,
                                    srccount, clusters)
        baseline = next(s for s in scenarios if s.key == "baseline")
        cells = score_all(
            hypotheses, variables, hpm, corpus, readings,
            include=baseline.variables_used
        )
        best, worst, unscored = bounds(hypotheses, variables, hpm, corpus)
        commit = commitment(
            hypotheses, variables, hpm, corpus, readings, baseline.variables_used
        )

        persist(conn, hypotheses, variables, corpus, cells, baseline,
                best, worst, unscored, commit)

        prof = evidence_profile(variables, corpus, baseline.variables_used)
        screened = screen(conn, variables, corpus)
        report = {
            "commitment": commit,
            "profile": prof,
            "screening": screened,
            "profile_agreement": profile_agreement(hypotheses, hpm, prof),
            "hypotheses": hypotheses,
            "variables": variables,
            "hpm": hpm,
            "corpus": corpus,
            "cells": cells,
            "scenarios": scenarios,
            "baseline": baseline,
            "best": best,
            "worst": worst,
            "unscored": unscored,
            "readings": readings,
            "source_counts": srccount,
            "clusters": clusters,
            "weight_sweep": weight_sweep(
                hypotheses, variables, hpm, corpus, readings,
                baseline.variables_used),
            "weight_sweep_clustered": weight_sweep(
                hypotheses, variables, hpm, corpus, readings,
                baseline.variables_used, clusters),
            "leave_one_out": leave_one_out(
                hypotheses, variables, hpm, corpus, readings, baseline
            ),
            "perturbations": hpm_perturbation(
                hypotheses, variables, hpm, corpus, readings, baseline
            ),
        }
        LOG.info(
            "scored %d variables x %d hypotheses; leader %s",
            len(baseline.variables_used), len(hypotheses), baseline.leader,
        )
        return report
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Score the RDORP evidence base.")
    parser.add_argument("--db", default=DB_DEFAULT, help="path to rdorp.sqlite")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    report = run(args.db)
    base = report["baseline"]
    print(f"Scored variables : {len(base.variables_used)} of {len(report['variables'])}")
    print(f"Evidence gaps    : {len(report['unscored'])}")
    for scenario in report["scenarios"]:
        order = scenario.ranking
        print(f"\n{scenario.label}")
        print("  " + "  ".join(f"{h}:{scenario.totals[h]:+.1f}" for h in order))
    print("\nPredictive commitment (points achieved of points at stake)")
    for h in base.ranking:
        c = report["commitment"][h]
        print(f"  {h} {base.totals[h]:+6.1f} / {c['max_possible']:5.1f}   "
              f"predictions {c['predictions_made']:>2}/{len(base.variables_used)} "
              f"(strong {c['strong_predictions']})")
    flips = [f for f in report["leave_one_out"] if f["changes_leader"]]
    print(f"\nSingle variables whose removal changes the leader: "
          f"{', '.join(f['ev_id'] for f in flips) or 'none'}")
    print(f"HPM perturbations that change the leader: {len(report['perturbations'])}")


if __name__ == "__main__":
    main()
