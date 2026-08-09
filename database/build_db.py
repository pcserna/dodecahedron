#!/usr/bin/env python3
"""
RDORP Database Builder
Creates and seeds rdorp.sqlite from project CSV sources.
Run from any directory: python database/build_db.py
"""

import sqlite3
import csv
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "rdorp.sqlite")


def read_csv(filename):
    path = os.path.join(DB_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS specimen_quality;
DROP TABLE IF EXISTS utility_assessments;
DROP TABLE IF EXISTS screening;
DROP TABLE IF EXISTS screening_candidates;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS hdm_scores;
DROP TABLE IF EXISTS corpus_observations;
DROP TABLE IF EXISTS hpm_readings;
DROP TABLE IF EXISTS hpm;
DROP TABLE IF EXISTS artifact_observations;
DROP TABLE IF EXISTS evidence_sources;
DROP TABLE IF EXISTS evidence_register;
DROP TABLE IF EXISTS evidence_variables;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS specimens;
DROP TABLE IF EXISTS hypotheses;
DROP TABLE IF EXISTS sources;

CREATE TABLE sources (
    source_id   TEXT PRIMARY KEY,
    authors     TEXT,
    year        INTEGER,
    title       TEXT NOT NULL,
    type        TEXT,
    doi         TEXT,
    url         TEXT,
    confidence  TEXT CHECK(confidence IN ('A','B','C','D','E')),
    notes       TEXT
);

CREATE TABLE specimens (
    rd_id               TEXT PRIMARY KEY,
    specimen_name       TEXT,
    findspot            TEXT NOT NULL,
    country             TEXT NOT NULL,
    roman_province      TEXT,
    context_category    TEXT CHECK(context_category IN (
                            'Military','Civilian','Villa','Temple',
                            'Grave','Hoard','River','Settlement','Unknown')),
    date_from           INTEGER,
    date_to             INTEGER,
    museum_name         TEXT,
    museum_city         TEXT,
    museum_country      TEXT,
    inventory_number    TEXT,
    material            TEXT,
    manufacturing_method TEXT,
    height_mm           REAL,
    width_mm            REAL,
    max_diameter_mm     REAL,
    weight_g            REAL,
    wall_thickness_mm   REAL,
    knob_diameter_mm    REAL,
    hole_01_mm          REAL,
    hole_02_mm          REAL,
    hole_03_mm          REAL,
    hole_04_mm          REAL,
    hole_05_mm          REAL,
    hole_06_mm          REAL,
    hole_07_mm          REAL,
    hole_08_mm          REAL,
    hole_09_mm          REAL,
    hole_10_mm          REAL,
    hole_11_mm          REAL,
    hole_12_mm          REAL,
    decoration_type     TEXT,
    decoration_desc     TEXT,
    wear_notes          TEXT,
    associated_finds    TEXT,
    primary_source_id   TEXT REFERENCES sources(source_id),
    confidence          TEXT CHECK(confidence IN ('A','B','C','D','E')),
    nouwen_number       INTEGER,
    guggenberger_number INTEGER,
    guggenberger_type   TEXT,
    notes               TEXT
);

CREATE TABLE hypotheses (
    hypothesis_id   TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT
);

CREATE TABLE evidence_variables (
    ev_id                    TEXT PRIMARY KEY,
    variable                 TEXT NOT NULL,
    category                 TEXT NOT NULL,
    definition               TEXT,
    unit                     TEXT,
    source_type              TEXT,
    discriminatory_power     TEXT,
    most_relevant_hypotheses TEXT
);

CREATE TABLE evidence_register (
    evidence_id         TEXT PRIMARY KEY,
    category            TEXT,
    evidence_statement  TEXT NOT NULL,
    -- 'Interpretation' records what a published author concluded. It is kept
    -- strictly separate from evidence and is never scored in hdm_scores.
    evidence_type       TEXT CHECK(evidence_type IN ('Observed','Constraint','Derived','Experimental','Interpretation')),
    confidence          TEXT CHECK(confidence IN ('High','Medium','Low')),
    relevant_hypotheses TEXT,
    primary_observable  TEXT
);

CREATE TABLE evidence_sources (
    evidence_id TEXT NOT NULL REFERENCES evidence_register(evidence_id),
    source_id   TEXT NOT NULL REFERENCES sources(source_id),
    PRIMARY KEY (evidence_id, source_id)
);

CREATE TABLE artifact_observations (
    observation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    rd_id           TEXT    NOT NULL REFERENCES specimens(rd_id),
    ev_id           TEXT    NOT NULL REFERENCES evidence_variables(ev_id),
    observed_value  TEXT,
    confidence      TEXT CHECK(confidence IN ('A','B','C','D','E')),
    source_id       TEXT    REFERENCES sources(source_id),
    page            TEXT,
    figure          TEXT,
    extraction_date TEXT,
    notes           TEXT
);

-- Hypothesis Prediction Matrix: expected observations per hypothesis if it is correct
CREATE TABLE hpm (
    hypothesis_id   TEXT NOT NULL REFERENCES hypotheses(hypothesis_id),
    ev_id           TEXT NOT NULL REFERENCES evidence_variables(ev_id),
    prediction      TEXT NOT NULL CHECK(prediction IN ('++','+','0','-','--')),
    rationale       TEXT,
    PRIMARY KEY (hypothesis_id, ev_id)
);

-- Per-cell readings of the corpus evidence.
--
-- corpus_observations.direction is a single reading of a variable, shared by
-- every hypothesis. That works for variables where the evidence means the same
-- thing whoever is asking - wear is either there or it is not. It fails for
-- distribution variables such as site type, province, associated finds and
-- dating, where the same distribution confirms one hypothesis and refutes
-- another. Those variables are currently marked discriminating = 0 and score
-- zero for everybody, which throws away the best-quantified evidence in the
-- corpus.
--
-- A row here says: this hypothesis made a prediction specific enough to be
-- read against that evidence, and this is how it reads. Cells with a row are
-- scored using it; cells without fall back to the shared direction, and score
-- zero if the variable is marked non-discriminating.
--
-- A reading may only be written from a prediction that was specified
-- independently of the observation. The rationale must record the basis.
CREATE TABLE hpm_readings (
    hypothesis_id   TEXT NOT NULL REFERENCES hypotheses(hypothesis_id),
    ev_id           TEXT NOT NULL REFERENCES evidence_variables(ev_id),
    direction       TEXT NOT NULL CHECK(direction IN (
                        'confirmed','weak_confirmed','ambiguous',
                        'weak_absent','absent')),
    rationale       TEXT NOT NULL,
    PRIMARY KEY (hypothesis_id, ev_id)
);

-- Corpus-level observations: one row per evidence variable that has been
-- aggregated across the corpus. This is the *sourced* input to HDM scoring.
-- Nothing may be scored in hdm_scores unless a corpus_observations row exists.
--
--   direction        how the corpus compares with the HPM prediction
--   evidence_class   Observed = recorded on artefacts / published statistics
--                    Derived  = produced by this project's own analysis
--                    Experimental = produced by controlled experiment
--   discriminating   0 when the HPM predictions for this variable are not
--                    specific enough to be confirmed or refuted (HPM defect);
--                    such variables score 0 and are reported as gaps.
CREATE TABLE corpus_observations (
    ev_id           TEXT PRIMARY KEY REFERENCES evidence_variables(ev_id),
    statement       TEXT NOT NULL,
    direction       TEXT NOT NULL CHECK(direction IN (
                        'confirmed','weak_confirmed','ambiguous',
                        'weak_absent','absent')),
    confidence      TEXT NOT NULL CHECK(confidence IN ('A','B','C','D','E')),
    evidence_class  TEXT NOT NULL CHECK(evidence_class IN (
                        'Observed','Derived','Experimental')),
    discriminating  INTEGER NOT NULL CHECK(discriminating IN (0,1)),
    evidence_cluster TEXT,
    source_id       TEXT REFERENCES sources(source_id),
    page            TEXT,
    figure          TEXT,
    extraction_date TEXT,
    notes           TEXT
);

-- Hypothesis Discrimination Matrix: actual scored agreement of artifact evidence with each hypothesis
-- score          : pure prediction-vs-observation score, -2..+2 (RDORP-010 s10)
-- dp_weight      : discriminatory-power weight of the variable
-- conf_weight    : source-confidence weight of the corpus observation
-- class_weight   : discount applied to non-Observed evidence
-- weighted_score : score * dp_weight * conf_weight * class_weight
CREATE TABLE hdm_scores (
    hypothesis_id   TEXT    NOT NULL REFERENCES hypotheses(hypothesis_id),
    ev_id           TEXT    NOT NULL REFERENCES evidence_variables(ev_id),
    score           REAL    CHECK(score BETWEEN -2 AND 2),
    confidence      TEXT CHECK(confidence IN ('A','B','C','D','E')),
    dp_weight       REAL,
    conf_weight     REAL,
    class_weight    REAL,
    weighted_score  REAL,
    notes           TEXT,
    PRIMARY KEY (hypothesis_id, ev_id)
);

-- Final ranking output (RDORP-010 s11)
CREATE TABLE results (
    hypothesis_id     TEXT PRIMARY KEY REFERENCES hypotheses(hypothesis_id),
    scenario          TEXT,
    raw_score         REAL,
    weighted_score    REAL,
    rank              INTEGER,
    scored_variables  INTEGER,
    evidence_gaps     INTEGER,
    worst_case        REAL,
    best_case         REAL,
    robust            INTEGER,
    notes             TEXT
);

-- Pre-registered predictions.
--
-- A guess written down before the data exists is a test; the same guess written
-- down afterwards is a story. This table exists so the difference is on the
-- record. Each row states what is expected, what outcome would refute it, and
-- how to find out, and is stamped with the date it was registered.
--
-- PREDICTIONS ARE NEVER SCORED. They are not evidence and they never enter
-- hdm_scores. When the measurement is eventually made it becomes an ordinary
-- sourced observation like any other, and the prediction row is resolved
-- against it. database/validate.py enforces that a prediction is not carrying
-- an ev_id that has already been scored without being resolved.
CREATE TABLE predictions (
    prediction_id   TEXT PRIMARY KEY,
    ev_id           TEXT REFERENCES evidence_variables(ev_id),
    hypothesis_ids  TEXT,
    registered_on   TEXT NOT NULL,
    predicted       TEXT NOT NULL,
    falsified_if    TEXT NOT NULL,
    method          TEXT,
    basis           TEXT,
    confidence      TEXT CHECK(confidence IN ('low','medium','high')),
    status          TEXT NOT NULL CHECK(status IN (
                        'open','confirmed','refuted','withdrawn')),
    outcome         TEXT,
    resolved_on     TEXT
);

-- Fast screening of candidate functional domains.
--
-- Authoring a full 42-variable HPM for every idea is expensive and, once the
-- evidence is known, increasingly contaminated. A screen is cheaper and more
-- honest: it records only the predictions a domain CANNOT AVOID making - the
-- ones that follow from the mechanism whether the proposer likes them or not -
-- and checks those against the corpus.
--
-- A screen never produces a ranking and screening candidates never enter
-- hdm_scores. Its only outputs are: eliminated, or promote to a full hypothesis.
CREATE TABLE screening_candidates (
    candidate_id    TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    description     TEXT NOT NULL,
    creates         TEXT,
    notes           TEXT
);

CREATE TABLE screening (
    candidate_id    TEXT NOT NULL REFERENCES screening_candidates(candidate_id),
    ev_id           TEXT NOT NULL REFERENCES evidence_variables(ev_id),
    prediction      TEXT NOT NULL CHECK(prediction IN ('++','+','0','-','--')),
    reading         TEXT CHECK(reading IN (
                        'confirmed','weak_confirmed','ambiguous',
                        'weak_absent','absent')),
    rationale       TEXT NOT NULL,
    PRIMARY KEY (candidate_id, ev_id)
);


-- Usage value: was the proposed function worth having, and in what way?
--
-- Evidential fit and worth are different questions. A hypothesis can agree with
-- every observation and still be implausible, because nobody casts difficult
-- bronze for two centuries to obtain something a stick would give them.
--
-- Value is recorded in THREE kinds, because they are not interchangeable and
-- the corpus discriminates sharply between them:
--
--   product_value     worth of the material output, NET OF THE CHEAPEST
--                     SUBSTITUTE. -2 to +2. A useful product with a free
--                     substitute scores negative.
--   craft_value       is the difficulty and cost of MAKING it part of its
--                     worth? 0 to 2. A tool should be made as cheaply as will
--                     serve; a masterpiece or votive is made expensively on
--                     purpose.
--   experience_value  does USING it deliver something valued to the user in
--                     itself - display, contemplation, participation, standing
--                     - rather than through a product? 0 to 2.
--
-- NONE OF THIS ENTERS hdm_scores. Folding a judgement about worth into the
-- evidence score would let opinion masquerade as evidence. It is reported as a
-- separate axis.
CREATE TABLE utility_assessments (
    subject_id       TEXT PRIMARY KEY,
    subject_type     TEXT NOT NULL CHECK(subject_type IN ('hypothesis','candidate')),
    product          TEXT NOT NULL,
    substitute       TEXT,
    product_value    INTEGER NOT NULL CHECK(product_value BETWEEN -2 AND 2),
    craft_value      INTEGER NOT NULL CHECK(craft_value BETWEEN 0 AND 2),
    experience_value INTEGER NOT NULL CHECK(experience_value BETWEEN 0 AND 2),
    rationale        TEXT NOT NULL
);


-- Specimen quality and admissibility.
--
-- Not every specimen is fit for every purpose. A fragment weighing 1.7 g is
-- perfectly good evidence of decoration and useless evidence of mass; an
-- unprovenanced collection piece may carry excellent measurements and no
-- authenticity guarantee. This table records fitness per purpose rather than
-- admitting or excluding specimens wholesale.
--
-- provenance_grade   A excavated from a stratified, dated deposit
--                    B excavated or reported find, documented findspot,
--                      institutional custody
--                    C findspot recorded, surface or detector find
--                    D institutional custody, no findspot
--                    E private hands or no findspot and no independent
--                      publication
-- completeness       complete | incomplete | fragment | unknown
-- measurement_grade  direct | one_remove | two_removes | from_figure | none
CREATE TABLE specimen_quality (
    rd_id               TEXT PRIMARY KEY REFERENCES specimens(rd_id),
    completeness        TEXT NOT NULL CHECK(completeness IN (
                            'complete','incomplete','fragment','unknown')),
    provenance_grade    TEXT NOT NULL CHECK(provenance_grade IN ('A','B','C','D','E')),
    measurement_grade   TEXT NOT NULL CHECK(measurement_grade IN (
                            'direct','one_remove','two_removes','from_figure','none')),
    admit_mass          INTEGER NOT NULL CHECK(admit_mass IN (0,1)),
    admit_geometry      INTEGER NOT NULL CHECK(admit_geometry IN (0,1)),
    admit_context       INTEGER NOT NULL CHECK(admit_context IN (0,1)),
    outlier             INTEGER NOT NULL CHECK(outlier IN (0,1)),
    note                TEXT
);

CREATE TABLE experiments (
    exp_id          TEXT PRIMARY KEY,
    hypothesis_ids  TEXT,
    objective       TEXT,
    protocol        TEXT,
    outcome         TEXT,
    notes           TEXT
);
"""

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SOURCES = [
    ("PUB-0001", "Robert Nouwen", 1993,
     "Les dodécaèdres gallo-romains ajourés et bouletés",
     "Book", None, None, "B",
     "Foundational specimen catalogue; primary reference for Nouwen numbers"),
    ("PUB-0002", "Michael Guggenberger", None,
     "Roman dodecahedron catalogue",
     "Catalogue", None, None, "B",
     "Updated comprehensive catalogue; primary reference for Guggenberger numbers"),
    ("PUB-0003", "Guggenberger, Michael and Leach, Stephen", 2025,
     "The Gallo-Roman Dodecahedron and the Receptacle of All Becoming",
     "Journal", "10.1017/S000358152510036X",
     "https://doi.org/10.1017/S000358152510036X",
     "B",
     "The Antiquaries Journal 105: 31-54; published online 17 Nov 2025. "
     "Full text held at docs/sources/galloroman_dodecahedron_and_the_receptacle_of_all_becoming.pdf. "
     "Co-author Guggenberger maintains the reference catalogue, so corpus statistics "
     "reported here are catalogue-grade (B); the paper's Platonic/Pythagorean argument "
     "is author interpretation and is NOT extracted as evidence."),
    ("PUB-0004", "Wikipedia contributors", 2024,
     "Roman dodecahedron — Wikipedia",
     "Online", None,
     "https://en.wikipedia.org/wiki/Roman_dodecahedron",
     "E",
     "General overview only; not citable as primary archaeological source"),
    ("PUB-0005", "Historic England / English Heritage", 2024,
     "Roman Dodecahedra — English Heritage summary",
     "Online", None, None, "C",
     "Institutional archaeological summary for British context"),
    ("PUB-0006", "Portable Antiquities Scheme", 2024,
     "Portable Antiquities Scheme database — Roman dodecahedra records",
     "Database", None,
     "https://finds.org.uk/pas/recorded-find/search/?object_types=dodecahedron&broad_period=Roman",
     "B",
     "Primary source for British PAS-recorded specimens; cite individual record ID in page field"),
    ("PUB-0007", "Society of Antiquaries of London", 1739,
     "Minutes of meeting, 28 June 1739 (SAL/02/003/117)",
     "Archive", None,
     "https://collections.sal.org.uk/sal.02.003.117",
     "A",
     "First recorded Roman dodecahedron; George North exhibits object from Aston, Hertfordshire"),
    ("PUB-0008", "Tipper, Samantha", 2024,
     "Beautifully crafted Roman dodecahedron discovered in Lincoln - but what were they for?",
     "Article", "10.64628/AB.3gxryddu3",
     "https://theconversation.com/beautifully-crafted-roman-dodecahedron-discovered-in-lincoln-but-what-were-they-for-229131",
     "C",
     "The Conversation; describes Norton Disney 2023 find; author is NDAG treasurer"),
    ("PUB-0009", "Allason-Jones, L. and Miket, R.", 1984,
     "Catalogue of Small Finds from South Shields Roman Fort",
     "Book", None, None, "B",
     "Gloucester: Society of Antiquaries of London; no. 3.741 covers the South Shields dodecahedron"),
    ("PUB-0010", "Guillier, G.; Delage, R.; Besombes, P.-A.", 2008,
     "Une fouille en bordure des thermes de Jublains (Mayenne): enfin un dodecaedre en contexte archeologique!",
     "Journal", "10.4000/rao.680",
     "https://journals.openedition.org/rao/680",
     "A",
     "Revue archeologique de l'Ouest 25: 269-289. DIRECTLY CONSULTED; full text "
     "held at docs/sources/GuillierEtAl_2008_RAO_25_269_289_DOI.pdf. Excavation report "
     "for the only dodecahedron recovered from a sealed, dated, stratified "
     "context. Highest-grade source in the database."),
    ("PUB-0011", "KIK-IRPA (Royal Institute for Cultural Heritage, Belgium)", 2003,
     "BALaT database — dodecaedre (object 10140871)",
     "Database", None,
     "https://hdl.handle.net/20.500.14037/object.10140871",
     "B",
     "Musee Curtius, Liege; inv. I.7108; cite: KIK-IRPA 2003; CC0 metadata"),
    ("PUB-0012", "British Museum", 2024,
     "British Museum Collection Online",
     "Database", None,
     "https://www.britishmuseum.org/collection",
     "B",
     "Primary source for BM-held specimens; cite individual registration number in page field"),
    ("PUB-0013", "English Heritage / Google Arts & Culture", 2024,
     "Copper alloy dodecahedron — Corbridge Roman Museum",
     "Online", None,
     "https://artsandculture.google.com/asset/copper-alloy-dodecahedron/9QHFN8rTLq2bgg",
     "C",
     "English Heritage object record via Google Arts & Culture; no measurements given"),
    ("PUB-0014", "Wikimedia Commons / Wikidata (Rama, photographer)", 2019,
     "Dodecahedron X-37086 — Musee departemental de l'Arles antique (Wikidata Q62511455)",
     "Online", None,
     "https://commons.wikimedia.org/wiki/File:Dodecaedron-X-37086-IMG_9257.jpeg",
     "C",
     "CC-BY-SA; confirms findspot (thermae, 1939), museum, inventory X-37086, material bronze, date 3rd c."),
    ("PUB-0015", "Benoit, F.", 1957,
     "Deux enigmes archeologiques: dodecaedre perle d'Arles et anneau octogonal boulète de Vichy",
     "Journal", None, None, "B",
     "OGAM 9: 104-114; primary publication of the Arles dodecahedron; measurements likely present"),
    ("PUB-0016", "Anonymous", 1924,
     "Roman dodecahedron from Wales (Notes)",
     "Journal", "10.1017/S0003581500091459", None, "B",
     "Antiquaries Journal 4: 273. FIRST PAGE ONLY DIRECTLY CONSULTED; held at "
     "docs/urn_cambridge.org_id_binary-alt_20160626093900-45875-firstPage-"
     "S0003581500091459a.jpg. Records that dodecahedra are often found in "
     "France and on the Rhine but few in Britain, that one of the best British "
     "examples is in the Society of Antiquaries collection from Carmarthen, and "
     "that a further Welsh example was communicated on 12 March 1846 by the Rev "
     "Edward Harries of Llandysilio (no 41 in de Saint-Venant's list). The "
     "remainder of the note is not available and the specimen it illustrates "
     "has NOT been matched to an RD_ID."),
    ("PUB-0017", "Duval, Paul-Marie", 1981,
     "Comment decrire les dodecaedres gallo-romains, en vue d'une etude comparee",
     "Journal", "10.3406/galia.1981.1829",
     "https://www.persee.fr/doc/galia_0016-4119_1981_num_39_2_1829",
     "B",
     "Gallia 39(2): 195-200. DIRECTLY CONSULTED; full text held at "
     "docs/sources/galia_0016-4119_1981_num_39_2_1829.pdf. Defines the face-numbering "
     "and recording convention adopted by this project as its standard "
     "face-ordering convention (see docs/GEOMETRY_SPECIFICATION.md). Also "
     "publishes the Vienne (Isere) specimen."),
    ("PUB-0018", "Greiner, Bernhard A.", 1996,
     "Romische Dodekaeder: Untersuchungen zur Typologie, Herstellung, Verbreitung, und Funktion",
     "Journal", None, None, "B",
     "Carnuntum Jahrbuch 1995: 9-44; German analysis of typology, manufacture, distribution, function"),
    ("PUB-0019", "Sparavigna, Amelia Carolina", 2012,
     "Roman dodecahedron as dioptron: analysis of freely available data",
     "Preprint", "10.48550/arXiv.1206.0946",
     "https://arxiv.org/abs/1206.0946",
     "D",
     "arXiv:1206.0946v2. DIRECTLY CONSULTED; full text held at "
     "docs/sources/1206.0946v2.pdf. ADVOCACY SOURCE: the author argues for the "
     "rangefinder interpretation (H002), so its argument is treated as "
     "interpretation. Its VALUE to this project is the measurement tables it "
     "reproduces for Jublains, Avenches, Carnuntum, Tongres and Vienne. "
     "Provenance of those tables varies from museum measurement (Avenches, "
     "Appendix B) to values read off a photograph with a superimposed grid "
     "(the two Coulon specimens), and each observation drawn from it is graded "
     "accordingly. Note that the author, arguing FOR a measuring instrument, "
     "nonetheless concludes that no standard for these objects appears to have "
     "existed."),
    ("PUB-0020", "Hill, Christopher", 1994,
     "Gallo-Roman Dodecahedra: A Progress Report",
     "Journal", "10.1017/s0003581500024458", None, "B",
     "Antiquaries Journal 74: 289-292; review article with Carmarthen/SAL specimen data"),
    ("PUB-0021", "Guggenberger, Michael", 2013,
     "The Gallo-Roman Dodecahedron",
     "Journal", "10.1007/s00283-013-9403-7", None, "B",
     "Mathematical Intelligencer 35(4): 56-60; overview with specimen data; first recorded specimen documented"),

    # -----------------------------------------------------------------------
    # Bibliography entries added from the reference list of PUB-0003.
    # NOT DIRECTLY CONSULTED: these are recorded for literature coverage only.
    # They must never be used as the source_id of an observation; observations
    # extracted from PUB-0003 cite PUB-0003 and name the ultimate reference in
    # their notes field.
    # -----------------------------------------------------------------------
    ("PUB-0022", "Guggenberger, Michael", 1999,
     "Die gallo-roemischen Dodekaeder (master's thesis, University of Innsbruck)",
     "Thesis", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited throughout PUB-0003. Underlying source for "
     "corpus statistics on measurements (193-207, tabs 9-26), typology (50-4), "
     "knobs (37-40), wear (33-4, 61-2) and find contexts (tab 8). HIGHEST-PRIORITY "
     "ACQUISITION: most corpus-level values currently rest on it at one remove."),
    ("PUB-0023", "Guggenberger, Michael", 2021,
     "Das gallo-roemische Dodekaeder / The Gallo-Roman Dodecahedron - complete list of finds, Guggenberger No 1-129",
     "Catalogue", None,
     "http://saegewerk.org/laboratory/dodekaeder-dodecahedron",
     "B",
     "DIRECTLY CONSULTED, August 2026, from a copy supplied by the project "
     "owner after the site returned an SSL error to automated retrieval; held "
     "at docs/sources/Das_galloroemische_Dodekaeder_Saegewerk.pdf. "
     "THE REFERENCE CATALOGUE, compiled 1992-2021, last updated 12 January "
     "2021. Complete list of 129 specimens with findspot, year of discovery "
     "and TYPE. Nos 1-92 correspond to Greiner 1996; nos 1-101 appear in "
     "Guggenberger 1999. Supplies the type attributions that EV048 requires "
     "and the catalogue numbers for eighteen specimens in this database. "
     "Header figures: 129 finds; dating 2nd/3rd-4th century AD; hole "
     "diameters 6-40 mm; height without knobs 40-100 mm; weight 35-580 g with "
     "one over 1000 g; nine countries."),
    ("PUB-0024", "Thompson, F H", 1970,
     "Dodecahedrons again",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 36 (n 36). The Antiquaries "
     "Journal 50: 93-6. PUB-0003 states this paper conclusively refuted the "
     "distance-measuring interpretation (H002). Required reading before H002 "
     "is scored on published argument rather than on artefact evidence."),
    ("PUB-0025", "Guillier, G; Delage, R; Besombes, P-A", 2008,
     "Jublains dodecahedron - stratigraphic dating",
     "Journal", None, None, "A",
     "NOT DIRECTLY CONSULTED as a separate record - see PUB-0010, which is the "
     "same publication. Retained only to flag p 284, cited in PUB-0003 n 13 for "
     "the first-half-of-3rd-century deposition date."),
    ("PUB-0026", "Coombe, P and Henig, M", 2020,
     "Roman sculpture and religious objects from the Severn estuary",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 34 (n 27, n 28) for the "
     "Gloucester/Severn cache (Guggenberger no 122) and Lydney (no 68)."),
    ("PUB-0027", "Wheeler, R E M and Wheeler, T V", 1932,
     "Report on the excavation of the prehistoric, Roman and post-Roman site in Lydney Park, Gloucestershire",
     "Excavation report", None, None, "A",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 34 (n 28), 86 fig 20. "
     "Primary excavation report for the Lydney temple of Nodens."),
    ("PUB-0028", "Barthel, W", 1909,
     "Einzelfunde, in L Jacobi (ed), Das Kastell Zugmantel",
     "Excavation report", None, None, "A",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 32 (n 13), 35 (n 32) for the "
     "Zugmantel, Feldberg, Bachem and Bad Cannstatt specimens."),
    ("PUB-0029", "Winkelmann, F", 1933,
     "Report on the Pfofeld limes finds",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 35 (n 30), 137-8 tab 16, for "
     "the Pfofeld dodecahedron and the adjacent Mercury/Hermes-Thoth statuette."),
    ("PUB-0030", "Kolling, A", 1993,
     "Schwarzenacker cult precinct",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 35 (n 31), 124."),
    ("PUB-0031", "Berton, L", 2007,
     "Les dodecaedres bouletes celto-romains",
     "Article", None, None, "C",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 35 (n 29). Detection Passion 72; "
     "source for the specimen found north of Paris beside a bronze statuette."),
    ("PUB-0032", "Parker, A and Tipper, S (eds), with Hitchens, L", 2025,
     "The Norton Disney dodecahedron",
     "Book", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 34 (n 25), 33. Excavation-team "
     "account of the Norton Disney find (RD-0005)."),
    ("PUB-0033", "Henig, Martin", 2025,
     "Note on the Norton Disney dodecahedron and religious interpretation",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0003, 34 (n 26), 29-30."),
    ("PUB-0034", "Gruell, Tibor", 2016,
     "The Gallo-Roman dodecahedra: a review",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited throughout PUB-0003 (148, 150-5)."),

    # -----------------------------------------------------------------------
    # Batch 003 bibliography: works cited by PUB-0010, PUB-0017 and PUB-0019.
    # NOT DIRECTLY CONSULTED. Never used as the source_id of an observation.
    # -----------------------------------------------------------------------
    ("PUB-0035", "Deonna, W", 1954,
     "Les dodecaedres gallo-romains en bronze, ajoures et bouletes. A propos du dodecaedre d'Avenches",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0017, 195 n 2 and PUB-0010. "
     "Association Pro Aventico Bulletin 16: 19-89. Counted 52 specimens: 22 "
     "France, 14 Germany, 6 Switzerland, 3 Holland, 4 Great Britain, 1-2 "
     "Austria-Hungary. Earliest corpus census this project can cite."),
    ("PUB-0036", "de Saint-Venant, J", 1907,
     "Dodecaedres perles gallo-romains",
     "Book", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0010 and PUB-0016. Source of the "
     "de Saint-Venant specimen numbering; proposed a 3rd-4th century date."),
    ("PUB-0037", "Cervi-Brunier, I", 1985,
     "Dodecaedre en plomb revetu d'argent, Geneve",
     "Journal", None, None, "B",
     "NOT DIRECTLY CONSULTED - cited in PUB-0010. A SOLID lead dodecahedron "
     "coated with silver, each face engraved with a sign of the Zodiac. NOT a "
     "hollow knobbed dodecahedron and therefore NOT admitted to the specimen "
     "corpus; recorded because it bears on comparative variables."),
    ("PUB-0038", "Mereaux-Tanguy, Pierre", 1975,
     "Le dodecaedre: mesureur d'angle?",
     "Article", None, None, "D",
     "NOT DIRECTLY CONSULTED - quoted at length in PUB-0019 (ref 12). Kadath, "
     "May-July 1975. Reports measurements of the Tongres and Carnuntum "
     "specimens; non-peer-reviewed periodical."),
    ("PUB-0039", "Kurzweil, Friedrich", 1956,
     "Das Pentagondodekaeder des Museum Carnuntinum und seine Zweckbestimmung",
     "Journal", None, None, "C",
     "NOT DIRECTLY CONSULTED - cited in PUB-0019 (ref 14). Carnuntum Jahrbuch "
     "1956: 23-9. Original measurement of the Carnuntum specimen and origin of "
     "the surveying-instrument interpretation."),
    ("PUB-0040", "Bosse Buchanan, Sandrine (Musee romain d'Avenches)", 2012,
     "Measured hole diameters of the Avenches dodecahedron (e-mail communication)",
     "Personal communication", None, None, "B",
     "NOT DIRECTLY CONSULTED - the twelve measured diameters are reproduced in "
     "PUB-0019 Appendix B, table B1, which is where this project read them. "
     "Museum measurement to 0.01 mm and the most precise hole dataset in the "
     "database. Observations cite PUB-0019 at confidence C because they reach "
     "this project at one remove; obtaining the measurements directly from the "
     "museum would raise them to B."),

    # -----------------------------------------------------------------------
    # Batch 004 - located by web search, August 2026
    # -----------------------------------------------------------------------
    ("PUB-0041", "Lamb, Greg", 2026,
     "A Functional Reassessment of Roman Dodecahedra as Tools for Forming Standardised Wax Objects",
     "Journal", None,
     "https://exarc.net/ark:/88735/10843",
     "C",
     "The EXARC Journal 2026/2, published 29 May 2026. DIRECTLY CONSULTED. "
     "THE FIRST EXPERIMENTAL ARCHAEOLOGY SOURCE IN THIS DATABASE. Proposes "
     "that dodecahedra were forming aids for standardised wax elements such as "
     "bullae securing cords on documents, and tests it with 3D-printed "
     "replicas and a beeswax/pine-resin mixture. IMPORTANT LIMITATION: the "
     "trials use replicas, so the paper reports NO observations of wear, "
     "residue or any other property of an archaeological specimen. Its claims "
     "about what the knobs and apertures are FOR are interpretation, not "
     "observation, and are recorded as such. This is also an untested "
     "hypothesis in its own right (a wax-forming tool) that is not yet in the "
     "hypothesis set."),
    ("PUB-0044", "Musee du Louvre", 2024,
     "Collections en ligne - Dodecaedre (ED 4271; INV 2699; Br 1602)",
     "Database", None,
     "https://collections.louvre.fr/en/ark:/53355/cl010257522",
     "B",
     "DIRECTLY CONSULTED, August 2026; full record also held at docs/sources/Louvre_ED_4271.txt. Departement des Antiquites grecques, "
     "etrusques et romaines. Full catalogue record with dimensions, "
     "construction and decoration. INDEPENDENTLY CORROBORATES the ten-of-twelve "
     "decoration rule and the soldered-knob construction, from a source "
     "unconnected to PUB-0003, PUB-0010 and PUB-0017."),
    ("PUB-0045", "Rijksmuseum van Oudheden", 2024,
     "Collectie topstukken - Twaalfhoek (Dodecaeder), Elst",
     "Database", None,
     "https://www.rmo.nl/collectie/topstukken/twaalfhoek/",
     "B",
     "DIRECTLY CONSULTED, August 2026, from a copy supplied by the project owner after the page returned HTTP 403 to automated retrieval; held at docs/sources/Twaalfhoek.txt. UPGRADED FROM C TO B: the earlier record rested on a search-engine extract and is now replaced by the museum text. First Netherlands specimen in the database. The museum cites P van der Heijden, Grens van het Romeinse Rijk. De Limes in Gelderland, 2016, 131."),
    ("PUB-0046", "Musee d'Archeologie nationale", 2023,
     "L'objet du mois: le dodecaedre boulete, un objet etonnant et mysterieux",
     "Online", None,
     "https://musee-archeologienationale.fr/sites/archeonat/files/documents/ODM23Juin03.pdf",
     "C",
     "DIRECTLY CONSULTED, August 2026; held at docs/sources/ODM23Juin03.pdf. Museum object-of-the-month sheet, a "
     "public-outreach document rather than a catalogue entry, hence C. States "
     "that the MAN holds FOUR dodecahedra, of which only MAN68333 is named "
     "here. An online 3D model is advertised and has not been retrieved."),
    ("PUB-0048", "The Hunt Museum / Europeana", 2024,
     "Roman dodecahedron, Hunt Museum Limerick, HCM157 (Europeana 325/HCM157)",
     "Database", None,
     "https://www.huntmuseum.com/stories/objects-in-focus/roman-empire-dodecahedron/",
     "C",
     "PHOTOGRAPH DIRECTLY EXAMINED, August 2026, supplied by the project owner. "
     "High-resolution colour image of Guggenberger no 126, catalogued by "
     "PUB-0023 with place of discovery 'unknown (not Ireland)', before 1985, "
     "type 1a. Ireland was never part of the Roman empire, so the object is a "
     "collection acquisition and not an Irish find. No measurements published "
     "in the material consulted."),
    ("PUB-0047", "KIK-IRPA / Europeana", 2024,
     "Musee Curtius, Liege - dodecaedre, inv. I.7108 (Europeana AP_10295723)",
     "Database", None,
     "https://www.europeana.eu/item/2048001/AP_10295723",
     "C",
     "DIRECTLY CONSULTED, August 2026, from a copy supplied by the project "
     "owner; held at docs/sources/I_7108.txt. Aggregator record for the specimen "
     "already held as RD-0015 from PUB-0011. Adds a date range of AD 301-399 "
     "and a material statement of lead and bronze. Graded C because the "
     "aggregator record carries no measurements and no findspot beyond the "
     "inventory number."),
    ("PUB-0043", "Diocletian (Edictum de pretiis rerum venalium)", 301,
     "Edict on Maximum Prices",
     "Archive", None,
     "https://en.wikipedia.org/wiki/Edict_on_Maximum_Prices",
     "C",
     "CONSULTED ONLY THROUGH SECONDARY SUMMARY, not in the original text. "
     "Cited for one point of cultural context and for nothing else: the edict "
     "of AD 301 lists fourteen types of birrus, one of them the birrus "
     "Britannicus, a British woollen hooded cape priced at 6,000 denarii, and "
     "hooded garments are a style associated with Gaul and the north-western "
     "provinces generally. This establishes that a distinctive, high-value, "
     "regionally branded textile industry existed in the same provinces and "
     "the same window as the dodecahedra. It says NOTHING about dodecahedra "
     "and is never used as evidence about them."),
    ("PUB-0042", "Norton Disney History and Archaeology Group", 2025,
     "The Norton Disney Dodecahedron - excavation account",
     "Online", None,
     "https://nortondisneyhag.org/?page_id=2406",
     "B",
     "DIRECTLY CONSULTED. The excavating group's own account of the 2023 "
     "Norton Disney find (RD-0005), including the 2024 re-investigation of the "
     "feature. Excavator-grade context information for a specimen previously "
     "recorded here only through a newspaper article (PUB-0008) and a synthesis "
     "(PUB-0003)."),
]

# Maps freetext labels used in evidence_register_v1.csv to source_ids
SOURCE_MAP = {
    "Wikipedia":            "PUB-0004",
    "English Heritage":     "PUB-0005",
    "ADS report":           "PUB-0006",
    "Literature synthesis": None,   # derived claim; no single primary source
}

# ---------------------------------------------------------------------------
# Hypothesis Prediction Matrix
# Format: (hypothesis_id, ev_id, prediction, rationale)
# Predictions represent prior expectations IF the hypothesis is correct.
# All 8 hypotheses × 40 variables = 320 entries.
# ---------------------------------------------------------------------------
HPM_DATA = [
    # EV001 Overall dimensions (High discriminatory power)
    ("H001", "EV001", "+",  "A structural node needs to be large enough to accept rods; hand-sized range expected"),
    ("H002", "EV001", "0",  "Measuring instrument could work at any scale within hand-held range"),
    ("H003", "EV001", "0",  "Ritual objects vary widely in size"),
    ("H004", "EV001", "+",  "Candle holder must accommodate candles; small to medium size expected"),
    ("H005", "EV001", "+",  "Textile tool must be hand-held; size range consistent"),
    ("H006", "EV001", "0",  "Astronomical instrument size is not strongly constrained"),
    ("H007", "EV001", "0",  "Military equipment size is not strongly constrained by hypothesis alone"),
    ("H008", "EV001", "0",  "Shrine component size is not strongly constrained"),
    # EV002 Mass
    ("H001", "EV002", "+",  "Structural node under load benefits from mass"),
    ("H002", "EV002", "0",  "Mass not diagnostically relevant to measuring function"),
    ("H003", "EV002", "0",  "Ritual objects are not constrained by mass"),
    ("H004", "EV002", "0",  "Mass not relevant to candle-holding function"),
    ("H005", "EV002", "0",  "Textile tool mass not diagnostically relevant"),
    ("H006", "EV002", "0",  "Mass not relevant to astronomical function"),
    ("H007", "EV002", "+",  "Military equipment may require durability; higher mass is consistent"),
    ("H008", "EV002", "0",  "Shrine component mass is not constrained"),
    # EV003 Wall thickness
    ("H001", "EV003", "+",  "Thicker walls provide greater strength for load-bearing connector"),
    ("H002", "EV003", "0",  "Wall thickness irrelevant to measuring function"),
    ("H003", "EV003", "0",  "Wall thickness irrelevant to ritual use"),
    ("H004", "EV003", "0",  "Wall thickness irrelevant to candle-holding"),
    ("H005", "EV003", "0",  "Wall thickness irrelevant to textile function"),
    ("H006", "EV003", "0",  "Wall thickness irrelevant to astronomical use"),
    ("H007", "EV003", "+",  "Military equipment benefits from robustness"),
    ("H008", "EV003", "0",  "Wall thickness irrelevant to shrine use"),
    # EV004 Hole diameter distribution — Very High discriminatory power
    ("H001", "EV004", "++", "Variable hole sizes match rods of different cross-sections in a modular system"),
    ("H002", "EV004", "++", "Holes of specific sizes serve as diameter gauges; variation is functionally necessary"),
    ("H003", "EV004", "0",  "Ritual use does not require any particular hole size pattern"),
    ("H004", "EV004", "-",  "Candles are manufactured to standard sizes; systematically varying holes are unexpected"),
    ("H005", "EV004", "++", "Different hole sizes accommodate different yarn thicknesses; variation is expected"),
    ("H006", "EV004", "+",  "Specific hole sizes could serve as sighting apertures at different angular scales"),
    ("H007", "EV004", "0",  "Military function does not predict any particular hole size pattern"),
    ("H008", "EV004", "0",  "Shrine function does not require specific hole sizes"),
    # EV005 Opposite-hole relationships — Very High discriminatory power
    ("H001", "EV005", "++", "A structural node requires matching opposing holes so rods pass through axially"),
    ("H002", "EV005", "+",  "Opposing pairs of equal diameter would serve as bilateral gauges"),
    ("H003", "EV005", "0",  "Ritual use has no requirement for opposing holes to match"),
    ("H004", "EV005", "-",  "Candle holder needs one upward-facing hole; opposing symmetry is not required"),
    ("H005", "EV005", "+",  "Yarn routing through opposing holes is plausible for textile use"),
    ("H006", "EV005", "+",  "Sighting through opposing holes requires alignment; matching sizes expected"),
    ("H007", "EV005", "0",  "Military function does not predict opposing-hole symmetry"),
    ("H008", "EV005", "0",  "Shrine use does not require opposing-hole symmetry"),
    # EV006 Hole profile
    ("H001", "EV006", "++", "Rods require cylindrical or gently tapered holes for secure seating"),
    ("H002", "EV006", "++", "Precision diameter gauging requires consistent hole profiles"),
    ("H003", "EV006", "0",  "Ritual use has no requirement for specific hole profile"),
    ("H004", "EV006", "+",  "Candles require a socket; some profile consistency expected"),
    ("H005", "EV006", "+",  "Yarn routing benefits from smooth, consistent hole profiles"),
    ("H006", "EV006", "+",  "Sighting apertures benefit from clean cylindrical profiles"),
    ("H007", "EV006", "0",  "Military function does not predict specific hole profile"),
    ("H008", "EV006", "0",  "Shrine function does not predict specific hole profile"),
    # EV007 Hole edge radius (chamfers)
    ("H001", "EV007", "+",  "Chamfers facilitate rod insertion and prevent binding"),
    ("H002", "EV007", "-",  "Chamfered edges reduce gauge precision; not expected on measuring instrument"),
    ("H003", "EV007", "0",  "Chamfers are not diagnostically relevant to ritual use"),
    ("H004", "EV007", "+",  "Chamfered edges prevent candle damage during insertion"),
    ("H005", "EV007", "++", "Chamfered edges prevent yarn abrasion; strongly expected for textile use"),
    ("H006", "EV007", "0",  "Edge treatment not relevant to astronomical use"),
    ("H007", "EV007", "0",  "Edge treatment not relevant to military function"),
    ("H008", "EV007", "0",  "Edge treatment not relevant to shrine use"),
    # EV008 Knob diameter
    ("H001", "EV008", "++", "Knobs provide locking or spacer function; specific diameter is structurally meaningful"),
    ("H002", "EV008", "0",  "Knob diameter is not required for measuring function"),
    ("H003", "EV008", "+",  "Decorative knobs enhance prestige of ritual object"),
    ("H004", "EV008", "+",  "Knobs could stabilise the object as a stand"),
    ("H005", "EV008", "+",  "Knobs could serve as yarn guides or anchors"),
    ("H006", "EV008", "0",  "Knob diameter not relevant to astronomical use"),
    ("H007", "EV008", "0",  "Knob diameter not relevant to military function"),
    ("H008", "EV008", "+",  "Decorative knobs are consistent with a prestige shrine object"),
    # EV009 Knob symmetry
    ("H001", "EV009", "++", "Symmetric knobs ensure isotropic structural behaviour under load"),
    ("H002", "EV009", "+",  "Symmetric knobs support balanced orientation for measuring"),
    ("H003", "EV009", "+",  "Symmetric form enhances aesthetic and ritual value"),
    ("H004", "EV009", "+",  "Symmetry ensures stable resting position"),
    ("H005", "EV009", "0",  "Knob symmetry not required for textile use"),
    ("H006", "EV009", "++", "Symmetric knobs allow any face to serve as reference plane for sighting"),
    ("H007", "EV009", "0",  "Knob symmetry not required for military use"),
    ("H008", "EV009", "+",  "Symmetric form is aesthetically expected for a shrine component"),
    # EV010 Face symmetry
    ("H001", "EV010", "+",  "Regular faces ensure consistent load distribution across connections"),
    ("H002", "EV010", "++", "Precision instrument requires accurate, regular geometry"),
    ("H003", "EV010", "0",  "Face symmetry is not required for ritual use"),
    ("H004", "EV010", "0",  "Face symmetry not required for candle use"),
    ("H005", "EV010", "0",  "Face symmetry not required for textile use"),
    ("H006", "EV010", "++", "Accurate geometric form required for reliable astronomical sighting"),
    ("H007", "EV010", "0",  "Face symmetry not required for military use"),
    ("H008", "EV010", "0",  "Face symmetry not required for shrine use"),
    # EV011 Alloy composition
    ("H001", "EV011", "+",  "High-tin bronze is harder and stronger; appropriate for a load-bearing node"),
    ("H002", "EV011", "0",  "Alloy composition not diagnostic for measuring function"),
    ("H003", "EV011", "+",  "High-quality alloy is consistent with prestige ritual object"),
    ("H004", "EV011", "0",  "Alloy composition not diagnostic for candle function"),
    ("H005", "EV011", "0",  "Alloy composition not diagnostic for textile function"),
    ("H006", "EV011", "0",  "Alloy composition not diagnostic for astronomical use"),
    ("H007", "EV011", "+",  "Military equipment uses durable, high-quality alloys"),
    ("H008", "EV011", "+",  "Prestige material is consistent with shrine component"),
    # EV012 Casting quality
    ("H001", "EV012", "+",  "Structural integrity requires high casting quality"),
    ("H002", "EV012", "++", "Precision measuring instrument requires high casting quality"),
    ("H003", "EV012", "+",  "Prestige ritual object expected to be well-cast"),
    ("H004", "EV012", "0",  "Casting quality not strongly required for candle function"),
    ("H005", "EV012", "0",  "Casting quality not strongly required for textile function"),
    ("H006", "EV012", "++", "Astronomical instrument requires precise casting"),
    ("H007", "EV012", "+",  "Military equipment benefits from high quality"),
    ("H008", "EV012", "+",  "Prestige shrine component expected to be well-cast"),
    # EV013 Casting defects
    ("H001", "EV013", "-",  "Casting defects reduce structural integrity of a connector"),
    ("H002", "EV013", "--", "Any casting defect would invalidate measuring precision"),
    ("H003", "EV013", "0",  "Minor defects are acceptable in ritual objects"),
    ("H004", "EV013", "0",  "Minor defects do not affect candle-holding function"),
    ("H005", "EV013", "0",  "Minor defects do not affect textile function"),
    ("H006", "EV013", "--", "Casting defects in sighting holes would invalidate astronomical use"),
    ("H007", "EV013", "-",  "Defects reduce military equipment reliability"),
    ("H008", "EV013", "0",  "Minor defects are acceptable in a shrine component"),
    # EV014 Surface finishing
    ("H001", "EV014", "0",  "Surface finishing not required for structural function"),
    ("H002", "EV014", "+",  "Smooth finish reduces manufacturing tolerance errors in gauging"),
    ("H003", "EV014", "+",  "Fine surface finish expected on prestige ritual objects"),
    ("H004", "EV014", "0",  "Surface finish not required for candle function"),
    ("H005", "EV014", "+",  "Smooth finish reduces yarn friction and wear"),
    ("H006", "EV014", "+",  "Smooth finish reduces sighting error"),
    ("H007", "EV014", "0",  "Surface finish not diagnostic for military function"),
    ("H008", "EV014", "+",  "Fine finish expected on prestige shrine component"),
    # EV015 Repair evidence
    ("H001", "EV015", "+",  "A valued functional connector would be repaired rather than discarded"),
    ("H002", "EV015", "+",  "A precision measuring tool would be repaired to preserve function"),
    ("H003", "EV015", "+",  "A valuable ritual object would be repaired"),
    ("H004", "EV015", "0",  "Candle holders are not typically repaired"),
    ("H005", "EV015", "+",  "A working tool would be repaired to extend use-life"),
    ("H006", "EV015", "+",  "A precision instrument would be repaired"),
    ("H007", "EV015", "+",  "Military equipment is repaired in the field"),
    ("H008", "EV015", "+",  "A valued shrine component would be repaired"),
    # EV016 Tool marks (secondary machining)
    ("H001", "EV016", "+",  "Secondary machining of holes refines rod fit in a structural connector"),
    ("H002", "EV016", "++", "Lathe-turned or drilled holes are expected for measuring precision"),
    ("H003", "EV016", "0",  "Post-casting machining not required for ritual function"),
    ("H004", "EV016", "0",  "Post-casting machining not required for candle function"),
    ("H005", "EV016", "0",  "Post-casting machining not diagnostic for textile use"),
    ("H006", "EV016", "++", "Precise sighting holes require secondary machining"),
    ("H007", "EV016", "0",  "Post-casting machining not diagnostic for military use"),
    ("H008", "EV016", "0",  "Post-casting machining not diagnostic for shrine use"),
    # EV017 Internal hole wear — Very High discriminatory power
    ("H001", "EV017", "++", "Repeated rod insertion and removal produces diagnostic wear inside holes"),
    ("H002", "EV017", "+",  "Gauge use produces wear inside holes from objects being measured"),
    ("H003", "EV017", "-",  "Ritual object with minimal use would show little internal wear"),
    ("H004", "EV017", "+",  "Candle insertion and removal produces internal wear"),
    ("H005", "EV017", "++", "Yarn passing continuously through holes produces strong internal wear"),
    ("H006", "EV017", "0",  "Astronomical sighting produces no internal wear"),
    ("H007", "EV017", "0",  "Military function does not predict internal hole wear"),
    ("H008", "EV017", "-",  "Shrine component with minimal handling shows little internal wear"),
    # EV018 External wear
    ("H001", "EV018", "+",  "Construction use produces external handling wear"),
    ("H002", "EV018", "0",  "External wear not diagnostic for measuring function"),
    ("H003", "EV018", "-",  "Ritual objects are typically handled carefully; low external wear expected"),
    ("H004", "EV018", "0",  "External wear not diagnostic for candle function"),
    ("H005", "EV018", "+",  "Textile tool in regular use shows external wear from handling"),
    ("H006", "EV018", "0",  "External wear not diagnostic for astronomical use"),
    ("H007", "EV018", "+",  "Military equipment in active use shows external wear"),
    ("H008", "EV018", "-",  "Shrine component handled carefully; low external wear expected"),
    # EV019 Rope wear — Very High discriminatory power
    ("H001", "EV019", "++", "Ropes routed through holes or over knobs in a connector produce strong groove wear"),
    ("H002", "EV019", "-",  "Rope wear would not result from measuring use"),
    ("H003", "EV019", "0",  "Rope wear could occur from suspension in ritual contexts"),
    ("H004", "EV019", "0",  "Rope wear is not expected for candle use"),
    ("H005", "EV019", "+",  "Yarn routing over knobs or through holes could produce rope-like wear"),
    ("H006", "EV019", "-",  "Rope wear is not expected from astronomical use"),
    ("H007", "EV019", "0",  "Military use might involve rope but not diagnostically"),
    ("H008", "EV019", "0",  "Shrine component might be suspended by rope but not diagnostically"),
    # EV020 Rotational wear — Very High discriminatory power
    ("H001", "EV020", "-",  "A structural node is not expected to rotate in service"),
    ("H002", "EV020", "-",  "A measuring instrument is not expected to rotate"),
    ("H003", "EV020", "0",  "Rotational wear could result from spinning ritual use"),
    ("H004", "EV020", "+",  "A candle stand might be rotated for candle adjustment"),
    ("H005", "EV020", "+",  "Textile use could involve rotation of the tool"),
    ("H006", "EV020", "0",  "Astronomical use does not involve continuous rotation"),
    ("H007", "EV020", "0",  "Military use does not predict rotational wear"),
    ("H008", "EV020", "0",  "Shrine use does not predict rotational wear"),
    # EV021 Impact damage
    ("H001", "EV021", "+",  "Construction-site use exposes connector to accidental impacts"),
    ("H002", "EV021", "-",  "A precision measuring tool would be protected from impacts"),
    ("H003", "EV021", "-",  "Ritual object protected from impacts"),
    ("H004", "EV021", "0",  "Candle stand could sustain minor impacts"),
    ("H005", "EV021", "0",  "Textile tool not expected to sustain significant impacts"),
    ("H006", "EV021", "-",  "Precision instrument protected from impacts"),
    ("H007", "EV021", "+",  "Military use in field conditions could produce impact damage"),
    ("H008", "EV021", "-",  "Shrine component protected from impacts"),
    # EV022 Abrasion
    ("H001", "EV022", "+",  "Construction use produces surface abrasion"),
    ("H002", "EV022", "0",  "Abrasion not diagnostic for measuring use"),
    ("H003", "EV022", "-",  "Ritual object not expected to show significant abrasion"),
    ("H004", "EV022", "0",  "Abrasion not diagnostic for candle function"),
    ("H005", "EV022", "+",  "Textile tool in regular use sustains abrasion"),
    ("H006", "EV022", "0",  "Abrasion not diagnostic for astronomical use"),
    ("H007", "EV022", "+",  "Military equipment in field use sustains abrasion"),
    ("H008", "EV022", "-",  "Shrine component not expected to show significant abrasion"),
    # EV023 Thermal alteration — Very High discriminatory power
    ("H001", "EV023", "--", "Structural connector is not exposed to heat; thermal alteration is contradictory"),
    ("H002", "EV023", "--", "Measuring instrument would be ruined by thermal alteration"),
    ("H003", "EV023", "+",  "Ritual use may involve fire, incense or heat"),
    ("H004", "EV023", "++", "Candle holder is in direct contact with flame; soot and wax strongly expected"),
    ("H005", "EV023", "--", "Textile tool is not exposed to heat; thermal alteration is contradictory"),
    ("H006", "EV023", "--", "Astronomical instrument not exposed to heat"),
    ("H007", "EV023", "-",  "Military equipment not normally exposed to sustained heat"),
    ("H008", "EV023", "+",  "Shrine component may be associated with ritual fire or candles"),
    # EV024 Residues — Very High discriminatory power
    ("H001", "EV024", "0",  "Structural connector does not produce diagnostic chemical residues"),
    ("H002", "EV024", "0",  "Measuring use does not produce diagnostic residues"),
    ("H003", "EV024", "+",  "Ritual use may leave incense, oil or other organic residues"),
    ("H004", "EV024", "++", "Wax residues from candles are strongly expected"),
    ("H005", "EV024", "+",  "Wool grease and fibre residues may survive in holes"),
    ("H006", "EV024", "0",  "Astronomical use does not produce diagnostic residues"),
    ("H007", "EV024", "0",  "Military use does not produce diagnostic chemical residues"),
    ("H008", "EV024", "+",  "Ritual oils or incense residues may be present"),
    # EV025 Site type — Very High discriminatory power
    ("H001", "EV025", "+",  "Structural connector expected at construction or settlement sites"),
    ("H002", "EV025", "0",  "Measuring instrument could appear at any site type"),
    ("H003", "EV025", "+",  "Ritual object expected at temples, hoards, or votive deposits"),
    ("H004", "EV025", "+",  "Candle holder expected at domestic or villa sites"),
    ("H005", "EV025", "+",  "Textile tool expected at domestic, villa, or civilian settlement sites"),
    ("H006", "EV025", "+",  "Astronomical instrument expected at high-status or administrative sites"),
    ("H007", "EV025", "++", "Military equipment strongly expected at forts and military sites"),
    ("H008", "EV025", "+",  "Shrine component expected at domestic or religious sites"),
    # EV026 Roman province (distribution)
    ("H001", "EV026", "0",  "Structural connectors could appear across the empire; province is not diagnostic"),
    ("H002", "EV026", "0",  "Measuring instruments could appear across the empire"),
    ("H003", "EV026", "0",  "Ritual objects are not geographically constrained"),
    ("H004", "EV026", "0",  "Candle holders are not geographically constrained"),
    ("H005", "EV026", "+",  "North-western provinces had distinct textile traditions; some distribution clustering possible"),
    ("H006", "EV026", "0",  "Astronomical instruments not geographically constrained"),
    ("H007", "EV026", "+",  "Military frontier provinces (Rhine, Danube, Britain) would concentrate military equipment"),
    ("H008", "EV026", "0",  "Shrine components not geographically constrained"),
    # EV027 Associated finds — Very High discriminatory power
    ("H001", "EV027", "+",  "Associated construction materials or structural components would support this hypothesis"),
    ("H002", "EV027", "+",  "Associated measuring instruments or surveying tools would support this hypothesis"),
    ("H003", "EV027", "++", "Associated votive objects, coins, or ritual deposits would strongly support this"),
    ("H004", "EV027", "+",  "Associated lighting equipment would support candle use"),
    ("H005", "EV027", "++", "Associated spindle whorls, needles, loom weights, or fibre remains strongly support textile use"),
    ("H006", "EV027", "+",  "Associated astronomical or mathematical instruments would support this hypothesis"),
    ("H007", "EV027", "++", "Associated weapons, armour, or military equipment would strongly support this"),
    ("H008", "EV027", "++", "Associated religious objects, shrine fittings, or cult items strongly support this"),
    # EV028 Stratigraphy
    ("H001", "EV028", "0",  "Stratigraphic context is not strongly diagnostic for structural use"),
    ("H002", "EV028", "0",  "Stratigraphic context is not strongly diagnostic for measuring use"),
    ("H003", "EV028", "+",  "Votive deposit or destruction layer stratigraphy supports ritual use"),
    ("H004", "EV028", "0",  "Stratigraphic context is not strongly diagnostic for candle use"),
    ("H005", "EV028", "0",  "Stratigraphic context is not strongly diagnostic for textile use"),
    ("H006", "EV028", "0",  "Stratigraphic context is not strongly diagnostic for astronomical use"),
    ("H007", "EV028", "+",  "Military occupation or destruction layer stratigraphy supports military use"),
    ("H008", "EV028", "+",  "Stratigraphic context near hearth or storage supports domestic shrine use"),
    # EV029 Dating — Very High discriminatory power
    ("H001", "EV029", "0",  "2nd–4th c. date is consistent with peak of Roman construction; not strongly diagnostic"),
    ("H002", "EV029", "0",  "2nd–4th c. date is not strongly diagnostic for measuring use"),
    ("H003", "EV029", "0",  "2nd–4th c. ritual use is not strongly diagnostic"),
    ("H004", "EV029", "0",  "2nd–4th c. date is not strongly diagnostic for candle use"),
    ("H005", "EV029", "0",  "2nd–4th c. date is not strongly diagnostic for textile use"),
    ("H006", "EV029", "0",  "2nd–4th c. date is not strongly diagnostic for astronomical use"),
    ("H007", "EV029", "+",  "2nd–4th c. is the peak of Roman military presence on northern frontier"),
    ("H008", "EV029", "0",  "2nd–4th c. date is not strongly diagnostic for shrine use"),
    # EV030 Number at site
    ("H001", "EV030", "++", "Multiple connectors at one site strongly support a structural system using many nodes"),
    ("H002", "EV030", "+",  "Multiple measuring instruments suggest a standardised tool set"),
    ("H003", "EV030", "0",  "Single or multiple ritual objects are equally plausible"),
    ("H004", "EV030", "0",  "Single or multiple candle holders are equally plausible"),
    ("H005", "EV030", "+",  "Multiple textile tools could indicate workshop context"),
    ("H006", "EV030", "0",  "Single astronomical instrument is expected; multiples are unusual"),
    ("H007", "EV030", "+",  "Multiple identical items suggest military standardised equipment"),
    ("H008", "EV030", "0",  "Single shrine component is the most expected situation"),
    # EV031 Military association
    ("H001", "EV031", "+",  "Military construction would use structural connectors"),
    ("H002", "EV031", "+",  "Military surveying uses measuring instruments"),
    ("H003", "EV031", "0",  "Military personnel also engaged in ritual; not strongly diagnostic"),
    ("H004", "EV031", "0",  "Candles were used in military contexts; not strongly diagnostic"),
    ("H005", "EV031", "0",  "Soldiers also engaged in textile work; not strongly diagnostic"),
    ("H006", "EV031", "+",  "Military surveying and artillery used astronomical/geometric instruments"),
    ("H007", "EV031", "++", "Direct military association is a strong predictor for military equipment"),
    ("H008", "EV031", "0",  "Military shrine use is possible but not distinctive"),
    # EV032 Ritual association
    ("H001", "EV032", "-",  "Ritual context is not expected for a utilitarian structural connector"),
    ("H002", "EV032", "-",  "Ritual context is not expected for a utilitarian measuring instrument"),
    ("H003", "EV032", "++", "Direct ritual association is the strongest predictor for a ritual object"),
    ("H004", "EV032", "+",  "Candles have ritual uses; some association possible"),
    ("H005", "EV032", "-",  "Textile tools are not typically associated with ritual deposits"),
    ("H006", "EV032", "0",  "Astronomical instruments could be used in ritual contexts"),
    ("H007", "EV032", "0",  "Military objects can be ritually deposited"),
    ("H008", "EV032", "++", "Direct ritual association is the strongest predictor for a shrine component"),
    # EV033 Rod compatibility — Very High discriminatory power
    ("H001", "EV033", "++", "Rod compatibility is a prerequisite for the structural connector hypothesis"),
    ("H002", "EV033", "+",  "Rods of known diameter could serve as reference objects for measuring"),
    ("H003", "EV033", "0",  "Ritual objects are not required to accept rods"),
    ("H004", "EV033", "+",  "Candles are effectively cylindrical rods; compatibility expected"),
    ("H005", "EV033", "+",  "Knitting needles or rods could be inserted for textile use"),
    ("H006", "EV033", "0",  "Astronomical sighting does not require rod insertion"),
    ("H007", "EV033", "0",  "Military function does not specifically require rod compatibility"),
    ("H008", "EV033", "0",  "Shrine use does not require rod insertion"),
    # EV034 Rope compatibility — Very High discriminatory power
    ("H001", "EV034", "++", "Rope routing through holes or over knobs is a core prediction of the connector hypothesis"),
    ("H002", "EV034", "-",  "Rope compatibility is not required for measuring function"),
    ("H003", "EV034", "0",  "Ritual objects can be suspended but rope routing is not diagnostic"),
    ("H004", "EV034", "-",  "Rope routing is not expected for candle use"),
    ("H005", "EV034", "+",  "Yarn (a form of rope) routing through holes is expected for textile use"),
    ("H006", "EV034", "-",  "Rope routing is not expected for astronomical use"),
    ("H007", "EV034", "0",  "Rope use with military equipment is possible but not diagnostic"),
    ("H008", "EV034", "0",  "Rope suspension of shrine component is possible but not diagnostic"),
    # EV035 Structural stability — Very High discriminatory power
    ("H001", "EV035", "++", "Structural stability under load is a core requirement of a connector/node"),
    ("H002", "EV035", "0",  "Structural stability is not required for measuring function"),
    ("H003", "EV035", "0",  "Ritual object does not require structural load-bearing capability"),
    ("H004", "EV035", "+",  "A candle stand requires stability to prevent toppling"),
    ("H005", "EV035", "0",  "Textile tool does not require structural load-bearing capability"),
    ("H006", "EV035", "0",  "Astronomical instrument does not require structural stability under load"),
    ("H007", "EV035", "0",  "Military function does not require structural stability under load"),
    ("H008", "EV035", "0",  "Shrine component does not require structural stability under load"),
    # EV036 Load transfer
    ("H001", "EV036", "++", "Plausible force paths through the dodecahedron are required for a structural node"),
    ("H002", "EV036", "0",  "Load transfer is not relevant to measuring function"),
    ("H003", "EV036", "0",  "Load transfer is not relevant to ritual use"),
    ("H004", "EV036", "0",  "Load transfer not relevant beyond simple candle weight"),
    ("H005", "EV036", "0",  "Load transfer not relevant to textile function"),
    ("H006", "EV036", "0",  "Load transfer not relevant to astronomical use"),
    ("H007", "EV036", "0",  "Load transfer not specifically relevant to military function"),
    ("H008", "EV036", "0",  "Load transfer not relevant to shrine function"),
    # EV037 Assembly potential
    ("H001", "EV037", "++", "Modular assembly of multiple specimens into a larger structure is the core prediction"),
    ("H002", "EV037", "0",  "Assembly into larger structures is not required for measuring function"),
    ("H003", "EV037", "0",  "Assembly is not required for ritual function"),
    ("H004", "EV037", "0",  "Assembly into candle arrays is possible but not predicted"),
    ("H005", "EV037", "0",  "Assembly not required for textile function"),
    ("H006", "EV037", "0",  "Assembly not required for astronomical function"),
    ("H007", "EV037", "0",  "Assembly not required for military function"),
    ("H008", "EV037", "0",  "Assembly not required for shrine function"),
    # EV038 Orientation dependence
    ("H001", "EV038", "-",  "An isotropic connector works in any orientation; orientation dependence is unexpected"),
    ("H002", "EV038", "++", "Measuring function requires consistent orientation relative to the object being measured"),
    ("H003", "EV038", "0",  "Ritual use could require specific orientation or be orientation-independent"),
    ("H004", "EV038", "++", "Candle holder must remain upright; strong orientation dependence expected"),
    ("H005", "EV038", "0",  "Textile tool orientation is flexible"),
    ("H006", "EV038", "++", "Astronomical sighting requires precise and repeatable orientation"),
    ("H007", "EV038", "0",  "Military use does not specifically require fixed orientation"),
    ("H008", "EV038", "+",  "Shrine components are often displayed in a specific orientation"),
    # EV039 Standardisation across specimens
    ("H001", "EV039", "+",  "A modular structural system benefits from standardised components"),
    ("H002", "EV039", "++", "A measuring instrument must be standardised to produce reproducible results"),
    ("H003", "EV039", "0",  "Ritual objects vary widely; standardisation is not expected"),
    ("H004", "EV039", "0",  "Candle holders are not required to be standardised"),
    ("H005", "EV039", "+",  "Standardised textile tools produce consistent yarn gauges"),
    ("H006", "EV039", "++", "Astronomical instruments must be standardised to produce reliable results"),
    ("H007", "EV039", "+",  "Military equipment is typically standardised for logistics"),
    ("H008", "EV039", "0",  "Shrine components are not required to be standardised"),
    # EV040 Regional variation
    ("H001", "EV040", "-",  "A universal structural system should show low regional variation"),
    ("H002", "EV040", "-",  "A universal measuring standard should show low regional variation"),
    ("H003", "EV040", "+",  "Regional cult traditions would produce regional variation in ritual objects"),
    ("H004", "EV040", "0",  "Regional variation in candle holders is plausible"),
    ("H005", "EV040", "+",  "Regional textile traditions could produce variation in tool design"),
    ("H006", "EV040", "-",  "Astronomical phenomena are universal; regional variation is unexpected"),
    ("H007", "EV040", "+",  "Regional military traditions could produce variation in equipment design"),
    ("H008", "EV040", "+",  "Regional shrine traditions could produce variation in component design"),
]


# ---------------------------------------------------------------------------
# H009 - Tent apex / crown fitting (mobile shelter node)
#
# Proposed after batches 001-003 were scored. The object is read as the
# top-centre hub of a portable tent: rafters or a mast seat in the openings,
# guy lines bear on the body, and the whole thing is struck, packed, carried
# and re-erected at every move.
#
# DECLARED CONTAMINATION RISK. RDORP-010 section 6 requires the HPM to be
# filled in before artifact data is examined. That was not possible here: the
# hypothesis was raised after the evidence base existed and after this project
# had read it. The predictions below are therefore derived only from the
# mechanics the hypothesis itself requires - what a load-bearing, repeatedly
# assembled, mass-issued field fitting must be like - and each rationale states
# the mechanical reason rather than any observation. That discipline reduces
# the risk; it does not remove it. H009's score is reported separately and is
# NOT strictly comparable with H001-H008, whose matrix predates batches 002
# and 003.
# ---------------------------------------------------------------------------
HPM_H009 = [
    # --- Geometry ---------------------------------------------------------
    ("H009", "EV001", "+",
     "A hub must be large enough for several rafter ends to converge without "
     "fouling, and small enough to carry on campaign"),
    ("H009", "EV002", "-",
     "Campaign equipment is transported by mule or on the march; a shelter "
     "fitting is under constant pressure to be light. Specific expectation: "
     "well under 150 g"),
    ("H009", "EV003", "++",
     "The hub is the single point through which rafter compression and fabric "
     "tension pass. Wall thickness is the whole of its strength. Specific "
     "expectation: substantially over 3 mm"),
    ("H009", "EV004", "-",
     "Rafters of a symmetrical tent are cut to one diameter, so their sockets "
     "should be interchangeable; systematically varying sockets are not what "
     "the function calls for"),
    ("H009", "EV005", "+",
     "If a central mast passes through the hub, one opposed pair must match "
     "its diameter at both ends"),
    ("H009", "EV006", "++",
     "A pole must seat squarely and withdraw without binding, which requires a "
     "clean cylindrical or gently tapered socket"),
    ("H009", "EV007", "+",
     "Chamfered edges ease repeated insertion and stop the rim shaving the "
     "pole end"),
    ("H009", "EV008", "0",
     "The function does not call for knobs; they are neither required nor "
     "excluded by it"),
    ("H009", "EV009", "0",
     "Knob placement is not constrained by the function"),
    ("H009", "EV010", "++",
     "A hub that distributes load to rafters at equal angles must itself be "
     "geometrically regular, or the tent is pulled out of true"),

    # --- Manufacturing -----------------------------------------------------
    ("H009", "EV011", "++",
     "A load-bearing fitting needs a hard, strong alloy. A high-lead casting "
     "alloy creeps and deforms under sustained load and would be the wrong "
     "choice. Specific expectation: high-tin, low-lead bronze"),
    ("H009", "EV012", "+",
     "Sound casting matters where the object is structural"),
    ("H009", "EV013", "--",
     "Voids, seams and miscasts sit directly in the load path of a hub and are "
     "a failure risk; they should have been rejected at manufacture"),
    ("H009", "EV014", "0",
     "Surface finish is irrelevant to a fitting hidden at the top of a tent"),
    ("H009", "EV015", "++",
     "Equipment in continuous field use is repaired rather than discarded; a "
     "campaign fitting should show ancient repairs"),
    ("H009", "EV016", "0",
     "Secondary machining is not required by the function"),

    # --- Wear --------------------------------------------------------------
    ("H009", "EV017", "++",
     "THE CENTRAL PREDICTION OF A MOBILE FITTING. Poles are driven in and "
     "withdrawn every time camp is struck. Repeated hardwood-on-bronze contact "
     "inside the sockets must leave wear"),
    ("H009", "EV018", "++",
     "Struck, bundled, loaded and unloaded at every move; abrasion in transport "
     "is unavoidable"),
    ("H009", "EV019", "++",
     "Guy lines bearing on the body under tension leave grooves or polish"),
    ("H009", "EV020", "0",
     "Nothing in the function requires the hub to rotate"),
    ("H009", "EV021", "+",
     "Field equipment is dropped and knocked; impact damage is expected"),
    ("H009", "EV022", "+",
     "Abrasion follows from packing and transport"),
    ("H009", "EV023", "0",
     "A tent hub has no relation to heat or flame"),
    ("H009", "EV024", "+",
     "Contact with leather, tallow or fabric dressing should leave organic "
     "traces in the sockets"),

    # --- Archaeological context --------------------------------------------
    ("H009", "EV025", "++",
     "Tents belong to armies and travelling parties. Specific expectation: "
     "military camps, marching camps and temporary sites should dominate, and "
     "permanent civilian settlement should be marginal"),
    ("H009", "EV026", "--",
     "Tents accompany the army wherever it goes. Specific expectation: finds "
     "across the whole campaigning empire, including Italy, Spain, Africa and "
     "the eastern provinces. A distribution confined to a few adjacent "
     "north-western provinces would falsify the hypothesis. The form of this "
     "argument is not original: PUB-0003, 33 deploys it against a primary "
     "military purpose, citing the mobility of Roman soldiers"),
    ("H009", "EV027", "++",
     "Specific expectation: association with tent pegs, pole shoes, leather, "
     "and military or travelling equipment"),
    ("H009", "EV028", "+",
     "Temporary camp surfaces and abandonment layers are where a lost tent "
     "fitting would come to rest"),
    ("H009", "EV029", "-",
     "The Roman army used leather tents from the late Republic onward. A "
     "fitting for them should appear across the imperial period rather than in "
     "a narrow late window"),
    ("H009", "EV030", "++",
     "A camp holds hundreds of tents. Multiple hubs at one site are strongly "
     "expected, and the total surviving population should be large"),
    ("H009", "EV031", "++",
     "Direct military association is the core contextual claim"),
    ("H009", "EV032", "--",
     "A shelter fitting has no business in temple deposits, graves or rivers; "
     "ritual association would count against it"),

    # --- Engineering -------------------------------------------------------
    ("H009", "EV033", "++",
     "Rafters or a mast must seat in the openings; rod compatibility is a "
     "prerequisite"),
    ("H009", "EV034", "++",
     "Guy lines must be attachable to or routable through the fitting"),
    ("H009", "EV035", "++",
     "The hub must hold its shape under the combined thrust of the rafters"),
    ("H009", "EV036", "++",
     "Force must pass from each rafter through the body to the others; "
     "plausible load paths are required"),
    ("H009", "EV037", "0",
     "One hub serves one tent; assembly of multiple dodecahedra into a larger "
     "structure is not part of this hypothesis. This is what separates H009 "
     "from H001"),
    ("H009", "EV038", "++",
     "A tent apex has a definite top and bottom and a defined axis; the "
     "fitting must be orientable"),

    # --- Comparative -------------------------------------------------------
    ("H009", "EV039", "++",
     "Issued equipment is standardised so that any rafter fits any hub and "
     "damaged parts can be swapped in the field"),
    ("H009", "EV040", "--",
     "Army equipment is uniform across the provinces; strong regional "
     "variation would indicate local craft production rather than issue"),
]


# ---------------------------------------------------------------------------
# H010 - Parasol / umbrella crown fitting
#
# The object is read as the crown of a hand-carried sunshade or rain shade:
# ribs seat in the openings radiating from the centre, a shaft passes through
# the vertical axis, and the canopy is stretched over the ribs.
#
# SAME DECLARED CONTAMINATION RISK AS H009, and by now a larger one: this is
# the second hypothesis proposed after the evidence base was read, and each
# further one is authored by a project that knows the answers better. The
# predictions below are again derived only from what the mechanism requires -
# a radially symmetrical canopy on a hand-held lever - and each rationale
# states that mechanical reason. H010 is reported separately from H001-H008.
# ---------------------------------------------------------------------------
HPM_H010 = [
    # --- Geometry ---------------------------------------------------------
    ("H010", "EV001", "+",
     "The crown of a hand-carried canopy must be small; anything larger than a "
     "fist becomes unwieldy at the top of a shaft"),
    ("H010", "EV002", "--",
     "Mass at the crown sits at the far end of a lever held at arm's length, so "
     "every gram is multiplied. A hand-carried shade is under severe pressure "
     "to be light. Specific expectation: well under 100 g"),
    ("H010", "EV003", "-",
     "Canopy loads are fabric weight and wind only. Heavy walls buy nothing and "
     "cost weight where weight matters most; thin walls are expected"),
    ("H010", "EV004", "--",
     "THE CENTRAL PREDICTION AGAINST THIS HYPOTHESIS. The ribs of a radially "
     "symmetrical canopy are identical, so their sockets must be identical. "
     "Sockets of systematically differing diameter would mean ribs of differing "
     "thickness, and the canopy would pull unevenly and hang askew"),
    ("H010", "EV005", "++",
     "A shaft passing through the crown requires one opposed pair matched to "
     "its diameter at both ends"),
    ("H010", "EV006", "++",
     "Rib ends must seat cleanly and squarely in their sockets"),
    ("H010", "EV007", "++",
     "Ribs bear and flex against the socket rim; a sharp edge would cut into "
     "wooden or cane ribs at the point of highest stress"),
    ("H010", "EV008", "-",
     "Projections at every vertex sit directly under the canopy fabric drawn "
     "over the crown and would chafe and tear it"),
    ("H010", "EV009", "0",
     "Knob placement is not constrained by the function"),
    ("H010", "EV010", "++",
     "Radial symmetry of the canopy requires a regular hub; an irregular crown "
     "produces an irregular canopy"),

    # --- Manufacturing -----------------------------------------------------
    ("H010", "EV011", "0",
     "The fitting is not load-critical, so alloy choice is not diagnostic"),
    ("H010", "EV012", "+",
     "A visible fitting on a status accessory is expected to be well cast"),
    ("H010", "EV013", "-",
     "Visible casting flaws on a display object would be rejected"),
    ("H010", "EV014", "++",
     "The crown is the most visible part of an object carried above head "
     "height; fine finish and decoration are strongly expected"),
    ("H010", "EV015", "+",
     "A valued personal possession is repaired rather than discarded"),
    ("H010", "EV016", "+",
     "Decorative secondary working is expected on a display fitting"),

    # --- Wear --------------------------------------------------------------
    ("H010", "EV017", "++",
     "Ribs seat, bear and, if the shade folds or is dismantled for storage, "
     "move within the sockets. Wood against bronze at the load points must "
     "leave wear"),
    ("H010", "EV018", "+",
     "Carried, handled and stored; surface contact is constant"),
    ("H010", "EV019", "+",
     "Stretcher cords or a tie holding the canopy furled bear on the fitting"),
    ("H010", "EV020", "+",
     "A shade is turned on its shaft to follow the sun"),
    ("H010", "EV021", "0",
     "Impact damage is not specifically predicted"),
    ("H010", "EV022", "+",
     "Fabric drawn repeatedly over the crown abrades it"),
    ("H010", "EV023", "--",
     "Nothing in the function of a shade involves heat, flame or wax"),
    ("H010", "EV024", "+",
     "Textile or leather fibres and canopy dressing should remain in the "
     "sockets and under the rim"),

    # --- Archaeological context --------------------------------------------
    ("H010", "EV025", "++",
     "Specific expectation: urban civilian settlements and elite domestic "
     "contexts, where a personal luxury accessory is used and lost. NOT "
     "military camps"),
    ("H010", "EV026", "-",
     "A sunshade is most useful where the sun is strongest, so a sun-shade "
     "reading predicts finds concentrated in Italy, Spain, Africa and the "
     "eastern provinces. AGAINST THIS: a rain shade predicts the opposite, and "
     "the north-western provinces are wet. Set at '-' rather than '--' because "
     "the two readings of the same object point in opposite directions and the "
     "hypothesis does not choose between them"),
    ("H010", "EV027", "++",
     "Specific expectation: a shaft or handle, ribs of wood, cane, bone or "
     "metal, textile or leather from the canopy, and personal or toilet items"),
    ("H010", "EV028", "0",
     "No particular stratigraphy follows from the function"),
    ("H010", "EV029", "0",
     "Shades are attested across the imperial period; no narrow window is "
     "predicted"),
    ("H010", "EV030", "-",
     "A personal accessory is lost singly; concentrations at one site are not "
     "expected"),
    ("H010", "EV031", "--",
     "A parasol is the antithesis of field equipment. A substantial share of "
     "finds from military camps counts against the hypothesis"),
    ("H010", "EV032", "0",
     "A personal possession placed in a grave is ambiguous between ritual "
     "deposition and ordinary furnishing, so this is not diagnostic"),

    # --- Engineering -------------------------------------------------------
    ("H010", "EV033", "++",
     "Ribs and a shaft must seat in the openings; rod compatibility is a "
     "prerequisite"),
    ("H010", "EV034", "+",
     "Stretcher cords or a furling tie must be attachable"),
    ("H010", "EV035", "+",
     "The crown must hold its shape under modest canopy and wind load"),
    ("H010", "EV036", "+",
     "Rib thrust must pass through the crown to the shaft"),
    ("H010", "EV037", "0",
     "One crown serves one canopy; assembling several dodecahedra into a larger "
     "structure is no part of this hypothesis"),
    ("H010", "EV038", "++",
     "A canopy crown has an unambiguous top, bottom and axis: the shaft below, "
     "the fabric above"),

    # --- Comparative -------------------------------------------------------
    ("H010", "EV039", "-",
     "A bespoke luxury accessory made by individual craftsmen need not conform "
     "to any standard, and variation between makers is expected. THIS IS WHERE "
     "H010 DIFFERS SHARPLY FROM H009: nothing about a parasol requires issued, "
     "interchangeable parts"),
    ("H010", "EV040", "+",
     "Craft production of a fashion accessory varies by region and workshop"),
]


# ---------------------------------------------------------------------------
# H011 - Archery targeting / ranging aid
#
# The object is read as a sighting aid carried by an archer: a target of known
# size is viewed through a pair of opposed apertures, the pair in which it just
# fills the far opening gives the range bracket, and the archer sets elevation
# accordingly. Distinct from H002, which covers surveying and general
# distance measurement; H011 is personal field kit used at speed.
#
# This hypothesis is worth testing separately from H002 because it fails and
# succeeds on a different set of variables. Nothing passes through the holes,
# so the corpus-wide absence of internal wear - which refutes H001, H009 and
# H010 - is what an optical device predicts.
#
# SAME DECLARED CONTAMINATION RISK as H009 and H010, and now the third
# instance. Predictions derive only from what optical ranging requires.
# ---------------------------------------------------------------------------
HPM_H011 = [
    # --- Geometry ---------------------------------------------------------
    ("H011", "EV001", "+",
     "Must be held at arm's length and carried on the person; hand-sized"),
    ("H011", "EV002", "-",
     "Carried on the body, probably on a cord, and raised repeatedly; light is "
     "better"),
    ("H011", "EV003", "-",
     "A thick wall turns each aperture into a tube, which restricts the field "
     "of view and blurs the coincidence between near and far rims. A thin wall "
     "gives the crisp aperture edge the method depends on"),
    ("H011", "EV004", "++",
     "Apertures of differing size ARE the instrument: each pair covers a "
     "different range bracket. Uniform holes would make the device useless"),
    ("H011", "EV005", "++",
     "The user sights through a PAIR, so the relationship between the near and "
     "far aperture of each pair is the quantity being read. That relationship "
     "must be systematic and known across the six pairs, or the brackets do not "
     "form a usable series"),
    ("H011", "EV006", "++",
     "A clean circular aperture is required for a crisp sight picture"),
    ("H011", "EV007", "--",
     "Chamfers and rounded rims destroy the sharp edge the eye judges "
     "coincidence against"),
    ("H011", "EV008", "+",
     "Knobs give a firm grip, keep the object from rolling, and protect the "
     "aperture rims on which the calibration depends"),
    ("H011", "EV009", "0",
     "Knob placement is not constrained by the function"),
    ("H011", "EV010", "++",
     "Range is computed from the separation of the two apertures, so the "
     "face-to-opposite-face distance is the instrument's baseline. It must be "
     "accurate and identical on every axis, or every reading carries an error"),

    # --- Manufacturing -----------------------------------------------------
    ("H011", "EV011", "0",
     "Alloy is not diagnostic for an optical device"),
    ("H011", "EV012", "++",
     "A measuring instrument is only as good as its manufacture"),
    ("H011", "EV013", "--",
     "Casting flaws on or near the apertures corrupt the calibration directly"),
    ("H011", "EV014", "+",
     "Marking is expected on a graduated instrument"),
    ("H011", "EV015", "+",
     "A calibrated personal instrument is worth repairing"),
    ("H011", "EV016", "++",
     "Engraved rings around the apertures are exactly what a graduated "
     "instrument needs, whether as calibration marks or as an index of which "
     "pair is which"),

    # --- Wear --------------------------------------------------------------
    ("H011", "EV017", "-",
     "NOTHING PASSES THROUGH THE HOLES. An optical device predicts no internal "
     "wear, and its absence would count in favour of the hypothesis. This is "
     "the variable on which H011 differs most sharply from H001, H009 and H010"),
    ("H011", "EV018", "+",
     "Carried and handled constantly in the field"),
    ("H011", "EV019", "+",
     "Suspension on a cord or chain at the neck or belt bears on the object"),
    ("H011", "EV020", "0",
     "Selecting a pair means turning the object in the hand, not rotating it "
     "on an axis; no rotational wear pattern is predicted"),
    ("H011", "EV021", "+",
     "Field carriage means knocks"),
    ("H011", "EV022", "+",
     "Handling and suspension abrade the surface"),
    ("H011", "EV023", "--",
     "Nothing in optical ranging involves heat or flame"),
    ("H011", "EV024", "--",
     "Any substance in the apertures would obstruct the sight line; the holes "
     "must be kept clear"),

    # --- Archaeological context --------------------------------------------
    ("H011", "EV025", "++",
     "Specific expectation: military camps, frontier posts and hunting or "
     "rural contexts, where archers operate. Urban civilian settlement is not "
     "where a ranging aid is used or lost"),
    ("H011", "EV026", "--",
     "Archers served across the whole empire, and a device that genuinely "
     "improved shooting would spread with them. Confinement to a few adjacent "
     "north-western provinces would falsify the hypothesis"),
    ("H011", "EV027", "++",
     "Specific expectation: arrowheads, bow fittings, quiver mounts, or other "
     "military or hunting equipment"),
    ("H011", "EV028", "0",
     "No particular stratigraphy follows"),
    ("H011", "EV029", "0",
     "Archery spans the imperial period; no narrow window is predicted"),
    ("H011", "EV030", "+",
     "A unit of archers implies several devices at one site"),
    ("H011", "EV031", "++",
     "Direct military association is the core contextual claim"),
    ("H011", "EV032", "--",
     "A field instrument has no place in temple deposits, graves or rivers"),

    # --- Engineering -------------------------------------------------------
    ("H011", "EV033", "0",
     "Nothing is inserted; rod compatibility is neither required nor excluded"),
    ("H011", "EV034", "+",
     "A suspension cord is expected"),
    ("H011", "EV035", "0",
     "Structural load bearing is irrelevant"),
    ("H011", "EV036", "0",
     "Load transfer is irrelevant"),
    ("H011", "EV037", "0",
     "Assembly into larger structures is no part of this hypothesis"),
    ("H011", "EV038", "++",
     "The device must be held in a known orientation with a known pair aligned "
     "to the eye; which pair is in use must be identifiable at a glance"),

    # --- Comparative -------------------------------------------------------
    ("H011", "EV039", "++",
     "A ranging device that is not calibrated returns wrong ranges. The "
     "aperture series must be regular within an object and reproducible "
     "between objects if the training is to transfer between archers"),
    ("H011", "EV040", "-",
     "Strong regional variation would mean each device reads differently, and "
     "no transferable ranging practice could exist"),
]


# ---------------------------------------------------------------------------
# H012 - Spool-knitting / cord-working frame (knob-based)
#
# The object is read as a frame for looped cord work. Yarn is passed round the
# five knobs surrounding a chosen face, successive loops are lifted over, and
# the worked tube emerges through that face's opening. Different faces give
# different tube diameters. Nothing is inserted through the object and nothing
# is loaded across it.
#
# This is deliberately sharper than H005, which encodes textile use in general.
# The distinction that matters is the WEAR SIGNATURE: the working surfaces of
# this mechanism are the knob necks and the outer lip of the opening, NOT the
# bore and NOT the body. H005 predicts internal hole wear; H012 predicts its
# absence and predicts knob wear instead. The corpus-wide statement that the
# surfaces do not look worn was made about faces and interiors, and the only
# variable that would test this mechanism did not exist until this hypothesis
# was written - see EV041.
#
# SAME DECLARED CONTAMINATION RISK as H009-H011, and here it is at its most
# acute: several of the predictions below are '0', and a '0' authored by a
# project that already knows the answer is indistinguishable from a dodge. Each
# neutral prediction states why the mechanism is genuinely indifferent to that
# variable. Read them sceptically.
# ---------------------------------------------------------------------------
HPM_H012 = [
    # --- Geometry ---------------------------------------------------------
    ("H012", "EV001", "+",
     "Held in one hand and worked with the other; hand-sized"),
    ("H012", "EV002", "+",
     "Mass steadies the frame against yarn tension while it is worked"),
    ("H012", "EV003", "-",
     "The shell only has to carry the knobs. Yarn tension is trivial, so heavy "
     "walls buy nothing"),
    ("H012", "EV004", "++",
     "Each opening sets the bore of the tube worked over the knobs around it. "
     "A graded set of openings is a graded set of tube diameters, which is the "
     "functional point of the object"),
    ("H012", "EV005", "0",
     "Each face is worked on its own. NEUTRAL BECAUSE THE MECHANISM IS "
     "INDIFFERENT: no yarn passes from one face to its opposite, so what the "
     "opposite opening measures is irrelevant. This is the variable on which "
     "H001 and H011 lose heavily and H012 has no stake"),
    ("H012", "EV006", "+",
     "The worked tube passes out through the opening; a clean profile avoids "
     "snagging"),
    ("H012", "EV007", "++",
     "A rounded or bevelled lip is essential where yarn is drawn over the edge "
     "under tension. A sharp rim would cut it"),
    ("H012", "EV008", "++",
     "Knob diameter and neck form ARE the working surface. Each must hold a "
     "loop and release it when lifted"),
    ("H012", "EV009", "++",
     "The five knobs around a worked face must be uniform, or the stitches "
     "come out uneven"),
    ("H012", "EV010", "0",
     "NEUTRAL BECAUSE THE MECHANISM IS INDIFFERENT: only the local pentagon "
     "being worked matters. Departure from overall regularity does not affect "
     "the work"),

    # --- Manufacturing -----------------------------------------------------
    ("H012", "EV011", "0",
     "Alloy is not diagnostic for a tool under negligible load"),
    ("H012", "EV012", "+",
     "A snag-free working surface matters more than structural soundness"),
    ("H012", "EV013", "0",
     "NEUTRAL BECAUSE THE MECHANISM IS INDIFFERENT: the two production holes "
     "are simply not worked. The commonest type has ten ringed openings plus "
     "one opposed unringed pair, which leaves exactly ten usable faces"),
    ("H012", "EV014", "+",
     "Decoration is expected on a personal possession"),
    ("H012", "EV015", "+",
     "A working tool is repaired rather than replaced"),
    ("H012", "EV016", "+",
     "Finishing of the lips and knob necks to avoid snagging"),

    # --- Wear --------------------------------------------------------------
    ("H012", "EV017", "-",
     "NOTHING PASSES THROUGH THE BORE UNDER LOAD; the worked tube hangs free. "
     "Internal hole wear is not expected, and its absence counts in favour. "
     "THIS IS THE PREDICTION THAT SEPARATES H012 FROM H005, which predicts "
     "'++' here"),
    ("H012", "EV018", "+",
     "Constant handling of the body of the tool"),
    ("H012", "EV019", "0",
     "NEUTRAL BECAUSE THE TERMS DIFFER: EV019 records grooves or polish from "
     "rope. Fine yarn is not rope, and the surface it bears on is the knob, "
     "which is EV041"),
    ("H012", "EV020", "0",
     "The frame is turned in the hand as work proceeds round a face; there is "
     "no axle and no rotating contact, so no rotational wear pattern forms"),
    ("H012", "EV021", "0",
     "Impact damage is not predicted by domestic use"),
    ("H012", "EV022", "++",
     "Yarn drawn repeatedly over and down the knob necks abrades them at the "
     "base"),
    ("H012", "EV023", "--",
     "Nothing in cord work involves heat, flame or wax"),
    ("H012", "EV024", "+",
     "Textile fibres should remain in the knob necks and against the lips"),
    ("H012", "EV042", "-",
     "Microwear will show contact on the outer lip where yarn is drawn over "
     "the edge, and NOT inside the bore. NOTE: H001-H011 are deliberately "
     "silent on EV042 because they were specified before the variable existed. "
     "Their predictions for it MUST be authored before the microwear study is "
     "read, not afterwards"),
    ("H012", "EV041", "++",
     "THE CENTRAL PREDICTION OF THIS HYPOTHESIS. Years of yarn drawn over the "
     "knobs must leave polish, grooving or abrasion on the knobs and their "
     "necks. This is the variable that decides H012, and it did not exist in "
     "the evidence set before the hypothesis was written"),

    # --- Archaeological context --------------------------------------------
    ("H012", "EV025", "+",
     "Specific expectation: domestic and settlement contexts, where cord work "
     "is done"),
    ("H012", "EV026", "+",
     "A craft technique is culturally transmitted and may be confined to the "
     "region that practises it"),
    ("H012", "EV027", "+",
     "Specific expectation: spindle whorls, loom weights, needles or other "
     "textile equipment"),
    ("H012", "EV028", "0",
     "No particular stratigraphy follows from domestic use"),
    ("H012", "EV029", "0",
     "No narrow chronological window follows from the mechanism"),
    ("H012", "EV030", "0",
     "A personal tool is lost singly, but a workshop could hold several"),
    ("H012", "EV031", "0",
     "Soldiers mend and make clothing, so a military presence neither supports "
     "nor contradicts"),
    ("H012", "EV032", "-",
     "A working tool in temple deposits and rivers is not what the mechanism "
     "predicts"),

    # --- Engineering -------------------------------------------------------
    ("H012", "EV033", "0",
     "Nothing is inserted; rod compatibility is irrelevant either way"),
    ("H012", "EV034", "+",
     "Yarn must pass over the knobs and out through the opening"),
    ("H012", "EV035", "+",
     "The frame must sit or be held steady while worked"),
    ("H012", "EV036", "0",
     "No load is transferred across the object"),
    ("H012", "EV037", "0",
     "Assembly into larger structures is no part of this hypothesis"),
    ("H012", "EV038", "0",
     "NEUTRAL BECAUSE THE MECHANISM IS INDIFFERENT: whichever face is being "
     "worked is turned downward for the moment; there is no fixed global "
     "orientation and none is required"),

    # --- Comparative -------------------------------------------------------
    ("H012", "EV039", "-",
     "A personal craft tool need not conform to any standard. The gauge wanted "
     "varies with the work and the worker, so variation between objects is "
     "what the mechanism predicts"),
    ("H012", "EV040", "+",
     "Craft traditions and their tools vary by region"),
]


# ---------------------------------------------------------------------------
# H013 - Rope-laying top (rotated, core through one aperture)
#
# The mechanism as specified: the core or leading line passes through ONE
# aperture; the strands run on the OUTSIDE of the object, held apart and guided
# by the knobs; the object is TURNED as the work advances, laying the strands
# around the core at a constant angle. Only one aperture is in use at a time,
# and different apertures suit different core and rope diameters.
#
# This is the direct counterpart of H012 and the pair is worth having. Both are
# cord-work hypotheses in the same domain, both use the knobs, both explain the
# graded apertures. They differ on exactly one thing: H012 drapes light yarn
# over the knobs with nothing passing through the bore and no rotation, while
# H013 runs a tensioned core THROUGH the bore and TURNS the object against it.
#
# That single difference puts H013 in front of three Very High wear variables
# that H012 sidesteps - EV017 internal hole wear, EV019 rope wear and EV020
# rotational wear - all three of which the corpus records as absent. It also
# reverses H012's EV042 prediction: H013 requires bore contact, H012 forbids it.
# Pre-registered prediction P-0004 therefore discriminates between them.
#
# SAME DECLARED CONTAMINATION RISK as H009-H012.
# ---------------------------------------------------------------------------
HPM_H013 = [
    # --- Geometry ---------------------------------------------------------
    ("H013", "EV001", "+",
     "Must be gripped and turned in the hand while the work advances"),
    ("H013", "EV002", "+",
     "Mass gives the turning tool inertia and helps hold steady tension"),
    ("H013", "EV003", "-",
     "Strand tension in hand-laid cord is modest; heavy walls buy nothing"),
    ("H013", "EV004", "++",
     "Each aperture suits a different core and finished-rope diameter. A "
     "graded set of apertures is a graded set of cord gauges, which is the "
     "functional point of the object"),
    ("H013", "EV005", "0",
     "NEUTRAL BECAUSE THE MECHANISM IS INDIFFERENT: only one aperture is in "
     "use at a time and the core does not continue to the opposite face, so "
     "what the opposite aperture measures is irrelevant"),
    ("H013", "EV006", "++",
     "The core runs through the aperture under tension while the object turns; "
     "a clean, true profile is required or the core binds and chafes"),
    ("H013", "EV007", "++",
     "The rim must be rounded, because the core bears against it continuously "
     "and a sharp edge would cut the fibre"),
    ("H013", "EV008", "++",
     "THE KNOBS ARE THE STRAND GUIDES. Their diameter and spacing set the "
     "angle at which each strand meets the core, which is what determines the "
     "lay of the finished rope"),
    ("H013", "EV009", "++",
     "The five knobs around the working aperture must be uniform and regularly "
     "placed, or the strands are laid at unequal angles and the rope is uneven"),
    ("H013", "EV010", "+",
     "Even strand spacing requires a regular pentagon around the working face"),

    # --- Manufacturing -----------------------------------------------------
    ("H013", "EV011", "0",
     "Alloy is not diagnostic for a tool under fibre tension"),
    ("H013", "EV012", "+",
     "A smooth surface is needed so the fibre is not abraded as it runs"),
    ("H013", "EV013", "0",
     "NEUTRAL BECAUSE THE MECHANISM IS INDIFFERENT: the two production holes "
     "are simply not chosen as the working aperture"),
    ("H013", "EV014", "+",
     "Decoration is expected on a personal working tool"),
    ("H013", "EV015", "+",
     "A tool in continuous use is repaired rather than replaced"),
    ("H013", "EV016", "+",
     "Finishing of the rim and knobs so that fibre does not snag"),

    # --- Wear --------------------------------------------------------------
    ("H013", "EV017", "++",
     "THE DECISIVE PREDICTION. A tensioned core passes through the aperture "
     "while the object is turned against it. Bore wear is unavoidable and "
     "should be circumferential. THIS IS WHERE H013 AND H012 SEPARATE: H012 "
     "predicts '-' here because nothing passes through its bore"),
    ("H013", "EV018", "+",
     "Constant handling of the body of the tool"),
    ("H013", "EV019", "++",
     "Every strand bears on a knob and on the aperture rim under tension "
     "throughout the work. If any hypothesis predicts rope wear, this one does"),
    ("H013", "EV020", "++",
     "The object is turned repeatedly under load and the contact between cord "
     "and object is rotational by construction"),
    ("H013", "EV021", "0",
     "Impact damage is not predicted by workshop use"),
    ("H013", "EV022", "++",
     "Fibre running under tension abrades the knobs and the aperture rim"),
    ("H013", "EV023", "--",
     "Nothing in cord laying involves heat, flame or wax"),
    ("H013", "EV024", "+",
     "Fibre traces should remain against the rim and in the knob necks"),
    ("H013", "EV041", "++",
     "Strands are guided by the knobs under tension throughout; knob wear is "
     "predicted as strongly here as by H012"),
    ("H013", "EV042", "+",
     "Microwear should show contact INSIDE the bore, and circumferentially. "
     "This is the exact opposite of H012's prediction, which is why the "
     "pre-registered prediction P-0004 discriminates between them"),

    # --- Archaeological context --------------------------------------------
    ("H013", "EV025", "+",
     "Specific expectation: settlement, domestic and workshop contexts, where "
     "cordage is made"),
    ("H013", "EV026", "+",
     "A craft technique is culturally transmitted and may be confined to the "
     "region that practises it"),
    ("H013", "EV027", "+",
     "Specific expectation: fibre-processing equipment, spindle whorls, raw "
     "fibre, or finished cordage"),
    ("H013", "EV028", "0",
     "No particular stratigraphy follows from workshop use"),
    ("H013", "EV029", "0",
     "Cordage is made in every period; no narrow window is predicted"),
    ("H013", "EV030", "0",
     "A personal tool is lost singly, but a workshop could hold several"),
    ("H013", "EV031", "0",
     "Rope is needed by armies and civilians alike, so a military presence "
     "neither supports nor contradicts"),
    ("H013", "EV032", "-",
     "A working tool in temple deposits and rivers is not what the mechanism "
     "predicts"),

    # --- Engineering -------------------------------------------------------
    ("H013", "EV033", "0",
     "Nothing rigid is inserted; rod compatibility is irrelevant either way"),
    ("H013", "EV034", "++",
     "A core routed through an aperture and strands routed over the knobs is "
     "entirely a claim about cord routing"),
    ("H013", "EV035", "+",
     "The body must hold its form against the combined pull of the strands"),
    ("H013", "EV036", "0",
     "No structural load is transferred across the object"),
    ("H013", "EV037", "0",
     "Assembly into larger structures is no part of this hypothesis"),
    ("H013", "EV038", "+",
     "There is a working axis while the tool is in use - the core through the "
     "chosen aperture, about which the object turns - though which aperture "
     "provides it is free"),

    # --- Comparative -------------------------------------------------------
    ("H013", "EV039", "-",
     "A personal craft tool need not conform to any standard; the gauge wanted "
     "varies with the work"),
    ("H013", "EV040", "+",
     "Craft traditions and their tools vary by region"),
]


# ---------------------------------------------------------------------------
# H014 - Wax bulla / seal former
#
# Promoted from screening candidate C-10, the only candidate of ten to survive
# with a positive screen. Softened wax is pressed within the object around a
# knotted cord to form a standardised sealing element; the knobs act as spacers
# limiting compression; the graded apertures take cords of differing thickness
# and give finger access to release the formed piece.
#
# CONTAMINATION STATUS DIFFERS FROM H009-H013, AND IN ITS FAVOUR. The hypothesis
# is NOT this project's invention: it was proposed and experimentally tested by
# Lamb (PUB-0041, EXARC Journal 2026/2) independently of this database, and it
# is the only hypothesis in the set with any experimental work behind it. What
# remains contaminated is the prediction matrix below, which this project
# authored knowing the evidence. That is a weaker contamination than H009-H013,
# where the hypothesis itself was reverse-engineered from the evidence.
#
# NOTE ALSO the limitation of the experiment: Lamb's trials used a 3D-printed
# replica and report no observation of any archaeological specimen. They show
# the shape can do the job. They are not evidence that any dodecahedron did.
# ---------------------------------------------------------------------------
HPM_H014 = [
    # --- Geometry ---------------------------------------------------------
    ("H014", "EV001", "+",
     "Held in one hand while wax is pressed with the other; hand-sized"),
    ("H014", "EV002", "+",
     "Mass steadies the tool against the pressing force"),
    ("H014", "EV003", "-",
     "The shell contains soft wax and carries no structural load; thin walls "
     "are sufficient and expected"),
    ("H014", "EV004", "++",
     "Graded apertures take cords of differing thickness, which is the "
     "functional claim of the hypothesis (PUB-0041)"),
    ("H014", "EV005", "0",
     "NEUTRAL: the cord is knotted within the object rather than drawn through "
     "an axis, and the source does not specify that it exits an opposite face"),
    ("H014", "EV006", "+",
     "A clean aperture lets the cord seat and the formed piece release"),
    ("H014", "EV007", "+",
     "A rounded lip releases wax cleanly and does not cut the cord"),
    ("H014", "EV008", "++",
     "THE KNOBS ARE THE SPACERS that limit compression and set the thickness "
     "of the formed piece. This is the mechanism's explicit claim (PUB-0041) "
     "and it is the only hypothesis in the set that assigns the knobs a "
     "primary working role rather than a protective or decorative one"),
    ("H014", "EV009", "++",
     "Spacers must be uniform, or the thickness of the formed piece varies "
     "around its perimeter"),
    ("H014", "EV010", "+",
     "A regular body gives a consistent formed shape"),

    # --- Manufacturing -----------------------------------------------------
    ("H014", "EV011", "0",
     "Alloy is not diagnostic for working soft wax"),
    ("H014", "EV012", "+",
     "A smooth surface releases wax without tearing it"),
    ("H014", "EV013", "0",
     "NEUTRAL: a face carrying casting flaws is simply not used as the "
     "working face"),
    ("H014", "EV014", "++",
     "Decoration around the aperture would IMPRESS ITSELF ON THE WAX. On this "
     "hypothesis the concentric rings are not ornament at all but the device "
     "that marks the sealing, which is what a bulla is for"),
    ("H014", "EV015", "+",
     "A working tool is repaired rather than replaced"),
    ("H014", "EV016", "++",
     "The engraved rings are the marking surface, and engraving them after "
     "casting is exactly the secondary working EV016 records"),

    # --- Wear --------------------------------------------------------------
    ("H014", "EV017", "-",
     "Wax is soft and the cord is knotted rather than drawn under tension. No "
     "bore wear is predicted and its absence counts in favour"),
    ("H014", "EV018", "+",
     "Constant handling of the body of the tool"),
    ("H014", "EV019", "0",
     "NEUTRAL: cords are knotted in place, not routed under tension"),
    ("H014", "EV020", "0",
     "Nothing in the mechanism rotates"),
    ("H014", "EV021", "0",
     "Impact damage is not predicted by desk use"),
    ("H014", "EV022", "0",
     "Wax is softer than bronze and does not abrade it"),
    ("H014", "EV023", "-",
     "Wax is worked soft, not melted in the object. Thermal alteration would "
     "count AGAINST the hypothesis, which is what distinguishes it from H004"),
    ("H014", "EV024", "++",
     "THE DECISIVE PREDICTION. Beeswax and resin worked in the object should "
     "leave recoverable residue on the interior and around the apertures. "
     "EV024 has never been measured"),

    # --- Archaeological context --------------------------------------------
    ("H014", "EV025", "++",
     "Specific expectation: urban, administrative and commercial contexts, "
     "matching the distribution of seal boxes (PUB-0041)"),
    ("H014", "EV026", "+",
     "Seal boxes are themselves concentrated in Britain and the north-western "
     "provinces, so regional confinement is what the hypothesis predicts. NOTE "
     "THIS IS UNUSUAL: every other utilitarian hypothesis is damaged by the "
     "restricted distribution, and this one expects it"),
    ("H014", "EV027", "++",
     "Specific expectation: seal boxes, styli, writing tablets, document "
     "fittings or other administrative equipment"),
    ("H014", "EV028", "0",
     "No particular stratigraphy follows"),
    ("H014", "EV029", "0",
     "Sealing practice spans the imperial period"),
    ("H014", "EV030", "0",
     "An office might hold one or several"),
    ("H014", "EV031", "0",
     "Seal boxes occur in administrative AND military contexts, so a military "
     "presence neither supports nor contradicts"),
    ("H014", "EV032", "-",
     "A desk tool in temple deposits, graves and rivers is not predicted"),

    # --- Engineering -------------------------------------------------------
    ("H014", "EV033", "0",
     "Nothing rigid is inserted"),
    ("H014", "EV034", "+",
     "Cords must pass into the object and be knotted within it"),
    ("H014", "EV035", "+",
     "The body must not deform under the pressing force"),
    ("H014", "EV036", "0",
     "No structural load is transferred across the object"),
    ("H014", "EV037", "0",
     "Assembly into larger structures is no part of this hypothesis"),
    ("H014", "EV038", "+",
     "A working face is chosen and presented upward while wax is pressed, "
     "though which face is free"),

    # --- Comparative -------------------------------------------------------
    ("H014", "EV039", "+",
     "Bullae are described by the hypothesis as standardised, so some "
     "consistency between tools is expected. THIS IS THE HYPOTHESIS'S "
     "WEAKEST POINT and it is not negotiable: the corpus is not standardised"),
    ("H014", "EV040", "+",
     "Regional workshops producing an administrative accessory would vary"),
    ("H014", "EV041", "0",
     "The knobs are pressed into soft wax, not drawn over by cord under "
     "tension; no knob wear is predicted either way"),
    ("H014", "EV042", "-",
     "Microwear should show no bore contact"),
]


# ---------------------------------------------------------------------------
# Per-cell readings (see the hpm_readings table comment)
#
# Only H009 has entries. H001-H008 predict site type, province, associated
# finds and dating too vaguely for the corpus evidence to be read against them,
# which is why those variables are marked discriminating = 0. H009 names what
# it expects in each case, so the same evidence can be read against it.
#
# This makes H009's test HARSHER than the test applied to H001-H008. That is
# the intended behaviour of the framework, not a bias against it: a hypothesis
# that says what it expects can be wrong, and the predictive-commitment figures
# report how much each hypothesis staked. The `same_footing` scenario in
# score_hdm.py re-runs the comparison with these readings ignored.
# ---------------------------------------------------------------------------
HPM_READINGS = [
    ("H009", "EV025", "absent",
     "H009 predicts '++' that military camps and temporary sites dominate. The "
     "corpus shows more than half of located finds from cities and other "
     "settlements and just under one-fifth from military camps (PUB-0003, 33). "
     "The predicted dominance is not present"),
    ("H009", "EV026", "confirmed",
     "H009 predicts '--' that a distribution confined to a few adjacent "
     "north-western provinces would falsify it. The corpus is c 70 per cent "
     "Gallic and Germanic and c 20 per cent British, with none from Italy, "
     "Spain, Africa or the eastern provinces (PUB-0003, 32). The confinement "
     "the prediction identified as falsifying is confirmed to be present"),
    ("H009", "EV027", "absent",
     "H009 predicts '++' association with tent pegs, pole shoes, leather and "
     "travelling equipment. The documented associations are bronze statuettes "
     "of deities, a bone object in a grave, a cache attributed to a temple, "
     "rich grave goods and a precision balance (PUB-0003, 34-6; PUB-0010, "
     "paras 42-47). None is shelter equipment"),
    ("H009", "EV029", "confirmed",
     "H009 predicts '-' that a narrow late window is unexpected, since the army "
     "used leather tents from the late Republic. The corpus range is c AD 200 "
     "to the late 4th century (PUB-0003, 32), which is the narrow late window "
     "the prediction counted against itself"),

    ("H010", "EV025", "confirmed",
     "H010 predicts '++' that urban civilian settlements and elite domestic "
     "contexts dominate and that military camps do not. The corpus shows more "
     "than half of located finds from cities and other settlements, against "
     "just under one-fifth from military camps (PUB-0003, 33). The predicted "
     "pattern is present. THIS IS THE VARIABLE ON WHICH H010 MOST CLEARLY "
     "OUTPERFORMS H009, which predicted the opposite from the same evidence"),
    ("H010", "EV026", "confirmed",
     "H010 predicts '-' that confinement away from the sunniest provinces "
     "counts against a sunshade. The corpus is c 70 per cent Gallic and "
     "Germanic and c 20 per cent British, with none from Italy, Spain, Africa "
     "or the eastern provinces (PUB-0003, 32). That confinement is present. "
     "NOTE the counter-reading recorded in the prediction rationale: the same "
     "distribution would support a RAIN shade, and this project takes no view "
     "on which reading is correct"),
    ("H010", "EV027", "absent",
     "H010 predicts '++' association with a shaft or handle, ribs, canopy "
     "textile or leather, and personal items. No parasol component has been "
     "reported alongside any dodecahedron. The one rod-like association in the "
     "corpus, the bone object beside the Gelduba specimen, is c 15 cm long and "
     "c 3 cm in diameter (PUB-0003, 35-6) - too short for a shaft and far too "
     "thick for a rib"),
    ("H010", "EV031", "weak_confirmed",
     "H010 predicts '--' that a substantial military share counts against it. "
     "Just under one-fifth of located finds come from military camps "
     "(PUB-0003, 33): present, but a minority, hence the half-weight reading"),

    ("H011", "EV025", "absent",
     "H011 predicts '++' that military, frontier and hunting contexts dominate. "
     "The corpus shows more than half of located finds from cities and other "
     "settlements against just under one-fifth from military camps (PUB-0003, "
     "33). The predicted dominance is not present"),
    ("H011", "EV026", "confirmed",
     "H011 predicts '--' that confinement to a few adjacent north-western "
     "provinces would falsify it, since archers served empire-wide and a device "
     "that improved shooting would travel with them. The corpus is c 70 per "
     "cent Gallic and Germanic and c 20 per cent British, with none from Italy, "
     "Spain, Africa or the eastern provinces (PUB-0003, 32). The confinement "
     "the prediction identified as falsifying is present"),
    ("H011", "EV027", "absent",
     "H011 predicts '++' association with arrowheads, bow fittings, quiver "
     "mounts or other military and hunting equipment. The documented "
     "associations are bronze statuettes of deities, a bone object in a grave, "
     "a cache attributed to a temple, rich grave goods and a precision balance "
     "(PUB-0003, 34-6; PUB-0010, paras 42-47). No archery equipment has been "
     "reported alongside any dodecahedron"),
    ("H011", "EV031", "weak_confirmed",
     "H011 predicts '++' direct military association. Just under one-fifth of "
     "located finds come from military camps (PUB-0003, 33): the association is "
     "real but is a minority of the corpus, hence the half-weight reading"),

    ("H012", "EV025", "confirmed",
     "H012 predicts '+' that domestic and settlement contexts dominate. More "
     "than half of located finds come from cities and other settlements "
     "(PUB-0003, 33). The predicted pattern is present"),
    ("H012", "EV026", "confirmed",
     "H012 predicts '+' that a culturally transmitted craft technique may be "
     "confined to the region that practises it. The corpus is confined to the "
     "Gallic, Germanic and British provinces (PUB-0003, 32), which is what a "
     "regionally transmitted craft would look like. NOTE THE WEAKNESS OF THIS "
     "READING: almost any culturally specific explanation predicts the same "
     "thing, so it discriminates poorly and is worth little"),
    ("H014", "EV025", "confirmed",
     "H014 predicts '++' urban, administrative and commercial dominance. More "
     "than half of located finds come from cities and other settlements "
     "(PUB-0003, 33). The predicted pattern is present"),
    ("H014", "EV026", "confirmed",
     "H014 predicts '+' regional confinement, because seal boxes are "
     "themselves concentrated in Britain and the north-western provinces "
     "(PUB-0041). The corpus is c 70 per cent Gallic and Germanic and c 20 per "
     "cent British (PUB-0003, 32). ALONE AMONG THE UTILITARIAN HYPOTHESES, "
     "H014 predicted the restricted distribution rather than being damaged "
     "by it"),
    ("H014", "EV027", "absent",
     "H014 predicts '++' association with seal boxes, styli, writing tablets "
     "or document fittings. No writing or sealing equipment has been reported "
     "with any dodecahedron; the associations are statuettes, grave goods, a "
     "temple cache and a precision balance (PUB-0003, 34-6; PUB-0010, paras "
     "42-47). THIS IS THE HYPOTHESIS'S LARGEST SINGLE LOSS"),
    ("H013", "EV025", "confirmed",
     "H013 predicts '+' that settlement, domestic and workshop contexts "
     "dominate. More than half of located finds come from cities and other "
     "settlements (PUB-0003, 33). The predicted pattern is present"),
    ("H013", "EV026", "confirmed",
     "H013 predicts '+' that a culturally transmitted craft may be confined to "
     "the region that practises it. The corpus is confined to the Gallic, "
     "Germanic and British provinces (PUB-0003, 32). SAME WEAKNESS AS THE H012 "
     "READING: almost any culturally specific explanation predicts this, so it "
     "discriminates poorly"),
    ("H013", "EV027", "absent",
     "H013 predicts '+' association with fibre-processing equipment, spindle "
     "whorls, raw fibre or finished cordage. No such material has been "
     "reported with any dodecahedron; the excavated Norton Disney feature "
     "yielded only bone, ceramic building material and pottery (PUB-0042), and "
     "the wider corpus associations are statuettes, grave goods and a "
     "precision balance (PUB-0003, 34-6; PUB-0010, paras 42-47)"),
    ("H012", "EV027", "absent",
     "H012 predicts '+' association with spindle whorls, loom weights, needles "
     "or other textile equipment. The documented associations are bronze "
     "statuettes of deities, a bone object in a grave, a temple cache, rich "
     "grave goods and a precision balance (PUB-0003, 34-6; PUB-0010, paras "
     "42-47). No textile equipment has been reported alongside any "
     "dodecahedron"),
]


# ---------------------------------------------------------------------------
# Corpus-level observations
#
# One row per evidence variable that has been aggregated across the corpus.
# This table is the ONLY input to HDM scoring: score_hdm.py refuses to score a
# variable that has no row here. It replaces the scoring dictionary that was
# previously hard-coded inside the scoring script with no source references.
#
# `statement` is the sourced fact.
# `direction` is this project's classification of that fact against the HPM
#             prediction, and is therefore a judgement, not an observation.
#             It is recorded separately so that it can be audited and changed
#             without touching the underlying evidence.
#
#   confirmed       the predicted property is present as a corpus-wide rule
#   weak_confirmed  present, but only in a minority of cases (half weight)
#   ambiguous       evidence exists but does not decide (scores 0)
#   weak_absent     predicted property fails as a general rule but holds in
#                   some cases (half weight, negative)
#   absent          the predicted property is not present
#
# `discriminating = 0` marks variables whose HPM predictions are not specific
# enough to be confirmed or refuted by any observation. These score 0 and are
# reported as HPM specification defects. Marking them rather than inventing a
# reading is what keeps the HPM from being tuned to the data after the fact.
#
# Format: (ev_id, statement, direction, confidence, evidence_class,
#          discriminating, source_id, page, figure, extraction_date, notes)
# ---------------------------------------------------------------------------
CORPUS_OBSERVATIONS = [

    # ----- Geometry -----------------------------------------------------
    ("EV001",
     "Diameter from face to opposite face varies from 4 cm to c 10 cm excluding "
     "knobs, and up to c 11 cm including knobs, across the whole corpus",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "31", None, "2026-08-07",
     "HPM predicts a hand-held size range for H001, H004 and H005; a 40-100 mm "
     "range is hand-held. Ultimate reference: Guggenberger 1999, 34"),

    ("EV002",
     "The reference catalogue gives the corpus weight range as 35-580 g, with "
     "one specimen over 1000 g (PUB-0023). Complete specimens in this database "
     "fall within it: 81 g (Jublains), 246 g (Mainz 3), 247 g (Much Hadham), "
     "245 g (Norton Disney), 553 g (Fishguard). Fragment weights of 1.67 g to "
     "82 g are recorded separately and are inadmissible for mass",
     "ambiguous", "B", "Observed", 0,
     "PUB-0023", "header", None, "2026-08-08",
     "HPM DEFECT: H001 and H007 predict '+' for mass on the reasoning that a "
     "load-bearing or military object 'benefits from mass', but no threshold "
     "mass is specified, so no measurement can confirm or refute the "
     "prediction. Scored 0 until the HPM specifies a mass expectation"),

    ("EV003",
     "Wall thickness across the corpus is 0.5-4 mm; the source describes the "
     "objects as 'remarkably thin-walled'",
     "absent", "B", "Observed", 1,
     "PUB-0003", "39", None, "2026-08-07",
     "CORRECTS BATCH 001, which scored this variable 'confirmed' and credited "
     "H001 and H007. The HPM predicts thicker walls for load bearing (H001) and "
     "robustness (H007). A 0.5-4 mm wall on a 40-100 mm object is thin, not "
     "thick, so the prediction is refuted rather than confirmed"),

    ("EV004",
     "Hole diameters vary from 0.6 cm to 4 cm; the largest hole of a specimen "
     "lies between 1.7 and 4 cm and the smallest between 0.6 and 2.8 cm. Every "
     "sufficiently complete specimen shows holes of differing size",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "31", None, "2026-08-07",
     "Corroborates the batch-001 finding from PAS specimens with a corpus-wide "
     "figure. Ultimate references: Guggenberger 2000a; 2013, 56; 1999, 193-207"),

    ("EV005",
     "The difference in diameter within a pair of opposite holes is "
     "statistically between c 0.2 cm and c 0.45 cm; some dodecahedra have pairs "
     "of approximately the same diameter, whereas others have very different "
     "diameters. Measured pairs now in the database bear this out: Avenches "
     "(RD-0034) has no equal pair and two pairs differing by more than 9 mm; "
     "Vienne (RD-0035) has two exactly equal pairs but, in the words of the "
     "author who devised the comparative recording method, no evident "
     "regularity otherwise; Jublains (RD-0020) has four near-equal pairs and "
     "two differing by 4 and 6.5 mm; Carnuntum (RD-0036) differs by 0.2-2.5 mm "
     "and Tongres (RD-0006) by 0.2-4 mm",
     "weak_absent", "B", "Observed", 1,
     "PUB-0003", "31", None, "2026-08-07",
     "SCORED IN BATCH 002, EVIDENCE BASE WIDENED IN BATCH 003 from one "
     "corpus-level statement to five specimens with measured opposite pairs "
     "(PUB-0017, 200; PUB-0019 tabs I, III, IV and Appendix B). The HPM "
     "predicts systematic correspondence between opposite holes for H001, "
     "because a connector needs matching holes on an axis. Correspondence is "
     "not the rule - it holds for two pairs on one specimen and for none on "
     "another - but neither is it absent, hence weak_absent rather than absent. "
     "Ultimate reference for the corpus statistic: Guggenberger 1999, cited at "
     "PUB-0003 n 1"),

    ("EV006",
     "The most common type (Greiner/Guggenberger 1a) has ten perfectly round "
     "holes; the remaining opposite pair is less perfectly round and often larger",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "32", None, "2026-08-07",
     "Ten of twelve holes round and consistent in profile"),

    ("EV008",
     "Knobs are all of the same size within a given object, with a broad range "
     "of diameters from object to object",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "39-40", None, "2026-08-07",
     "Ultimate reference: Guggenberger 1999, 38"),

    ("EV009",
     "Almost all specimens carry twenty knobs, one at each vertex; knobs within "
     "an object are all of the same size; one specimen (Guggenberger no 66) has "
     "three knobs at each vertex; knobs are never pointed or intentionally "
     "faceted; there is no specimen without knobs",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "39-40", None, "2026-08-07",
     "FIRST SCORING OF THIS VARIABLE. Ultimate reference: Guggenberger 1999, "
     "37-8 fig 17"),

    ("EV047",
     "No dodecahedron in this database has been authenticated by metallurgical "
     "or technical analysis against forgery, and none of the sources read "
     "raises the question. Provenance security nevertheless varies enormously. "
     "ONE specimen has a sealed, dated, stratified context (RD-0020 Jublains). "
     "Two of the three specimens that carry usable aperture data are private "
     "collection pieces without archaeological context: RD-0035 Vienne, "
     "described by its publisher, who owned it, as a 'piece de collection sans "
     "contexte archeologique connu'; and RD-0022 Mainz 3, which has NO findspot "
     "at all, is known only from a named private collection, and was previously "
     "unpublished until 2025. SEPARATELY, ancient imitation is proposed in the "
     "literature: PUB-0003, 32 n 10, citing Greiner 1996, 13, records that many "
     "British specimens have special features and that 'some of which do not "
     "appear to be so skilfully designed. They may point out to local "
     "imitations of classic dodecahedra'",
     "ambiguous", "B", "Observed", 0,
     "PUB-0003", "32", None, "2026-08-08",
     "ADDED AFTER THE QUESTION WAS ASKED WHETHER PART OF THE CORPUS MIGHT BE "
     "IMITATION OR FORGERY. Scored 0: no hypothesis predicts anything about "
     "authenticity, so the variable cannot discriminate between them. It is "
     "recorded because it bears on the RELIABILITY OF OTHER VARIABLES rather "
     "than on any hypothesis. "
     "THE SERIOUS CONSEQUENCE IS FOR EV039. The absence of standardisation is "
     "among the most load-bearing findings in this project - it is the main "
     "reason every gauging and measuring hypothesis fails - and it is measured "
     "by POOLING the whole corpus. If part of that corpus consists of local "
     "imitations of a classic type, as PUB-0003 reports Greiner proposing, then "
     "some of the observed variability is variability BETWEEN a type and its "
     "copies rather than within a class of originals. Standardisation has never "
     "been tested WITHIN a Greiner/Guggenberger type. Until it has, EV039's "
     "direction carries an unquantified confound. See prediction P-0011"),

    ("EV048",
     "Type attributions are now known for the whole reference corpus: of 129 "
     "catalogued specimens, 82 are type 1a, 17 are untyped, 6 are 2a, 4 each "
     "are 3a and 1b, and the remainder are single or double instances of "
     "types 2b, 3b, 4, 5a, 5b and 6 (PUB-0023). Twenty specimens in this "
     "database now carry a type, twelve of them 1a. MEASUREMENTS PER TYPE ARE "
     "NOT AVAILABLE: only two type-1a specimens in this database have an "
     "admissible overall diameter, which is far too few to compare "
     "within-type variability against the pooled figure",
     "ambiguous", "B", "Observed", 0,
     "PUB-0023", "complete list of finds", None, "2026-08-08",
     "PREDICTION P-0011 CANNOT YET BE RESOLVED, and this observation records "
     "exactly why. The reference catalogue supplies the TYPE of every known "
     "specimen but not its MEASUREMENTS; those are in Guggenberger 1999 "
     "(PUB-0022), which remains unread. With n = 2 for type 1a against n = 8 "
     "pooled, the coefficients of variation computed here (20.8 per cent "
     "against 23.4 per cent) are not meaningful and are recorded only to show "
     "the test was attempted. The confound on EV039 identified at RDORP-012 "
     "section 2.6 therefore remains unquantified, and acquiring PUB-0022 is "
     "now the single action that would resolve it"),

    ("EV046",
     "A single axis is marked out on the great majority of specimens, by the "
     "ABSENCE of decoration rather than its presence. The commonest type "
     "engraves circles around ten apertures and leaves two bare, and those two "
     "are OPPOSITE one another, so the pair defines a unique axis through the "
     "solid. On the only stratified specimen the same two faces also differ in "
     "form - their openings are oval, 21x26 mm, where the other ten are "
     "circular - and the excavators record that they are 'placed in opposition "
     "on the object, possibly materialising a top and a bottom'. The same "
     "10-of-12 pattern is recorded on Guggenberger no 11 and on Vienne, where "
     "the two largest opposed openings carry no fillets",
     "confirmed", "A", "Observed", 0,
     "PUB-0010", "para 48", "fig 11", "2026-08-08",
     "MARKED NON-DISCRIMINATING, AND THE REASON IS A DEFECT CAUGHT IN THIS "
     "FRAMEWORK RATHER THAN A GAP IN THE EVIDENCE. EV046 and EV013 describe "
     "THE SAME PHYSICAL FEATURE from opposite sides. EV013 records the "
     "opposed pair without engraved circles, not perfectly round and often "
     "larger, as production holes arising from casting, and penalises H001, "
     "H002, H006, H007, H009, H010 and H011 for it. EV046 records the same "
     "pair as a marked axis and would reward any hypothesis that wants an "
     "orientation. Scoring both double-counts one fact with opposite signs. "
     "Until an independent line of evidence for a marked axis exists - one "
     "that does not reduce to the production-hole pair - EV046 scores zero for "
     "everyone, including the candidate that proposed it. "
     "ORIGINAL NOTE FOLLOWS. Added after the decoration evidence was extracted. No existing variable "
     "captured this: EV014 records that decoration is present, EV038 asks "
     "whether the FUNCTION needs a fixed orientation, EV010 records symmetry. "
     "None asks whether an axis is MARKED. It is, and consistently. "
     "IMPORTANT TENSION WITH EV038, which is scored weak_absent because no "
     "specimen has a base, a suspension loop or any structural means of being "
     "held in a set position, and the knobs let it rest on any face. Both are "
     "true: the object carries a marked axis and no way of fixing it. "
     "EV038 IS DELIBERATELY NOT RE-SCORED HERE. Changing a direction because a "
     "newly proposed reading would benefit is exactly the tuning this "
     "framework guards against. If the paired data from P-0009 confirms that "
     "the marking indexes an axis, EV038 must be respecified - and the "
     "respecification written BEFORE it is seen which hypotheses gain. "
     "All existing hypotheses are silent on EV046, having been specified "
     "before it existed, so it scores zero for everyone and changes no "
     "ranking"),

    ("EV010",
     "The objects depart measurably from regular geometry. On the only "
     "stratified specimen the face-to-opposite-face distance itself varies from "
     "48 to 52 mm depending on which axis is measured, and two of its twelve "
     "openings are oval (21x26 mm) rather than circular. On the most precisely "
     "measured specimen, five of twelve holes are recorded with two differing "
     "diameters and a sixth is described as probably elliptic",
     "absent", "B", "Observed", 1,
     "PUB-0010", "para 48", "fig 11", "2026-08-07",
     "FIRST SCORING OF THIS VARIABLE, from batch 003. The HPM predicts accurate "
     "regular geometry for H002 and H006 ('++', a precision instrument requires "
     "it) and for H001 ('+', regular faces distribute load evenly). Regular "
     "geometry is not what the measurements show. Second source: PUB-0019 "
     "Appendix B tab B1 for the Avenches hole ellipticities"),

    # ----- Manufacturing -------------------------------------------------
    ("EV044",
     "Interiors are consistently described as roughly or crudely cast and "
     "unfinished: 'interior surfaces more roughly cast' (RD-0001), 'interior "
     "described as crudely cast' (RD-0002), 'interior left roughcast' "
     "(RD-0003), 'interior concave and crudely cast' (RD-0008), 'reverse "
     "concave with rough and unfinished surface' (RD-0011), 'interior concave, "
     "crudely finished' (RD-0012). No specimen in the database is recorded "
     "with interior engraving, scale, marking or a smoothed working surface",
     "absent", "B", "Observed", 1,
     "PUB-0006", "PAS records", None, "2026-08-08",
     "ADDED WITH C-14. EV012 records casting quality overall and EV014 records "
     "decoration of the exterior; neither could distinguish inside from "
     "outside, so the screen credited a projection hypothesis on variables "
     "that were actually evidence against it. The contrast is the point: these "
     "objects are finished and engraved on the OUTSIDE and left rough on the "
     "INSIDE, which is the opposite of what any hypothesis requiring an "
     "internal working or projection surface needs. Ten of twelve exteriors "
     "carry engraved concentric rings; no interior carries anything"),

    ("EV011",
     "The objects are made of copper alloy (eg bronze). XRF on Norton Disney "
     "gives Cu 75 percent, Sn 7 percent, Pb 18 percent; the Musee Curtius "
     "specimen is recorded as bronze and lead",
     "confirmed", "C", "Observed", 1,
     "PUB-0003", "31", None, "2026-08-07",
     "Corpus-level material statement from PUB-0003; quantitative analyses come "
     "from PUB-0008 and PUB-0011 and are held per specimen under EV011. Note "
     "that 18 percent lead is a casting alloy, not a high-tin structural bronze"),

    ("EV012",
     "Some specimens were difficult to cast; many dodecahedra from Roman "
     "Britain 'do not appear to be so skilfully designed' and may be local "
     "imitations. British PAS specimens consistently show a roughly cast, "
     "unfinished interior with a smoother exterior",
     "weak_confirmed", "B", "Observed", 1,
     "PUB-0003", "32", None, "2026-08-07",
     "DOWNGRADED FROM BATCH 001, which scored confirmed and credited H002 and "
     "H006 with full marks for precision casting. Casting quality is high in "
     "part of the corpus and explicitly poor in another part, so only partial "
     "confirmation is warranted. Batch 003 evidence pulls both ways and leaves "
     "the partial reading in place: the Avenches specimen holds a tolerance "
     "below 0.2 mm (PUB-0019 Appendix B) and the Jublains specimen was cast by "
     "lost wax and then carefully trued up (PUB-0010, para 48), while about "
     "70 per cent of the corpus carries production holes and the interiors of "
     "the British specimens in this database are consistently described as "
     "crudely cast. Ultimate reference: Greiner 1996, 13"),

    ("EV013",
     "About 70 per cent of specimens carry production holes "
     "(Produktionsloecher); the opposite pair of holes without engraved circles "
     "is not perfectly round and is often larger than the rest, which is in "
     "most cases explained by the production process",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "32", None, "2026-08-07",
     "FIRST SCORING OF THIS VARIABLE. Production holes are casting artefacts, "
     "ie defects in the sense of EV013. The HPM predicts '--' for H002 and H006 "
     "and '-' for H001 and H007, because a precision instrument should not carry "
     "casting artefacts on its working surfaces. Ultimate references: "
     "Guggenberger 1999, 28, 34, 50; Greiner 1996, 20"),

    ("EV014",
     "COVERAGE: the commonest type (Greiner/Guggenberger 1a) carries engraved "
     "circles around TEN of its twelve faces; the remaining two, an opposed "
     "pair, carry none and are the production holes. Confirmed directly on the "
     "stratified specimen: 'ten of the twelve faces have their opening "
     "underlined by concentric circles; the other two faces have none' "
     "(RD-0020). The same 10-of-12 pattern holds on Guggenberger no 11 (two to "
     "five circles around ten of twelve) and on Vienne (RD-0035), where the two "
     "largest opposed openings carry no fillets. The exception is type 2a: "
     "Mainz 3 (RD-0022) carries five ring-and-dot motifs on ALL twelve faces. "
     "COUNT: two, three, four, five or six rings are all recorded; three is "
     "typical. BETWEEN SPECIMENS there is no consistency in the pattern at all",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "32, 36", "fig 4", "2026-08-07",
     "Decoration is present and deliberate throughout the corpus, and its "
     "COVERAGE is highly regular even though its PATTERN is not: the "
     "undecorated faces are the production-hole pair, so the decoration marks "
     "the ten deliberately made apertures and skips the two casting artefacts. "
     "TWO WITHIN-SPECIMEN REGULARITIES ARE ALSO RECORDED, and both bear on "
     "EV043: (a) on RD-0035 ring count rises as hole diameter falls - 4 and 6 "
     "fillets for the 14 mm holes, 3 for the 22 mm, none for the 23 and 24 mm "
     "- which Duval judges probably empirical, the smaller hole simply leaving "
     "more room; (b) on RD-0020 each pair of OPPOSITE holes is reported to "
     "carry the same decoration (PUB-0019, 9, read off a figure, confidence D). BUT THE FIRST REGULARITY IS NOT UNIVERSAL: RD-0020 carries three rings on all ten decorated faces irrespective of aperture size. EXP-0005 shows these are two different workshop rules - constant pitch with variable count, against constant count with variable pitch - and that under EITHER rule the rings carry no labelling information independent of aperture diameter."),

    ("EV016",
     "Concentric circles are engraved into the metal after casting",
     "confirmed", "B", "Observed", 1,
     "PUB-0003", "32", None, "2026-08-07",
     "FIRST SCORING OF THIS VARIABLE. Engraving is secondary machining, which "
     "is what EV016 records. Ultimate reference: Guggenberger 1999, 29, 36-7, "
     "50-1"),

    # ----- Wear ----------------------------------------------------------
    ("EV017",
     "The outer and inner surfaces of the Gallo-Roman dodecahedra, aside from a "
     "few exceptions and later destruction and corrosion, generally do not look "
     "worn",
     "absent", "C", "Observed", 1,
     "PUB-0003", "45", None, "2026-08-07",
     "THE SINGLE MOST DISCRIMINATING RESULT IN THE DATABASE. The HPM predicts "
     "'++' internal hole wear for H001 and H005, both of which require repeated "
     "mechanical contact through the holes. Its corpus-wide absence refutes "
     "that prediction. Ultimate reference: Guggenberger 1999, 33-4, 61-2. "
     "CONFIDENCE DOWNGRADED FROM B TO C IN BATCH 003 because of a direct "
     "conflict: PUB-0017, 200 reports that on the Vienne specimen (RD-0035) the "
     "two largest opposed openings have a periphery less regularly cut than the "
     "others, as if worn by some friction, due for example to a stick that "
     "passed through both simultaneously. PUB-0003, 32 accounts for the same "
     "feature across the corpus as production holes arising from casting, "
     "present in about 70 per cent of specimens. Duval's wording is hedged, it "
     "concerns one specimen, and he states that no conclusion can be drawn from "
     "it; the corpus-level direction therefore stays absent, but not at full "
     "confidence. FURTHER LIMITATION: all of this is macroscopic. PUB-0003, 52 "
     "states that microscopic wear analysis has not been carried out and lists "
     "it as an open question"),

    ("EV018",
     "The outer surfaces generally do not look worn, aside from a few "
     "exceptions and later destruction and corrosion",
     "absent", "B", "Observed", 1,
     "PUB-0003", "45", None, "2026-08-07",
     "CONFLICT PRESERVED: four PAS records in this database (RD-0001, RD-0004, "
     "RD-0009 pitted or worn; RD-0005 undamaged) describe surface condition per "
     "specimen. PUB-0003 attributes such surface damage to post-depositional "
     "corrosion and destruction rather than use wear. Both readings are "
     "retained; the corpus-level direction follows the cataloguer"),

    ("EV019",
     "No rope wear, grooves or polish from rope is reported anywhere in the "
     "corpus; the general statement that the surfaces do not look worn covers "
     "the holes and knobs",
     "absent", "C", "Observed", 1,
     "PUB-0003", "45, 52", None, "2026-08-07",
     "Confidence C rather than B because this is partly an argument from "
     "silence: PUB-0003, 52 explicitly asks whether there are any microscopic "
     "signs of wear, which shows the question has not been settled by "
     "systematic study"),

    ("EV020",
     "No evidence of repeated rotation is reported anywhere in the corpus",
     "absent", "C", "Observed", 1,
     "PUB-0003", "45, 52", None, "2026-08-07",
     "Same limitation as EV019: absence of a report, supported by the general "
     "no-wear statement, is weaker than a systematic negative result"),

    # EV023 and EV024 are deliberately NOT scored. See INTERPRETATIONS and the
    # evidence-gap section of the analytical report: the only residue record in
    # the corpus (Feldberg, RD-0031) is described by the source itself as
    # possibly unreliable, and PUB-0003, 52 lists residue analysis as an open
    # question. Scoring 'absent' here would penalise H004 and H003 on the basis
    # of work that has never been done.

    # ----- Archaeological context ----------------------------------------
    ("EV025",
     "Of the dodecahedra with a recorded find location: more than half come "
     "from cities or other settlements; just under one-fifth from military "
     "camps; c 8.5 per cent from find contexts with plausible sacred "
     "connections; c 7 per cent from graves or necropolis areas; c 5.5 per cent "
     "from well backfills or refuse pits; c 4 per cent from coin or bronze "
     "hoards; and c 4 per cent from rivers",
     "ambiguous", "B", "Observed", 0,
     "PUB-0003", "33", None, "2026-08-07",
     "HPM DEFECT, NOT AN EVIDENCE GAP. This is now the best-quantified variable "
     "in the corpus, but seven of the eight hypotheses predict a bare '+' for "
     "'site type' without naming which site type they expect, so the "
     "distribution cannot confirm or refute them. Its discriminating content is "
     "routed instead through EV031 and EV032, whose predictions are specific. "
     "The HPM must be respecified for EV025 BEFORE the next scoring round, and "
     "that respecification must be written without reference to this "
     "distribution. Ultimate reference: Guggenberger 2024, I-X"),

    ("EV026",
     "c 70 per cent of finds come from the Gallic and Germanic provinces, "
     "especially the territory of the former Gallia Comata, and c 20 per cent "
     "from Britannia; around 90 per cent come from areas that briefly belonged "
     "to the Gallic Empire (AD 260-74). The easternmost find is Brigetio in "
     "Pannonia and one comes from Deonica in Moesia superior; none are known "
     "from Italy, Spain, Africa or the eastern provinces",
     "ambiguous", "B", "Observed", 0,
     "PUB-0003", "32", None, "2026-08-07",
     "HPM DEFECT: only H005 and H007 predict anything for province, and neither "
     "names an expected region, so the distribution cannot test them. Recorded "
     "because it is the strongest constraint in the corpus on any hypothesis "
     "that implies an empire-wide function"),

    ("EV027",
     "Documented associations include a bronze statuette of a goddess one metre "
     "away (Guggenberger no 110), a bronze statuette of Mercury as "
     "Hermes-Thoth in the same area (no 20), a bone object c 15 cm long "
     "immediately adjacent in a grave (no 11), a cache attributed to a temple "
     "(no 122), and three richly furnished graves",
     "ambiguous", "C", "Observed", 0,
     "PUB-0003", "34-6", None, "2026-08-07",
     "HPM DEFECT: every hypothesis predicts '+' or '++' for associated finds "
     "and none names the finds it expects, so any association confirms all of "
     "them equally. The individual associations are recorded per specimen and "
     "are strong evidence; they cannot be scored until the HPM says what each "
     "hypothesis expects to find alongside a dodecahedron"),

    ("EV029",
     "Dodecahedra were used from around AD 200 to the late fourth century AD; "
     "the stratified Jublains specimen was deposited in the first half of the "
     "3rd century; the dating of Bachem, Feldberg, Zugmantel and Bad Cannstatt "
     "remains uncertain and may be 2nd century",
     "ambiguous", "B", "Observed", 0,
     "PUB-0003", "32", None, "2026-08-07",
     "HPM DEFECT: only H007 predicts anything for dating and it names no "
     "period. Recorded as a firm chronological constraint for future use"),

    ("EV028",
     "Only one dodecahedron has ever been recovered from a sealed, dated, "
     "stratified deposit: RD-0020, from destruction layer F1058 of a small "
     "drystone building over a cellar at Jublains, burnt at the turn of the 2nd "
     "and 3rd centuries and in use during the first half of the 3rd. Very few "
     "specimens have been recovered from archaeological excavations in "
     "stratified contexts at all",
     "ambiguous", "A", "Observed", 0,
     "PUB-0010", "paras 41, 54, 60-61", None, "2026-08-07",
     "NOT SCORED, FOR TWO REASONS, DESPITE BEING THE HIGHEST-GRADE EVIDENCE IN "
     "THE DATABASE. First, n = 1: one stratigraphic sequence cannot establish a "
     "corpus-level pattern, and the corpus statement that stratified finds are "
     "very rare (PUB-0003, 32) is precisely what makes it unrepresentative. "
     "Second, the HPM prediction is loose: H003 predicts '+' for 'votive "
     "deposit or destruction layer' stratigraphy, which an accidental house "
     "fire satisfies without telling us anything about ritual use. Recorded so "
     "that the evidence is visible and so that the HPM defect is on the record"),

    ("EV031",
     "Just under one-fifth of dodecahedra with a recorded find location come "
     "from military camps; the overwhelming majority derive from civilian "
     "contexts, although there is some concentration around the frontiers",
     "weak_confirmed", "B", "Observed", 1,
     "PUB-0003", "33", None, "2026-08-07",
     "Military association is real but is a minority of the corpus, so it "
     "counts at half weight. PUB-0003 draws the further conclusion that a "
     "primary military purpose can be ruled out; that conclusion is the "
     "authors' INTERPRETATION and is recorded as such, not scored here"),

    ("EV032",
     "c 8.5 per cent of located finds come from contexts with plausible sacred "
     "connections, a further c 7 per cent from graves or necropolis areas and "
     "c 4 per cent from rivers. Specific cases include a cult precinct "
     "(no 21), the temple of Nodens at Lydney (no 68), a cache attributed to a "
     "temple (no 122) and three richly furnished graves",
     "weak_confirmed", "C", "Observed", 1,
     "PUB-0003", "33-5", None, "2026-08-07",
     "Half weight for two reasons: sacred contexts are a minority of the "
     "corpus, and only the 8.5 per cent category is described by the source as "
     "sacred - reading graves and river finds as ritual deposition is a "
     "conventional but contestable interpretation"),

    # ----- Engineering (this project's own derived assessments) ------------
    # These four variables are NOT archaeological observations. They are
    # assessments produced by this project from published measurements, and
    # they are the variables that carried H001 in batch 001. They are kept,
    # but they are classed Derived, discounted, and excluded entirely from the
    # observed-only scenario in the sensitivity analysis.
    ("EV033",
     "ASSESSMENT: measured hole diameters (9.4-40.6 mm across specimens) admit "
     "cylindrical rods. ARCHAEOLOGICAL CORROBORATION: a bone object c 15 cm "
     "long and c 3 cm in diameter lay immediately adjacent to the Gelduba "
     "specimen, whose production holes measure 24 and 23 mm",
     "confirmed", "C", "Derived", 1,
     "PUB-0003", "35-6", None, "2026-08-07",
     "The geometric assessment is this project's own. The Gelduba association "
     "is a published observation, and PUB-0003 infers from it a possible "
     "temporary mounting on a handle - that inference is the authors' and is "
     "recorded in evidence_register. NOTE the counter-case in this database: "
     "on RD-0011 the opposing holes measure 9.4 and c 22.6 mm, so a single rod "
     "cannot pass through both"),

    ("EV034",
     "ASSESSMENT: hole diameters and knob dimensions permit rope or cord to be "
     "routed through the holes and anchored over the knobs",
     "confirmed", "C", "Derived", 1,
     None, None, None, "2026-08-07",
     "NO SOURCE: this is a geometric assessment made by this project, not a "
     "published observation, and no archaeological evidence of rope use exists. "
     "It is contradicted by EV019, which finds no rope wear anywhere in the "
     "corpus. Excluded from the observed-only scenario"),

    ("EV035",
     "ASSESSMENT: the dodecahedral form with twenty vertex knobs rests stably "
     "on any face, and a 3 mm bronze wall resists modest compressive load",
     "weak_confirmed", "C", "Derived", 1,
     None, None, None, "2026-08-07",
     "NO SOURCE, and downgraded from batch 001: the corpus wall thickness is "
     "0.5-4 mm (EV003), not the 3 mm of the single specimen this assessment was "
     "based on, so load-bearing capacity across the corpus is lower than the "
     "batch-001 assessment assumed"),

    ("EV036",
     "ASSESSMENT: six pairs of opposing faces provide six potential through-rod "
     "axes along which axial load could be transferred",
     "weak_confirmed", "C", "Derived", 1,
     None, None, None, "2026-08-07",
     "NO SOURCE, and downgraded from batch 001 because EV005 now shows that "
     "opposite holes usually differ in diameter by 2-4.5 mm, so most of the six "
     "notional axes cannot in fact carry a single straight rod"),

    ("EV037",
     "Overall diameter across the corpus spans 4-10 cm, a ratio of 2.5:1. A "
     "modular structural system requires interchangeable components of "
     "consistent dimension",
     "absent", "B", "Observed", 1,
     "PUB-0003", "31", None, "2026-08-07",
     "Confidence upgraded from batch 001 (C to B): the size range is now a "
     "published corpus statistic rather than this project's own measurement of "
     "five specimens. Directly refutes the core H001 prediction"),

    ("EV038",
     "Every specimen carries knobs at all twenty vertices and rests equally on "
     "any face; no specimen has a distinguished base or axis. The single "
     "related Gallo-Roman icosahedron, from Arloff, does have such an axis: "
     "three of its knobs are larger and are arranged around the smaller of its "
     "only pair of holes",
     "weak_absent", "C", "Observed", 1,
     "PUB-0003", "37-8, 40", None, "2026-08-07",
     "WELL CONTROLLED: the Arloff icosahedron shows what a Gallo-Roman "
     "polyhedron built for a fixed orientation actually looks like - three "
     "enlarged knobs forming feet around the smaller of its only pair of holes "
     "- and the dodecahedra do not look like that. The HPM predicts '++' "
     "orientation dependence for H002, H004 and H006. DOWNGRADED FROM absent TO "
     "weak_absent IN BATCH 003: the excavators of the only stratified specimen "
     "note that its two opposed circle-less oval openings are placed in "
     "opposition and may possibly materialise a top and a bottom (PUB-0010, "
     "para 48). Their wording is hedged and it is a single specimen, but it is "
     "a first-hand observation and it points the other way. Ultimate "
     "references: Nouwen 1993, 58-9; Guggenberger 1999, 37-8"),

    # ----- Comparative ----------------------------------------------------
    ("EV039",
     "Hole diameters span 0.6-4 cm and overall diameters 4-10 cm across the "
     "corpus; knob diameters cover a broad range from object to object; there "
     "is no consistency in the pattern of circles on the faces. Within single "
     "specimens the coefficient of variation of hole diameter reaches 40 per "
     "cent and no arithmetic progression is present",
     "absent", "B", "Observed", 1,
     "PUB-0003", "31, 32, 39-40", None, "2026-08-07",
     "Confidence upgraded from batch 001 (C to B). The published corpus ranges "
     "corroborate the statistical result computed by this project from measured "
     "specimens. Batch 003 added two independent corroborations, both from "
     "authors who were actively looking for a standard and did not find one. "
     "PUB-0017, 200: Duval devised his comparative recording method precisely "
     "to detect regularity and concludes there is no evident regularity in the "
     "general distribution of the openings, either in their juxtaposition or in "
     "their opposition. PUB-0019, section 5: Sparavigna, arguing FOR the "
     "measuring-instrument interpretation, concludes that it does not seem that "
     "a standard or rule for these instruments existed. No metrological "
     "standard is detectable at any level"),

    ("EV040",
     "Many dodecahedra with special features come from Roman Britain, some of "
     "which do not appear to be so skilfully designed and may be local "
     "imitations of classic dodecahedra; several typological groups are "
     "distinguished and the pattern of face decoration is inconsistent",
     "confirmed", "C", "Observed", 1,
     "PUB-0003", "32", None, "2026-08-07",
     "FIRST SCORING OF THIS VARIABLE. Regional variation is present. Ultimate "
     "reference: Greiner 1996, 10-13"),
]


# ---------------------------------------------------------------------------
# Pre-registered predictions
#
# Registered 2026-08-08, before any of the measurements below had been made.
# These are this project's own guesses. They are not evidence, they are never
# scored, and several of them predict AGAINST the hypothesis currently leading
# the table. That is the point: a prediction that only ever supports the
# favourite is not a test.
#
# Format: (prediction_id, ev_id, hypothesis_ids, registered_on, predicted,
#          falsified_if, method, basis, confidence, status, outcome, resolved_on)
# ---------------------------------------------------------------------------
PREDICTIONS = [
    ("P-0001", "EV041", "H012; H005", "2026-08-08",
     "NEGATIVE. Examination of the knobs and knob necks of well-preserved "
     "specimens will NOT show directional use-polish or grooving. Any abrasion "
     "found will be non-directional and will correlate with damage elsewhere "
     "on the same object.",
     "Refuted if directional polish or grooving is found running over the knob "
     "and down the neck, in the same orientation on the five knobs around one "
     "or more faces, on an object otherwise well preserved.",
     "Low-magnification then SEM examination of knob necks on a complete "
     "specimen with intact patina; compare against faces and interior.",
     "The single positive record in the corpus (RD-0001, abrasion at the base "
     "of most knobs) comes from a PAS description that also reports several "
     "faces pitted or gouged and a patchy patina, which points to ploughing "
     "and corrosion rather than use. The corpus-wide statement is that the "
     "surfaces do not look worn (PUB-0003, 45).",
     "medium", "open", None, None),

    ("P-0011", "EV048", "H002; H006; H011; C-01; C-03; C-05; C-13", "2026-08-08",
     "NO BETTER WITHIN TYPE. Standardisation measured within a single "
     "Greiner/Guggenberger type will prove no better than standardisation "
     "measured across the pooled corpus. The absence of a metrological "
     "standard is a property of the objects, not an artefact of mixing "
     "originals with local imitations.",
     "Refuted if specimens of one type prove substantially more uniform in "
     "overall diameter, aperture set or wall thickness than the corpus as a "
     "whole. That would mean the pooled variability partly reflects "
     "type-mixing, would weaken EV039's direction, and would to that extent "
     "rehabilitate every gauging and measuring hypothesis that EV039 currently "
     "defeats.",
     "Group the measured specimens by Greiner/Guggenberger type and compute the "
     "coefficient of variation of overall diameter and of aperture diameters "
     "within each type, against the pooled figures. Requires type "
     "attributions, which are in PUB-0022 and PUB-0023, neither directly "
     "consulted.",
     "PUB-0003, 32 n 10 records Greiner's suggestion that some British "
     "specimens with special features 'may point out to local imitations of "
     "classic dodecahedra'. If so, the corpus is not one population. EV039 has "
     "only ever been measured on the pooled corpus, and it is among the most "
     "load-bearing findings in this project.",
     "medium", "open", None, None),

    ("P-0010", "EV045", "H003; H008; C-16", "2026-08-08",
     "DIFFICULT. Attempts to reproduce a dodecahedron by lost-wax casting to "
     "the standard of the better specimens will prove demanding, with a "
     "substantial failure rate, and will require skill beyond routine bronze "
     "founding.",
     "Refuted if experimental casting shows the form to be routine for a "
     "competent Roman founder. That would remove the foundation of the "
     "craft-value reading (C-16) and of the claim that the objects were "
     "inherently valuable, and would return the field to the utilitarian "
     "hypotheses despite their evidential problems.",
     "Experimental lost-wax casting in a copper alloy of the recorded "
     "composition (75 Cu, 7 Sn, 18 Pb), attempting the hollow form with "
     "integral or soldered knobs; record failure rate and required "
     "interventions. Separately, search museum and excavation records for any "
     "mould, casting waste, sprue, reject or workshop debris associated with "
     "dodecahedra.",
     "PUB-0003, 32 states that some of these were difficult to cast and that "
     "this alone made them inherently valuable objects passed from one "
     "generation to the next. That is an assertion, not a measurement, and the "
     "whole craft-value reading rests on it. NOTE ALSO that no mould, casting "
     "waste or reject is recorded anywhere in this database - we do not know "
     "where a single dodecahedron was made. The one experimental study in the "
     "project (EXP-0001) used 3D-printed replicas and so sidesteps the casting "
     "question entirely.",
     "medium", "open", None, None),

    ("P-0009", "EV043", "H003; H008", "2026-08-08",
     "DISTINGUISHABLE. On complete, well-preserved specimens, every aperture "
     "will prove distinguishable from every other on the same object, by "
     "diameter or by the number of engraved rings, with the separation "
     "exceeding the workshop tolerance.",
     "Refuted if complete specimens are found on which two or more apertures "
     "are indistinguishable by both diameter and ring count. Already partly "
     "refuted by RD-0035, where three apertures share a diameter and a ring "
     "count; confirmed by RD-0034, where all twelve differ.",
     "Measure all twelve apertures AND count the rings on each SEPARATELY, on "
     "every complete specimen accessible, recording which apertures are "
     "opposite which. Recording them separately is essential: ring count "
     "appears to track diameter, so the two must be disentangled before "
     "either can be said to label anything, and the opposed-pair question "
     "(D3a) can only be settled from paired data. Desk and museum work, no "
     "destructive analysis, the cheapest test in the project.",
     "Deduced, not observed. If the topology is fixed while every dimension "
     "varies, the function cannot have depended on measurement; and if the "
     "engraved decoration is concentrated around the apertures and varies in "
     "count, the apertures were meant to be told apart by eye. Together these "
     "imply the apertures functioned as twelve distinguishable categories "
     "rather than twelve sizes. Distinguishability is the observable "
     "consequence.",
     "medium", "open", None, None),

    ("P-0002", "EV024", "H003; H004; H008; H012", "2026-08-08",
     "POSITIVE IN A MINORITY. Organic residues will be recoverable from the "
     "interior and from the aperture rims of a minority of well-preserved, "
     "unconserved specimens.",
     "Refuted if a systematic study of several well-preserved specimens "
     "recovers no organic residue at all.",
     "GC-MS or FTIR on interior scrapings and aperture rims of specimens that "
     "have not been cleaned or consolidated.",
     "The requirement profile describes an object mechanically capable but "
     "never mechanically used, which is what a container of perishable "
     "contents looks like. PUB-0003, 40 n 67 raises exactly this: 'if the "
     "openings would have been filled with a mechanically sensitive substance "
     "that has not yet been detected'. The Feldberg wax record (RD-0031) is "
     "contested but not disproved.",
     "low", "open", None, None),

    ("P-0003", "EV023", "H004; H003", "2026-08-08",
     "NEGATIVE. No soot, scorching or heat alteration will be found on the "
     "interior of specimens.",
     "Refuted if soot or thermal alteration is found on the interior of any "
     "well-preserved specimen.",
     "Visual and microscopic examination of interior surfaces; residue "
     "analysis for combustion products.",
     "No source in the database reports thermal alteration on any specimen, "
     "and the thin walls and open form make an object a poor lamp. A positive "
     "result would revive H004 almost single-handedly.",
     "medium", "open", None, None),

    ("P-0004", "EV042", "H001; H005; H011; H012", "2026-08-08",
     "RIM, NOT BORE. Microwear analysis will find, at most, light contact wear "
     "on the outer lip of the apertures, and will NOT find wear inside the "
     "bores.",
     "Refuted if bore wear is found. Bore wear would revive H001 and H005 "
     "directly and would falsify the reading of the object as something that "
     "held contents rather than passed things through.",
     "SEM microwear on aperture bores and lips of a complete specimen.",
     "Duval (PUB-0017, 200) reports an appearance of friction wear on the two "
     "largest opposed openings of the Vienne specimen; PUB-0003, 32 accounts "
     "for the same feature as casting production holes. Microwear "
     "distinguishes the two.",
     "medium", "open", None, None),

    ("P-0005", "EV007", "H005; H012; H011", "2026-08-08",
     "BEVELLED. Aperture lips will prove to be bevelled or rounded rather than "
     "square-cut, across most of the corpus.",
     "Refuted if lips are predominantly square-cut and sharp, which would "
     "favour the optical reading (H011) over the cord-work reading (H012).",
     "Profile measurement of aperture edges; already recorded for RD-0001 "
     "('all holes bevelled') and needs extending across the corpus.",
     "One recorded observation, on RD-0001, and the general impression of "
     "carefully finished apertures. Weak basis.",
     "low", "open", None, None),

    ("P-0006", "EV015", "All", "2026-08-08",
     "RARE. Ancient repairs will prove rare across the corpus.",
     "Refuted if a systematic survey finds ancient repairs on a substantial "
     "share of specimens, which would imply real working use and would revive "
     "the tool hypotheses generally.",
     "Survey of published catalogues and museum records for solder, patching, "
     "replaced knobs and re-cast elements.",
     "Objects that are valued but not worked have little to break. The only "
     "candidate in the database is RD-0013, where iron corrosion under the "
     "knobs is described as a possible repair OR as iron ore in the soil.",
     "medium", "open", None, None),

    ("P-0007", "EV030", "H001; H009; H011", "2026-08-08",
     "SINGLETONS. Sites will overwhelmingly yield one dodecahedron each.",
     "Refuted if several sites yield multiple specimens, which would revive "
     "H001 (a system using many nodes) and H009 (a camp holding many tents) "
     "at once.",
     "Extraction of site-level counts from the Guggenberger catalogue "
     "(PUB-0023).",
     "No multiple-find site appears anywhere in the sources read so far, and "
     "about 134 objects are spread across four provinces.",
     "high", "open", None, None),

    ("P-0008", "EV021", "All", "2026-08-08",
     "POST-DEPOSITIONAL. Impact damage, where present, will correlate with "
     "agricultural disturbance rather than with use.",
     "Refuted if impact damage clusters on functionally significant surfaces "
     "such as aperture rims or knob crowns on stratified specimens.",
     "Comparison of damage patterns between metal-detector finds from "
     "cultivated land and the stratified or museum-curated specimens.",
     "Most of the recorded corpus consists of PAS finds from ploughsoil, and "
     "the one stratified specimen (RD-0020) is intact apart from a barely "
     "visible crack.",
     "high", "open", None, None),
]



# ---------------------------------------------------------------------------
# Candidate functional domains for screening
#
# One entry per everyday use proposed across the military, maritime, farming,
# animal-husbandry, administrative and craft domains. Each records only the
# predictions the mechanism CANNOT AVOID - what it must commit to whether the
# proposer likes it or not - so that a domain can be eliminated cheaply without
# authoring a full 42-variable HPM.
#
# Screening is not scoring. The outputs are "eliminated" or "promote".
# ---------------------------------------------------------------------------
SCREENING_CANDIDATES = [
    ("C-01", "Artillery shot gauge", "Military",
     "Stone or lead shot is passed through the apertures to sort it into "
     "calibrated sizes for ballistae and catapults.",
     "Calibrated ammunition of consistent weight",
     "The graded apertures are the obvious attraction of this idea."),
    ("C-02", "Harness or yoke junction fitting", "Military / Farming",
     "A junction block through which traces, reins or yoke straps are routed "
     "and held apart on a draught or cavalry harness.",
     None,
     "Would explain the apertures and the knobs as routing and spacing."),
    ("C-03", "Net-making mesh gauge", "Maritime",
     "Cord is passed round the object to set a constant mesh while netting is "
     "worked; different apertures give different mesh sizes.",
     "Fishing or fowling net of standard mesh",
     "The closest maritime analogue to the graded-aperture idea."),
    ("C-04", "Rigging fairlead or lead block", "Maritime",
     "Standing or running rigging is led through the apertures to change "
     "direction without chafing.",
     None,
     "Would explain apertures, hollow form and bronze."),
    ("C-05", "Volumetric grain or liquid measure", "Farming / Commerce",
     "The hollow interior serves as a fixed measure; apertures fill and empty "
     "it.",
     "A measured quantity of grain, seed or liquid",
     "The one candidate for which the Jublains balance association is "
     "suggestive."),
    ("C-06", "Seed-sowing or dibbing gauge", "Farming",
     "Pressed into tilled soil to set seed spacing and depth, or used to "
     "meter seed.",
     "Evenly spaced sowing",
     "Would explain the knobs as depth stops."),
    ("C-07", "Livestock bell or rattle", "Animal husbandry",
     "A hollow body containing a loose clapper, hung on a beast so it can be "
     "located; knobs protect the body.",
     "Sound",
     "The hollow form and protective knobs are the attraction."),
    ("C-08", "Tether or hobble ring", "Animal husbandry",
     "A rope junction to which an animal is tied, or through which hobble "
     "ropes are routed.",
     None,
     "Would explain apertures, knobs and bronze."),
    ("C-09", "Byre or beehive fumigation holder", "Animal husbandry",
     "Holds smouldering material to smoke a byre, hive or store against "
     "insects; apertures admit air and let smoke out.",
     "Smoke",
     "The only candidate that predicts thermal alteration, which makes it "
     "cheaply testable."),
    ("C-17", "Levelling sight for water engineering", "Engineering / Surveying",
     "Suspended so that gravity fixes the vertical, the object presents a "
     "face-pair axis at a known elevation - including exactly 0 degrees when "
     "hung from an edge - and is sighted through to set a level or a gradient "
     "for an aqueduct, channel or drain.",
     "A levelled line or a set gradient",
     "THE FIRST CANDIDATE TO MAKE USE OF EV046, the marked axis, and therefore "
     "the first to be scored on it. Refuted on precision by EXP-0004 and on "
     "documentation by the fact that Vitruvius names the instruments actually "
     "used for this task."),
    ("C-15", "Suspended solar altitude sight", "Astronomical",
     "The object is hung from a knob so that gravity fixes the vertical. When "
     "the sun's altitude matches a face-pair axis, light passes cleanly through "
     "both opposite apertures and throws a shadowless disc of light inside the "
     "object's shadow. Which pair aligns, and when, indicates the season.",
     "A reading of solar altitude, and hence of the date",
     "THE BEST-CONSTRUCTED MECHANICAL PROPOSAL IN THE PROJECT, and the only one "
     "whose central quantity is SCALE-INVARIANT: the axis angles are fixed by "
     "the polyhedron regardless of the object's size, which is exactly what the "
     "deduction in the results summary says the function must be. Refuted by "
     "computation rather than by the corpus - see EXP-0003."),
    ("C-14", "Zodiac sundial by internal light projection", "Astronomical",
     "Held or mounted in a fixed orientation, sunlight entering one aperture "
     "projects a patch onto the interior wall. The position of the patch at "
     "local noon indicates the solar declination and hence the zodiac month, "
     "in the manner of the zodiac declination curves carried by Roman conical "
     "and hemispherical dials.",
     "A reading of the date or zodiac sign",
     "The only candidate in the project refuted by computation rather than by "
     "the corpus alone. See EXP-0002."),
    ("C-13", "Garment or tailoring size gauge", "Craft / Textile",
     "Each aperture is a fixed gauge against which a tubular garment part - a "
     "glove finger, cuff, hose or sleeve opening - is checked or sized during "
     "cutting and making up. The graded apertures form a graded set of sizes.",
     "Garment parts made to a repeatable size",
     "DISTINCT FROM H012, H014 AND C-12: a gauge CHECKS a size, it does not "
     "FORM anything. That single difference changes what the mechanism needs "
     "and, crucially, leaves the knobs unexplained."),
    ("C-11", "Knob-based dividers or angle gauge", "Metrology / Surveying",
     "The twenty vertex knobs provide a fixed set of inter-knob distances and "
     "angles. The object is used like a set of dividers or a three-dimensional "
     "template to step distances or set angles on a workpiece or on the ground.",
     "Marked-out distances and angles",
     "Distinct from H002 and H011, which use the apertures optically. Here the "
     "KNOBS are the working reference points and the apertures are irrelevant. "
     "NOTE ON THE MARITIME FRAMING: there were no sea charts in the Roman "
     "world. Navigation used the periplus, a written pilot book; the first "
     "portolan charts appear in the late 13th century. A divider used against a "
     "chart therefore has no chart to work on, and the candidate is screened "
     "only in its land-surveying and workshop framing."),
    ("C-12", "Soft-material forming and handling tool", "Craft",
     "The object forms, shapes or holds material softer than bronze - leather, "
     "wax, foil, soft metal sheet or another precious soft substance. The knobs "
     "act as standoffs and spacers setting thickness; the graded apertures suit "
     "different work sizes; relief around the apertures impresses into the "
     "material.",
     "Formed pieces of leather, wax, foil or soft metal",
     "THE GENERALISATION OF H014. Where H014 names the material (wax) and the "
     "product (sealing bullae), this candidate names only the property that "
     "matters mechanically: everything the tool touched was softer than it. "
     "READ THE SCREEN SCORE WITH GREAT CARE - see the notes on this candidate "
     "in the report."),
    ("C-10", "Wax bulla or seal former", "Administrative",
     "Softened wax is pressed within the object around a knotted cord to form "
     "a standardised sealing element; knobs act as spacers limiting "
     "compression.",
     "Standardised wax bullae securing cords on documents",
     "The hypothesis of PUB-0041 (Lamb 2026), tested experimentally on a "
     "replica. Screened here; not yet promoted to a scored hypothesis."),
]

# Format: (candidate_id, ev_id, prediction, reading_override, rationale)
SCREENING = [
    # --- C-17 Levelling sight for water engineering -------------------------
    ("C-17", "EV046", "++", None,
     "A levelling sight must present a known axis, and the object marks one. "
     "NOTE: C-17 IS THE FIRST CANDIDATE SCORED ON EV046, which was added after "
     "every hypothesis had been specified. This advantages it relative to "
     "H001-H014, all of which are silent on the variable"),
    ("C-17", "EV006", "++", None,
     "A through-sight needs truly circular apertures at both ends"),
    ("C-17", "EV003", "-", None,
     "Thin walls give a sharper sight; a thick wall makes a tube"),
    ("C-17", "EV017", "-", None,
     "Optical use; nothing passes through, so the absence of bore wear counts "
     "in favour"),
    ("C-17", "EV010", "++", None,
     "The readings are angles; departure from regular geometry is direct "
     "instrument error, and EXP-0004 shows the margin is already too thin to "
     "absorb any"),
    ("C-17", "EV039", "++", None,
     "A level must give the same reading in any workman's hands. The corpus "
     "varies 2.5:1 in size and its pair differences, which set the precision, "
     "vary from 0.3 to 10.2 mm between specimens"),
    ("C-17", "EV019", "++", None,
     "Suspension from a cord is required by the mechanism and must bear on the "
     "object"),
    ("C-17", "EV025", "+", "confirmed",
     "Predicts urban and engineering contexts, which the corpus shows"),
    ("C-17", "EV027", "++", "absent",
     "Predicts association with surveying or levelling equipment - a "
     "chorobates, dioptra, groma, libra, or a plumb bob. None is recorded with "
     "any dodecahedron"),
    ("C-17", "EV026", "--", "confirmed",
     "Aqueducts were built across the whole empire, and most spectacularly in "
     "Italy, Africa and the East. An instrument for building them had no "
     "reason to stay in the north-western provinces; the confinement is "
     "present"),

    # --- C-15 Suspended solar altitude sight --------------------------------
    ("C-15", "EV006", "++", None,
     "A shadowless disc is a null reading and needs truly circular apertures "
     "at both ends of the sight line"),
    ("C-15", "EV003", "-", None,
     "Thin walls give a sharper null; a thick wall turns the aperture into a "
     "tube and blurs the alignment"),
    ("C-15", "EV017", "-", None,
     "Optical use; nothing passes through, so the absence of bore wear counts "
     "in favour"),
    ("C-15", "EV039", "-", None,
     "THE CANDIDATE'S DISTINCTIVE STRENGTH. The face-axis angles are fixed by "
     "the polyhedron and are identical in a 40 mm and a 100 mm specimen, so "
     "the instrument needs no standardisation at all. It is the only proposal "
     "in the project for which the absence of a standard is predicted rather "
     "than merely tolerated"),
    ("C-15", "EV010", "++", None,
     "The readings ARE angles, so departure from regular geometry is direct "
     "instrument error"),
    ("C-15", "EV004", "0", None,
     "NEUTRAL, AND A DEBIT RATHER THAN A DODGE: the mechanism does not need "
     "graded apertures at all. Aperture size affects only the tolerance of the "
     "null, not which elevation is read. The candidate leaves the single "
     "strongest feature of the corpus unexplained"),
    ("C-15", "EV005", "+", None,
     "Opposite apertures should be near-matched, since their difference sets "
     "the angular tolerance of the null: about 1 to 3 degrees for the observed "
     "2 to 4.5 mm pair differences over a 50 mm path"),
    ("C-15", "EV019", "++", None,
     "Repeated suspension from a cord must bear on the knob and leave rope wear"),
    ("C-15", "EV041", "++", None,
     "The suspension cord bears directly on whichever knob is used"),
    ("C-15", "EV012", "+", None,
     "Clean aperture edges are needed for a sharp null"),
    ("C-15", "EV025", "+", "confirmed",
     "Predicts urban and domestic contexts, which the corpus shows"),
    ("C-15", "EV027", "++", "absent",
     "Predicts association with calendrical or astronomical equipment; none is "
     "recorded with any dodecahedron"),
    ("C-15", "EV026", "-", "confirmed",
     "EXP-0003 shows the four noon-reachable elevations are identical from "
     "43.7 to 55 degrees north, so the instrument is latitude-insensitive "
     "across the empire and had no reason to remain in the north-western "
     "provinces. Confinement therefore counts against it"),

    # --- C-14 Zodiac sundial by internal light projection --------------------
    ("C-14", "EV004", "++", None,
     "Twelve apertures for twelve zodiac months is the functional claim"),
    ("C-14", "EV010", "++", None,
     "A dial reads angles. Geometric fidelity is the whole instrument, and "
     "EXP-0002 shows irregularity degrades the resolution further"),
    ("C-14", "EV039", "++", None,
     "A dial is calibrated for one latitude and must be reproducible; the "
     "corpus spans 43 to 55 degrees north with no systematic geometric "
     "variation and no standardisation at all"),
    ("C-14", "EV038", "++", None,
     "A dial must be oriented to the meridian and held fixed. No specimen has "
     "a base, a suspension loop or any distinguished axis; the knobs let it "
     "rest on any face"),
    ("C-14", "EV044", "++", None,
     "The interior IS the projection surface. It must be smoothed and it must "
     "carry engraved declination curves, as every Roman zodiac dial does. The "
     "corpus interiors are rough, unfinished and unmarked"),
    ("C-14", "EV012", "++", None,
     "The interior is the projection surface and must be smooth and true. The "
     "PAS records in this database consistently describe interiors as roughly "
     "or crudely cast and unfinished (RD-0001, RD-0002, RD-0003, RD-0008, "
     "RD-0011, RD-0012)"),
    ("C-14", "EV014", "++", None,
     "Every Roman zodiac dial carries engraved declination curves ON THE "
     "PROJECTION SURFACE. The engraving on these objects is entirely on the "
     "EXTERIOR, around the apertures; no specimen has interior markings"),
    ("C-14", "EV017", "-", None,
     "Optical use; nothing passes through the apertures, so the absence of "
     "bore wear counts in favour"),
    ("C-14", "EV025", "+", "confirmed",
     "Predicts urban and domestic contexts, which the corpus shows"),
    ("C-14", "EV027", "++", "absent",
     "Predicts association with other timekeeping or astronomical equipment. "
     "None is recorded with any dodecahedron"),
    ("C-14", "EV026", "+", "confirmed",
     "A latitude-calibrated instrument would be confined to a band of "
     "latitudes, which is the one argument in this candidate's favour. WEAK: "
     "the corpus spans 43 to 55 degrees north, some 12 degrees, which is far "
     "too wide for a single calibration"),

    # --- C-13 Garment or tailoring size gauge -------------------------------
    ("C-13", "EV004", "++", None,
     "A graded set of apertures IS a graded set of garment sizes. This is the "
     "whole functional claim"),
    ("C-13", "EV006", "++", None,
     "A gauge aperture must be truly circular or the size it reports is wrong"),
    ("C-13", "EV007", "++", None,
     "The lip must be rounded, because cloth or leather is drawn against it "
     "and a sharp rim would snag or cut the work"),
    ("C-13", "EV017", "-", None,
     "Only soft material passes the aperture, and briefly. Absence of bore "
     "wear counts in favour. NOTE this is the same premise as C-12 and it was "
     "chosen knowing the wear result"),
    ("C-13", "EV013", "-", None,
     "A casting flaw on a working aperture distorts the size it reports"),
    ("C-13", "EV016", "+", None,
     "Engraved rings around an aperture could serve to identify which size it "
     "is, which a graded set needs"),
    ("C-13", "EV003", "-", None,
     "A gauge carries no load; thin walls suffice"),
    ("C-13", "EV008", "0", None,
     "NEUTRAL, AND THIS IS THE CANDIDATE'S WEAK POINT RATHER THAN A DODGE: a "
     "sizing gauge does not need knobs at all, let alone twenty of them. The "
     "hypothesis leaves the most distinctive feature of the object "
     "unexplained, which is exactly what H014 and C-12 do explain"),
    ("C-13", "EV010", "0", None,
     "NEUTRAL: each aperture is independently a gauge, so overall regularity "
     "of the body is irrelevant. This is a genuine indifference and is what "
     "separates C-13 from C-11, where the references are relations BETWEEN "
     "knobs and global regularity does matter"),
    ("C-13", "EV039", "+", None,
     "A workshop gauge need only be self-consistent to make matched pairs, so "
     "standardisation between objects is expected but not required. Predicted "
     "at '+' rather than '++' for that reason"),
    ("C-13", "EV025", "+", "confirmed",
     "Predicts urban workshop and domestic contexts, which the corpus shows"),
    ("C-13", "EV026", "+", "confirmed",
     "Garment forms were regionally specific in a way that artillery and "
     "fishing were not. The north-western provinces had a distinctive and "
     "high-value textile tradition: the birrus Britannicus is named in "
     "Diocletian's Price Edict of AD 301, mid-window, at 6,000 denarii, and "
     "hooded garments are a Gallic and north-western style (PUB-0043). A tool "
     "for a regionally specific garment may legitimately be regionally "
     "confined"),
    ("C-13", "EV027", "++", "absent",
     "Predicts needles, shears, thimbles, awls, spindle whorls, loom weights "
     "or cloth alongside. None is recorded with any dodecahedron"),
    ("C-13", "EV040", "+", None,
     "Regional garment traditions imply regionally varying tools"),
    ("C-13", "EV024", "+", None,
     "Textile or leather fibres should remain against the aperture lips"),

    # --- C-11 Knob-based dividers or angle gauge ---------------------------
    ("C-11", "EV039", "++", None,
     "A distance or angle gauge that varies between objects transfers no "
     "measurement. DECISIVE: overall diameter varies 2.5:1 across the corpus"),
    ("C-11", "EV010", "++", None,
     "Inter-knob distances must be predictable from the form; an irregular "
     "body gives unpredictable references"),
    ("C-11", "EV013", "--", None,
     "Casting distortion displaces the reference points and corrupts every "
     "measurement taken from them"),
    ("C-11", "EV009", "++", None,
     "The reference points must be uniform in size and placement"),
    ("C-11", "EV008", "++", None,
     "Knob diameter must be consistent or the contact point shifts"),
    ("C-11", "EV017", "-", None,
     "Nothing passes through the apertures; absence of bore wear counts in "
     "favour, as it does for H011"),
    ("C-11", "EV025", "+", "confirmed",
     "Predicts urban, architectural and workshop contexts, which the corpus "
     "shows"),
    ("C-11", "EV027", "++", "absent",
     "Predicts association with surveying or drafting equipment - groma, "
     "dividers, rules, styli. None is recorded with any dodecahedron"),
    ("C-11", "EV026", "--", "confirmed",
     "Measurement practice was empire-wide; confinement to the north-west "
     "would falsify, and the confinement is present"),

    # --- C-12 Soft-material forming and handling tool -----------------------
    ("C-12", "EV017", "--", None,
     "THE UNIFYING PREMISE. Nothing harder than bronze ever contacts the tool, "
     "so no bore wear can form. All four wear predictions below follow "
     "deductively from this one premise rather than being chosen separately"),
    ("C-12", "EV018", "-", None,
     "Soft material cannot abrade the exterior"),
    ("C-12", "EV019", "-", None,
     "No cord is drawn under tension across the object"),
    ("C-12", "EV020", "-", None,
     "Nothing rotates against the object"),
    ("C-12", "EV004", "++", None,
     "Graded apertures suit different work sizes"),
    ("C-12", "EV008", "++", None,
     "The knobs are standoffs that set the thickness of the formed piece"),
    ("C-12", "EV009", "++", None,
     "Standoffs must be uniform or thickness varies across the work"),
    ("C-12", "EV003", "-", None,
     "The tool carries no structural load; thin walls suffice"),
    ("C-12", "EV014", "++", None,
     "Relief around an aperture impresses itself into soft material, which "
     "makes the decoration a working surface rather than ornament"),
    ("C-12", "EV016", "++", None,
     "Engraving after casting creates that impressing surface"),
    ("C-12", "EV039", "-", None,
     "A craft tool need not conform to any standard; the gauge wanted varies "
     "with the work"),
    ("C-12", "EV040", "+", None,
     "Craft traditions and their tools vary by region"),
    ("C-12", "EV025", "+", "confirmed",
     "Predicts workshop and urban domestic contexts, which the corpus shows"),
    ("C-12", "EV026", "+", "confirmed",
     "A regionally transmitted craft may be regionally confined. WEAK: almost "
     "any culturally specific explanation predicts this"),
    ("C-12", "EV027", "++", "absent",
     "Predicts craft equipment alongside - awls, punches, offcuts, scrap foil, "
     "raw material. None is recorded with any dodecahedron. THIS IS THE "
     "CANDIDATE'S ONLY HARD CONTRADICTION and it is the same one that costs "
     "H014 its largest single loss"),
    ("C-12", "EV024", "++", None,
     "Residues of whatever was worked should remain on the interior and around "
     "the apertures. THE DECISIVE AND UNMEASURED TEST"),
    # --- C-01 Artillery shot gauge ---------------------------------------
    ("C-01", "EV039", "++", None,
     "A gauge that is not standardised sorts nothing; two gauges must agree"),
    ("C-01", "EV017", "++", None,
     "Stone or lead shot dragged through bronze apertures abrades them"),
    ("C-01", "EV003", "++", None,
     "A gauge handled with shot must be robust"),
    ("C-01", "EV010", "++", None,
     "Aperture geometry must be true or the calibration is wrong"),
    ("C-01", "EV025", "++", "absent",
     "Predicts military dominance; corpus is more than half urban settlement "
     "and under one-fifth military (PUB-0003, 33)"),
    ("C-01", "EV026", "--", "confirmed",
     "Artillery served empire-wide; confinement to the north-west would "
     "falsify. The confinement is present (PUB-0003, 32)"),
    ("C-01", "EV027", "++", "absent",
     "Predicts shot, artillery fittings or military kit alongside; none is "
     "recorded with any dodecahedron"),

    # --- C-02 Harness or yoke junction ------------------------------------
    ("C-02", "EV019", "++", None,
     "Straps and traces under draught tension bear on the fitting constantly"),
    ("C-02", "EV017", "++", None,
     "Anything routed through an aperture under draught load wears the bore"),
    ("C-02", "EV003", "++", None,
     "A draught fitting carries real load and must be substantial"),
    ("C-02", "EV035", "++", None,
     "Must not deform under harness tension"),
    ("C-02", "EV039", "++", None,
     "Harness parts are replaced and must interchange"),
    ("C-02", "EV025", "++", "absent",
     "Predicts military and rural dominance; the corpus is urban civilian"),
    ("C-02", "EV027", "++", "absent",
     "Predicts harness fittings, bits or vehicle parts alongside; none is "
     "recorded"),

    # --- C-03 Net-making mesh gauge ---------------------------------------
    ("C-03", "EV039", "++", None,
     "A mesh gauge that varies between objects produces unusable netting"),
    ("C-03", "EV019", "++", None,
     "Cord is drawn round the gauge under tension at every mesh"),
    ("C-03", "EV041", "++", None,
     "Cord bearing on the knobs at every mesh must wear them"),
    ("C-03", "EV026", "--", "confirmed",
     "Fishing and fowling are practised across the empire; confinement to the "
     "north-west would falsify, and the confinement is present"),
    ("C-03", "EV025", "++", "absent",
     "Predicts coastal, riverine and lacustrine sites; the corpus is inland "
     "urban settlement"),
    ("C-03", "EV027", "++", "absent",
     "Predicts net weights, floats or hooks alongside; none is recorded"),

    # --- C-04 Rigging fairlead ---------------------------------------------
    ("C-04", "EV019", "++", None,
     "A fairlead exists to take rope load; rope wear is its defining trace"),
    ("C-04", "EV017", "++", None,
     "Rope running through an aperture under load grooves the bore"),
    ("C-04", "EV003", "++", None,
     "Rigging loads are large; thin walls would collapse"),
    ("C-04", "EV036", "++", None,
     "Must transfer load between rope and hull or spar"),
    ("C-04", "EV025", "++", "absent",
     "Predicts ports, wrecks and riverine sites; the corpus is inland urban"),
    ("C-04", "EV026", "--", "confirmed",
     "Shipping is Mediterranean above all; absence from Italy, Spain, Africa "
     "and the East falsifies"),

    # --- C-05 Volumetric measure -------------------------------------------
    ("C-05", "EV039", "++", None,
     "A measure that is not standardised measures nothing. THIS IS DECISIVE: "
     "overall diameter varies 2.5:1 across the corpus"),
    ("C-05", "EV010", "++", None,
     "Internal volume must be true and reproducible"),
    ("C-05", "EV013", "--", None,
     "Casting voids alter internal volume and would be rejected"),
    ("C-05", "EV004", "--", None,
     "Apertures perforating the vessel make it unable to hold anything "
     "measurable. THIS ALONE ELIMINATES THE CANDIDATE"),
    ("C-05", "EV026", "--", "confirmed",
     "Roman measures were empire-wide; regional confinement falsifies"),

    # --- C-06 Seed-sowing or dibbing gauge ---------------------------------
    ("C-06", "EV018", "++", None,
     "Pressed into soil repeatedly; abrasive wear is unavoidable"),
    ("C-06", "EV021", "++", None,
     "Contact with stones in tilled soil chips and dents"),
    ("C-06", "EV039", "++", None,
     "Spacing must be reproducible between tools"),
    ("C-06", "EV025", "++", "absent",
     "Predicts rural and agricultural contexts; the corpus is urban settlement"),
    ("C-06", "EV003", "++", None,
     "A tool pressed into soil must be robust; the corpus is 0.5-4 mm"),

    # --- C-07 Livestock bell or rattle -------------------------------------
    ("C-07", "EV017", "++", None,
     "A clapper striking the interior leaves impact traces around the "
     "apertures and inside"),
    ("C-07", "EV021", "++", None,
     "A bell on a beast is knocked constantly"),
    ("C-07", "EV019", "++", None,
     "Suspension from a collar or strap wears the suspension point"),
    ("C-07", "EV018", "++", None,
     "Constant contact with hide, vegetation and other stock"),
    ("C-07", "EV025", "++", "absent",
     "Predicts rural and pastoral contexts; the corpus is urban settlement"),
    ("C-07", "EV038", "++", None,
     "A hung bell has a fixed orientation and needs a suspension loop; no "
     "dodecahedron has one"),

    # --- C-08 Tether or hobble ring ----------------------------------------
    ("C-08", "EV019", "++", None,
     "A tether point exists to take rope load under an animal's pull"),
    ("C-08", "EV017", "++", None,
     "Rope through an aperture under an animal's weight grooves the bore"),
    ("C-08", "EV003", "++", None,
     "Must resist the pull of a large animal; 0.5-4 mm of leaded bronze "
     "would not"),
    ("C-08", "EV035", "++", None,
     "Must not deform or burst under shock loading"),
    ("C-08", "EV025", "++", "absent",
     "Predicts rural, pastoral and military-transport contexts"),

    # --- C-09 Fumigation holder --------------------------------------------
    ("C-09", "EV023", "++", None,
     "Smouldering material inside must leave soot and heat alteration. THIS "
     "IS THE CANDIDATE'S DECISIVE AND CURRENTLY UNTESTED PREDICTION"),
    ("C-09", "EV024", "++", None,
     "Combustion residues should remain on the interior"),
    ("C-09", "EV018", "+", None,
     "Handled and hung in use"),
    ("C-09", "EV025", "++", "absent",
     "Predicts rural, byre and apiary contexts; the corpus is urban settlement"),
    ("C-09", "EV011", "++", None,
     "Repeated heating of an 18 per cent lead alloy would be a poor choice; "
     "lead melts at 327 degrees Celsius"),

    # --- C-10 Wax bulla or seal former --------------------------------------
    ("C-10", "EV008", "++", None,
     "The knobs act as spacers limiting compression, per PUB-0041"),
    ("C-10", "EV004", "++", None,
     "Graded apertures accommodate cords of varying thickness, per PUB-0041"),
    ("C-10", "EV017", "-", None,
     "Wax is soft and cords are knotted rather than drawn; no bore wear is "
     "predicted, and its absence counts in favour"),
    ("C-10", "EV024", "++", None,
     "Beeswax and resin worked in the object should leave recoverable "
     "residue. THIS IS THE CANDIDATE'S DECISIVE AND CURRENTLY UNTESTED "
     "PREDICTION"),
    ("C-10", "EV039", "+", None,
     "Bullae are described as standardised, so some consistency between tools "
     "is expected"),
    ("C-10", "EV025", "++", "confirmed",
     "Predicts administrative and urban contexts, comparable to seal boxes. "
     "More than half of located finds are from cities and settlements"),
    ("C-10", "EV027", "++", "absent",
     "Predicts seal boxes, styli, writing equipment or document fittings "
     "alongside; none is recorded with any dodecahedron"),
    ("C-10", "EV023", "-", None,
     "Wax is worked soft, not melted in the object; absence of thermal "
     "alteration counts in favour"),
]


# ---------------------------------------------------------------------------
# Usage-value assessments
#
# The governing fact is that these objects are EXPENSIVE: difficult to cast, in
# copper alloy, finely finished and engraved, individually varied, made for two
# centuries. A tool is made as cheaply as will serve. An object whose worth lies
# in its making, or in the experience of using it, is made expensively ON
# PURPOSE - and is not standardised, because each is its own achievement.
#
# The corpus properties therefore discriminate between the three kinds of value,
# and they do so consistently. That is a result, not an assumption.
#
# Format: (id, type, product, substitute, product_value, craft_value,
#          experience_value, rationale)
# ---------------------------------------------------------------------------
UTILITY = [
    ("H001", "hypothesis", "A modular structure assembled from rods",
     "Carpentry joints and iron fittings, cheaper and far stronger",
     -1, 0, 0,
     "A structural node is useful, but 0.5-4 mm of leaded bronze cannot carry "
     "load, and the joinery it would replace was solved cheaply everywhere in "
     "wood and iron. Nothing about a hidden structural fitting rewards fine "
     "finishing or engraving"),
    ("H002", "hypothesis", "An estimate of distance",
     "The groma and the dioptra, both documented, plus trained pacing",
     -2, 0, 0,
     "Distance measurement mattered greatly, which is why Rome had named, "
     "standardised, written-up instruments for it. An unstandardised object "
     "cannot compete with a groma"),
    ("H003", "hypothesis", "Symbolic or ritual efficacy, and standing",
     "None: the object IS the product",
     2, 2, 2,
     "SCORES ON ALL THREE, AND IS THE ONLY FAMILY THAT DOES. The expense is "
     "functional rather than anomalous: difficulty of manufacture ADDS to the "
     "worth of a votive or prestige object instead of subtracting from it; the "
     "absence of standardisation is what individual commissioning looks like; "
     "and the value is delivered in the using, not in an output"),
    ("H004", "hypothesis", "Light",
     "A pottery lamp, near-free and in every house",
     -2, 0, 1,
     "Light was valuable and already had a cheap universal solution. A costly "
     "lamp holder could carry display value, but no thermal evidence supports "
     "the function at all"),
    ("H005", "hypothesis", "Looped or knitted fabric",
     "A wooden or bone spool, effectively free",
     -1, 0, 0,
     "The product is useful; the material is unexplained"),
    ("H006", "hypothesis", "Celestial measurement",
     "Documented instruments; and see EXP-0002 and EXP-0003",
     -2, 0, 1,
     "Cannot deliver the product at all on the computed geometry"),
    ("H007", "hypothesis", "Unspecified military function",
     "Unclear, because the product is unclear",
     -1, 0, 0,
     "A hypothesis that does not name its product cannot be assessed for worth"),
    ("H008", "hypothesis", "A focus for domestic or personal cult",
     "None: the object IS the product",
     2, 2, 2,
     "As H003. The making and the holding are the point"),
    ("H009", "hypothesis", "A pitched shelter",
     "Rope lashing or a turned wooden hub, trivially cheaper",
     -2, 0, 0,
     "Shelter is valuable and Rome solved it with leather, rope and wood"),
    ("H010", "hypothesis", "Shade or rain cover",
     "A turned wooden crown",
     -1, 0, 1,
     "A canopy crown carries almost no load and has no reason to be bronze, "
     "though a visible fitting on a status accessory could carry display value"),
    ("H011", "hypothesis", "A range estimate for shooting",
     "Trained instinct, which is how archers actually shoot",
     -2, 0, 0,
     "An instrument that must be raised, oriented and read is slower than the "
     "shot it serves"),
    ("H012", "hypothesis", "Looped cord tubes, gloves or hose",
     "A wooden or bone spool, effectively free",
     -1, 0, 0,
     "THE STRONGEST EVIDENTIAL HYPOTHESIS IS AMONG THE WEAKEST ON WORTH. "
     "Peg-frames for looped cord work are made of scrap wood in every culture "
     "that does this. Nothing about the task rewards leaded bronze, fine "
     "finishing or engraved rings, and the work itself is ordinary labour"),
    ("H013", "hypothesis", "Laid cord or rope",
     "Hand-laying, or a wooden laying top",
     -1, 0, 0,
     "As H012, with the added cost of a tool that must be turned under tension"),
    ("H014", "hypothesis", "Standardised wax sealings for documents",
     "A simple mould, or forming the wax freehand",
     0, 1, 1,
     "The most defensible utilitarian case. Administrative consistency has real "
     "institutional value, an office could afford bronze, and a durable former "
     "outlasts a mould. Some craft value attaches to a fine office instrument, "
     "and sealing is a small ceremony with its own standing. But the corpus is "
     "NOT standardised, which is exactly the value the product should deliver"),
    ("C-12", "candidate", "Formed leather, wax, foil or soft metal",
     "Wooden or bone formers, and simple moulds",
     0, 1, 0,
     "Inherits H014's position. Bronze is defensible for a former that must "
     "keep its shape through many pressings, which is the one genuine argument "
     "for the material anywhere in the utilitarian family"),
    ("C-13", "candidate", "Garment parts made to a repeatable size",
     "A knotted cord or a marked stick, effectively free",
     -1, 0, 0,
     "Sizing is real work and the cheapest possible instrument to improvise"),
    ("C-14", "candidate", "A reading of the date or zodiac sign",
     "Sundials, surviving in their hundreds and described by Vitruvius, and "
     "the public fasti posted in every town",
     -2, 0, 1,
     "TIME AS A PRODUCT, ASSESSED. The date was valuable AND already available, "
     "free, more precisely and more conveniently. Some experience value could "
     "attach to a personal instrument of the heavens"),
    ("C-15", "candidate", "A reading of solar altitude, hence the season",
     "Sundials, the public fasti, and the agricultural calendar preserved in "
     "Columella and Palladius",
     -2, 0, 1,
     "Delivers eight irregular events a year with a blind window of 2.2 months "
     "at Arles rising to 4.6 months at Corbridge, at roughly four days' "
     "precision near the equinoxes and far worse near the solstices, and needs "
     "three different modes of support. A sundial on a wall is cheaper, "
     "continuous and better"),
    ("C-16", "candidate", "The making itself: a demonstration of mastery, and "
     "an object to be possessed, handled and shown",
     "None: no cheaper object demonstrates the same mastery",
     0, 2, 2,
     "PROPOSED IN RESPONSE TO THE OBSERVATION THAT THE CRAFTING IS ITSELF THE "
     "VALUE. The reading is the chef-d'oeuvre or masterpiece interpretation "
     "recorded by Coulon 1910 and cited in PUB-0019: these objects are 'des "
     "exercices de maitres, des sortes de chefs-d'oeuvre'. It predicts, without "
     "strain, every corpus property that embarrasses the utilitarian family: "
     "expensive material, difficult casting, fine finishing, engraving "
     "concentrated where it is most visible, NO standardisation because each is "
     "its own achievement, no wear because it is handled and shown rather than "
     "worked, no toolkit because it is not a tool, deposition in graves and "
     "hoards as a valued possession, one per owner, and no mention in technical "
     "literature because it belongs to no trade. ITS WEAKNESS IS THE MIRROR OF "
     "ITS STRENGTH: it is consistent with everything and forbids almost "
     "nothing. Its one real test is EV045"),
]


# ---------------------------------------------------------------------------
# Specimen quality and admissibility
#
# Applied rules, not case-by-case judgement:
#   admit_mass      requires completeness = complete. A fragment's weight is
#                   not a specimen's weight, and pooling the two makes every
#                   mass statistic meaningless.
#   admit_geometry  requires completeness in (complete, incomplete) AND
#                   measurement_grade in (direct, one_remove). Whole-object
#                   dimensions cannot be taken from a fragment, and values read
#                   off a figure or arriving at two removes carry no stated
#                   tolerance.
#   admit_context   requires a recorded findspot and provenance_grade <= D.
#   outlier         flagged where a measurement falls outside the published
#                   corpus range (PUB-0003, 31: 4-10 cm face to face excluding
#                   knobs, up to c 11 cm including them).
#
# Format: (rd_id, completeness, provenance, measurement, mass, geom, ctx,
#          outlier, note)
# ---------------------------------------------------------------------------
F = "fragment"

SPECIMEN_QUALITY = [
    ("RD-0037", "complete",   "D", "one_remove",  0, 1, 0, 0,
     "Louvre catalogue record; purchased 1825, provenance queried by the "
     "museum. No weight published"),
    ("RD-0038", "unknown",    "D", "two_removes", 0, 0, 1, 0,
     "REJECTED FOR GEOMETRY. Findspot is recorded, but the museum page could "
     "not be loaded and the height reaches this project through a "
     "search-engine extract"),
    ("RD-0039", "unknown",    "D", "none",        0, 0, 1, 0,
     "No measurements published in the source consulted"),
    ("RD-0040", "unknown",    "E", "none",        0, 0, 0, 0,
     "Collection piece with no findspot, held in a country that was never "
     "Roman. No measurements. Contributes only the surface-condition "
     "photograph"),
    ("RD-0001", "complete",   "C", "direct",      1, 1, 1, 0,
     "PAS detector find, cultivated land; complete and directly measured"),
    ("RD-0002", "incomplete", "C", "direct",      0, 1, 1, 0,
     "SIX COMPLETE FACES AND HALF OF FIVE MORE despite the name carrying no "
     "'fragment' label. Its 270 g is the weight of an incomplete object and is "
     "inadmissible for mass"),
    ("RD-0003", F,            "C", "direct",      0, 0, 1, 0, "Two joining pieces"),
    ("RD-0004", F,            "C", "direct",      0, 0, 1, 0, "Fragment"),
    ("RD-0005", "complete",   "B", "direct",      1, 1, 1, 0,
     "Excavated 2023 in Trench 4, feature recorded, museum-held. Complete, "
     "undamaged; the best-preserved specimen in the corpus"),
    ("RD-0006", "unknown",    "E", "none",        0, 0, 0, 0,
     "REJECTED FOR ALL SCORING. Sole source is PUB-0004, a Wikipedia article, "
     "confidence E. The only E-grade specimen. Retained as a corpus entry and "
     "as the possible subject of the PUB-0019 tab IV measurements, an "
     "attribution that is itself unconfirmed"),
    ("RD-0007", "unknown",    "B", "none",        0, 0, 1, 0,
     "1739 archival record, the first dodecahedron ever reported; no "
     "measurements survive"),
    ("RD-0008", F,            "C", "direct",      0, 0, 1, 0, "Fragment"),
    ("RD-0009", F,            "C", "direct",      0, 0, 1, 0, "Fragment"),
    ("RD-0010", F,            "C", "direct",      0, 0, 1, 0, "Fragment, 1.7 g"),
    ("RD-0011", F,            "C", "direct",      0, 0, 1, 0,
     "Fragment; supplies the 9.4 / 22.6 mm opposing-hole pair"),
    ("RD-0012", F,            "C", "direct",      0, 0, 1, 0, "Fragment"),
    ("RD-0013", F,            "C", "direct",      0, 0, 1, 0, "Four fragments"),
    ("RD-0014", F,            "C", "direct",      0, 0, 1, 0, "Fragment"),
    ("RD-0015", "unknown",    "D", "one_remove",  0, 1, 0, 0,
     "Museum record; findspot given as 'Couthuin OR Bassenge', unresolved"),
    ("RD-0016", "complete",   "D", "one_remove",  1, 1, 0, 0,
     "British Museum, acquired 1878; findspot 'British Isles', no location"),
    ("RD-0017", "complete",   "D", "one_remove",  1, 0, 0, 1,
     "OUTLIER ON DIAMETER ONLY, REJECTED FROM GEOMETRY. Maximum diameter "
     "127.71 mm exceeds the published corpus maximum of about 110 mm including "
     "knobs (PUB-0003, 31 n 2) and the 40-100 mm height range given without "
     "knobs by PUB-0023. Either the museum figure includes what the corpus "
     "figures exclude, or the object is atypical. "
     "THE WEIGHT ARGUMENT PREVIOUSLY MADE HERE WAS WRONG AND IS WITHDRAWN: "
     "this record formerly called 553.2 g anomalous at 2.2 times the next "
     "heaviest complete specimen in THIS database, a sample of five. PUB-0023 "
     "gives the corpus weight range as 35-580 g with one specimen over "
     "1000 g, so 553.2 g sits inside the published range and is not "
     "remarkable. The error came from treating this project's own small "
     "sample as the reference population. Guggenberger no 62, type 5a"),
    ("RD-0018", "unknown",    "C", "none",        0, 0, 1, 0, "Museum record, no measurements"),
    ("RD-0019", "unknown",    "D", "none",        0, 0, 1, 0, "Catalogue entry, confidence D"),
    ("RD-0020", "complete",   "A", "direct",      1, 1, 1, 0,
     "THE REFERENCE SPECIMEN. Excavated 1995 from sealed destruction layer "
     "F1058, peer-reviewed excavation report, museum-held, complete apart from "
     "a barely visible crack. The only specimen whose authenticity is secured "
     "by context"),
    ("RD-0021", "unknown",    "C", "none",        0, 0, 1, 0, "Museum record via Wikidata"),
    ("RD-0022", "complete",   "E", "direct",      1, 1, 0, 0,
     "PROVENANCE E: no findspot of any kind, private collection, unpublished "
     "until 2025. Measurements are direct and detailed, so it is admitted for "
     "mass and geometry, but every statistic it enters must be reported with "
     "and without it"),
    ("RD-0023", "unknown",    "C", "one_remove",  0, 1, 1, 0,
     "Grave context reported at one remove; two production-hole diameters"),
    ("RD-0024", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Context at one remove"),
    ("RD-0025", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Context at one remove"),
    ("RD-0026", F,            "C", "one_remove",  0, 0, 1, 0, "Fragment, temple site"),
    ("RD-0027", F,            "C", "one_remove",  0, 0, 1, 0, "Fragment, cache"),
    ("RD-0028", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Detector find, statuette association"),
    ("RD-0029", "unknown",    "C", "one_remove",  0, 0, 1, 0,
     "Context classification conflicts between settlement and hoard"),
    ("RD-0030", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Grave, at one remove"),
    ("RD-0031", "unknown",    "C", "one_remove",  0, 0, 1, 0,
     "Supplies the contested yellow-wax residue record"),
    ("RD-0032", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Findspot only"),
    ("RD-0033", "unknown",    "C", "one_remove",  0, 0, 1, 0, "Findspot only"),
    ("RD-0034", "complete",   "D", "one_remove",  0, 1, 0, 0,
     "Museum-held but findspot not stated in the source read, and the twelve "
     "measured diameters reach this project through PUB-0019 rather than from "
     "the museum. Admitted for geometry, on which it is the single most "
     "important specimen, and excluded from mass, which is not recorded"),
    ("RD-0035", "complete",   "E", "direct",      0, 1, 0, 0,
     "PROVENANCE E: collection piece with no known archaeological context, "
     "published by its owner. Admitted for geometry because the measurements "
     "are direct and carefully made, and because it is the only specimen that "
     "tests EV043 against RD-0034. Mass not recorded"),
    ("RD-0036", "unknown",    "D", "two_removes", 0, 0, 0, 0,
     "REJECTED FOR GEOMETRY. Aperture pairs reach this project at two removes, "
     "PUB-0039 via PUB-0038 via PUB-0019, and no source states a tolerance"),
]

# ---------------------------------------------------------------------------
# Experiments
#
# Controlled trials, whether run by this project or reported in the literature.
# An experiment on a REPLICA tells us what a shape can do; it tells us nothing
# about what an archaeological object did. Results are kept here and in
# evidence_register, never in corpus_observations, and are never scored.
#
# Format: (exp_id, hypothesis_ids, objective, protocol, outcome, notes)
# ---------------------------------------------------------------------------
EXPERIMENTS = [
    ("EXP-0005", "H003; H008",
     "Test whether the number and diameter of the concentric rings engraved "
     "around each aperture are determined by the geometry of the face, and "
     "whether the two undecorated faces are undecorated for want of room.",
     "Analytical. For a regular dodecahedron of edge e, the pentagonal face has "
     "circumradius R = e/(2 sin 36) = 0.85065 e, which is the distance from "
     "face centre to knob, and apothem a = e/(2 tan 36) = 0.68819 e, which is "
     "the largest radius a complete circle can occupy before the pentagon edges "
     "cut it. Hence a/R = cos 36 = 0.80902. The annulus available for rings is "
     "the band between the aperture radius and a. Ring counts were then "
     "predicted at a uniform 2 mm pitch and compared with the two specimens for "
     "which per-face ring counts are published.",
     "THE CONSTRAINT: no complete ring can exceed 80.9 per cent of the distance "
     "from the face centre to the knobs, on any dodecahedron of any size. "
     "THE MODEL WORKS ON DECORATED FACES. Vienne (RD-0035, edge 24.70 mm "
     "derived from 55 mm face to face): the 14 mm apertures leave a 10.0 mm "
     "annulus, room for about 5 rings, and Duval records 4 and 6; the 22 mm "
     "apertures leave 6.0 mm, room for about 3, and he records 3. "
     "IT FAILS DECISIVELY ON THE UNDECORATED PAIR. The 23 and 24 mm apertures "
     "leave 5.5 and 5.0 mm, room for 2 to 3 rings, and both carry NONE. "
     "TWO WORKSHOP RULES, NOT ONE. Jublains (RD-0020, edge stated as 21 mm) "
     "carries three rings on all ten decorated faces regardless of aperture "
     "size, including a 22 mm aperture whose 3.45 mm annulus fits only about "
     "1.7 rings at the same pitch. Vienne varies the count and holds the pitch; "
     "Jublains holds the count and tightens the pitch.",
     "COMPUTED BY THIS PROJECT, August 2026; regular geometry assumed, and "
     "EV010 records that the objects are not regular, so the figures are "
     "nominal. TWO CONSEQUENCES. First, the zero ring count on the opposed "
     "pair is NOT explained by lack of space, which is quantitative support for "
     "the production-hole reading: those faces were skipped because they are "
     "casting artefacts, not because the engraver ran out of room. Second, "
     "because one workshop rule makes ring count constant and the other makes "
     "it a function of aperture diameter, THE RINGS CARRY NO INDEPENDENT "
     "LABELLING INFORMATION UNDER EITHER RULE - constant count distinguishes "
     "nothing, and count-determined-by-diameter is redundant with diameter. "
     "This bears directly on EV043 and on prediction P-0009."),

    ("EXP-0007", "H013; H014; C-15; C-17",
     "Test whether the decoration determines an orientation of the "
     "dodecahedron, as distinct from merely marking an axis.",
     "Group theory, verified by explicit construction. The rotation group of "
     "the dodecahedron was built as permutations of the twelve faces and "
     "confirmed to have order 60. The stabiliser of a single unordered opposed "
     "face-pair was then computed, and the stabiliser of a labelling in which "
     "that pair is distinguished and the other ten faces are identical.",
     "MARKING AN AXIS IS NOT DETERMINING AN ORIENTATION. Distinguishing one "
     "opposed pair out of six reduces the 60 rotations to 10: it fixes WHICH "
     "AXIS but leaves five rotations about that axis and a flip exchanging its "
     "two ends. "
     "IF THE REMAINING TEN FACES CARRY IDENTICAL DECORATION, nothing further "
     "is broken and all 10 orientations survive. That is the Jublains case "
     "(RD-0020), which carries three rings on every decorated face. "
     "ON SPECIMENS WHOSE FACES DIFFER, orientation is fully determined - but "
     "trivially, because the faces are individually distinguishable. Any "
     "sufficiently irregular object determines its own orientation in that "
     "sense, and it is not evidence of design. "
     "NOTHING OBSERVED DISTINGUISHES THE TWO ENDS OF THE AXIS. The two "
     "undecorated faces are equivalent to each other on every specimen "
     "recorded, so there is no up and no down.",
     "COMPUTED BY THIS PROJECT, August 2026, on the regular solid; EV010 "
     "records that the objects are not regular, which can only reduce symmetry "
     "further and therefore strengthens the trivial-determination point rather "
     "than the design point. THE CONCLUSION BEARS ON EV038 AND EV046: the "
     "decoration marks an axis at most, and on at least one specimen not even "
     "that much beyond the axis. Combined with the finding at EV046 that the "
     "marked axis is most probably a casting scar, there is no evidence that "
     "any dodecahedron was designed to be held in a particular orientation."),

    ("EXP-0006", "H003; H008; H006",
     "Test whether the concentric rings engraved around the apertures could "
     "encode the twelve signs of the zodiac, or any twelve-fold scheme, by "
     "assigning a distinct ring count to each face.",
     "Counting argument against the published ring counts. The observed range "
     "of ring counts anywhere in the corpus is 0 to 6 (PUB-0003 n 4, which "
     "records up to six and cites Guggenberger no 11 as carrying two to five; "
     "PUB-0017, 200 records 0, 3, 4 and 6 on one object). That is at most seven "
     "distinct values available to label twelve faces.",
     "NO. By the pigeonhole principle, twelve faces distributed over at most "
     "seven values force at least five faces to share a count with another "
     "face, on every specimen. Ring count alone can therefore never uniquely "
     "label twelve signs on any dodecahedron in the known corpus. "
     "THE ONE SPECIMEN WITH PUBLISHED PER-FACE COUNTS BEARS THIS OUT DIRECTLY. "
     "On Vienne (RD-0035) the seven published faces already repeat: faces 2, 3 "
     "prime and 5 prime all carry three rings, and faces 1 and 1 prime both "
     "carry none. Five faces are unpublished and cannot rescue it, because the "
     "repetition is already present. "
     "NOR DOES PAIRING RING COUNT WITH APERTURE DIAMETER RESCUE IT. On Vienne "
     "the rings conspicuously fail to separate the three faces that share a "
     "22 mm aperture, all of which carry three rings. THE RINGS ARE NOT WHOLLY "
     "REDUNDANT, HOWEVER, AND AN EARLIER VERSION OF THIS RECORD OVERSTATED "
     "THAT: faces 4 prime and 6 prime share a 14 mm aperture and carry FOUR "
     "and SIX rings respectively, so on that pair the rings do break a tie "
     "that diameter does not, and the space-filling model of EXP-0005 does not "
     "account for the difference either. The residual variation is real but "
     "small, and it falls far short of the twelve distinct values a twelve-fold "
     "scheme would need.",
     "COMPUTED BY THIS PROJECT, August 2026. THE DECISIVE COMPARISON IS "
     "EXTERNAL: a Roman dodecahedron bearing the zodiac does exist - the Geneva "
     "specimen (PUB-0037), solid lead coated with silver, with a sign of the "
     "zodiac ENGRAVED ON EACH FACE. When a Roman wanted the zodiac on a "
     "dodecahedron he cut the signs. The hollow knobbed objects carry rings "
     "instead, and rings cannot do that work. No hollow knobbed dodecahedron "
     "has ever been recorded with a zodiac sign, a month name, a numeral or any "
     "inscription."),

    ("EXP-0004", "C-17",
     "Test whether a suspended dodecahedron could level an aqueduct or set the "
     "gradient of a water channel, using a sight through a pair of opposite "
     "apertures against a gravity-fixed vertical.",
     "Analytical computation. (a) Elevations of the six face-pair axes for each "
     "mode of support, from EXP-0003. (b) Angular tolerance of a through-sight, "
     "taken as arctan((d_far - d_near) / 2L), where the beam admitted by the "
     "near aperture clears the far one. (c) Comparison with the gradients "
     "Roman aqueducts were actually built to.",
     "MARGINALLY ADEQUATE FOR THE CRUDEST PERMITTED GRADIENT, HOPELESS FOR REAL "
     "PRACTICE. A horizontal sight line IS available: hung from an edge, one "
     "face-pair axis lies at exactly 0 degrees. But the sight tolerance is set "
     "by the difference between paired apertures. The single closest pair in "
     "the corpus, 14.2 and 14.5 mm on Avenches over a 46.5 mm path, gives 0.18 "
     "degrees; typical pair differences of 2 to 4.5 mm give 1.15 to 2.58 "
     "degrees. Against Vitruvius's stated minimum gradient of half a foot per "
     "hundred feet (1:200, 0.2865 deg) the best pair on the best specimen is "
     "just sufficient and a typical pair is 4 to 9 times too coarse. Against "
     "gradients actually built - 1:3000 at Nimes, 1:4000 on parts of the Aqua "
     "Marcia, 1:20000 on the flattest surveyed stretch at Nimes - even the best "
     "pair is 10, 13 and 65 times too coarse respectively. The reason is "
     "baseline: levelling accuracy scales with the length of the instrument, "
     "and Vitruvius's chorobates is a bench of about twenty Roman feet, some "
     "120 times the 50 mm face-to-face path of a dodecahedron.",
     "COMPUTED BY THIS PROJECT, August 2026; no artefact examined. The "
     "gradient figures are standard values for the aqueducts named and were not "
     "verified against primary survey data by this project. NOTE THE HONEST "
     "SHAPE OF THE RESULT: this is not a flat refutation. The instrument could "
     "just about set the crudest gradient Vitruvius permits, using the best "
     "pair on the most precisely made specimen. It could not survey an "
     "aqueduct, and a Roman engineer with a chorobates had no reason to try."),

    ("EXP-0003", "C-15",
     "Test whether suspending a dodecahedron from a chosen knob and reading the "
     "solar altitude at which sunlight passes cleanly through a pair of "
     "opposite apertures - a shadowless disc of light inside the shadow - can "
     "index twelve dates in the year.",
     "Analytical computation. Dodecahedron vertices derived as the centroids of "
     "the faces of the dual icosahedron, verified by the requirement that each "
     "vertex be equidistant in angle from exactly three face normals (37.38 deg "
     "x 3). For each possible support - 20 knobs, 12 faces, 30 edge midpoints - "
     "the support direction is taken as vertical and the elevation above the "
     "horizontal of each of the six face-pair axes is computed. Reachability is "
     "then checked against solar noon altitude, 90 - latitude + declination, "
     "for declination between -23.44 and +23.44 degrees, at four corpus sites.",
     "THREE NEGATIVE RESULTS, ONE OF THEM DECISIVE FOR THE PROPOSAL AS STATED. "
     "(1) THE CHOICE OF KNOB CONVEYS NO INFORMATION. The dodecahedron is "
     "vertex-transitive, so all 20 knobs are geometrically equivalent and every "
     "one yields an identical configuration. There is nothing to choose. "
     "(2) Suspension from a knob yields only TWO distinct face-axis elevations, "
     "10.81 and 52.62 degrees, not twelve. Resting on a face yields 26.57 and "
     "90; hanging from an edge yields 0, 31.72 and 58.28. Across every possible "
     "support there are SEVEN distinct elevations in total. "
     "(3) Of those seven, only four are reachable by the noon sun - 26.57, "
     "31.72, 52.62 and 58.28 - and they are THE SAME FOUR at Arles, Jublains, "
     "Norton Disney and Corbridge, from 43.7 to 55 degrees north. Four "
     "elevations crossed twice a year gives eight calendar events, not twelve.",
     "COMPUTED BY THIS PROJECT, August 2026, and reproducible from first "
     "principles; no artefact was examined. AN EARLIER RUN OF THIS COMPUTATION "
     "WAS WRONG and is recorded here for transparency: it used an incompatible "
     "cyclic convention for the vertex coordinates and reported two distinct "
     "knob classes, which would have implied that knob choice mattered. The "
     "error was caught by checking that every vertex sits at equal angle to "
     "exactly three face normals, which the bad coordinates failed. "
     "LIMITATIONS: a regular dodecahedron is assumed, and EV010 shows the "
     "objects are irregular; irregularity would blur the elevations rather than "
     "multiply them. NOTE ALSO result (3) cuts against the distribution "
     "argument: an instrument giving identical readings from 43.7 to 55 degrees "
     "north is latitude-insensitive across the whole empire and had no reason "
     "to stay in the north-western provinces."),

    ("EXP-0002", "C-14",
     "Test whether a hollow dodecahedron can resolve twelve zodiac divisions "
     "by projecting sunlight through one aperture onto its interior, in the "
     "manner of the zodiac declination curves carried by Roman conical and "
     "hemispherical dials.",
     "Analytical computation, not physical trial. (a) Angles between the "
     "twelve face axes of a regular dodecahedron, from the dual icosahedron "
     "vertices. (b) Annual travel of the projected light patch on the interior "
     "wall, L*tan(46.88 deg), where L is the internal path length and 46.88 deg "
     "is the full annual swing of solar noon altitude. (c) Diameter of the "
     "patch, d + L*tan(0.53 deg), being the aperture image plus the solar "
     "penumbra. (d) Resolvable divisions = travel / patch.",
     "TWO INDEPENDENT NEGATIVE RESULTS. (a) The twelve face axes are separated "
     "by only three distinct angles: 63.435, 116.565 and 180 degrees. The "
     "smallest, 63.435 deg, is 1.35 times the ENTIRE 46.88 deg annual swing of "
     "solar noon altitude, so at any fixed site at most one face axis can ever "
     "align with the noon sun and no second axis can enter the band. Direct "
     "face-axis alignment therefore cannot index twelve dates. (b) For the "
     "projection reading, twelve divisions require an aperture-to-path ratio of "
     "L/d >= 12.5. Measured specimens give 3.9 to 5.6: Avenches 46.5/8.7 = 5.3 "
     "(5.4 divisions), Mainz 3 (4.0), Jublains 48/10.5 = 4.6 (4.7 divisions). "
     "Every measured specimen falls short by about a factor of two, resolving "
     "roughly four to six divisions rather than twelve.",
     "COMPUTED BY THIS PROJECT, August 2026. Reproducible from the measurements "
     "in the specimens table and standard solar geometry; no artefact was "
     "examined. LIMITATIONS: it assumes a regular dodecahedron, which EV010 "
     "shows the objects are not, and it takes L as the face-to-opposite-face "
     "distance. Neither assumption is favourable to the negative result - "
     "irregularity would worsen resolution, not improve it. NOTE the corollary: "
     "four to six divisions IS achievable, so a seasonal or solstitial reading "
     "is not excluded by resolution alone, only a twelve-fold one."),

    ("EXP-0001", "H003; H008",
     "Test whether a dodecahedron can act as a forming aid for standardised "
     "wax elements such as bullae securing cords on documents.",
     "3D-printed polylactic acid replica of external diameter c 65 mm. Wax "
     "mixture of approximately 80 per cent beeswax and 20 per cent pine resin "
     "by weight. Softened wax pressed within the tool around knotted cotton "
     "twine; ten tokens produced in one session; perimeter thickness measured "
     "on each.",
     "Perimeter thickness approximately 4.0 to 4.5 mm across all ten examples. "
     "The author reports consistent depth control independent of user "
     "variation, and attributes it to the knobs acting as spacers limiting "
     "compression.",
     "Reported in PUB-0041 (Lamb 2026, EXARC Journal 2026/2). NOT RUN BY THIS "
     "PROJECT and NOT REPLICATED HERE. CRITICAL LIMITATION: the trial used a "
     "3D-printed replica, so it demonstrates only that the SHAPE can perform "
     "the task. It reports no observation of any archaeological specimen and "
     "provides no evidence that any dodecahedron was ever used this way. A "
     "successful replica trial raises a hypothesis to testable; it does not "
     "support it. The hypothesis it proposes - a wax-forming tool - is NOT yet "
     "in the hypothesis set and has not been scored."),
]


# ---------------------------------------------------------------------------
# Published interpretations
#
# Conclusions drawn by published authors. They are recorded so that the
# project's reasoning can be compared against the literature, and they are
# NEVER scored: hdm_scores is built only from corpus_observations.
#
# Format: (evidence_id, category, statement, type, confidence,
#          relevant_hypotheses, primary_observable, source_id)
# ---------------------------------------------------------------------------
INTERPRETATIONS = [
    ("EI-0001", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 33): given that the "
     "overwhelming majority of dodecahedra derive from civilian contexts and "
     "that the distribution is geographically limited despite the mobility of "
     "Roman soldiers, a primary military purpose can be ruled out.",
     "Interpretation", "High", "H007", "EV025; EV031", "PUB-0003"),

    ("EI-0002", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 36, citing Thompson "
     "1970, 93-5): the suggested use as a distance-measuring device must be "
     "rejected, having been conclusively refuted.",
     "Interpretation", "High", "H002", "EV039; EV038", "PUB-0003"),

    ("EI-0003", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 37): there is "
     "nowadays fairly broad consensus that the purpose cannot be found without "
     "considering the symbolism of the shape, and it is often assumed to be "
     "some kind of ritual object, possibly used in divination, perhaps in "
     "combination with a light source.",
     "Interpretation", "Medium", "H003; H008", "EV025; EV032", "PUB-0003"),

    ("EI-0004", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 35-6): the position "
     "of the Gelduba dodecahedron immediately adjacent to a bone object "
     "suggests a functional connection between the two, and there may perhaps "
     "have been a temporary mounting of the dodecahedron upon a kind of handle "
     "passing through its pair of production holes.",
     "Interpretation", "Medium", "H001; H004; H008", "EV027; EV033", "PUB-0003"),

    ("EI-0005", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 40): the primary "
     "function of the knobs seems to be to provide support, stability and "
     "protection to the dodecahedron, indicating a purpose beyond decoration, "
     "and hints at a usage distinct from that of Roman dice, which never "
     "feature knobs.",
     "Interpretation", "Medium", "H003; H008", "EV008; EV009", "PUB-0003"),

    ("EI-0006", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 34, citing Hitchens "
     "2023 and Henig 2025): the Norton Disney specimen could have been placed "
     "on top of the pit in order to close it ritually, and may originate from "
     "a shrine.",
     "Interpretation", "Medium", "H003; H008", "EV025", "PUB-0003"),

    ("EI-0007", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Guggenberger and Leach 2025, 51-2): the "
     "dodecahedron's inspiration may have been the receptacle of all becoming "
     "in Plato's Timaeus, realised in abstract form, and it may have been used "
     "as a receptacle in theurgic divination by Gallo-Roman Druids and a wider "
     "circle of initiates. The authors state this is not yet proven.",
     "Interpretation", "Low", "H003; H008", "EV025; EV032", "PUB-0003"),

    ("EI-0009", "Archaeological Context",
     "AUTHOR INTERPRETATION (Guillier, Delage and Besombes 2008, para 62): "
     "depending on whether greater importance is given to the balance or to the "
     "dodecahedron, the Jublains building may have been the shop of a merchant "
     "or craftsman - a money changer, goldsmith, bronzesmith, or dealer in "
     "spices or precious materials - or else the den of a diviner or seer, the "
     "two not being incompatible.",
     "Interpretation", "High", "H002; H003; H008", "EV025; EV027", "PUB-0010"),

    ("EI-0010", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Duval 1981, 200): the two largest opposed "
     "openings of the Vienne dodecahedron have a periphery that appears less "
     "regularly cut than the others, as if worn by friction from a stick "
     "passing through both simultaneously. The author states that no conclusion "
     "can be drawn from the analysis of a single dodecahedron.",
     "Interpretation", "Medium", "H001; H004", "EV017; EV033", "PUB-0017"),

    ("EI-0011", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Sparavigna 2012): the common features of the "
     "analysed dodecahedra allow the conclusion that the object was probably a "
     "dioptron used as a coincidence rangefinder, with distance given by "
     "L = GH x B / (D - D'). The same author records, against her own thesis, "
     "that it does not seem that a standard or rule for these instruments "
     "existed, and that a Roman dodecahedron cannot have been used for sorting "
     "because it is a biased body.",
     "Interpretation", "Low", "H002", "EV004; EV005; EV039", "PUB-0019"),

    ("EI-0012", "Comparative Analysis",
     "AUTHOR INTERPRETATION (Sparavigna 2012, 4): the presence of wax inside a "
     "dodecahedron does not imply a candle holder, because Romans used wax "
     "tablets for writing and calculation, so wax may simply have been used by "
     "the owner.",
     "Interpretation", "Low", "H004", "EV023; EV024", "PUB-0019"),

    ("EI-0013", "Documentation",
     "AUTHOR STATEMENT OF METHOD (Duval 1981, 195-199): a comparative study of "
     "dodecahedra requires flat projections drawn to a single principle. Face 1 "
     "is the face with the largest opening; the object is set on the face "
     "opposite it; the remaining upper faces are numbered 2 to 6 "
     "anticlockwise viewed from above, in decreasing order of opening diameter; "
     "opposite faces take the numbers 1' to 6'; and the twenty vertices are "
     "lettered a-j and a'-j'. The author notes that the answer to whether any "
     "rhythm exists in the openings has never been given, nor even sought, for "
     "want of such records.",
     "Constraint", "High", "All", "EV004; EV005; EV010; EV039", "PUB-0017"),

    ("EI-0014", "Experimental Archaeology",
     "AUTHOR INTERPRETATION (Lamb 2026): Roman dodecahedra were forming aids "
     "for the production of standardised wax elements such as bullae used to "
     "secure cords on administrative documents. The author reports that the "
     "protruding knobs act as functional spacers limiting compression and "
     "ensuring consistent thickness, and that the variable apertures "
     "accommodate cords of varying thickness and allow finger access into the "
     "hollow interior for release.",
     "Interpretation", "Medium", "H003; H008", "EV008; EV004; EV023; EV024",
     "PUB-0041"),

    ("EI-0015", "Experimental Archaeology",
     "EXPERIMENTAL RESULT, REPLICA ONLY (Lamb 2026): ten wax tokens produced "
     "in one session with a 3D-printed replica of external diameter c 65 mm "
     "and a wax mixture of about 80 per cent beeswax and 20 per cent pine "
     "resin gave perimeter thicknesses of approximately 4.0 to 4.5 mm across "
     "all examples, which the author reports as consistent depth control "
     "independent of user variation.",
     "Experimental", "Medium", "H003; H008", "EV008", "PUB-0041"),

    ("EI-0016", "Documentation",
     "REASONING BY THIS PROJECT, NOT AN OBSERVATION. PUB-0003, 36 records that "
     "there is no contemporaneous description of the Gallo-Roman dodecahedron "
     "and not even a depiction. That silence is not uniform across the "
     "proposed functions, and the asymmetry is informative. Roman technical "
     "literature catalogues the equipment of some domains exhaustively and of "
     "others hardly at all: military equipment (Vegetius), agriculture "
     "(Columella, Palladius), architecture and surveying (Vitruvius, the "
     "Corpus Agrimensorum), water engineering with its calibrated pipe "
     "apertures (Frontinus), and traded commodities and craft wages "
     "(Diocletian's Price Edict of AD 301, some 1,200 entries, from the middle "
     "of the dodecahedron window and naming garments down to the birrus "
     "Britannicus). Provincial craft practice, Gaulish religion and domestic "
     "work are by contrast barely documented. Documentary silence therefore "
     "counts heavily against the domains that have surviving technical "
     "literature and hardly at all against those that do not. THIS PROJECT HAS "
     "NOT READ THOSE TREATISES and does not assert the individual absences "
     "from first-hand reading; the argument is offered as a structural one "
     "about where silence is and is not evidence.",
     "Constraint", "Medium", "All", "EV025; EV026; EV029", "PUB-0003"),

    ("EI-0017", "Comparative Analysis",
     "REASONING BY THIS PROJECT, NOT AN OBSERVATION. Frontinus describes the "
     "Roman calibrated water-pipe apertures (the quinaria system). It is the "
     "closest Roman analogue to a graded set of apertures used as a standard, "
     "and it is named, standardised and written down. The Gallo-Roman "
     "dodecahedron is none of those three. What a genuine Roman graded-aperture "
     "gauge looks like in the record is therefore known, and the dodecahedron "
     "does not look like it.",
     "Constraint", "Medium", "H002; H006; H011", "EV039", "PUB-0003"),

    ("EI-0008", "Documentation",
     "AUTHOR STATEMENT OF OPEN QUESTIONS (Guggenberger and Leach 2025, 52): to "
     "make further progress, archaeology must determine whether there is any "
     "trace of another substance inside or outside some dodecahedra, whether "
     "there are any microscopic signs of wear, and whether broken specimens "
     "were broken deliberately or accidentally.",
     "Constraint", "High", "All", "EV017; EV019; EV020; EV023; EV024", "PUB-0003"),
]


# ---------------------------------------------------------------------------
# Greiner/Guggenberger type attributions, from the reference catalogue
# (PUB-0023). Matched to this database by findspot, and only where the
# catalogue entry is UNIQUE for that findspot.
#
# DELIBERATELY NOT ASSIGNED:
#   RD-0022 Mainz 3      the catalogue of January 2021 lists Mainz 1, Mainz 2
#                        and Mombach but no Mainz 3, which was first published
#                        in 2025 as Guggenberger no 134. The keyword match to
#                        Mainz 1 (no 16) is wrong and is not made.
#   RD-0036 Carnuntum    the catalogue lists THREE Carnuntum specimens
#                        (nos 78, 79, 80) and the measurement chain behind
#                        RD-0036 does not say which was examined.
#   RD-0033 Deonica      not in the 2021 catalogue; published by Vujovic 2021.
# ---------------------------------------------------------------------------
GUGGENBERGER_TYPE = {
    "RD-0001": "1a?",
    "RD-0003": "6",
    "RD-0004": "1a",
    "RD-0006": "4",
    "RD-0007": "?",
    "RD-0009": "1a",
    "RD-0017": "5a",
    "RD-0018": "6?",
    "RD-0019": "1a",
    "RD-0020": "1a",
    "RD-0021": "1a",
    "RD-0024": "1a",
    "RD-0025": "1a",
    "RD-0026": "1a",
    "RD-0029": "5a",
    "RD-0031": "1a",
    "RD-0032": "1a",
    "RD-0034": "1a",
    "RD-0035": "1a",
    "RD-0038": "2a",
}
GUGGENBERGER_NUMBER = {
    
    "RD-0001": "118",
    "RD-0003": "115",
    "RD-0004": "119",
    "RD-0006": "4",
    "RD-0007": "59",
    "RD-0009": "120",
    "RD-0017": "62",
    "RD-0018": "61",
    "RD-0019": "69",
    "RD-0020": "98",
    "RD-0021": "29",
    "RD-0024": "20",
    "RD-0025": "21",
    "RD-0026": "68",
    "RD-0029": "60",
    "RD-0031": "10",
    "RD-0032": "92",
    "RD-0034": "86",
    "RD-0035": "58",
    "RD-0038": "75",
}

# ---------------------------------------------------------------------------
# Evidence clusters
#
# Scoring sums across variables as though each were an independent
# observation. Several are not: they restate one underlying fact in different
# terms, or rest on one sentence in one source. Summing them counts that fact
# once per variable.
#
# Variables sharing a cluster share a budget. The cluster contributes its
# single strongest cell rather than the sum of its cells, so one observation
# counts once however many variables express it.
#
# Cluster membership is a JUDGEMENT about shared evidential basis, not about
# shared topic, and each is justified below. Unclustered variables stand alone.
# ---------------------------------------------------------------------------
EVIDENCE_CLUSTERS = {
    # One sentence in PUB-0003, 45, reporting one statement from Guggenberger
    # 1999, expressed as four variables and scored four times, three of them
    # at Very High power. The largest single distortion in the analysis.
    "EV017": "wear",
    "EV018": "wear",
    "EV019": "wear",
    "EV020": "wear",

    # All three rest on the same published corpus size range of 4-10 cm
    # (PUB-0003, 31): that the objects are hand-sized, that they are too
    # variable to be interchangeable, and that they conform to no standard.
    "EV001": "corpus_size_range",
    "EV037": "corpus_size_range",
    "EV039": "corpus_size_range",

    # The same measured aperture diameters, read once as a distribution and
    # once as a relation between opposed pairs.
    "EV004": "aperture_metrics",
    "EV005": "aperture_metrics",

    # The same manufacturing evidence: casting quality and the production
    # holes are two readings of how these objects were made.
    "EV012": "casting",
    "EV013": "casting",

    # This project's own geometric reasoning about the same measurements,
    # expressed as four separate assessments. Already discounted as Derived,
    # but still summed four times.
    "EV033": "engineering_derived",
    "EV034": "engineering_derived",
    "EV035": "engineering_derived",
    "EV036": "engineering_derived",
}

def build_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.executescript(SCHEMA)

    cur.executemany(
        "INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?)",
        SOURCES
    )

    for row in read_csv("hypotheses.csv"):
        cur.execute(
            "INSERT INTO hypotheses(hypothesis_id, name) VALUES (?,?)",
            (row["HypothesisID"], row["Name"])
        )

    for row in read_csv("Evidence_Master_List_v1.csv"):
        cur.execute(
            "INSERT INTO evidence_variables VALUES (?,?,?,?,?,?,?,?)",
            (row["EvidenceID"],
             row["Evidence Variable"],
             row["Category"],
             row.get("Definition"),
             row.get("Unit/Type"),
             row.get("Source Type"),
             row.get("Discriminatory Power"),
             row.get("Most Relevant Hypotheses"))
        )

    for row in read_csv("evidence_register_v1.csv"):
        cur.execute(
            "INSERT INTO evidence_register VALUES (?,?,?,?,?,?,?)",
            (row["EvidenceID"],
             row["Category"],
             row["EvidenceStatement"],
             row["EvidenceType"],
             row["Confidence"],
             row["RelevantHypotheses"],
             row["PrimaryObservable"])
        )
        raw = row.get("RepresentativeSources", "")
        for label in [s.strip() for s in raw.split(";")]:
            sid = SOURCE_MAP.get(label)
            if sid:
                cur.execute(
                    "INSERT OR IGNORE INTO evidence_sources VALUES (?,?)",
                    (row["EvidenceID"], sid)
                )

    cur.executemany(
        "INSERT INTO hpm(hypothesis_id, ev_id, prediction, rationale) VALUES (?,?,?,?)",
        HPM_DATA + HPM_H009 + HPM_H010 + HPM_H011 + HPM_H012 + HPM_H013 + HPM_H014
    )

    cur.executemany(
        "INSERT INTO hpm_readings(hypothesis_id, ev_id, direction, rationale) "
        "VALUES (?,?,?,?)",
        HPM_READINGS
    )

    # Specimens: one row per physical artifact
    # Columns: rd_id, specimen_name, findspot, country, roman_province,
    #   context_category, date_from, date_to, museum_name, museum_city,
    #   museum_country, inventory_number, material, manufacturing_method,
    #   height_mm, width_mm, max_diameter_mm, weight_g, wall_thickness_mm,
    #   knob_diameter_mm, hole_01..12_mm, decoration_type, decoration_desc,
    #   wear_notes, associated_finds, primary_source_id, confidence,
    #   nouwen_number, guggenberger_number, notes
    SPECIMENS = [
        # RD-0001: Much Hadham, Hertfordshire (PAS BH-692011)
        # Complete specimen; discovered 22 Aug 2018 by metal detector
        ("RD-0001", "Much Hadham dodecahedron",
         "Much Hadham, East Hertfordshire", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         None, None, None,                 # museum: returned to finder
         "PAS:BH-692011",                  # inventory_number used for PAS ID
         "Copper alloy", "Cast",
         None, None, 82.0, 247.23, 3.0, 9.5,  # height, width, max_diam, weight, wall, knob_avg
         None, None, None, None, None, None,   # holes 1-6
         None, None, None, None, None, None,   # holes 7-12 (individual unknown)
         "Geometric",
         "Faint double-lined circumferential border surrounding each hole",
         "Patchy mid-green and brown patina; pitting and gouging on several faces; "
         "abrasion around base of most knobs; one knob partially detached but attached",
         None, "PUB-0006", "B", None, None,
         "Smallest hole 13.7mm, largest 20mm; all holes bevelled; "
         "possibly the most complete specimen known from Britannia per PAS record"),

        # RD-0002: Fridaythorpe, East Riding of Yorkshire (PAS YORYM-41CD72)
        # Incomplete; 6 complete + parts of 5 further faces; discovered 5 Dec 2008
        ("RD-0002", "Fridaythorpe dodecahedron",
         "Fridaythorpe, East Riding of Yorkshire", "United Kingdom", "Britannia",
         "Unknown", 1, 400,
         None, None, None,
         "PAS:YORYM-41CD72",
         "Copper alloy", "Cast",
         None, 82.4, None, 270.0, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None,
         "Some holes surrounded by incised pentagonal line",
         "One knob broken off (loose); metal mid greyish-green; rough broken edges",
         None, "PUB-0006", "B", None, None,
         "Incomplete: 6 complete faces + half of 5 more; "
         "interior crudely cast; holes of different sizes irregularly cut; "
         "face width ~42mm, face length ~38mm"),

        # RD-0003: Compton, Surrey (PAS SUR-729950)
        # Fragment: two joining pieces forming most of one face + parts of 5 adjacent
        # Discovered 1 Apr 2009 by metal detector
        ("RD-0003", "Compton dodecahedron fragment",
         "Compton, Guildford, Surrey", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         None, None, None,
         "PAS:SUR-729950",
         "Copper alloy", "Cast",
         None, None, None, 82.0, None, 13.5,  # weight=82g is FRAGMENT weight
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None,
         None,
         None, "PUB-0006", "B", None, None,
         "Fragment weight 82g; one complete face hole ~15.75mm; "
         "no additional decoration; interior roughcast; "
         "only dodecahedron known from southern England outside London per PAS 2009"),

        # RD-0004: Stockbridge, Hampshire (PAS HAMP-CE1119)
        # Fragment: 2 complete faces + remains of 6; metal detector find
        ("RD-0004", "Stockbridge dodecahedron fragment",
         "Stockbridge, Test Valley, Hampshire", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         "Hampshire Cultural Trust", "Winchester", "United Kingdom",
         "PAS:HAMP-CE1119; HCT:WINCM 629",
         "Copper alloy", "Cast",
         29.1, 48.7, None, 46.79, 3.7, None,  # height=depth, width, weight are FRAGMENT
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Raised rim with sunken surround and inner ring around each hole",
         "Raised rim around perforations; sunken circular area; raised ring closer to hole than edge",
         "Metal rather pitted and worn; dark to mid-green patina",
         None, "PUB-0006", "B", None, None,
         "Fragment: 2 complete faces + ~half of 6 more; "
         "face dimension 29-30mm corner to side-centre; "
         "holes: 10-11mm (complete faces), 18.3mm (adjacent face)"),

        # RD-0005: Norton Disney, Lincolnshire (Tipper 2024 / NDAG excavation)
        # Complete; discovered June 2023 in archaeological excavation
        ("RD-0005", "Norton Disney dodecahedron",
         "Norton Disney, Lincolnshire", "United Kingdom", "Britannia",
         "Settlement", 43, 410,
         "The Collection (Lincoln Museum)", "Lincoln", "United Kingdom",
         None,
         "Copper alloy", "Cast",
         None, None, 80.0, 245.0, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None,
         "No wear; described as completely undamaged with no evidence of any wear at all",
         None, "PUB-0008", "C", None, "132",
         "Found June 2023 by NDAG in trench 4, large pit; near Roman villa excavated 1935; "
         "XRF: Cu 75%, Sn 7%, Pb 18% (Gerry McDonnell); "
         "3D scanned (Univ. Lincoln); sent to Newcastle Univ. for further analysis; "
         "33rd dodecahedron found in England; first from East Midlands"),

        # RD-0006: Tongeren, Belgium (Wikipedia / Gallo-Roman Museum)
        # Provenance: Leopoldwal, Tongeren, 1939; museum inv. 4002
        ("RD-0006", "Tongeren dodecahedron",
         "Leopoldwal, Tongeren (Atuatuca Tungrorum)", "Belgium", "Gallia Belgica",
         "Unknown", 150, 400,
         "Gallo-Roman Museum", "Tongeren", "Belgium",
         "4002",
         "Bronze (copper alloy)", "Cast",
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0004", "E", None, None,
         "Source: Wikipedia image caption; inv. 4002; "
         "findspot Leopoldwal 1939; measurements not available from this source"),

        # RD-0007: Aston, Hertfordshire (SAL minutes 1739)
        # First recorded dodecahedron; field find exhibited to Society of Antiquaries
        ("RD-0007", "Aston (Hertfordshire) dodecahedron",
         "Aston, Hertfordshire", "United Kingdom", "Britannia",
         "Unknown", None, None,
         None, None, None,  # current location unknown from this source
         None,
         "Bronze", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0007", "A", None, "59",
         "First recorded dodecahedron; exhibited at SAL meeting 28 June 1739 by George North; "
         "described as twelve-sided bronze object from a field in Aston, Hertfordshire; "
         "measurements and current location not stated in archival record"),

        # RD-0008: Near Market Lavington, Wiltshire (PAS WILT-37C5E1)
        # Fragment: one complete edge + two cylindrical lugs + four short edge sections
        # Discovered 2014 by metal detector; date range AD 100-300 (tighter than most)
        ("RD-0008", "Near Market Lavington dodecahedron fragment",
         "Near Market Lavington, Wiltshire", "United Kingdom", "Britannia",
         "Unknown", 100, 300,
         "Wiltshire Heritage Museum", "Devizes", "United Kingdom",
         "PAS:WILT-37C5E1; WHM:1591",
         "Copper alloy", "Cast",
         None, 26.15, None, 27.13, None, 13.05,  # width and knob from fragment
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None,
         None,
         None, "PUB-0006", "B", None, None,
         "Fragment: one edge + 2 cylindrical lugs (13.05mm and 12.40mm dia) + 4 short edge sections; "
         "fragment measures 37.65 x 26.15 x 21.05mm; "
         "interior concave and crudely cast; exterior relatively smooth"),

        # RD-0009: Stamford Bridge, East Riding of Yorkshire (PAS YORYM-E841F9)
        # Very small fragment: one complete edge + two spherical lugs
        # Discovered by metal detector; museum ref YMT: E05656
        ("RD-0009", "Stamford Bridge dodecahedron fragment",
         "Stamford Bridge, East Riding of Yorkshire", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         "Yorkshire Museum", "York", "United Kingdom",
         "PAS:YORYM-E841F9; YMT:E05656",
         "Copper alloy", "Cast",
         7.2, 18.7, None, 3.8, None, None,  # height=thickness, width from fragment
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Incised",
         "Double incised border around two visible hole edges (= two concentric rings)",
         "Metal worn; mid-green patina",
         None, "PUB-0006", "B", None, None,
         "Tiny fragment: one edge + 2 spherical lugs; edges of 3 circles visible; "
         "29.5 x 18.7 x 7.2mm; interior hollow, undecorated"),

        # RD-0010: Yelnow, Bedford (PAS PUBLIC-959804)
        # Very small fragment: one corner only (3 faces converge + spherical knob)
        # Discovered 12 Feb 2011, depth 0-10cm, by metal detector
        ("RD-0010", "Yelnow dodecahedron fragment",
         "Yelnow, Bedford", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         None, None, None,  # returned to finder
         "PAS:PUBLIC-959804",
         "Copper alloy", "Cast",
         8.7, 10.0, None, 1.67, None, None,  # height and width from fragment
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Incised",
         "Incised grooved decoration on two surviving face portions, forming two rings "
         "as outer boundary of pentagonal faces",
         None,
         None, "PUB-0006", "B", None, None,
         "Smallest PAS fragment: 12.5 x 10 x 8.7mm; one corner where 3 faces meet; "
         "single spherical knob intact; depth of discovery 0-10cm"),

        # RD-0011: Llandow, Vale of Glamorgan, Wales (PAS NMGW-063819)
        # Fragment: one complete edge, two knops, partial faces including two opposing face holes
        # XRF: Cu, Sn, trace Fe, Pb (qualitative); museum ref NMWPA 2024.110.5
        # KEY OBSERVATION: two opposing holes of very different diameters (9.4mm vs 22.6mm)
        ("RD-0011", "Llandow dodecahedron fragment",
         "Llandow, Vale of Glamorgan", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         "National Museum Wales", "Cardiff", "United Kingdom",
         "PAS:NMGW-063819; NMWPA:2024.110.5",
         "Copper alloy", "Cast",
         11.6, 24.5, None, 7.73, 1.1, 6.0,  # depth, width, wall_thickness, knob
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Incised",
         "Smaller face (9.4mm hole): circumferential groove at aperture edge + two concentric "
         "grooves on outer margin; larger face (~22.6mm hole): crudely finished, no decoration",
         None,
         None, "PUB-0006", "B", None, None,
         "Two opposing faces preserved: 9.4mm and ~22.6mm holes; stark size difference; "
         "knop: 6.0 x 5.7mm high, neck 4.5mm; XRF: Cu, Sn, trace Fe, Pb (qualitative); "
         "dark blackish-green patina with lighter green patches"),

        # RD-0012: Alveston, South Gloucestershire (PAS GLO-9EE34F)
        # Tiny fragment: single corner/knob only
        # Object certainty: 'Possibly' (uncertain identification)
        # Date range AD 100-300; interior crudely cast; exterior smooth
        ("RD-0012", "Alveston dodecahedron fragment",
         "Alveston, South Gloucestershire", "United Kingdom", "Britannia",
         "Unknown", 100, 300,
         None, None, None,
         "PAS:GLO-9EE34F",
         "Copper alloy", "Cast",
         None, 20.0, None, 34.51, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None,
         None,
         None, "PUB-0006", "B", None, None,
         "Object certainty: 'Possibly' dodecahedron; one globular knob + short corner sections; "
         "25 x 20 x 36mm; weight 34.51g; interior concave and crudely finished; "
         "exterior relatively smooth"),

        # RD-0013: Minting, East Lindsey, Lincolnshire (PAS LIN-F437DA)
        # FOUR SEPARATE CORNER FRAGMENTS from one probable specimen; plough damage
        # Fragment 1: L33.50mm, knob 14.28mm, plate 3.33mm, wt 20.37g
        # Fragment 2: L27.61mm, knob 13.92mm, plate 3.55mm, wt 17.41g
        # Fragment 3: L26.77mm, knob 13.46mm, plate 3.26mm, wt 12.01g
        # Fragment 4: L27.91mm, knob 14.01mm, plate 3mm,    wt 16.63g
        # Total weight: 66.42g; object certainty 'Probably'
        ("RD-0013", "Minting dodecahedron fragments",
         "Minting, East Lindsey, Lincolnshire", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         None, None, None,
         "PAS:LIN-F437DA",
         "Copper alloy", "Cast",
         None, None, None, 66.42, 3.29, 13.92,  # weight=all 4 fragments; wall=avg; knob=avg
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None,
         "Iron corrosion on underside of knobs in fragments 1 and 4; plough damage on all",
         None, "PUB-0006", "B", None, None,
         "Object certainty: 'Probably' dodecahedron; 4 separate corner fragments; "
         "knob diameters: 14.28, 13.92, 13.46, 14.01mm (very consistent); "
         "plate thickness: 3.33, 3.55, 3.26, 3.0mm; "
         "found nearby LIN-8D3A01; mid-green patina with brown patches"),

        # RD-0014: Potterspury, West Northamptonshire (PAS NARC1474)
        # Fragment: V-shaped piece (one edge + two corners); cast-in-one-piece
        # Discovery: 2000-2001, metal detector; "bun feet" knobs
        ("RD-0014", "Potterspury dodecahedron fragment",
         "Potterspury, West Northamptonshire", "United Kingdom", "Britannia",
         "Unknown", 43, 410,
         None, None, None,
         "PAS:NARC1474",
         "Copper alloy", "Cast",
         None, 17.74, None, 4.33, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Incised",
         "Multiple incised concentric circles on two surviving face portions",
         None,
         None, "PUB-0006", "B", None, None,
         "Fragment: V-shaped cross-section, one edge + two corners; "
         "two small spherical knobs resembling bun feet; "
         "30.14 x 17.74mm; cast-in-one-piece construction noted"),

        # RD-0015: Couthuin or Bassenge, Liege province, Belgium (Musee Curtius / KIK-IRPA)
        # 4th-century specimen; bronze and lead alloy; diameter 44mm
        # Provenance uncertain: Couthuin (Heron commune) or Bassenge (both Liege province)
        ("RD-0015", "Couthuin/Bassenge dodecahedron",
         "Couthuin or Bassenge, Liege province", "Belgium", "Gallia Belgica",
         "Unknown", 301, 399,
         "Musee Curtius", "Liege", "Belgium",
         "I.7108",
         "Bronze and lead", "Cast",
         None, None, 44.0, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0011", "B", None, None,
         "KIK-IRPA object number 10140871; inv. I.7108; "
         "provenance: 'Couthuin ou Bassenge' (Liege province); "
         "dated AD 301-399 per KIK-IRPA record; alloy: bronze and lead; "
         "CC0 metadata license"),

        # RD-0016: British Isles, location unknown (BM 1878,0311.48)
        # Object certainty: '?' in BM catalogue; donated via Sir Augustus Wollaston Franks
        # Previous owners: Rev. Dr William Sparrow Simpson; Frederick Bousfield
        ("RD-0016", "British Museum dodecahedron (1878)",
         "British Isles (exact location unknown)", "United Kingdom", None,
         "Unknown", None, None,
         "British Museum", "London", "United Kingdom",
         "1878,0311.48",
         "Copper alloy", None,
         None, None, 56.4, 39.83, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0012", "B", None, None,
         "BM registration 1878,0311.48; object certainty marked '?' in BM catalogue; "
         "aperture diameter range 12.45-17.73mm; "
         "donated by Sir Augustus Wollaston Franks; "
         "previous owners: Rev. Dr W.S. Simpson; Frederick Bousfield; "
         "not on display"),

        # RD-0017: Fishguard, Pembrokeshire, Wales (BM 1924,0411.1)
        # Exceptionally large specimen: 127.71mm diameter, 553.20g
        # Purchased from Thomas James 1924; referenced in Roman Britain guide 1964
        ("RD-0017", "Fishguard dodecahedron",
         "Fishguard, Pembrokeshire", "United Kingdom", "Britannia",
         "Unknown", None, None,
         "British Museum", "London", "United Kingdom",
         "1924,0411.1",
         "Copper alloy", None,
         None, None, 127.71, 553.2, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0012", "B", None, None,
         "BM registration 1924,0411.1; among the largest known Roman dodecahedra at 127.71mm; "
         "aperture diameter range 27.67-40.55mm; "
         "purchased from Thomas James 1924; "
         "reference: Roman Britain 1964 Guide p.78, fig.40.5; not on display"),

        # RD-0018: Corbridge Roman town (Corstopitum), Northumberland (English Heritage)
        # At Corbridge Roman Museum; referenced in Allason-Jones & Miket 1984
        # No measurements available from accessible sources
        ("RD-0018", "Corbridge dodecahedron",
         "Corbridge Roman town (Corstopitum), Northumberland", "United Kingdom", "Britannia",
         "Military", None, None,
         "Corbridge Roman Museum (English Heritage)", "Corbridge", "United Kingdom",
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0013", "C", None, None,
         "Displayed at Corbridge Roman Museum; confirmed via English Heritage / Google Arts & Culture; "
         "referenced in Allason-Jones & Miket 1984 and multiple PAS records (BH-692011, YORYM-41CD72); "
         "no measurements available from accessible online sources"),

        # RD-0019: South Shields Roman fort (Arbeia), Tyne and Wear (secondary citation via PAS)
        # Accession 1923.13 at Great North Museum / Arbeia; military context
        # Face measurements from secondary citation in PAS YORYM-41CD72
        ("RD-0019", "South Shields (Arbeia) dodecahedron",
         "South Shields Roman fort (Arbeia), Tyne and Wear", "United Kingdom", "Britannia",
         "Military", None, None,
         "Great North Museum", "Newcastle upon Tyne", "United Kingdom",
         "1923.13",
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0009", "D", None, None,
         "Accession 1923.13; found at South Shields Roman fort (Arbeia); "
         "face width 52mm, face length 48mm per museum website cited in PAS YORYM-41CD72; "
         "Allason-Jones & Miket 1984 no. 3.741; military site context confirmed"),

        # RD-0020: Jublains (Noeodunum), Mayenne, France (Guillier, Delage & Besombes 2008)
        # THE ONLY KNOWN SPECIMEN FROM A CONTROLLED ARCHAEOLOGICAL EXCAVATION
        # Found at the edge of the Roman thermal baths complex; Gallia Lugdunensis
        # Measurements not accessible from available online sources; paper behind paywall
        # CORRECTED IN BATCH 003 after direct consultation of PUB-0010.
        # Batch 001 recorded this specimen as a baths-context find because the
        # excavation lay alongside the thermae. The report shows the object came
        # from the burnt destruction layer F1058 of a small commercial building
        # with a cellar on Street 8, not from the baths. Measurements added.
        ("RD-0020", "Jublains (Noviodunum) dodecahedron",
         "Jublains (Noviodunum), 'Impasse Romaine', Mayenne - destruction layer "
         "F1058 of a small building with cellar on ancient Street 8, at the "
         "junction of Cardo A and Decumanus 8, adjoining the thermae",
         "France", "Gallia Lugdunensis",
         "Settlement", 200, 250,
         "Musee archeologique de Jublains", "Jublains", "France",
         None,
         "Copper alloy (bronze?)", "Lost-wax cast, then carefully finished",
         59.0, None, 74.0, 81.0, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Concentric circles",
         "Ten faces have a circular opening underlined by concentric circles "
         "engraved in the metal; the two remaining faces carry no concentric "
         "circles and have oval openings",
         "Intact apart from a barely visible crack on one edge",
         "Trebuchet (precision balance): complete beam 225 mm weighing 20 g, "
         "with two pans of 59x52x16 mm (12 g) and 49x54x17 mm (11 g), from the "
         "same destruction layer",
         "PUB-0010", "A", None, "98",
         "PUB-0010, 269-289. THE ONLY DODECAHEDRON FROM A SEALED, DATED, "
         "STRATIFIED CONTEXT. Height 59 mm as it stands but only 48-52 mm face "
         "to face; maximum diameter 74 mm; 81 g; twelve pentagonal faces of "
         "21 mm edge; ten circular openings of 10.5-22 mm; two opposed oval "
         "openings of 21x26 mm; a small ball of about 5-6 mm at each vertex, "
         "soldered to the body. Knob diameter and individual hole diameters "
         "left NULL because the report gives ranges, not per-face values; the "
         "ranges are recorded as observations. Per-face diameters read off "
         "PUB-0010 fig 12 by PUB-0019 are recorded as separate D-grade "
         "observations and deliberately NOT merged into this A-grade row."),

        # RD-0021: Arles (Arelate), Bouches-du-Rhone, France (Wikidata Q62511455 / Commons)
        # Found 1939 at the Roman thermae (baths) of Arelate; Musee de l'Arles antique
        # SECOND BATHS-CONTEXT SPECIMEN alongside Jublains (RD-0020)
        # Primary publication: Benoit 1957 (OGAM 9: 104-114) — not yet accessed
        ("RD-0021", "Arles (thermae) dodecahedron",
         "Arelate (Arles), thermae, Bouches-du-Rhone", "France", "Gallia Narbonensis",
         "Civilian", None, None,
         "Musee departemental de l'Arles antique", "Arles", "France",
         "X-37086",
         "Bronze", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0014", "C", None, None,
         "Wikidata Q62511455; Commons CC-BY-SA photo by Rama 2019; "
         "discovered 1939 at Roman thermae of Arelate (Arles); "
         "primary publication: Benoit 1957 OGAM 9: 104-114 (not yet accessed); "
         "3rd century AD; Gallia Narbonensis; "
         "PATTERN: second baths-context specimen alongside Jublains (RD-0020)"),

        # ===================================================================
        # Batch 002 - specimens documented in Guggenberger & Leach 2025
        # (PUB-0003). These are continental and context-bearing finds that
        # directly reduce the British / metal-detector bias of batch 001.
        # Guggenberger catalogue numbers are given in guggenberger_number.
        # ===================================================================

        # RD-0022: "Mainz 3", Guggenberger no 134. Previously unpublished;
        # published for the first time in PUB-0003, 36 fig 4, with full
        # measurements taken by the cataloguer. Findspot NOT recorded - the
        # object is known only from a collection, so findspot stays unknown.
        ("RD-0022", "Mainz 3 dodecahedron",
         "Unknown (ex Henryk Klunder collection, Mainz)", "Unknown", None,
         "Unknown", None, None,
         "Private collection", "Winterthur", "Switzerland",
         None,
         "Copper alloy", "Cast",
         None, None, 55.0, 246.0, 1.5, 5.0,
         # hole_01..12: one pair 15.0/17.0, a second pair 14.0/15.0,
         # remaining eight holes only given as a range c 10.0-12.5 mm -> NULL
         15.0, 17.0, 14.0, 15.0, None, None,
         None, None, None, None, None, None,
         "Ring-and-dot",
         "All faces carry five ring-and-dot motifs; Greiner/Guggenberger type 2a",
         None,
         None, "PUB-0003", "B", None, "134",
         "PUB-0003, 36 fig 4. Complete. Diameter 5.5 cm face to opposite face "
         "without knobs. Eight remaining holes stated only as a range "
         "(c 1.0-c 1.25 cm) and therefore left NULL rather than estimated. "
         "Only fully measured specimen added in batch 002."),

        # RD-0023: Gelduba / Gellep, Guggenberger no 11
        ("RD-0023", "Gelduba (Gellep) grave dodecahedron",
         "Gelduba (Krefeld-Gellep), west of the Rhine", "Germany", "Germania inferior",
         "Grave", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         # the two production holes are recorded: 24.0 and 23.0 mm
         24.0, 23.0, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         "Bone object, length c 150 mm, diameter c 30 mm, immediately adjacent; "
         "richly furnished grave of a woman who died around AD 350",
         "PUB-0003", "C", None, "11",
         "PUB-0003, 35-6 and n 33-4. Grave of a wealthy woman, d c AD 350. "
         "The adjacent bone object ('rod') was in very poor condition, was not "
         "preserved, and is known only from a drawing of the grave. "
         "Production holes 2.4 cm and 2.3 cm."),

        # RD-0024: Pfofeld, Guggenberger no 20
        ("RD-0024", "Pfofeld dodecahedron",
         "Pfofeld, Roman Limes (palisade trench near a watchtower)", "Germany",
         "Raetia",
         "Military", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         "Bronze statuette of Mercury as Hermes-Thoth, found in the same area",
         "PUB-0003", "C", None, "20",
         "PUB-0003, 35 and n 30 (citing Winkelmann 1933, 137-8 tab 16; "
         "Guggenberger 1999, 20, 178). Listed by PUB-0003 n 18 among find "
         "contexts with plausible sacred connections despite the limes location."),

        # RD-0025: Schwarzenacker, Guggenberger no 21
        ("RD-0025", "Schwarzenacker dodecahedron",
         "Schwarzenacker, urban Gallo-Roman cult precinct", "Germany",
         "Germania superior",
         "Temple", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "21",
         "PUB-0003, 35 and n 31 (citing Kolling 1993, 124). Found 'near' the "
         "sacrificial shafts of an urban Gallo-Roman cult precinct; the source's "
         "quotation marks around 'near' are preserved as stated proximity only."),

        # RD-0026: Lydney Park, Guggenberger no 68
        ("RD-0026", "Lydney dodecahedron fragment",
         "Lydney Park, Gloucestershire (temple complex of Nodens)",
         "United Kingdom", "Britannia",
         "Temple", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "68",
         "PUB-0003, 34 and n 28 (citing Wheeler and Wheeler 1932, 86 fig 20). "
         "Fragmented. From the site of the temple complex of the local god "
         "Nodens, but PUB-0003 states the exact find context is unknown."),

        # RD-0027: Severn estuary / Gloucester cache, Guggenberger no 122
        ("RD-0027", "Severn estuary (Gloucester) dodecahedron fragment",
         "Southern side of the Severn estuary, south-west of Gloucester",
         "United Kingdom", "Britannia",
         "Hoard", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         "Part of a cache identified as originating from a temple, "
         "perhaps the temple of Diana at Gloucester",
         "PUB-0003", "C", None, "122",
         "PUB-0003, 34 and n 27 (citing Coombe and Henig 2020, 234, 238 fig 9, "
         "259-60). Fragmented. Temple attribution of the cache is the cited "
         "authors' identification, not a stratigraphic observation."),

        # RD-0028: north of Paris, Guggenberger no 110
        ("RD-0028", "Paris-region dodecahedron",
         "North of Paris (modest Gallo-Roman domestic structure)", "France",
         "Gallia Lugdunensis",
         "Civilian", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         "Bronze statuette of a goddess (Juno?) one metre away",
         "PUB-0003", "C", None, "110",
         "PUB-0003, 35 and n 29 (citing Berton 2007). Metal-detector find "
         "inside a 'modest Gallo-Roman domestic structure'. Deity "
         "identification as Juno is queried in the source and is preserved "
         "with its question mark."),

        # RD-0029: Carmarthenshire, Guggenberger no 60
        ("RD-0029", "Carmarthenshire dodecahedron",
         "Carmarthenshire", "United Kingdom", "Britannia",
         "Hoard", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "60",
         "PUB-0003, 35 fig 3 (photo, SAL). CONFLICT: PUB-0003 n 16 lists "
         "no 60 among finds from cities or other settlements and n 21 lists "
         "no 60 among coin or bronze hoards. Both classifications preserved; "
         "context_category set to Hoard as the more specific of the two."),

        # RD-0030: Bachem, Guggenberger no 5
        ("RD-0030", "Bachem grave dodecahedron",
         "Bachem", "Germany", "Germania inferior",
         "Grave", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         "Richly furnished grave assemblage",
         "PUB-0003", "C", None, "5",
         "PUB-0003, 35 and n 32 (citing Barthel 1909, 94; Nouwen 1993, 31-2, 35; "
         "Guggenberger 1999, 152, 154, 163-4). One of three dodecahedra from "
         "richly furnished graves. PUB-0003 n 13 notes the dating is uncertain "
         "and may be 2nd century."),

        # RD-0031: Feldberg, Guggenberger no 10
        ("RD-0031", "Feldberg dodecahedron",
         "Feldberg Roman fort", "Germany", "Germania superior",
         "Military", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "10",
         "PUB-0003, 45 and n 103, n 105. Found 1892. Recorded as having traces "
         "of yellow wax; PUB-0003 states explicitly that this observation may "
         "not be fully reliable (Guggenberger 1999, 61-2, 144, 162). Listed by "
         "PUB-0003 n 17 among military-camp finds. Dating uncertain, possibly "
         "2nd century (n 13). ONLY RESIDUE OBSERVATION IN THE CORPUS."),

        # RD-0032: Brigetio, Guggenberger no 92 - easternmost find
        ("RD-0032", "Brigetio dodecahedron",
         "Brigetio, Pannonia", "Hungary", "Pannonia superior",
         "Unknown", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "92",
         "PUB-0003, 32. Easternmost known find. Recorded here to document the "
         "outer limit of the distribution; no measurements available."),

        # RD-0033: Deonica, Guggenberger no 130
        ("RD-0033", "Deonica dodecahedron",
         "Deonica, Moesia superior", "Serbia", "Moesia superior",
         "Unknown", None, None,
         None, None, None,
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0003", "C", None, "130",
         "PUB-0003, 32 and n 11 (citing Vujovic 2021). Outlying south-eastern "
         "find; no measurements available."),


        # ===================================================================
        # Batch 005 - museum collection records located by search, Aug 2026
        # ===================================================================
        ("RD-0037", "Louvre dodecahedron",
         "France (?), attributed to Gaul (?)", "France", None,
         "Unknown", None, None,
         "Musee du Louvre", "Paris", "France",
         "ED 4271; INV 2699; Br 1602",
         "Bronze", "Hollow cast, with soldered knobs",
         71.0, 82.0, 85.0, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Concentric circles",
         "Ten faces decorated with concentric circles of varying size; two "
         "faces remain smooth. Knobs attached by soldering",
         "Bronze surface shows corrosion",
         None, "PUB-0044", "B", None, None,
         "Purchased 1825 from the Durand collection. Height 7.1 cm between the "
         "smooth faces including the feet, 6.2 cm without; width 8.2 cm; depth "
         "8.5 cm. No weight recorded. Not currently on display. THE MUSEUM'S "
         "OWN PHRASE 'height between the smooth faces' implies the two "
         "undecorated faces are opposite one another, which corroborates the "
         "marked-axis observation independently of PUB-0010."),

        ("RD-0038", "Elst (Overbetuwe) dodecahedron",
         "Elst, Overbetuwe, Gelderland", "Netherlands", "Germania inferior",
         "Unknown", 1, 300,
         "Rijksmuseum van Oudheden", "Leiden", "Netherlands",
         None,
         "Bronze", None,
         75.0, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0045", "C", None, None,
         "FIRST NETHERLANDS SPECIMEN IN THE DATABASE. Donated November 1876. "
         "Height 7.5 cm. Museum dating given as 1-300 AD, which is EARLIER "
         "than the corpus window of c AD 200-400 recorded at EV029; museum "
         "period ranges are commonly loose and this is recorded as a conflict "
         "rather than as a correction. SOURCE CAVEAT: the museum page returned "
         "HTTP 403 and these values come from a search-engine extract of it, "
         "not from the page itself."),

        ("RD-0039", "MAN68333 (Reims?) dodecahedron",
         "Reims (?), Marne", "France", "Gallia Belgica",
         "Unknown", None, None,
         "Musee d'Archeologie nationale", "Saint-Germain-en-Laye", "France",
         "MAN68333",
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0046", "C", None, None,
         "From the Joseph de Baye collection; findspot given by the museum "
         "with a query. NO MEASUREMENTS PUBLISHED in the source consulted. The "
         "same source states the MAN holds FOUR dodecahedra in total, so three "
         "further specimens exist in that collection and are not yet recorded "
         "here. An online 3D model is advertised and would supply geometry if "
         "retrieved."),

        ("RD-0040", "Hunt Museum (Limerick) dodecahedron",
         "Unknown; catalogued as 'not Ireland'", "Unknown", None,
         "Unknown", None, None,
         "The Hunt Museum", "Limerick", "Ireland",
         "HCM157",
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Concentric circles",
         "Multiple concentric rings engraved around each aperture; dark "
         "green-brown patina over faces and recesses",
         "Bright unpatinated metal exposed on the crown of every visible knob; "
         "see the EV041 observations for what this does and does not show",
         None, "PUB-0048", "C", None, "126",
         "Guggenberger no 126, type 1a. Held in Ireland, which was never Roman, "
         "so the object is a collection acquisition; PUB-0023 records the "
         "findspot explicitly as 'unknown (not Ireland)'. Acquired before "
         "1985. No measurements available. Added because its photograph is the "
         "clearest surface-condition image in the project."),

        # ===================================================================
        # Batch 003 - specimens with measured hole sets, from PUB-0017
        # (Duval 1981) and PUB-0019 (Sparavigna 2012). These are the first
        # specimens in the database with a complete or near-complete record of
        # individual hole diameters, which is what EV004, EV005 and EV039 need.
        # ===================================================================

        # RD-0034: Avenches (Aventicum). Twelve hole diameters measured by the
        # Musee romain d'Avenches to 0.01 mm - the most precise geometric
        # dataset in the database. Reproduced in PUB-0019 Appendix B tab B1.
        # Face numbering follows Duval 1981 (1..6, 1'..6'), mapped here to
        # hole_01..hole_06 = faces 1..6 and hole_07..hole_12 = faces 1'..6'.
        ("RD-0034", "Avenches (Aventicum) dodecahedron",
         "Avenches (Aventicum)", "Switzerland", "Germania superior",
         "Unknown", None, None,
         "Musee romain d'Avenches", "Avenches", "Switzerland",
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         26.5, 15.4, 18.3, 13.4, 10.4, 17.6,      # faces 1-6
         24.2, 20.15, 8.7, 14.5, 20.6, 14.2,      # faces 1'-6'
         None, None, None,
         None, "PUB-0019", "C", None, None,
         "Measured by Sandrine Bosse Buchanan, Musee romain d'Avenches "
         "(PUB-0040), reproduced in PUB-0019 Appendix B tab B1, which is where "
         "this project read them. Confidence C rather than B because the values "
         "reach us at one remove. Face 1' is recorded as probably elliptic "
         "(24.16 and 25.08 mm); the smaller value is stored and the ellipticity "
         "is recorded as an observation. Faces 6, 2', 4' and 5' are given as a "
         "range with the source's own stated midpoint, which is what is stored; "
         "no midpoint has been computed here. PUB-0019 reports an overall "
         "diameter of '58.5 cm', which is impossible and inconsistent with the "
         "46.5 mm face-to-face distance given in the same sentence; "
         "max_diameter_mm is therefore left NULL rather than corrected."),

        # RD-0035: Vienne (Isere). Published by Duval 1981 as the worked
        # example of his recording method. Private collection, no context.
        ("RD-0035", "Vienne (Isere) dodecahedron",
         "Vienne (Isere)", "France", "Gallia Narbonensis",
         "Unknown", None, None,
         "Private collection", None, None,
         None,
         "Copper alloy", None,
         None, None, 55.0, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         "Concentric circles",
         "Number of engraved concentric fillets increases as hole diameter "
         "decreases: 4 and 6 fillets around the 14 mm holes, 3 around the 22 mm "
         "holes, none around the 23 and 24 mm holes",
         "The two largest opposed openings (23 and 24 mm) have a periphery less "
         "regularly cut than the others",
         None, "PUB-0017", "B", None, None,
         "PUB-0017, 199-200 and figs 3-4. External diameter excluding knobs "
         "55 mm; twelve holes ranging 13.5-24 mm. Individual per-face diameters "
         "appear on fig 3, which is not legible in the available scan, so only "
         "the values stated in the running text are recorded as observations "
         "and the hole columns are left NULL. 'Piece de collection sans "
         "contexte archeologique connu' - no archaeological context."),

        # RD-0036: Carnuntum. Measurements originate with Kurzweil 1956 and
        # reach this project through PUB-0038 quoted in PUB-0019 - two removes.
        ("RD-0036", "Carnuntum dodecahedron",
         "Carnuntum", "Austria", "Pannonia superior",
         "Unknown", None, None,
         "Museum Carnuntinum", "Bad Deutsch-Altenburg", "Austria",
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0019", "D", None, None,
         "PUB-0019 tab III, quoting PUB-0038, which reports measurements made "
         "by Kurzweil (PUB-0039). Confidence D: the values reach this project "
         "at two removes and none of the three states a tolerance. Six "
         "opposite-hole pairs are recorded as observations; face-to-face "
         "distance given as 40 mm."),
    ]
    for rd, num in GUGGENBERGER_NUMBER.items():
        pass  # applied after insert, below

    cur.executemany(
        """INSERT INTO specimens (
            rd_id, specimen_name, findspot, country, roman_province,
            context_category, date_from, date_to, museum_name, museum_city,
            museum_country, inventory_number, material, manufacturing_method,
            height_mm, width_mm, max_diameter_mm, weight_g, wall_thickness_mm,
            knob_diameter_mm, hole_01_mm, hole_02_mm, hole_03_mm, hole_04_mm,
            hole_05_mm, hole_06_mm, hole_07_mm, hole_08_mm, hole_09_mm,
            hole_10_mm, hole_11_mm, hole_12_mm, decoration_type,
            decoration_desc, wear_notes, associated_finds, primary_source_id,
            confidence, nouwen_number, guggenberger_number, notes
        ) VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )""",
        SPECIMENS
    )

    # Catalogue number and type from PUB-0023, applied after insert so that the
    # specimen literals stay readable and the attribution stays auditable.
    for rd, num in GUGGENBERGER_NUMBER.items():
        cur.execute("UPDATE specimens SET guggenberger_number=? WHERE rd_id=?",
                    (num, rd))
    for rd, typ in GUGGENBERGER_TYPE.items():
        cur.execute("UPDATE specimens SET guggenberger_type=? WHERE rd_id=?",
                    (typ, rd))

    # Artifact observations: one row per specimen × evidence variable × source
    # Columns: rd_id, ev_id, observed_value, confidence, source_id, page, figure,
    #          extraction_date, notes
    OBSERVATIONS = [
        # --- RD-0001: Much Hadham (PAS BH-692011) ---
        ("RD-0001", "EV001", "82mm maximum diameter; face dimensions 38mm x 38mm",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV002", "247.23 g",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV003", "3 mm (plate thickness)",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV004",
         "Smallest hole 13.7mm; largest hole 20mm; all 12 faces perforated with varying diameters",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Individual face-by-face diameters not listed in PAS record"),
        ("RD-0001", "EV006",
         "Slightly bevelled rounded edges on all perforations",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV008",
         "Knob height approx. 9mm; diameter 9-10mm; triangular cross-section at base, sub-spherical form",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07",
         "20 knobs present; upper layer missing on several, revealing red corrosion"),
        ("RD-0001", "EV009",
         "All 20 knobs triangular-base sub-spherical; consistent form across specimen",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV010",
         "All 12 faces described as equally sized (38mm x 38mm); smoothed",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV012",
         "Exterior well-finished and smoothed; interior surfaces more roughly cast; preservation grade 2",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV013",
         "Upper layer of metal absent on several knobs, revealing red corrosion; casting not perfect",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV014",
         "Exterior surfaces smoothed; explicitly stated as smoothed in PAS description",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV018",
         "Several faces pitted or gouged; abrasion around base of most knobs; patchy patina",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV022",
         "Abrasion present around the base of most knobs",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07", None),
        ("RD-0001", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Findspot: Much Hadham, East Hertfordshire"),
        ("RD-0001", "EV039",
         "Hole diameters range 13.7-20mm; variation present within single specimen",
         "B", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Standardisation across corpus cannot be assessed from a single specimen"),

        # --- RD-0002: Fridaythorpe, Yorkshire (PAS YORYM-41CD72) ---
        ("RD-0002", "EV001",
         "Overall width 82.4mm; face width ~42mm, face length ~38mm (approximate)",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07",
         "Specimen incomplete; overall dimensions approximate"),
        ("RD-0002", "EV002",
         "270 g (incomplete specimen; true complete weight would be higher)",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07",
         "Weight is of incomplete specimen; 6 complete + ~5 partial faces"),
        ("RD-0002", "EV004",
         "Large circular holes of different sizes; holes described as irregularly cut",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07",
         "Individual diameters not listed; variation confirmed"),
        ("RD-0002", "EV009",
         "One knob broken off but retained loose; remaining knobs intact",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07", None),
        ("RD-0002", "EV012",
         "Interior described as crudely cast; exterior not described as finished",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07", None),
        ("RD-0002", "EV016",
         "Some holes surrounded by incised pentagonal line (post-casting decoration)",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07",
         "Pentagonal incised line around holes; likely post-casting tool work"),
        ("RD-0002", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-07",
         "Findspot: Fridaythorpe, East Riding of Yorkshire"),

        # --- RD-0003: Compton, Surrey (PAS SUR-729950) ---
        ("RD-0003", "EV002",
         "82 g (fragment weight only; one face + parts of five faces)",
         "B", "PUB-0006", "SUR-729950", None, "2026-08-07", None),
        ("RD-0003", "EV004",
         "Complete face: hole ~15.75mm diameter; edges of three further holes visible but unmeasured",
         "B", "PUB-0006", "SUR-729950", None, "2026-08-07",
         "Only one face fully preserved; variation across all 12 faces cannot be assessed"),
        ("RD-0003", "EV008",
         "Knob diameter ~13.5mm at each of four surviving corners",
         "B", "PUB-0006", "SUR-729950", None, "2026-08-07", None),
        ("RD-0003", "EV012",
         "Interior left roughcast; no additional decoration noted",
         "B", "PUB-0006", "SUR-729950", None, "2026-08-07", None),
        ("RD-0003", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "SUR-729950", None, "2026-08-07",
         "Findspot: Compton, Guildford, Surrey"),

        # --- RD-0004: Stockbridge, Hampshire (PAS HAMP-CE1119) ---
        ("RD-0004", "EV002",
         "46.79 g (fragment weight: 2 complete faces + remains of ~6 faces)",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07", None),
        ("RD-0004", "EV003",
         "3.7 mm wall thickness",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07", None),
        ("RD-0004", "EV004",
         "10-11mm on two complete adjacent faces; 18.3mm on a third adjacent face; variation confirmed",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07",
         "Face-to-corner measurement ~7.5mm (similar on known faces); individual diameters partly recorded"),
        ("RD-0004", "EV006",
         "Raised rim around perforation; sunken circular area within pentagonal face; "
         "raised ring between hole and edge",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07", None),
        ("RD-0004", "EV008",
         "Knob height ~10-11mm; width 6.5-7.5mm; triangular cross-section at base, expanding to globular",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07", None),
        ("RD-0004", "EV018",
         "Metal described as rather pitted and worn; dark to mid-green patina",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07", None),
        ("RD-0004", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "HAMP-CE1119", None, "2026-08-07",
         "Findspot: Stockbridge, Test Valley, Hampshire"),

        # --- RD-0005: Norton Disney, Lincolnshire (Tipper 2024) ---
        ("RD-0005", "EV001",
         "Approximately 80mm across (stated as 'about 8cm across')",
         "C", "PUB-0008", None, None, "2026-08-07",
         "Approximate figure given in popular article; 3D scan exists at Univ. Lincoln"),
        ("RD-0005", "EV002",
         "245 g",
         "C", "PUB-0008", None, None, "2026-08-07", None),
        ("RD-0005", "EV011",
         "Cu 75%, Sn 7%, Pb 18% by handheld XRF (analyst: Gerry McDonnell, archaeometallurgist)",
         "C", "PUB-0008", None, None, "2026-08-07",
         "Handheld XRF is semi-quantitative; full quantitative analysis planned at Newcastle Univ."),
        ("RD-0005", "EV017",
         "No internal hole wear observed; described as completely undamaged",
         "C", "PUB-0008", None, None, "2026-08-07",
         "Direct quote: 'no evidence of any wear at all' (Richard Parker, NDAG secretary)"),
        ("RD-0005", "EV018",
         "No external wear observed; described as completely undamaged",
         "C", "PUB-0008", None, None, "2026-08-07",
         "Same source as EV017"),
        ("RD-0005", "EV025",
         "Large pit near Roman villa (excavated 1935); rural settlement context",
         "C", "PUB-0008", None, None, "2026-08-07",
         "Pottery from Iron Age to Roman period found across site; Romano-British figurine nearby"),

        # --- RD-0006: Tongeren, Belgium (Wikipedia PUB-0004) ---
        ("RD-0006", "EV025",
         "Leopoldwal, Tongeren; context not specified in Wikipedia image caption",
         "E", "PUB-0004", None, None, "2026-08-07",
         "Minimum data only from image caption; further source required for all fields"),

        # --- RD-0007: Aston, Hertfordshire (SAL minutes 1739) ---
        ("RD-0007", "EV025",
         "A field in Aston, Hertfordshire; rural agricultural context (pre-excavation era find)",
         "A", "PUB-0007", "SAL/02/003/117", None, "2026-08-07",
         "Only contextual information available from archival record"),

        # --- RD-0008: Near Market Lavington, Wiltshire (PAS WILT-37C5E1) ---
        ("RD-0008", "EV002",
         "27.13 g (fragment: one edge + two lugs + four short sections)",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07", None),
        ("RD-0008", "EV003",
         "Not directly stated; plate visible in fragment",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07",
         "Fragment dimensions: 37.65 x 26.15 x 21.05mm"),
        ("RD-0008", "EV004",
         "Edges of three circles visible; described as each face having a hole of different size",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07",
         "Holes not individually measurable from this fragment"),
        ("RD-0008", "EV008",
         "Two cylindrical lugs: 13.05mm and 12.40mm diameter",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07",
         "Note: described as cylindrical rather than spherical; two surviving knobs"),
        ("RD-0008", "EV012",
         "Interior concave and crudely cast; exterior relatively smooth",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07", None),
        ("RD-0008", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07",
         "Findspot: Near Market Lavington, Wiltshire; date range AD 100-300"),
        ("RD-0008", "EV029",
         "AD 100-300 (tighter range than most PAS records, which use AD 43-410)",
         "B", "PUB-0006", "WILT-37C5E1", None, "2026-08-07", None),

        # --- RD-0009: Stamford Bridge, Yorkshire (PAS YORYM-E841F9) ---
        ("RD-0009", "EV002",
         "3.8 g (tiny fragment: one edge + two spherical lugs)",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07", None),
        ("RD-0009", "EV004",
         "Edges of three circular holes visible; individual diameters not measurable",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07",
         "Fragment too small for diameter measurement"),
        ("RD-0009", "EV012",
         "Reverse hollow and undecorated; exterior described as worn",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07", None),
        ("RD-0009", "EV014",
         "Double incised border around two of the hole edges; presumably two concentric rings",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07", None),
        ("RD-0009", "EV018",
         "Metal described as worn; mid-green patina",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07", None),
        ("RD-0009", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "YORYM-E841F9", None, "2026-08-07",
         "Findspot: Stamford Bridge, East Riding of Yorkshire"),

        # --- RD-0010: Yelnow, Bedford (PAS PUBLIC-959804) ---
        ("RD-0010", "EV002",
         "1.67 g (very tiny fragment: one corner only)",
         "B", "PUB-0006", "PUBLIC-959804", None, "2026-08-07", None),
        ("RD-0010", "EV014",
         "Incised grooved decoration on surviving face portions, forming two rings "
         "as outer boundary of pentagonal faces",
         "B", "PUB-0006", "PUBLIC-959804", None, "2026-08-07", None),
        ("RD-0010", "EV025",
         "Cultivated land (disturbed); metal detector; depth 0-10cm; "
         "exact Roman context unknown",
         "B", "PUB-0006", "PUBLIC-959804", None, "2026-08-07",
         "Findspot: Yelnow, Bedford; discovery 12 Feb 2011"),

        # --- RD-0011: Llandow, Vale of Glamorgan (PAS NMGW-063819) ---
        # Critical EV005 observation: two preserved opposing face holes differ dramatically
        ("RD-0011", "EV002",
         "7.73 g (fragment: one edge, two knops, partial faces)",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07", None),
        ("RD-0011", "EV003",
         "1.1 mm (wall thickness of smaller preserved face)",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Described as 'very thin'; measured on the smaller-hole face"),
        ("RD-0011", "EV004",
         "Two holes partially visible: 9.4mm (with decoration) and approx. 22.6mm (crudely finished); "
         "PAS description states perforations are of different sizes across faces",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Only two of twelve face holes partially preserved; full diameter range unknown"),
        ("RD-0011", "EV005",
         "Two preserved faces described as 'opposing': smaller hole 9.4mm vs larger hole approx. 22.6mm; "
         "opposing faces have markedly different hole diameters",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "NOTE: PAS record uses term 'opposing face'; geometric verification not possible "
         "from fragment alone; observation should be treated as provisional pending "
         "3D reconstruction"),
        ("RD-0011", "EV006",
         "Smaller face (9.4mm): circumferential groove at aperture edge; "
         "larger face (~22.6mm): crudely finished aperture",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Different finishing quality between small and large holes on same specimen"),
        ("RD-0011", "EV008",
         "Knop diameter 6.0mm x 5.7mm high; neck diameter 4.5mm; integrally cast",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07", None),
        ("RD-0011", "EV011",
         "XRF results: Cu, Sn, trace Fe, Pb (qualitative only; percentages not reported)",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Semi-quantitative XRF; quantitative analysis not available from PAS record"),
        ("RD-0011", "EV012",
         "Interior: reverse concave with rough and unfinished surface; "
         "exterior: well-defined knops and incised decoration on smaller face",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07", None),
        ("RD-0011", "EV014",
         "Smaller face: circumferential groove at aperture + two concentric grooves on outer margin; "
         "end faces: curving incised grooves; "
         "larger (~22.6mm) face: no decoration",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Decorative treatment varies with hole size: smaller hole decorated, larger hole plain"),
        ("RD-0011", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Findspot: Llandow, Vale of Glamorgan, Wales"),

        # --- RD-0012: Alveston, South Gloucestershire (PAS GLO-9EE34F) ---
        ("RD-0012", "EV002",
         "34.51 g (one corner knob fragment)",
         "B", "PUB-0006", "GLO-9EE34F", None, "2026-08-07",
         "High weight for small fragment; dense globular knob contributes most of mass"),
        ("RD-0012", "EV012",
         "Interior: concave, crudely finished; exterior: relatively smooth",
         "B", "PUB-0006", "GLO-9EE34F", None, "2026-08-07", None),
        ("RD-0012", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "GLO-9EE34F", None, "2026-08-07",
         "Findspot: Alveston, South Gloucestershire; date range AD 100-300; "
         "object certainty: 'Possibly' dodecahedron"),

        # --- RD-0013: Minting, Lincolnshire (PAS LIN-F437DA) ---
        ("RD-0013", "EV002",
         "Total fragment weight 66.42 g (four corner pieces: 20.37 + 17.41 + 12.01 + 16.63 g)",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07",
         "Four separate fragments probably from same specimen"),
        ("RD-0013", "EV003",
         "Plate thickness: 3.33, 3.55, 3.26, 3.0mm across four fragments (mean ~3.3mm)",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07",
         "Consistent wall thickness across all four fragments supports single-specimen origin"),
        ("RD-0013", "EV008",
         "Knob diameters: 14.28, 13.92, 13.46, 14.01mm across four fragments "
         "(range 13.46-14.28mm; mean ~13.9mm; very consistent)",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07",
         "Consistency of knob diameters across all four fragments strongly supports "
         "single-specimen origin; globular form confirmed"),
        ("RD-0013", "EV012",
         "Each fragment: interior concave triangular underside; exterior mid-green patina "
         "with developed brown patches; plough damage on all",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07", None),
        ("RD-0013", "EV015",
         "Iron corrosion on underside of knobs in fragments 1 and 4; "
         "described as possible repair or iron ore in soil",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07",
         "Possible ancient iron repair; ambiguous: could be soil contamination"),
        ("RD-0013", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "LIN-F437DA", None, "2026-08-07",
         "Findspot: Minting, East Lindsey, Lincolnshire; "
         "nearby find LIN-8D3A01 warrants cross-reference"),

        # --- RD-0014: Potterspury, West Northamptonshire (PAS NARC1474) ---
        ("RD-0014", "EV002",
         "4.33 g (V-shaped fragment: one edge + two corners)",
         "B", "PUB-0006", "NARC1474", None, "2026-08-07", None),
        ("RD-0014", "EV008",
         "Two small spherical knobs described as resembling bun feet; "
         "one at each end of the surviving edge",
         "B", "PUB-0006", "NARC1474", None, "2026-08-07", None),
        ("RD-0014", "EV012",
         "Cast-in-one-piece construction explicitly noted in PAS description",
         "B", "PUB-0006", "NARC1474", None, "2026-08-07",
         "This is an important manufacturing observation: "
         "most specimens have separately soldered knobs; cast-in-one-piece is unusual"),
        ("RD-0014", "EV014",
         "Multiple incised concentric circles on two surviving face portions "
         "(one set either side of the central ridge)",
         "B", "PUB-0006", "NARC1474", None, "2026-08-07", None),
        ("RD-0014", "EV025",
         "Cultivated land; metal detector find; exact Roman context unknown",
         "B", "PUB-0006", "NARC1474", None, "2026-08-07",
         "Findspot: Potterspury, West Northamptonshire"),

        # --- RD-0015: Couthuin/Bassenge, Liege, Belgium (KIK-IRPA 10140871) ---
        ("RD-0015", "EV001",
         "Diameter 44mm (overall); among the smaller known specimens",
         "B", "PUB-0011", "10140871", None, "2026-08-07",
         "Source: KIK-IRPA BALaT; only dimension given is diameter 4.4cm"),
        ("RD-0015", "EV011",
         "Alloy: bronze and lead (plomb); both listed as materials in KIK-IRPA record",
         "B", "PUB-0011", "10140871", None, "2026-08-07",
         "Lead content in alloy; quantitative composition not given"),
        ("RD-0015", "EV025",
         "Provenance: Couthuin or Bassenge, Liege province, Belgium; "
         "specific context not given in source",
         "B", "PUB-0011", "10140871", None, "2026-08-07",
         "Couthuin is in Heron commune; Bassenge is a separate municipality; "
         "exact site type unknown"),
        ("RD-0015", "EV026",
         "Roman province Gallia Belgica; Liege province, Belgium",
         "B", "PUB-0011", "10140871", None, "2026-08-07", None),
        ("RD-0015", "EV029",
         "AD 301-399 (4th century); tighter date range than most specimens",
         "B", "PUB-0011", "10140871", None, "2026-08-07",
         "Date from KIK-IRPA record; dating method not specified"),

        # --- RD-0016: British Isles unknown location (BM 1878,0311.48) ---
        ("RD-0016", "EV001",
         "Overall diameter 56.40mm",
         "B", "PUB-0012", "1878,0311.48", None, "2026-08-07", None),
        ("RD-0016", "EV002",
         "39.83 g",
         "B", "PUB-0012", "1878,0311.48", None, "2026-08-07", None),
        ("RD-0016", "EV004",
         "Aperture diameter range 12.45-17.73mm (BM catalogue lists as range, not per-face)",
         "B", "PUB-0012", "1878,0311.48", None, "2026-08-07",
         "Object certainty marked '?' in BM catalogue; identification may be uncertain"),
        ("RD-0016", "EV025",
         "Findspot: British Isles (no specific location recorded in BM catalogue)",
         "B", "PUB-0012", "1878,0311.48", None, "2026-08-07",
         "Donated via Sir A.W. Franks; provenance unknown beyond 'British Isles'"),

        # --- RD-0017: Fishguard, Pembrokeshire, Wales (BM 1924,0411.1) ---
        ("RD-0017", "EV001",
         "Overall diameter 127.71mm; one of the largest Roman dodecahedra known",
         "B", "PUB-0012", "1924,0411.1", None, "2026-08-07",
         "127.71mm exceeds the commonly cited upper limit of 110mm; "
         "warrants further verification against primary measurement"),
        ("RD-0017", "EV002",
         "553.20 g; among the heaviest known specimens",
         "B", "PUB-0012", "1924,0411.1", None, "2026-08-07",
         "Consistent with large overall diameter; Wikipedia cites max ~1kg for an unstated specimen"),
        ("RD-0017", "EV004",
         "Aperture diameter range 27.67-40.55mm; absolute values proportionally larger "
         "than most specimens, consistent with overall large size",
         "B", "PUB-0012", "1924,0411.1", None, "2026-08-07",
         "Range of 12.88mm between smallest and largest hole; "
         "comparable percentage variation to smaller specimens"),
        ("RD-0017", "EV025",
         "Purchased; no excavation context recorded",
         "B", "PUB-0012", "1924,0411.1", None, "2026-08-07",
         "Purchased from Thomas James, Fishguard, 1924; "
         "exact find circumstances unknown"),
        ("RD-0017", "EV026",
         "Roman province Britannia; Pembrokeshire, Wales",
         "B", "PUB-0012", "1924,0411.1", None, "2026-08-07", None),

        # --- RD-0018: Corbridge Roman town (English Heritage) ---
        ("RD-0018", "EV025",
         "Roman town and fort (Corstopitum); known military and civilian settlement on Hadrian's Wall",
         "C", "PUB-0013", None, None, "2026-08-07",
         "Corbridge was a significant supply base and settlement on Dere Street"),
        ("RD-0018", "EV031",
         "Military association confirmed: Corbridge was a Roman fort and supply base",
         "C", "PUB-0013", None, None, "2026-08-07",
         "Site has both military and civilian Roman occupation phases"),

        # --- RD-0019: South Shields (Arbeia) Roman fort (secondary citation) ---
        ("RD-0019", "EV001",
         "Face width 52mm, face length 48mm (cited from museum website in PAS YORYM-41CD72)",
         "D", "PUB-0009", "p.218-219 no.3.741", None, "2026-08-07",
         "Secondary citation: measurements from museum website as quoted in PAS record; "
         "not directly from primary catalogue; confidence D pending direct verification"),
        ("RD-0019", "EV025",
         "Roman fort (Arbeia), South Shields; confirmed military context",
         "B", "PUB-0009", "p.218-219 no.3.741", None, "2026-08-07",
         "Arbeia is a well-documented Roman auxiliary fort at mouth of River Tyne"),
        ("RD-0019", "EV031",
         "Military association: found at Roman auxiliary fort",
         "B", "PUB-0009", "p.218-219 no.3.741", None, "2026-08-07",
         "One of the few British dodecahedra with confirmed military fort provenance"),

        # --- RD-0020: Jublains, Mayenne, France (Guillier et al. 2008) ---
        ("RD-0020", "EV025",
         "Edge of Roman thermal baths complex at Jublains (Noeodunum); "
         "civilian public building context; not military",
         "A", "PUB-0010", "p.269-289", None, "2026-08-07",
         "This is the only Roman dodecahedron from a verified, controlled excavation; "
         "thermal baths = public civilian infrastructure, not military or ritual"),
        ("RD-0020", "EV028",
         "Found in stratigraphic context during controlled excavation; "
         "specific stratigraphic detail requires access to full paper text",
         "A", "PUB-0010", "p.269-289", None, "2026-08-07",
         "Context verified by professional archaeologists (INRAP); "
         "paper sub-title emphasises this is the first properly contextualised find"),
        ("RD-0020", "EV026",
         "Roman province Gallia Lugdunensis; Jublains is civitas capital of the Aulerci Diablintes",
         "A", "PUB-0010", "p.269-289", None, "2026-08-07", None),
        ("RD-0020", "EV032",
         "Thermal baths context does not directly support ritual association; "
         "baths were civilian social/hygienic infrastructure",
         "A", "PUB-0010", "p.269-289", None, "2026-08-07",
         "Context contradicts H003 (ritual) as primary interpretation for this specimen; "
         "however one specimen is insufficient to draw corpus conclusions"),

        # -----------------------------------------------------------------------
        # ENGINEERING ASSESSMENTS (EV033-EV037): Derived from measured geometry
        # These are desk assessments, not physical measurements.
        # Confidence level: C (derived from B-grade geometric measurements)
        # -----------------------------------------------------------------------

        # EV033 Rod compatibility — assessed from hole diameter data
        # RD-0001 (Much Hadham): holes 13.7-20mm; overall diam 82mm
        ("RD-0001", "EV033",
         "ASSESSMENT: Cylindrical rods of 13.5mm diameter fit through all 12 holes. "
         "Each hole (13.7-20mm) accepts a specific rod diameter. "
         "Rod insertion is mechanically feasible.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Derived from measured hole diameters 13.7-20mm; "
         "Roman wooden dowels/rods in 10-20mm diameter are archaeologically attested"),
        # RD-0017 (Fishguard): holes 27.67-40.55mm; proportionally large
        ("RD-0017", "EV033",
         "ASSESSMENT: Holes 27.67-40.55mm accommodate substantial rods/poles or large tool handles. "
         "Rod insertion feasible; scale consistent with structural use of large timber.",
         "C", "PUB-0012", "1924,0411.1", None, "2026-08-07",
         "Derived from BM catalogue hole range; proportionally similar to smaller specimens"),
        # RD-0016 (BM 1878): holes 12.45-17.73mm; overall diam 56.4mm
        ("RD-0016", "EV033",
         "ASSESSMENT: Holes 12.45-17.73mm accommodate rods of 12-17mm diameter. "
         "Rod insertion mechanically feasible.",
         "C", "PUB-0012", "1878,0311.48", None, "2026-08-07",
         "Derived from BM catalogue; object certainty '?' noted"),
        # RD-0011 (Llandow): opposing holes 9.4mm and ~22.6mm
        ("RD-0011", "EV033",
         "ASSESSMENT: Opposing faces have holes of 9.4mm and ~22.6mm. "
         "Rods cannot pass through both opposing holes simultaneously unless two different rod sizes are used. "
         "This geometry is incompatible with a through-rod passing axially through opposing holes "
         "unless the holes are not geometrically opposing.",
         "C", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Critical constraint: if 9.4mm and 22.6mm are truly opposing faces, "
         "no single rod can pass through both; "
         "see EV005 note on geometric verification needed"),

        # EV034 Rope compatibility — assessed from hole and knob dimensions
        ("RD-0001", "EV034",
         "ASSESSMENT: Smallest hole 13.7mm allows rope of up to ~12mm diameter to pass through. "
         "Knobs (~9.5mm diameter) can serve as anchors or routing guides for rope of 4-8mm diameter. "
         "Rope routing through holes and over knobs is geometrically feasible.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Derived from hole range 13.7-20mm and knob diameter 9-10mm; "
         "Roman cordage in 5-15mm diameter is archaeologically attested"),
        ("RD-0011", "EV034",
         "ASSESSMENT: Smaller hole (9.4mm) constrains rope to <8mm diameter. "
         "Larger hole (~22.6mm) is permissive. "
         "Rope routing is feasible through the larger hole; constrained through the smaller.",
         "C", "PUB-0006", "NMGW-063819", None, "2026-08-07",
         "Derived from hole measurements 9.4mm and ~22.6mm"),

        # EV035 Structural stability — assessed from form and wall thickness
        ("RD-0001", "EV035",
         "ASSESSMENT: The dodecahedral form with 20 vertex knobs provides stable 3-point resting "
         "on any surface. Wall thickness 3mm with bronze alloy provides rigid structural shell. "
         "No deformation evidence in any examined specimen. "
         "Structurally stable as a free-standing object.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Derived from wall thickness 3mm, bronze alloy, dodecahedral geometry; "
         "3-point stability is inherent to the regular form"),

        # EV036 Load transfer — assessed from geometry of opposing face holes
        ("RD-0001", "EV036",
         "ASSESSMENT: Six pairs of opposing faces provide 6 potential through-rod axes. "
         "A rod inserted through opposing holes of equal diameter transfers axial load. "
         "For RD-0001 (holes 13.7-20mm), varying hole sizes mean only same-diameter opposing "
         "pairs can carry through-rods; load transfer is directionally selective, not isotropic. "
         "Plausible but requires specific rod sizes per axis.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Derived from geometry; load capacity depends on rod-hole fit and material properties"),

        # EV037 Assembly potential — assessed from corpus size variation
        # This is a corpus-level observation, attached to representative specimen RD-0001
        ("RD-0001", "EV037",
         "ASSESSMENT (corpus-level): Overall diameters span 44mm to 127.71mm across measured specimens "
         "(ratio 2.9:1). A modular structural system requires standardised component sizes. "
         "The 3x size range is incompatible with interchangeable modular nodes. "
         "Individual specimens can accept rods/ropes, but assembly of multiple dodecahedra "
         "into a common structural system is not supported by the current evidence.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Corpus-level derived assessment; based on 5 specimens with reliable size measurements: "
         "RD-0015 (44mm), RD-0016 (56.4mm), RD-0001/RD-0002 (~82mm), RD-0017 (127.71mm)"),

        # -----------------------------------------------------------------------
        # EV039 Standardisation — corpus-level statistical assessment
        # -----------------------------------------------------------------------
        ("RD-0001", "EV039",
         "ASSESSMENT (corpus-level): No metrological standard detected. "
         "Overall diameters: 44, 56.4, ~80, ~82, 127.71mm — no common unit or ratio pattern. "
         "Hole diameter ranges: 9.4-40.55mm across specimens with no consistent sizing. "
         "Wall thickness: 1.1-3.7mm — wide variation. "
         "E013 in evidence register: 'No authenticated inscriptions or numerals are known'. "
         "E029: 'No accepted metrological standard has been demonstrated'. "
         "Conclusion: absence of standardisation across the corpus.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Corpus-level derived from 5 specimens with reliable size data; "
         "consistent with evidence register E029"),

        # -----------------------------------------------------------------------
        # EV040 Regional variation — corpus-level contextual assessment
        # -----------------------------------------------------------------------
        ("RD-0001", "EV040",
         "ASSESSMENT (corpus-level): Current corpus is predominantly British (17/21 specimens). "
         "2 Belgian (Tongeren, Liege) and 2 French (Jublains, Arles) specimens entered. "
         "Insufficient continental coverage for systematic regional variation analysis. "
         "Pending: data from German, Dutch, Swiss, Luxembourg and Austrian museum collections.",
         "C", "PUB-0006", "BH-692011", None, "2026-08-07",
         "Corpus-level observation; geographic bias in current dataset due to PAS coverage; "
         "full analysis requires Guggenberger & Nouwen catalogue data"),

        # --- RD-0021: Arles (thermae), France (Wikidata Q62511455) ---
        ("RD-0021", "EV025",
         "Roman thermae (public baths) at Arelate (Arles); civilian public infrastructure; "
         "discovered 1939 during work at or near the thermal baths",
         "C", "PUB-0014", "Q62511455", None, "2026-08-07",
         "PATTERN: second baths-context specimen alongside Jublains (RD-0020); "
         "thermal baths = civilian public building, not military or ritual context"),
        ("RD-0021", "EV026",
         "Roman province Gallia Narbonensis; Arelate (Arles) was a major Roman colony",
         "C", "PUB-0014", "Q62511455", None, "2026-08-07", None),
        ("RD-0021", "EV029",
         "3rd century AD (per Wikidata record)",
         "C", "PUB-0014", "Q62511455", None, "2026-08-07",
         "Dating method not specified in Wikidata record"),

        # ===================================================================
        # Batch 002 - observations extracted from Guggenberger & Leach 2025
        # (PUB-0003). Page numbers are journal pages of The Antiquaries
        # Journal 105 (article pp 31-54). Where PUB-0003 itself cites an
        # earlier work, the ultimate reference is named in the notes field;
        # source_id always remains PUB-0003, the publication actually read.
        # ===================================================================

        # --- RD-0022 Mainz 3 (Guggenberger no 134) ---
        ("RD-0022", "EV001",
         "Diameter face to opposite face 5.5 cm (55 mm) excluding knobs; complete specimen",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07",
         "Measured by the cataloguer; first publication of this specimen"),
        ("RD-0022", "EV002", "246 g",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07", None),
        ("RD-0022", "EV003", "Wall thickness c 1.5 mm",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07", None),
        ("RD-0022", "EV004",
         "One pair of holes 15/17 mm and a second pair 14/15 mm; all other holes "
         "in a very small range of c 10.0-12.5 mm",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07",
         "Individual diameters of the eight remaining holes not given; "
         "range recorded verbatim, values NOT interpolated"),
        ("RD-0022", "EV005",
         "Two recorded pairs of opposite holes: 15/17 mm (difference 2 mm) and "
         "14/15 mm (difference 1 mm)",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07",
         "Within-pair differences fall inside the corpus range of c 2-4.5 mm "
         "reported at p 31 n 1"),
        ("RD-0022", "EV008", "Knob diameter c 5 mm",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07", None),
        ("RD-0022", "EV014",
         "All faces carry five ring-and-dot motifs; Greiner/Guggenberger type 2a",
         "B", "PUB-0003", "36", "fig 4", "2026-08-07", None),
        ("RD-0022", "EV025",
         "No findspot recorded; known only from the Henryk Klunder collection, Mainz, "
         "now in a private collection in Winterthur, Switzerland",
         "B", "PUB-0003", "34, 36", "fig 4", "2026-08-07",
         "Unprovenanced. Contributes measurements but no context evidence"),

        # --- RD-0023 Gelduba/Gellep (Guggenberger no 11) ---
        ("RD-0023", "EV025",
         "Richly furnished grave of a wealthy woman who died around AD 350",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "One of only three dodecahedra from richly furnished graves "
         "(with Bassenge and Bachem)"),
        ("RD-0023", "EV027",
         "An object of bone, length c 15 cm and diameter c 3 cm, lay immediately "
         "adjacent to the dodecahedron in the grave",
         "C", "PUB-0003", "35-6", None, "2026-08-07",
         "OBSERVATION vs INTERPRETATION: the adjacency and dimensions are the "
         "observation. PUB-0003's suggestion of 'a functional connection' and of "
         "'temporary mounting upon a kind of handle' is author interpretation and "
         "is recorded in evidence_register, not here. The bone object was in very "
         "poor condition, was not preserved, and is known only from a drawing of "
         "the grave - so it cannot be re-examined"),
        ("RD-0023", "EV004",
         "Pair of production holes 2.4 cm and 2.3 cm (24 and 23 mm)",
         "C", "PUB-0003", "36", None, "2026-08-07", None),
        ("RD-0023", "EV029",
         "Grave of a woman who died around AD 350",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "Dating derives from the grave assemblage as reported"),

        # --- RD-0024 Pfofeld (Guggenberger no 20) ---
        ("RD-0024", "EV025",
         "Found along the Roman Limes, in the same area of a palisade trench "
         "near a watchtower",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "PUB-0003 n 18 nevertheless lists no 20 among find contexts with "
         "plausible sacred connections; both readings preserved"),
        ("RD-0024", "EV027",
         "A bronze statuette of Mercury as Hermes-Thoth was found in the same area",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "Ultimate reference: Winkelmann 1933, 137-8 tab 16"),
        ("RD-0024", "EV031",
         "Limes context: palisade trench near a watchtower",
         "C", "PUB-0003", "35", None, "2026-08-07", None),

        # --- RD-0025 Schwarzenacker (Guggenberger no 21) ---
        ("RD-0025", "EV025",
         "Found 'near' the sacrificial shafts of an urban Gallo-Roman cult precinct",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "Quotation marks around 'near' are the source's own; exact distance "
         "not stated. Ultimate reference: Kolling 1993, 124"),
        ("RD-0025", "EV032",
         "Association with the sacrificial shafts of a cult precinct",
         "C", "PUB-0003", "35", None, "2026-08-07", None),

        # --- RD-0026 Lydney (Guggenberger no 68) ---
        ("RD-0026", "EV025",
         "From the site of the temple complex of the local god Nodens at Lydney; "
         "the exact find context is unknown",
         "C", "PUB-0003", "34", None, "2026-08-07",
         "Ultimate reference: Wheeler and Wheeler 1932, 86 fig 20. Site "
         "association only - not a stratified context"),
        ("RD-0026", "EV032",
         "Recovered from a temple site (Nodens), exact context unknown",
         "C", "PUB-0003", "34", None, "2026-08-07", None),

        # --- RD-0027 Severn estuary / Gloucester (Guggenberger no 122) ---
        ("RD-0027", "EV025",
         "Part of a cache identified as originating from a temple, perhaps the "
         "temple of Diana at Gloucester",
         "C", "PUB-0003", "34", None, "2026-08-07",
         "Ultimate reference: Coombe and Henig 2020. The temple origin is the "
         "cited authors' identification of the cache, not a stratigraphic "
         "observation of the dodecahedron"),
        ("RD-0027", "EV027",
         "Recovered as part of a cache of objects",
         "C", "PUB-0003", "34", None, "2026-08-07", None),

        # --- RD-0028 north of Paris (Guggenberger no 110) ---
        ("RD-0028", "EV025",
         "Found by a metal detectorist in a 'modest Gallo-Roman domestic structure'",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "Ultimate reference: Berton 2007"),
        ("RD-0028", "EV027",
         "A bronze statuette of a goddess (Juno?) lay one metre away",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "The identification as Juno is queried in the source and the query is "
         "preserved. Distance of one metre is as stated"),

        # --- RD-0029 Carmarthenshire (Guggenberger no 60) ---
        ("RD-0029", "EV025",
         "CONFLICT: listed both among finds from cities or other settlements "
         "(n 16) and among coin or bronze hoards (n 21)",
         "C", "PUB-0003", "33", "fig 3", "2026-08-07",
         "Both classifications preserved per RDORP conflict rule; a hoard "
         "deposited within a settlement would satisfy both"),

        # --- RD-0030 Bachem (Guggenberger no 5) ---
        ("RD-0030", "EV025",
         "One of three dodecahedra from richly furnished graves",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "Ultimate references: Barthel 1909, 94; Nouwen 1993, 31-2, 35"),
        ("RD-0030", "EV029",
         "Dating uncertain; PUB-0003 notes Bachem among specimens that may date "
         "from the 2nd century",
         "C", "PUB-0003", "32", None, "2026-08-07",
         "PUB-0003 n 13 states explicitly that the dating of this specimen "
         "remains uncertain"),

        # --- RD-0031 Feldberg (Guggenberger no 10) ---
        ("RD-0031", "EV024",
         "Recorded as having traces of yellow wax",
         "D", "PUB-0003", "45", None, "2026-08-07",
         "RELIABILITY EXPLICITLY QUESTIONED BY THE SOURCE: PUB-0003 n 103 states "
         "'this observation may not be fully reliable' (Guggenberger 1999, 61-2, "
         "144, 162). Recorded at confidence D for that reason. This is the only "
         "residue observation in the corpus, and it is contested"),
        ("RD-0031", "EV025",
         "Feldberg Roman fort; listed among military-camp find contexts",
         "C", "PUB-0003", "33", None, "2026-08-07", None),
        ("RD-0031", "EV029",
         "Found 1892; dating uncertain, possibly 2nd century",
         "C", "PUB-0003", "32", None, "2026-08-07",
         "PUB-0003 n 13 lists Feldberg among specimens whose dating is uncertain"),

        # --- RD-0032 Brigetio (Guggenberger no 92) ---
        ("RD-0032", "EV026",
         "Brigetio, Pannonia - the easternmost known findspot",
         "C", "PUB-0003", "32", None, "2026-08-07", None),

        # --- RD-0033 Deonica (Guggenberger no 130) ---
        ("RD-0033", "EV026",
         "Deonica, Moesia superior - outlying south-eastern findspot",
         "C", "PUB-0003", "32", None, "2026-08-07",
         "Ultimate reference: Vujovic 2021"),

        # --- Additions to batch-001 specimens from PUB-0003 ---
        ("RD-0005", "EV025",
         "Discovered on the top of a large pit full of building debris, 700 m "
         "east of a villa rustica",
         "C", "PUB-0003", "34", None, "2026-08-07",
         "More precise than the batch-001 record (PUB-0008), which gave only "
         "'large pit near Roman villa'. Both retained; distance now specified. "
         "PUB-0003 also reports Hitchens' suggestion that it may have been placed "
         "to ritually close the pit and Guggenberger's/Henig's suggestion that it "
         "may originate from a shrine - both are INTERPRETATION and are recorded "
         "in evidence_register, not as observations"),
        ("RD-0007", "EV025",
         "First recorded dodecahedron; presented to the Society of Antiquaries "
         "of London in 1739; Guggenberger catalogue no 59",
         "C", "PUB-0003", "32", "fig 1", "2026-08-07",
         "Confirms the batch-001 archival record (PUB-0007) and supplies the "
         "catalogue number"),
        ("RD-0015", "EV025",
         "PUB-0003 lists a Bassenge (Belgium) dodecahedron, Guggenberger no 2, "
         "as one of three specimens from richly furnished graves",
         "C", "PUB-0003", "35", None, "2026-08-07",
         "POSSIBLE IDENTITY, NOT ASSERTED: RD-0015 is recorded by PUB-0011 as "
         "from 'Couthuin or Bassenge, Liege province'. Guggenberger no 2 may be "
         "the same object, which would give RD-0015 a grave context. The "
         "identification is not made by either source and is left unresolved; "
         "RD-0015 context_category therefore remains Unknown"),
        ("RD-0020", "EV028",
         "Deposition of the stratified Jublains dodecahedron took place in the "
         "first half of the 3rd century",
         "B", "PUB-0003", "32", None, "2026-08-07",
         "PUB-0003 n 13, citing Guillier et al 2008, 284. Corroborates the "
         "batch-001 record and supplies Guggenberger no 98"),

        # ===================================================================
        # Batch 003 - observations from the three publications consulted
        # directly: PUB-0010 (Guillier et al 2008, grade A excavation report),
        # PUB-0017 (Duval 1981) and PUB-0019 (Sparavigna 2012).
        # ===================================================================

        # --- RD-0020 Jublains: the only stratified specimen (PUB-0010) ------
        ("RD-0020", "EV001",
         "Height 59 mm as it stands, but only 48-52 mm from face to opposite "
         "face; maximum diameter 74 mm; twelve pentagonal faces of 21 mm edge",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07",
         "The 48-52 mm spread across face-to-face axes is itself a measure of "
         "the object's departure from a regular dodecahedron"),
        ("RD-0020", "EV002", "81 g",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07",
         "Lightest complete specimen in the database; compare 246 g (RD-0022), "
         "247 g (RD-0001), 245 g (RD-0005), 553 g (RD-0017)"),
        ("RD-0020", "EV004",
         "Ten faces have circular openings varying from 10.5 to 22 mm; the two "
         "remaining faces have oval openings of 21x26 mm",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07",
         "Per-face diameters are not tabulated in the report; the drawing "
         "(fig 12) is a Duval rabattement from which PUB-0019 later read "
         "values, recorded separately below at lower confidence"),
        ("RD-0020", "EV005",
         "The two faces without concentric circles, which carry the oval "
         "openings, are placed in opposition on the object, possibly "
         "materialising a 'top' and a 'bottom'",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07",
         "The excavators' phrase is 'y materialisant eventuellement un haut et "
         "un bas' - a hedged suggestion, not an assertion. Relevant to EV038"),
        ("RD-0020", "EV006",
         "Ten openings circular; two openings oval (21x26 mm)",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07",
         "CONFLICTS WITH NOTHING, but note that PUB-0003, 32 explains the "
         "irregular opposed pair across the corpus as production holes"),
        ("RD-0020", "EV008",
         "Each vertex carries a small ball about 5-6 mm in diameter",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07", None),
        ("RD-0020", "EV011",
         "Copper alloy, described by the excavators as 'bronze?' with the "
         "query retained",
         "A", "PUB-0010", "para 41", None, "2026-08-07",
         "No analysis was performed; the query is the excavators' own"),
        ("RD-0020", "EV012",
         "Appears to have been cast by the lost-wax process and then carefully "
         "trued up ('coule a la cire perdue puis soigneusement rectifie')",
         "A", "PUB-0010", "para 48", None, "2026-08-07",
         "Direct support for post-casting finishing; see EV016"),
        ("RD-0020", "EV014",
         "Ten of the twelve faces have their opening underlined by concentric "
         "circles engraved in the metal; the other two faces have none",
         "A", "PUB-0010", "para 48", "fig 11", "2026-08-07", None),
        ("RD-0020", "EV015",
         "Intact apart from a barely visible crack on one edge",
         "A", "PUB-0010", "para 48", None, "2026-08-07",
         "No repair present; recorded because it establishes that the object "
         "was complete when deposited, in a burnt destruction layer"),
        ("RD-0020", "EV016",
         "The vertex balls are soldered to the body of the dodecahedron itself "
         "('soudee au corps meme du dodecaedre')",
         "A", "PUB-0010", "para 48", None, "2026-08-07",
         "CONFLICT: RD-0014 is recorded by PUB-0006 as cast in one piece. Both "
         "readings preserved. If knobs were separately made and attached on "
         "this specimen, the manufacturing sequence is more complex than "
         "single-pour casting and the knobs are a deliberate addition"),
        ("RD-0020", "EV025",
         "Recovered from destruction layer F1058 of a small drystone building "
         "over an excavated cellar, on ancient Street 8 at the junction of "
         "Cardo A and Decumanus 8, in the shadow of a large public building "
         "(the thermae); the building burned at the turn of the 2nd and 3rd "
         "centuries",
         "A", "PUB-0010", "paras 41, 60-61", None, "2026-08-07",
         "CORRECTS THE BATCH-001 RECORD, which read this as a baths context "
         "because the excavation lay at the edge of the thermae. The building "
         "is a separate structure across the street. The excavators state the "
         "position was ideal for a commercial establishment. THIS IS THE ONLY "
         "SEALED, DATED, STRATIFIED DODECAHEDRON CONTEXT KNOWN"),
        ("RD-0020", "EV027",
         "Found in the same destruction layer as a complete trebuchet "
         "(precision balance): beam 225 mm long weighing 20 g, with two "
         "tortoise-shell-shaped pans of 59x52x16 mm (12 g) and 49x54x17 mm "
         "(11 g), each pierced with three 2 mm holes; the complete pan holds "
         "20 cubic cm level and 36 heaped. The accompanying pottery has a "
         "higher proportion of closed vessels and fewer kitchen vessels than "
         "contemporary assemblages",
         "A", "PUB-0010", "paras 42-47, 60", "fig 10", "2026-08-07",
         "THE STRONGEST ASSOCIATED-FIND RECORD IN THE DATABASE. The excavators "
         "note the balance served to check the alloy of a coin or to weigh "
         "precious materials, with a capacity not exceeding one Roman pound "
         "(327.45 g). Their reading of the assemblage as either a merchant's or "
         "craftsman's shop or the den of a diviner, and their remark that the "
         "two are not incompatible, is INTERPRETATION and is recorded in "
         "evidence_register"),
        ("RD-0020", "EV029",
         "The building was occupied during the first half of the 3rd century "
         "and destroyed by fire at the turn of the 2nd and 3rd centuries; the "
         "object is judged to have been in use during the first half of the "
         "3rd century",
         "A", "PUB-0010", "paras 54, 60", None, "2026-08-07",
         "A coin of Nero beneath the earliest road make-up dates the street "
         "grid to the early Flavian period, and a coin of Tetricus attests "
         "later activity; the dodecahedron itself is dated by the destruction "
         "layer"),
        ("RD-0020", "EV031",
         "No military association: an urban commercial building in a civitas "
         "capital",
         "A", "PUB-0010", "paras 60-62", None, "2026-08-07", None),
        # Per-face values read by PUB-0019 off the fig 12 rabattement.
        ("RD-0020", "EV004",
         "Opposite-hole pairs read off the fig 12 rabattement: (1,1') elliptic "
         "26x21.5 and 25.5x21.5 mm; (6',2) 22 and 21.5 mm; (5',3) 17 and "
         "16.5 mm; (4',4) 22 and 21 mm; (3',5) 15.5 and 11.5 mm; (2',6) 10.5 "
         "and 17 mm",
         "D", "PUB-0019", "tab I", "fig A1", "2026-08-07",
         "SECOND-HAND AND LOWER CONFIDENCE: values read by PUB-0019 from "
         "PUB-0010 fig 12, not measured. Recorded separately from the A-grade "
         "row above and deliberately not merged with it"),
        ("RD-0020", "EV005",
         "Within-pair differences of the six opposite pairs: 0.5, 0.5, 0.5, "
         "1.0, 4.0 and 6.5 mm",
         "D", "PUB-0019", "tab I", None, "2026-08-07",
         "Derived by PUB-0019 from its own tab I readings. Four pairs are "
         "nearly equal and two differ greatly - the mixed pattern PUB-0003, 31 "
         "n 1 describes for the corpus"),
        ("RD-0020", "EV014",
         "Each pair of opposite holes carries the same decoration; the "
         "decoration is composed of three circles",
         "D", "PUB-0019", "9", "fig 2", "2026-08-07",
         "PUB-0019 suggests this could be a mnemonic code for calculations; "
         "that suggestion is INTERPRETATION and is recorded separately"),

        # --- RD-0034 Avenches: the most precise hole dataset ----------------
        ("RD-0034", "EV004",
         "Twelve measured hole diameters in mm: 26.5, 15.4, 18.3, 13.4, 10.4, "
         "17.6, 24.2, 20.15, 8.7, 14.5, 20.6, 14.2",
         "C", "PUB-0019", "Appendix B tab B1", None, "2026-08-07",
         "Measured by the Musee romain d'Avenches (PUB-0040) to 0.01 mm and "
         "reproduced in PUB-0019. The only complete twelve-hole dataset in the "
         "database. Range 8.7-26.5 mm, a factor of 3.0 within a single object"),
        ("RD-0034", "EV005",
         "Opposite-hole pairs and their differences: (1,1') 26.5/24.2 = 2.3 mm; "
         "(2,2') 15.4/20.15 = 4.75 mm; (3,3') 18.3/8.7 = 9.6 mm; (4,4') "
         "13.4/14.5 = 1.1 mm; (5,5') 10.4/20.6 = 10.2 mm; (6,6') 17.6/14.2 = "
         "3.4 mm",
         "C", "PUB-0019", "Appendix B tab B1", None, "2026-08-07",
         "Differences computed here from the source's measured diameters; the "
         "arithmetic is derived, the diameters are observed. No pair is equal "
         "and two differ by more than 9 mm, so no single straight rod could "
         "pass through those axes"),
        ("RD-0034", "EV006",
         "Four holes are recorded with two differing diameters, indicating "
         "departure from circularity: hole 1 26.46/26.62, hole 6 17.38/17.85, "
         "hole 2' 19.9/20.43, hole 4' 14.27/14.68 and hole 5' 20.4/20.83; hole "
         "1' (24.16/25.08) is described as probably elliptic",
         "C", "PUB-0019", "Appendix B tab B1", None, "2026-08-07",
         "Direct evidence that holes are not perfectly circular even on a "
         "well-made specimen"),
        ("RD-0034", "EV012",
         "The measured tolerance of the hole diameters is below 0.2 mm",
         "C", "PUB-0019", "Appendix B", None, "2026-08-07",
         "The source's own assessment of the maker's tolerance. This is the "
         "best available evidence of manufacturing precision and it sits "
         "alongside the corpus statement that many British specimens are less "
         "skilfully made (PUB-0003, 32)"),
        ("RD-0034", "EV025",
         "Aventicum (Avenches); find context not stated in the available source",
         "C", "PUB-0019", "3.2", None, "2026-08-07", None),

        # --- RD-0035 Vienne: Duval's worked example ------------------------
        ("RD-0035", "EV001",
         "External diameter of the object, excluding the knobs, is 55 mm",
         "B", "PUB-0017", "200", "fig 4", "2026-08-07", None),
        ("RD-0035", "EV004",
         "The twelve hole diameters vary from 13.5 to 24 mm; several are "
         "repeated: 22 mm three times (faces 2, 3', 5'), 20 mm twice (faces 4, "
         "6) and 14 mm twice (faces 4', 6')",
         "B", "PUB-0017", "200", "fig 3", "2026-08-07",
         "Per-face values for the remaining holes appear on fig 3, which is not "
         "legible in the available scan, and are therefore not recorded"),
        ("RD-0035", "EV005",
         "In two cases the diameters of opposed openings are equal: 20 mm "
         "(faces 4 and 4') and 14 mm (faces 6 and 6'). Beyond these "
         "coincidences there is no evident regularity in the general "
         "distribution of the openings, either in their juxtaposition or in "
         "their opposition",
         "B", "PUB-0017", "200", "fig 3", "2026-08-07",
         "KEY OBSERVATION FOR EV005 AND EV039. Duval, who devised the "
         "comparative recording method precisely in order to look for such "
         "regularity, states that none is evident. He also states explicitly "
         "that no conclusion can be drawn from a single specimen"),
        ("RD-0035", "EV014",
         "There is no regularity in the distribution of the engraved "
         "concentric fillets relative to the openings they surround; the only "
         "pattern is that they become more numerous as the hole diameter "
         "decreases, leaving more room: 4 and 6 fillets for the 14 mm holes, 3 "
         "for the 22 mm holes, none for the 23 and 24 mm holes",
         "B", "PUB-0017", "200", "fig 3", "2026-08-07",
         "Duval suggests the reason is probably empirical, ie available space "
         "rather than meaning"),
        ("RD-0035", "EV017",
         "The two largest opposed openings (23 and 24 mm) have a periphery that "
         "appears less regularly cut than the others, as if they had been worn "
         "by some friction, due for example to a stick that passed through both "
         "of them simultaneously",
         "C", "PUB-0017", "200", "fig 3", "2026-08-07",
         "CONFLICTS DIRECTLY WITH THE CORPUS-LEVEL RECORD. PUB-0003, 45 states "
         "that the surfaces of dodecahedra generally do not look worn, and "
         "PUB-0003, 32 explains exactly this feature - an opposed pair of "
         "larger, less regular openings without concentric circles - as "
         "production holes arising from the casting process, present in about "
         "70 per cent of specimens. BOTH READINGS ARE PRESERVED. Duval's "
         "wording is hedged throughout ('parait', 'comme s'ils avaient ete "
         "uses'), it is an appearance on one specimen, and he states that no "
         "conclusion can be drawn from it. Confidence C rather than B for that "
         "reason. This conflict is the reason EV017 is scored at confidence C "
         "at corpus level rather than B"),
        ("RD-0035", "EV025",
         "Collection piece with no known archaeological context",
         "B", "PUB-0017", "198", None, "2026-08-07", None),

        # --- RD-0036 Carnuntum ---------------------------------------------
        ("RD-0036", "EV005",
         "Six opposite-hole pairs in mm: 20.1/20.3, 13.2/13.7, 21.4/22.4, "
         "25/26.5, 15.3/17.3, 13/10.5; face-to-face distance 40 mm",
         "D", "PUB-0019", "tab III", None, "2026-08-07",
         "Within-pair differences 0.2, 0.5, 1.0, 1.5, 2.0 and 2.5 mm. Values "
         "reach this project at two removes (PUB-0039 via PUB-0038 via "
         "PUB-0019) and no tolerance is stated by any of them"),

        # --- RD-0006 Tongeren: hole pairs from the Tongres museum -----------
        ("RD-0006", "EV005",
         "Six opposite-hole pairs in mm: 16/16.2, 7.5/8.5, 10.5/12.5, 20/22.5, "
         "12.5/15.5, 16.5/12.5; face-to-face distance 63 mm",
         "D", "PUB-0019", "tab IV", None, "2026-08-07",
         "PUB-0019 tab IV, quoting PUB-0038, whose author states he obtained "
         "the exact measurements from the director of the Musee gallo-romain de "
         "Tongres. Within-pair differences 0.2, 1.0, 2.0, 2.5, 3.0 and 4.0 mm. "
         "POSSIBLE BUT UNCONFIRMED MATCH to RD-0006, which is recorded from "
         "PUB-0004 as the Tongeren (Leopoldwal) specimen; PUB-0019 does not "
         "give a findspot, only the holding museum. If the museum holds more "
         "than one specimen this attribution is wrong. Recorded here with that "
         "caveat rather than as a new specimen, to avoid creating a duplicate"),
        ("RD-0006", "EV004",
         "Hole diameters range from 7.5 to 22.5 mm within the single object",
         "D", "PUB-0019", "tab IV", None, "2026-08-07",
         "Derived from the tab IV pair listing; same attribution caveat"),

        # --- Batch 004: Norton Disney, from the excavators (PUB-0042) -------
        ("RD-0005", "EV025",
         "Found in situ in Trench 4 in June 2023 by a volunteer, without metal "
         "detector use, in what appears to be an excavated hole or quarry pit "
         "containing 4th century Roman pottery. Re-investigation in 2024 "
         "suggested the feature was a sand quarry pit whose fill contained "
         "bone, ceramic building material and 3rd century pottery",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "EXCAVATOR-GRADE CONTEXT, replacing reliance on a newspaper article. "
         "CONFLICTS RECORDED: PUB-0003, 34 describes the feature as 'a large "
         "pit full of building debris 700 m east of a villa rustica' and this "
         "account calls it a sand quarry pit; PUB-0003 places the object on top "
         "of the pit, this account says in situ within it; and the pottery is "
         "given as 4th century in association but 3rd century in the fill. All "
         "readings preserved. The excavators also note the ceramic building "
         "material does not appear to originate from the Norton Disney villa, "
         "which weakens the association with the villa"),
        ("RD-0005", "EV027",
         "Fill of the feature contained bone, ceramic building material and "
         "3rd century pottery; 4th century Roman pottery is reported in "
         "association with the object",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "No functional equipment of any kind was recovered with it - no "
         "poles, cordage tools, textile equipment, weapons or instruments"),
        ("RD-0005", "EV029",
         "Associated with 4th century pottery; deposition estimated at about "
         "1700 years before the 2023 excavation; the pit fill contained 3rd "
         "century pottery",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "The 3rd-century fill and 4th-century association are not reconciled "
         "in the source and are recorded as stated"),
        ("RD-0005", "EV012",
         "Well cast, complete with no damage, in excellent condition; an "
         "example of very fine craftsmanship, finished to a high standard",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "Corroborates the batch-001 record from PUB-0008"),
        ("RD-0005", "EV018",
         "Complete with no damage and in excellent condition",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "IMPORTANT NEGATIVE: the best-preserved specimen in the database, "
         "recovered by excavation rather than from ploughsoil, shows no wear "
         "and no damage. This is the strongest single support for the "
         "corpus-level finding at EV017 and EV018, because it cannot be "
         "explained away as post-depositional loss of surface"),
        ("RD-0005", "EV041",
         "Complete and undamaged; no knob wear described",
         "B", "PUB-0042", "excavation account", None, "2026-08-08",
         "NOT a positive statement that the knobs are unworn - the account was "
         "not written to answer that question, and no magnification was used. "
         "Recorded because RD-0005 is the specimen on which EV041 could most "
         "usefully be tested: excavated, complete, uncorroded and curated"),

        # --- EV047 provenance security of the specimens that carry the data --
        ("RD-0022", "EV047",
         "No findspot of any kind. Known only from the named Henryk Klunder "
         "collection, Mainz, now in a private collection in Winterthur. "
         "Previously unpublished; published for the first time in 2025",
         "B", "PUB-0003", "34, 36", "fig 4", "2026-08-08",
         "THE LEAST SECURE SPECIMEN IN THE DATABASE, and one of only three with "
         "usable aperture measurements. Unprovenanced, privately held, and "
         "first published by a co-author who also maintains the reference "
         "catalogue. NO SUGGESTION OF INAUTHENTICITY IS MADE BY ANY SOURCE OR "
         "BY THIS PROJECT; the point is that the usual external checks - "
         "excavated context, independent publication, institutional custody - "
         "are all absent, so nothing corroborates it. It supplies the type 2a "
         "case in which all twelve faces are decorated, and one of the two "
         "apparent aperture duplicates"),
        ("RD-0035", "EV047",
         "Collection piece with no known archaeological context, in the "
         "possession of the author who published it",
         "B", "PUB-0017", "198", None, "2026-08-08",
         "Duval is a serious scholar publishing a considered method, and "
         "nothing impugns the object. But it is unexcavated and privately "
         "held, and it is the specimen that PARTLY REFUTES EV043 and that "
         "supplies the wear-appearance conflict at EV017. Two of this "
         "project's more consequential observations rest on an unprovenanced "
         "object"),
        ("RD-0034", "EV047",
         "Held by the Musee romain d'Avenches; find context not stated in the "
         "available source",
         "C", "PUB-0019", "3.2", None, "2026-08-08",
         "Institutional custody, which is the best provenance among the "
         "measured specimens, but the findspot is not recorded in the source "
         "read and the measurements reach this project at one remove. It "
         "supplies the ONLY complete twelve-aperture dataset and the sole "
         "confirmation of EV043"),
        ("RD-0020", "EV047",
         "Excavated in 1995 from a sealed destruction layer, published in a "
         "peer-reviewed excavation report, held by the Musee archeologique de "
         "Jublains",
         "A", "PUB-0010", "paras 41, 48", None, "2026-08-08",
         "THE ONLY SPECIMEN IN THE DATABASE WHOSE AUTHENTICITY IS SECURED BY "
         "CONTEXT. An object lifted from a stratified burnt layer by "
         "excavators cannot be a modern forgery. It is also, and not "
         "coincidentally, the specimen this project has most often had to fall "
         "back on"),

        # --- EV043 Aperture distinguishability, added with the deduction ----
        ("RD-0034", "EV043",
         "All twelve measured apertures are distinct: 26.5, 15.4, 18.3, 13.4, "
         "10.4, 17.6, 24.2, 20.15, 8.7, 14.5, 20.6 and 14.2 mm. The closest "
         "pair differs by 0.3 mm (14.2 and 14.5)",
         "C", "PUB-0019", "Appendix B tab B1", None, "2026-08-08",
         "THE ONLY SPECIMEN IN THE DATABASE WITH A COMPLETE APERTURE SET, and "
         "on it no two apertures are the same size. The 0.3 mm minimum "
         "separation EXCEEDS the maker's tolerance, which PUB-0019 assesses at "
         "below 0.2 mm from the same measurements - so the apertures are "
         "separated by more than the workshop's own precision limit. Whether "
         "that separation is deliberate or incidental is NOT determined by "
         "this observation"),
        ("RD-0035", "EV043",
         "Diameters are duplicated: 22 mm on three faces, 20 mm on two and "
         "14 mm on two. The engraved rings partly compensate - the two 14 mm "
         "apertures carry 4 and 6 fillets respectively - but the three 22 mm "
         "apertures are all recorded with 3 fillets",
         "B", "PUB-0017", "200", "fig 3", "2026-08-08",
         "COUNTER-CASE TO RD-0034, and the reason this variable is worth "
         "having. Where diameter fails to distinguish two apertures, ring "
         "count does so for the 14 mm pair and does NOT for the 22 mm group. "
         "Duval's per-face diameters are on fig 3, which is not legible in the "
         "available scan, so this rests on his running text alone"),
        ("RD-0022", "EV043",
         "Two of the four recorded apertures are given as 15 mm, in different "
         "opposed pairs (15/17 and 14/15)",
         "B", "PUB-0003", "36", "fig 4", "2026-08-08",
         "WEAK: the source records only four apertures individually and gives "
         "the remaining eight as a range, and the figures are stated to the "
         "nearest 0.5 cm in places. An apparent duplicate at this resolution "
         "does not establish that two apertures were indistinguishable"),

        # --- Batch 005: museum collection records --------------------------
        ("RD-0037", "EV014",
         "Ten faces decorated with concentric circles of varying size; two "
         "faces remain smooth",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08",
         "INDEPENDENT CORROBORATION OF THE TEN-OF-TWELVE RULE, from a museum "
         "record unconnected to PUB-0003, PUB-0010 or PUB-0017. Until now that "
         "rule rested on one corpus statement plus two specimens. This is the "
         "second source the evidence-base audit identified as missing"),
        ("RD-0037", "EV046",
         "The museum records the height as 7.1 cm 'between the smooth faces', "
         "which implies the two undecorated faces lie opposite one another",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08",
         "INDEPENDENT CORROBORATION OF THE MARKED AXIS. The phrasing is the "
         "museum's own and was not written to make any point about "
         "orientation, which makes it good evidence. EV046 remains "
         "non-discriminating because it still describes the same physical "
         "feature as EV013; a second source removes the single-voice problem "
         "but not the double-counting one"),
        ("RD-0037", "EV016",
         "Hollow cast, with the knobs attached by soldering",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08",
         "SECOND INDEPENDENT SOURCE FOR SOLDERED KNOBS, after PUB-0010 para 48 "
         "on the Jublains specimen. This weakens the conflict previously "
         "recorded against the PAS description of RD-0014 as cast in one "
         "piece: two institutional records now describe separately attached "
         "knobs"),
        ("RD-0037", "EV001",
         "Height 7.1 cm between the smooth faces including the feet, 6.2 cm "
         "without the feet; width 8.2 cm; depth 8.5 cm",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08",
         "The 6.2 / 7.1 / 8.2 / 8.5 cm spread on a single object is a further "
         "instance of the departure from regular geometry recorded at EV010"),
        ("RD-0037", "EV011",
         "Bronze",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08", None),
        ("RD-0037", "EV025",
         "Provenance given as France (?), attributed to Gaul (?); purchased "
         "1825 from the Durand collection",
         "B", "PUB-0044", "ED 4271", None, "2026-08-08",
         "Both queries are the museum's own. No findspot; an early-19th-century "
         "collection purchase"),

        ("RD-0038", "EV001", "Height 7.5 cm",
         "C", "PUB-0045", None, None, "2026-08-08",
         "Via search-engine extract; the museum page returned HTTP 403"),
        ("RD-0038", "EV025",
         "Found at Elst, Overbetuwe, Gelderland; donated to the museum in "
         "November 1876",
         "C", "PUB-0045", None, None, "2026-08-08",
         "First Netherlands findspot in the database. The Netherlands is named "
         "in PUB-0010 among the countries of the known distribution but was "
         "unrepresented here"),
        ("RD-0038", "EV029",
         "Museum dating: Roman period, 1-300 AD",
         "C", "PUB-0045", None, None, "2026-08-08",
         "CONFLICTS WITH EV029, which records the corpus window as c AD 200 to "
         "the late 4th century. Museum period ranges are commonly loose and "
         "this is recorded as a conflict, not as a correction to the corpus "
         "chronology"),

        ("RD-0039", "EV025",
         "Findspot given by the museum as Reims (?), Marne; from the Joseph de "
         "Baye collection",
         "C", "PUB-0046", None, None, "2026-08-08",
         "The query is the museum's own"),
        ("RD-0039", "EV030",
         "The Musee d'Archeologie nationale holds four dodecahedra",
         "C", "PUB-0046", None, None, "2026-08-08",
         "RELEVANT TO EV030, which has no corpus observation. Four specimens "
         "in one institution is a collection fact, not a site fact, and does "
         "NOT bear on whether multiple specimens occur at one findspot. "
         "Recorded because three of those four are not yet in this database"),

        # --- Batch 006: records supplied by the project owner --------------
        ("RD-0001", "EV010",
         "Each of the twelve faces is 38 mm in length and width; plate "
         "thickness 3 mm; knobs roughly 9 mm high and 9 to 10 mm in diameter; "
         "maximum diameter 82 mm",
         "B", "PUB-0006", "BH-692011", None, "2026-08-08",
         "Full PAS record, supplied directly. Adds face dimensions and "
         "confirms the figures previously recorded. The record also states "
         "Preservation grade 2, method of manufacture Cast, completeness "
         "Complete, and flags the find as of note with potential for "
         "inclusion in Britannia"),
        ("RD-0001", "EV007",
         "All of the apertures have slightly bevelled rounded edges",
         "B", "PUB-0006", "BH-692011", None, "2026-08-08",
         "FIRST OBSERVATION FOR EV007, which had none. Bears on prediction "
         "P-0005, which expects bevelled rather than square-cut lips"),
        ("RD-0001", "EV029",
         "Dated by the recorder to the Roman period as a whole, AD 43-410",
         "B", "PUB-0006", "BH-692011", None, "2026-08-08",
         "A default period range for an unstratified detector find, not an "
         "independent dating. It should not be read as widening the corpus "
         "window recorded at EV029"),

        ("RD-0015", "EV029",
         "Dated by the aggregator record to AD 301-399",
         "C", "PUB-0047", "I.7108", None, "2026-08-08",
         "FIRST DATING FOR THIS SPECIMEN. Consistent with the corpus window"),
        ("RD-0015", "EV011",
         "Material given as lead and bronze",
         "C", "PUB-0047", "I.7108", None, "2026-08-08",
         "Corroborates the PUB-0011 record and, with the 18 per cent lead "
         "measured on RD-0005, supports the reading of the alloy as a casting "
         "alloy rather than a structural bronze"),

        ("RD-0038", "EV004",
         "Each face carries one hole, and the holes are of differing size; "
         "knobs at the intersections",
         "B", "PUB-0045", None, None, "2026-08-08",
         "The museum's own description. Independent corroboration of the "
         "one-aperture-per-face rule and of size variation within an object"),
        ("RD-0038", "EV047",
         "Found at Elst; catalogued as Guggenberger no 75, type 2a, year of "
         "discovery 1875; donated to the museum in November 1876; inventory "
         "number ENc",
         "B", "PUB-0023", "no 75", None, "2026-08-08",
         "Provenance secured by two independent records agreeing on findspot "
         "and date: the reference catalogue gives discovery in 1875 and the "
         "museum gives donation in November 1876"),

        ("RD-0040", "EV014",
         "Rings are engraved as a group at the PERIPHERY of each face, close to "
         "the pentagon edges, with a broad plain annulus between the aperture "
         "and the innermost ring. Counted from the photograph, faces with "
         "larger apertures carry fewer rings, about two, and faces with smaller "
         "apertures carry more, about three to four. The uppermost face in the "
         "image appears plain",
         "D", "PUB-0048", None, "Europeana 325/HCM157", "2026-08-09",
         "COUNTED FROM A PHOTOGRAPH at oblique angles; the counts are "
         "approximate and the faces away from the camera cannot be read at all. "
         "Two points are nonetheless legible. The rings are placed relative to "
         "the FACE EDGE rather than packed outward from the aperture, which is "
         "what EXP-0005 predicts if the engraver works inward from the "
         "geometric limit. And the inverse relation between aperture size and "
         "ring count follows the Vienne rule (RD-0035) rather than the constant "
         "count of Jublains (RD-0020). The apparently plain uppermost face is "
         "consistent with the undecorated opposed pair, but only one of the two "
         "is visible so this cannot be confirmed"),

        # --- EV041 knob wear: assessment from photographs -------------------
        # These are the first observations in the project made from images
        # rather than from a publication. They are graded D and the reasoning
        # is set out in full, because surface condition read from a photograph
        # by a non-specialist is the weakest evidence the project holds.
        ("RD-0040", "EV041",
         "Bright, unpatinated yellow metal is exposed on the crown of every "
         "visible knob, against a dark green-brown patina covering all faces, "
         "recesses and engraved rings. The exposure is confined to the "
         "outermost point of each knob and is consistent across all knobs "
         "regardless of their orientation in the photograph",
         "D", "PUB-0048", None, "Europeana 325/HCM157", "2026-08-09",
         "OBSERVED FROM A PHOTOGRAPH, NOT FROM THE OBJECT, AND BY A "
         "NON-SPECIALIST. What is certain is that patina has been lost "
         "preferentially from the high points. What that means is NOT settled "
         "by the image, and the most economical explanation is not ancient "
         "use. PATINA FORMS DURING BURIAL. Wear inflicted in antiquity, before "
         "deposition, would have been covered by burial patina and would not be "
         "bright today. Bright metal therefore indicates patina removed AFTER "
         "excavation - by cleaning, polishing, mounting or handling. This is a "
         "collection piece with no findspot, acquired before 1985, which is "
         "precisely the class of object that gets polished. "
         "THE COUNTER-ARGUMENT, which the image cannot settle: wear leaves a "
         "SHAPE signature as well as a colour one. Flattening or facetting of "
         "the knob crowns beyond their cast form would survive burial and "
         "repatination and could not be produced by dusting. Several crowns "
         "appear broad and flat in the image, but that cannot be separated "
         "from casting form and lighting at this resolution. "
         "WHAT WOULD SETTLE IT: whether any polish is directional, whether it "
         "cuts through corrosion products or underlies them, and whether the "
         "crown profile departs from the cast form of the unworn knobs"),
        ("RD-0001", "EV041",
         "In six published views the knobs are covered by the same mid-green "
         "corrosion and pale mineral encrustation as the rest of the object; "
         "no bright metal is exposed anywhere. Reddish cuprite shows where the "
         "outer layer has been lost on several knobs",
         "D", "PUB-0006", "BH-692011", "docs/sources/Roman dodecahedron.jpg", "2026-08-09",
         "OBSERVED FROM PHOTOGRAPHS. THE CONTROL CASE, and the reason the "
         "RD-0040 image is worth recording at all. This specimen is a "
         "ploughsoil metal-detector find that has not been polished, and its "
         "knobs are indistinguishable in surface condition from its faces. The "
         "contrast with RD-0040 shows that bright knob crowns are not simply "
         "how a bronze dodecahedron looks, but it equally shows what an "
         "uncleaned specimen looks like - which is the state in which the "
         "microwear question must be asked. NOTE the tension with the PAS "
         "record's own wording for this object, which reports 'several areas of "
         "abrasion around the base of most knops': at photographic resolution "
         "that abrasion is not distinguishable from the general corrosion and "
         "plough damage the same record describes"),

        # --- EV041 Knob wear: the variable added with H012 ------------------
        # These are re-readings of PAS descriptions already held under EV018
        # and EV022, recorded again under EV041 because knob wear is a
        # different question from face wear and was not separable before.
        ("RD-0001", "EV041",
         "Abrasion present around the base of most knobs",
         "B", "PUB-0006", "BH-692011", None, "2026-08-08",
         "THE ONLY POSITIVE KNOB-WEAR RECORD IN THE CORPUS, and the reason "
         "EV041 was created. The corpus-wide statement that the surfaces "
         "generally do not look worn (PUB-0003, 45) was made about faces and "
         "interiors; it does not address the knobs and their necks. Whether "
         "this abrasion is use wear or post-depositional damage is NOT "
         "determined - the same record describes several faces as pitted or "
         "gouged and the patina as patchy, which points to ploughing and "
         "corrosion. Recorded as an open question, not as evidence of use"),
        ("RD-0002", "EV041",
         "One knob broken off and retained loose; remaining knobs intact; "
         "no wear described",
         "B", "PUB-0006", "YORYM-41CD72", None, "2026-08-08",
         "Absence of a wear description is not a negative observation; the PAS "
         "record was not made to answer this question"),
        ("RD-0013", "EV041",
         "Knob diameters 14.28, 13.92, 13.46 and 14.01 mm across four "
         "fragments; no wear or asymmetry described",
         "B", "PUB-0006", "LIN-8BA9C4", None, "2026-08-08",
         "Recorded because closely matched knob diameters across fragments of "
         "one object bear on EV009 and would also bear on differential wear, "
         "had any been described"),

        # --- RD-0029 Carmarthenshire: holding institution ------------------
        ("RD-0029", "EV025",
         "One of the best British examples is in the Society of Antiquaries "
         "collection, from Carmarthen",
         "B", "PUB-0016", "273", None, "2026-08-07",
         "Corroborates the SAL photograph credit in PUB-0003, 35 fig 3. The "
         "same note records that a further Welsh dodecahedron was communicated "
         "on 12 March 1846 by the Rev Edward Harries of Llandysilio and is "
         "no 41 in de Saint-Venant's list; only the first page of the note is "
         "available, so that specimen is NOT matched to an RD_ID"),
    ]
    cur.executemany(
        """INSERT INTO artifact_observations
           (rd_id, ev_id, observed_value, confidence, source_id, page, figure,
            extraction_date, notes)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        OBSERVATIONS
    )

    cur.executemany(
        """INSERT INTO corpus_observations
           (ev_id, statement, direction, confidence, evidence_class,
            discriminating, source_id, page, figure, extraction_date, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        CORPUS_OBSERVATIONS
    )

    for ev_id, cluster in EVIDENCE_CLUSTERS.items():
        cur.execute("UPDATE corpus_observations SET evidence_cluster=? "
                    "WHERE ev_id=?", (cluster, ev_id))

    cur.executemany(
        "INSERT INTO predictions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        PREDICTIONS
    )

    cur.executemany(
        "INSERT INTO experiments VALUES (?,?,?,?,?,?)",
        EXPERIMENTS
    )

    cur.executemany(
        "INSERT INTO utility_assessments VALUES (?,?,?,?,?,?,?,?)",
        UTILITY
    )

    cur.executemany(
        "INSERT INTO specimen_quality VALUES (?,?,?,?,?,?,?,?,?)",
        SPECIMEN_QUALITY
    )

    cur.executemany(
        "INSERT INTO screening_candidates VALUES (?,?,?,?,?,?)",
        SCREENING_CANDIDATES
    )
    cur.executemany(
        "INSERT INTO screening VALUES (?,?,?,?,?)",
        SCREENING
    )

    cur.executemany(
        "INSERT INTO evidence_register VALUES (?,?,?,?,?,?,?)",
        [row[:7] for row in INTERPRETATIONS]
    )
    cur.executemany(
        "INSERT OR IGNORE INTO evidence_sources VALUES (?,?)",
        [(row[0], row[7]) for row in INTERPRETATIONS]
    )

    conn.commit()

    print(f"Database: {DB_PATH}")
    for table in ["sources", "hypotheses", "evidence_variables",
                  "evidence_register", "evidence_sources", "hpm",
                  "specimens", "artifact_observations", "corpus_observations",
                  "hdm_scores", "results", "predictions",
                  "experiments", "screening_candidates", "screening",
                  "utility_assessments", "specimen_quality"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {n:4d} rows")

    conn.close()


if __name__ == "__main__":
    build_database()
