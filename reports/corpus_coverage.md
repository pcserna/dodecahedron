# Corpus Coverage and Representativeness

| Field | Value |
| ----- | ----- |
| Document ID | RDORP-COV |
| Generated | 2026-08-10 |
| Database | `database\rdorp.sqlite` |
| Generator | `database/reports.py` |

Generated file. Do not edit by hand: change the master data in `database/build_db.py` and re-run `python run_pipeline.py`.

## 1. Coverage

- Specimens recorded: **57**
- Known corpus: about **134** (PUB-0003, 32)
- Coverage: **43 per cent**

## 2. Geographic representativeness

The known corpus is about 70 per cent Gallic and Germanic and about 20 per cent British (PUB-0003, 32). The recorded corpus is compared with that below.

| Country | Recorded | Share |
| ------- | -------- | ----- |
| United Kingdom | 23 | 40% |
| Germany | 10 | 18% |
| France | 10 | 18% |
| Switzerland | 5 | 9% |
| Unknown | 2 | 4% |
| Netherlands | 2 | 4% |
| Belgium | 2 | 4% |
| Serbia | 1 | 2% |
| Hungary | 1 | 2% |
| Austria | 1 | 2% |

## 3. Archaeological context

The known corpus, among specimens with a recorded find location, is more than half settlements, just under one-fifth military camps, c 8.5 per cent sacred, c 7 per cent graves, c 5.5 per cent pits and wells, c 4 per cent hoards and c 4 per cent rivers (PUB-0003, 33).

| Context category | Recorded |
| ---------------- | -------- |
| Unknown | 43 |
| Military | 4 |
| Temple | 2 |
| Settlement | 2 |
| Hoard | 2 |
| Grave | 2 |
| Civilian | 2 |

## 4. Source confidence of recorded specimens

| Grade | Specimens |
| ----- | --------- |
| A | 2 |
| B | 17 |
| C | 18 |
| D | 19 |
| E | 1 |

## 5. Observation density per evidence variable

| EV | Variable | Power | Specimen observations |
| -- | -------- | ----- | --------------------- |
| EV001 | Overall dimensions | High | 12 |
| EV002 | Mass | High | 16 |
| EV003 | Wall thickness | High | 6 |
| EV004 | Hole diameter distribution | Very High | 17 |
| EV005 | Opposite-hole relationships | Very High | 8 |
| EV006 | Hole profile | High | 5 |
| EV007 | Hole edge radius | Medium | 1 |
| EV008 | Knob diameter | Medium | 9 |
| EV009 | Knob symmetry | Medium | 2 |
| EV010 | Face symmetry | High | 2 |
| EV011 | Alloy composition | High | 6 |
| EV012 | Casting quality | High | 12 |
| EV013 | Casting defects | High | 1 |
| EV014 | Surface finishing | Medium | 11 |
| EV015 | Repair evidence | Medium | 2 |
| EV016 | Tool marks | High | 3 |
| EV017 | Internal hole wear | Very High | 2 |
| EV018 | External wear | High | 5 |
| EV019 | Rope wear | Very High | 0 |
| EV020 | Rotational wear | Very High | 0 |
| EV021 | Impact damage | Medium | 0 |
| EV022 | Abrasion | Medium | 1 |
| EV023 | Thermal alteration | Very High | 0 |
| EV024 | Residues | Very High | 1 |
| EV025 | Site type | Very High | 42 |
| EV026 | Roman province | Medium | 6 |
| EV027 | Associated finds | Very High | 6 |
| EV028 | Stratigraphy | High | 2 |
| EV029 | Dating | Very High | 11 |
| EV030 | Number at site | Medium | 1 |
| EV031 | Military association | High | 4 |
| EV032 | Ritual association | High | 3 |
| EV033 | Rod compatibility | Very High | 4 |
| EV034 | Rope compatibility | Very High | 2 |
| EV035 | Structural stability | Very High | 1 |
| EV036 | Load transfer | High | 1 |
| EV037 | Assembly potential | High | 1 |
| EV038 | Orientation dependence | High | 0 |
| EV039 | Standardisation | High | 2 |
| EV040 | Regional variation | High | 1 |
| EV041 | Knob wear | Very High | 6 |
| EV042 | Microwear location | Very High | 0 |
| EV043 | Aperture distinguishability | Very High | 3 |
| EV044 | Interior finish and marking | High | 0 |
| EV045 | Manufacturing difficulty | Very High | 0 |
| EV046 | Marked axis | Very High | 1 |
| EV047 | Authenticity and provenance security | Very High | 5 |
| EV048 | Within-type standardisation | Very High | 0 |

## 6. What would most improve the corpus

1. **Consult PUB-0022 (Guggenberger 1999) directly.** Almost every corpus-level value currently in the database is taken from PUB-0003 citing it at one remove. It also holds the per-specimen measurement tables that would populate the geometry variables properly.
2. **Add continental specimens with measurements.** The recorded corpus is skewed towards British metal-detector finds, which carry measurements but almost no archaeological context.
3. **Obtain microscopic wear analysis on any specimen.** This is the single largest evidence gap and the source of the most discriminating result currently in the database.
4. **Obtain residue analysis.** EV023 and EV024 are both rated Very High and are deliberately unscored because no reliable analysis exists.
