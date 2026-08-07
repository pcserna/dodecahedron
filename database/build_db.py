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
     "Journal", None, None, "B",
     "Recent synthesis of evidence and hypotheses"),
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
    ("PUB-0006", "Portable Antiquities Scheme / ADS", 2024,
     "Roman Dodecahedra finds — ADS / PAS database",
     "Database", None,
     "https://archaeologydataservice.ac.uk",
     "B",
     "Archaeological dataset; primary source for British finds and context data"),
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
