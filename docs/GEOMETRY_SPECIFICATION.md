---
Document ID: RDORP-011
Title: Geometry Specification and Face-Ordering Convention
Version: 0.1.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-07
Last Updated: 2026-08-07
Related Documents:
  - RDORP-004 Database Schema
  - RDORP-010 Analytical Method
---

# Geometry Specification and Face-Ordering Convention

## 1. Purpose

RDORP-004 section G stores twelve face measurements per specimen and states
that, where orientation is unknown, numbering follows "the project's standard
face-ordering convention (defined separately in the Geometry Specification)".
That specification did not exist. This document supplies it.

Without a convention, `hole_01_mm` through `hole_12_mm` are not comparable
between specimens and no statement about opposite-hole relationships (EV005),
hole distribution (EV004), face symmetry (EV010) or standardisation (EV039)
can be tested across the corpus.

---

## 2. The convention

RDORP adopts the convention published by **Paul-Marie Duval, "Comment décrire
les dodécaèdres gallo-romains, en vue d'une étude comparée", *Gallia* 39(2),
1981, 195–200** (source `PUB-0017`). It is adopted rather than invented
because it is already in use — the excavators of the Jublains specimen drew
their record "selon les préconisations de Paul-Marie Duval" (`PUB-0010`,
para 49) — and because a shared convention is worth more than a better one
nobody else follows.

### 2.1 Numbering the faces

1. **Face 1** is the face with the opening of maximum diameter. If more than
   one face shares that maximum, one of them is chosen arbitrarily and the
   choice is recorded in the specimen notes.
2. The dodecahedron is set down on the face **opposite** face 1.
3. Viewed from above, the object presents two superimposed sets of six faces.
   Duval calls them the **upper half (A)** and the **lower half (B)**. Each
   half has one horizontal face and five oblique faces.
4. **Face 2** is the upper face whose opening diameter comes second in
   decreasing order. Ties are again broken arbitrarily and recorded.
5. Faces **2, 3, 4, 5, 6** follow **anticlockwise** when viewed from above.
6. The face opposite face *n* is numbered ***n'***. Viewed from above through
   the openings, faces 2', 3', … also run anticlockwise.
7. The twenty vertices are lettered **a–j** and **a'–j'**, anticlockwise.
   On knobbed specimens these are the knobs.

### 2.2 Mapping to the database

| Duval face | Column |
| ---------- | ------ |
| 1  | `hole_01_mm` |
| 2  | `hole_02_mm` |
| 3  | `hole_03_mm` |
| 4  | `hole_04_mm` |
| 5  | `hole_05_mm` |
| 6  | `hole_06_mm` |
| 1' | `hole_07_mm` |
| 2' | `hole_08_mm` |
| 3' | `hole_09_mm` |
| 4' | `hole_10_mm` |
| 5' | `hole_11_mm` |
| 6' | `hole_12_mm` |

**Opposite pairs are therefore `hole_0n_mm` and `hole_0(n+6)_mm`.** This is
what makes EV005 computable directly from the specimen table.

A specimen whose measurements were published without this convention, and
which cannot be re-examined, must have its hole columns left NULL and its
values recorded as text in `artifact_observations`. Assigning published
diameters to face numbers by guesswork would fabricate the very relationships
EV005 is meant to test.

---

## 3. Recording a specimen

Duval's method has two outputs, and both are required for a complete record.

1. **Schematic plan.** The two halves are drawn separately, flattened, so
   that opposite vertices of opposite faces point in opposite directions.
2. **Facsimile at constant scale**, preferably 1:1, showing each face with all
   ornamental detail and the exact placement of concentric circles, arranged
   in two columns so that faces *n* and *n'* can be compared directly.

The two representations are kept distinct: one schematic, one realistic.

---

## 4. Measurements to record

| Quantity | Unit | Notes |
| -------- | ---- | ----- |
| Overall diameter excluding knobs | mm | Face to opposite face. Record the range if it varies by axis. |
| Overall diameter including knobs | mm | |
| Height as the object stands | mm | May differ from face-to-face diameter. |
| Edge length of a pentagonal face | mm | |
| Hole diameter, per face | mm | Following section 2. Record two values where the opening is not circular. |
| Wall thickness | mm | Record range if it varies. |
| Knob diameter | mm | Record whether knobs are uniform. |
| Mass | g | |
| Number of concentric circles, per face | count | |

**Where a source gives a range rather than a value, the range is recorded as
an observation and the numeric column is left NULL.** Midpoints are never
computed. This rule is enforced by `database/validate.py`.

---

## 5. Known departures from regular geometry

Recorded here because they are the reason a convention is necessary, and
because they are themselves evidence (EV010).

- The Jublains specimen (`RD-0020`) measures 48–52 mm face to face depending
  on the axis chosen, and two of its twelve openings are oval (21 × 26 mm)
  rather than circular (`PUB-0010`, para 48).
- On the Avenches specimen (`RD-0034`), five of twelve holes are recorded with
  two differing diameters and a sixth is described as probably elliptic
  (`PUB-0019`, Appendix B).
- Across the corpus, the most common type has ten round holes plus one opposed
  pair that is "not so perfectly round and often larger", generally explained
  as production holes (`PUB-0003`, 32).

Consequently, "the diameter" of a dodecahedron is not a single number, and any
analysis that treats it as one is unsound.

---

## 6. Open question this convention exists to answer

Duval's own statement of the problem, still unanswered (`PUB-0017`, 195):

> Is there a rhythm in these openings, in their juxtaposition or in their
> opposition? Do the ornaments that accompany them — concentric circles or
> small circles, in variable number — obey a significant distribution? The
> answer to these questions has never been given, nor even sought, for want of
> flat records made with clarity and founded on a single principle.

As of this version the database holds complete or near-complete hole sets for
five specimens. That is not enough to answer him.

---

## 7. Revision History

| Version | Date       | Description                                        |
| ------- | ---------- | -------------------------------------------------- |
| 0.1.0   | 2026-08-07 | Initial specification; adopts Duval 1981.          |
