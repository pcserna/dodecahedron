# Task prompt — independent direction rating (RDORP-013 item A3, part 2)

**Run this in a fresh session, ideally with a different person or model from
the one that wrote the observations.**

---

## The blindfold, and why it points this way

Every corpus observation in this project carries a **statement** (what a source
says) and a **direction** (how this project reads that statement). The
statement is evidence. The direction is a judgement, and it was made by the
same party that wrote the hypotheses, assigned the confidences and computed
the scores. Nobody has ever checked it.

You are the check. You will see the statements. You must **not** see the
hypotheses, the scores, or the reasoning already recorded.

**Do not open, read, grep or query any of the following:**

- `docs/RDORP-012_Results_Summary.md`, `docs/RDORP-013_Hardening_Plan.md`
- `reports/` — any file
- the `hypotheses`, `hpm`, `hdm_scores`, `results`, `hpm_readings`,
  `screening`, `utility_assessments` tables
- the `notes`, `direction`, `confidence` or `evidence_class` columns of
  `corpus_observations`
- `database/build_db.py`

You do not need the repository. Everything is in this file.

**Do not try to work out which hypothesis a direction would favour.** If you
find yourself wondering whether a rating helps or hurts some theory, you have
drifted outside the task. Rate the statement against the variable definition
and nothing else.

---

## What you are deciding

For each item you get a variable, its definition, and a sourced statement about
the corpus of Roman dodecahedra. Decide how the statement bears on that
variable, on this scale:

| Direction | Meaning |
| --------- | ------- |
| `confirmed` | The property named by the variable is present as a corpus-wide rule |
| `weak_confirmed` | Present, but only in a minority of cases |
| `ambiguous` | Evidence exists but does not decide |
| `weak_absent` | Fails as a general rule, but holds in some cases |
| `absent` | The property is not present |

Then give a **source confidence A–E**:

| Grade | Meaning |
| ----- | ------- |
| A | Excavated, stratified, peer-reviewed primary report |
| B | Museum or catalogue record, authoritative synthesis |
| C | Peer-reviewed secondary, or a record reaching you at one remove |
| D | Non-peer-reviewed, or values read off a figure, or at two removes |
| E | General web source |

Judge the confidence from what the statement itself reveals about its basis.
Where a statement rests on an absence of reports rather than on examination,
say so — that is exactly the kind of thing this exercise exists to catch.

---

## Guidance

- **Rate the statement, not the topic.** "No rope wear is reported anywhere"
  is not the same evidential act as "the surfaces were examined and no rope
  wear was found." Grade accordingly.
- **A minority is not a rule.** If a statement says a property holds in a fifth
  of cases, `weak_confirmed` is the honest rating, not `confirmed`.
- **`ambiguous` is a real answer.** Use it where the statement genuinely does
  not decide, rather than forcing a direction.
- Work through in order. Do not revise earlier ratings after seeing later ones.

---

## The items

### EV001 — Overall dimensions

*Definition: Overall height, width and bounding dimensions*

> Diameter from face to opposite face varies from 4 cm to c 10 cm excluding
> knobs, and up to c 11 cm including knobs, across the whole corpus

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV003 — Wall thickness

*Definition: Average and local wall thickness*

> Wall thickness across the corpus is 0.5-4 mm; the source describes the
> objects as 'remarkably thin-walled'

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV004 — Hole diameter distribution

*Definition: Diameters of all 12 openings*

> Hole diameters vary from 0.6 cm to 4 cm; the largest hole of a specimen lies
> between 1.7 and 4 cm and the smallest between 0.6 and 2.8 cm. Every
> sufficiently complete specimen shows holes of differing size

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV005 — Opposite-hole relationships

*Definition: Pairing and correspondence of opposite holes*

> The difference in diameter within a pair of opposite holes is statistically
> between c 0.2 cm and c 0.45 cm; some dodecahedra have pairs of approximately
> the same diameter, whereas others have very different diameters. Measured
> pairs now in the database bear this out: Avenches (RD-0034) has no equal
> pair and two pairs differing by more than 9 mm; Vienne (RD-0035) has two
> exactly equal pairs but, in the words of the author who devised the
> comparative recording method, no evident regularity otherwise; Jublains
> (RD-0020) has four near-equal pairs and two differing by 4 and 6.5 mm;
> Carnuntum (RD-0036) differs by 0.2-2.5 mm and Tongres (RD-0006) by 0.2-4 mm

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV006 — Hole profile

