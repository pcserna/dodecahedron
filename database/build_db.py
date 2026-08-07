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

DROP TABLE IF EXISTS hdm_scores;
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
    evidence_type       TEXT CHECK(evidence_type IN ('Observed','Constraint','Derived','Experimental')),
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

-- Hypothesis Discrimination Matrix: actual scored agreement of artifact evidence with each hypothesis
CREATE TABLE hdm_scores (
    hypothesis_id   TEXT    NOT NULL REFERENCES hypotheses(hypothesis_id),
    ev_id           TEXT    NOT NULL REFERENCES evidence_variables(ev_id),
    score           INTEGER CHECK(score BETWEEN -2 AND 2),
    confidence      TEXT CHECK(confidence IN ('A','B','C','D','E')),
    notes           TEXT,
    PRIMARY KEY (hypothesis_id, ev_id)
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
    ("PUB-0003", "Guggenberger & Leach", 2025,
     "The Gallo-Roman Dodecahedron and the Receptacle of All Becoming",
     "Journal", "10.1017/S000358152510036X", None, "B",
     "The Antiquaries Journal 105: 31-54; recent synthesis"),
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
     "Journal", "10.4000/rao.680", None, "A",
     "Revue archeologique de l'Ouest 25: 269-289; first dodecahedron in secure excavation context"),
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
     "Roman dodecahedron from Wales",
     "Journal", "10.1017/S0003581500091459", None, "B",
     "Antiquaries Journal, July 1924; likely primary publication of Fishguard (BM 1924,0411.1) specimen"),
    ("PUB-0017", "Duval, Paul-Marie", 1981,
     "Comment decrire les dodecaedres gallo-romains, en vue d'une etude comparee",
     "Journal", "10.3406/galia.1981.1829",
     "https://www.persee.fr/doc/galia_0016-4119_1981_num_39_2_1829",
     "B",
     "Gallia 39(2): 195-200; defines measurement protocol for comparative study; KEY METHODOLOGICAL PAPER"),
    ("PUB-0018", "Greiner, Bernhard A.", 1996,
     "Romische Dodekaeder: Untersuchungen zur Typologie, Herstellung, Verbreitung, und Funktion",
     "Journal", None, None, "B",
     "Carnuntum Jahrbuch 1995: 9-44; German analysis of typology, manufacture, distribution, function"),
    ("PUB-0019", "Sparavigna, Amelia Carolina", 2012,
     "Roman dodecahedron as dioptron: analysis of freely available data",
     "Preprint", "10.48550/arXiv.1206.0946",
     "https://arxiv.org/abs/1206.0946",
     "D",
     "arXiv:1206.0946; analyzes hole diameter data from freely available sources; argues for rangefinder use"),
    ("PUB-0020", "Hill, Christopher", 1994,
     "Gallo-Roman Dodecahedra: A Progress Report",
     "Journal", "10.1017/s0003581500024458", None, "B",
     "Antiquaries Journal 74: 289-292; review article with Carmarthen/SAL specimen data"),
    ("PUB-0021", "Guggenberger, Michael", 2013,
     "The Gallo-Roman Dodecahedron",
     "Journal", "10.1007/s00283-013-9403-7", None, "B",
     "Mathematical Intelligencer 35(4): 56-60; overview with specimen data; first recorded specimen documented"),
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
        HPM_DATA
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
         None, "PUB-0008", "C", None, None,
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
         None, "PUB-0007", "A", None, None,
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
        ("RD-0020", "Jublains (thermal baths) dodecahedron",
         "Jublains (Noeodunum), Mayenne", "France", "Gallia Lugdunensis",
         "Civilian", None, None,
         "Musee archeologique de Jublains", "Jublains", "France",
         None,
         "Copper alloy", None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None,
         None, "PUB-0010", "A", None, None,
         "Source: Guillier, Delage & Besombes 2008, RAO 25: 269-289; "
         "found at edge of Roman thermal baths (bord des thermes) at Jublains; "
         "Jublains is the Roman civitas capital Noeodunum of the Aulerci Diablintes; "
         "this is the only Roman dodecahedron from a verified, controlled excavation context; "
         "measurements not accessible from available online sources; "
         "context: civilian public baths complex, not military"),

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
    ]
    cur.executemany(
        """INSERT INTO specimens VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )""",
        SPECIMENS
    )

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
    ]
    cur.executemany(
        """INSERT INTO artifact_observations
           (rd_id, ev_id, observed_value, confidence, source_id, page, figure,
            extraction_date, notes)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        OBSERVATIONS
    )

    conn.commit()

    print(f"Database: {DB_PATH}")
    for table in ["sources", "hypotheses", "evidence_variables",
                  "evidence_register", "evidence_sources", "hpm",
                  "specimens", "artifact_observations", "hdm_scores"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {n:4d} rows")

    conn.close()


if __name__ == "__main__":
    build_database()