*Definition: Cylindrical, tapered or irregular*

> The most common type (Greiner/Guggenberger 1a) has ten perfectly round
> holes; the remaining opposite pair is less perfectly round and often larger

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV008 — Knob diameter

*Definition: Diameter of vertex knobs*

> Knobs are all of the same size within a given object, with a broad range of
> diameters from object to object

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV009 — Knob symmetry

*Definition: Regularity of knob placement*

> Almost all specimens carry twenty knobs, one at each vertex; knobs within an
> object are all of the same size; one specimen (Guggenberger no 66) has three
> knobs at each vertex; knobs are never pointed or intentionally faceted;
> there is no specimen without knobs

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV010 — Face symmetry

*Definition: Deviation from regular geometry*

> The objects depart measurably from regular geometry. On the only stratified
> specimen the face-to-opposite-face distance itself varies from 48 to 52 mm
> depending on which axis is measured, and two of its twelve openings are oval
> (21x26 mm) rather than circular. On the most precisely measured specimen,
> five of twelve holes are recorded with two differing diameters and a sixth
> is described as probably elliptic

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV011 — Alloy composition

*Definition: Chemical composition*

> The objects are made of copper alloy (eg bronze). XRF on Norton Disney gives
> Cu 75 percent, Sn 7 percent, Pb 18 percent; the Musee Curtius specimen is
> recorded as bronze and lead

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV012 — Casting quality

*Definition: General casting quality*

> Some specimens were difficult to cast; many dodecahedra from Roman Britain
> 'do not appear to be so skilfully designed' and may be local imitations.
> British PAS specimens consistently show a roughly cast, unfinished interior
> with a smoother exterior

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV013 — Casting defects

*Definition: Voids, seams, miscasts*

> About 70 per cent of specimens carry production holes (Produktionsloecher);
> the opposite pair of holes without engraved circles is not perfectly round
> and is often larger than the rest, which is in most cases explained by the
> production process

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV014 — Surface finishing

*Definition: Grinding, polishing, scraping*

> COVERAGE: the commonest type (Greiner/Guggenberger 1a) carries engraved
> circles around TEN of its twelve faces; the remaining two, an opposed pair,
> carry none and are the production holes. Confirmed directly on the
> stratified specimen: 'ten of the twelve faces have their opening underlined
> by concentric circles; the other two faces have none' (RD-0020). The same
> 10-of-12 pattern holds on Guggenberger no 11 (two to five circles around ten
> of twelve) and on Vienne (RD-0035), where the two largest opposed openings
> carry no fillets. The exception is type 2a: Mainz 3 (RD-0022) carries five
> ring-and-dot motifs on ALL twelve faces. COUNT: two, three, four, five or
> six rings are all recorded; three is typical. BETWEEN SPECIMENS there is no
> consistency in the pattern at all

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV016 — Tool marks

*Definition: Secondary machining traces*

> Concentric circles are engraved into the metal after casting

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV017 — Internal hole wear

*Definition: Wear inside openings*

> The outer and inner surfaces of the Gallo-Roman dodecahedra, aside from a
> few exceptions and later destruction and corrosion, generally do not look
> worn

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV018 — External wear

*Definition: Wear on external surfaces*

> The outer surfaces generally do not look worn, aside from a few exceptions
> and later destruction and corrosion

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV019 — Rope wear

*Definition: Grooves or polish from rope*

> No rope wear, grooves or polish from rope is reported anywhere in the
> corpus; the general statement that the surfaces do not look worn covers the
> holes and knobs

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV020 — Rotational wear

*Definition: Evidence of repeated rotation*

> No evidence of repeated rotation is reported anywhere in the corpus

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV031 — Military association

*Definition: Direct military evidence*

> Just under one-fifth of dodecahedra with a recorded find location come from
> military camps; the overwhelming majority derive from civilian contexts,
> although there is some concentration around the frontiers

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV032 — Ritual association

*Definition: Direct ritual evidence*

> c 8.5 per cent of located finds come from contexts with plausible sacred
> connections, a further c 7 per cent from graves or necropolis areas and c 4
> per cent from rivers. Specific cases include a cult precinct (no 21), the
> temple of Nodens at Lydney (no 68), a cache attributed to a temple (no 122)
> and three richly furnished graves

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV033 — Rod compatibility

*Definition: Can rods fit securely?*

> ASSESSMENT: measured hole diameters (9.4-40.6 mm across specimens) admit
> cylindrical rods. ARCHAEOLOGICAL CORROBORATION: a bone object c 15 cm long
> and c 3 cm in diameter lay immediately adjacent to the Gelduba specimen,
> whose production holes measure 24 and 23 mm

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV034 — Rope compatibility

*Definition: Can ropes be routed?*

> ASSESSMENT: hole diameters and knob dimensions permit rope or cord to be
> routed through the holes and anchored over the knobs

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV035 — Structural stability

*Definition: Stable under load*

> ASSESSMENT: the dodecahedral form with twenty vertex knobs rests stably on
> any face, and a 3 mm bronze wall resists modest compressive load

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV036 — Load transfer

*Definition: Plausible force paths*

> ASSESSMENT: six pairs of opposing faces provide six potential through-rod
> axes along which axial load could be transferred

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV037 — Assembly potential

*Definition: Supports modular construction*

> Overall diameter across the corpus spans 4-10 cm, a ratio of 2.5:1. A
> modular structural system requires interchangeable components of consistent
> dimension

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV038 — Orientation dependence

*Definition: Requires fixed orientation*

> Every specimen carries knobs at all twenty vertices and rests equally on any
> face; no specimen has a distinguished base or axis. The single related
> Gallo-Roman icosahedron, from Arloff, does have such an axis: three of its
> knobs are larger and are arranged around the smaller of its only pair of
> holes

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV039 — Standardisation

*Definition: Similarity across artifacts*

> Hole diameters span 0.6-4 cm and overall diameters 4-10 cm across the
> corpus; knob diameters cover a broad range from object to object; there is
> no consistency in the pattern of circles on the faces. Within single
> specimens the coefficient of variation of hole diameter reaches 40 per cent
> and no arithmetic progression is present

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV040 — Regional variation

*Definition: Geographic patterns*

> Many dodecahedra with special features come from Roman Britain, some of
> which do not appear to be so skilfully designed and may be local imitations
> of classic dodecahedra; several typological groups are distinguished and the
> pattern of face decoration is inconsistent

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---

### EV044 — Interior finish and marking

*Definition: Condition of the internal surface: whether it is smoothed or left as cast, and whether it carries any engraving, scale or marking. Distinct from EV012, which records casting quality overall, and EV014, which records decoration of the exterior*

> Interiors are consistently described as roughly or crudely cast and
> unfinished: 'interior surfaces more roughly cast' (RD-0001), 'interior
> described as crudely cast' (RD-0002), 'interior left roughcast' (RD-0003),
> 'interior concave and crudely cast' (RD-0008), 'reverse concave with rough
> and unfinished surface' (RD-0011), 'interior concave, crudely finished'
> (RD-0012). No specimen in the database is recorded with interior engraving,
> scale, marking or a smoothed working surface

**Direction:** `____________`  **Confidence A–E:** `___`

**Reason:**

---


## Declaration

- Did you consult any of the forbidden sources? yes / no
- Which items were hardest to rate, and why?
- On which items would you expect a second rater to disagree with you?
- Did any statement strike you as resting on weaker evidence than its wording
  suggests?

---

## What happens next

Your ratings are compared against the ones already recorded, and the
disagreement rate is reported as an inter-rater reliability figure. Every
disagreement is a place where the result depends on a judgement rather than on
the evidence.

**Disagreeing is the useful outcome.** If you agree with everything, the
exercise has told us nothing except that two raters can share a bias.
