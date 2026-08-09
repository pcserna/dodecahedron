# Blind respecification of six evidence variables (RDORP-013 item A5)

Specified by: Claude Opus 5 (Claude Code session), working only from
`docs/A5_BLIND_SPECIFICATION_PROMPT.md`
Date: 2026-08-09
Consulted forbidden sources: **no**

---

## Disclosure before the matrix

- **What I opened.** The prompt itself; a directory listing of `docs/`; the
  first 45 lines of `docs/A3a_BLIND_MATRIX_H012.md` (an earlier blind
  prediction matrix of my own — predictions, no observations) to match its
  format; and a `grep` of `docs/RDORP-013_Hardening_Plan.md` for the literal
  string `A5`, to find out where this file was meant to go. That grep returned
  six lines. Two of them characterise the *quality* of the evidence on these
  variables ("carry good evidence no hypothesis can be tested against",
  "recovers the best-quantified evidence in the corpus"). Neither states what
  any observation is, but they are more than nothing and I record them.
- **What I did not open.** `docs/RDORP-012_Results_Summary.md`, any file in
  `reports/`, any table or CSV of observations, screenings, readings, results
  or scores, and `database/build_db.py`. No web search was run.
- **Independence is partial.** I am a model of the same family that most
  likely produced the matrix these predictions replace, and I share its
  priors. I also carry general knowledge about Roman material culture, which is
  what the mechanical reasoning is built from. Treat this as a second
  specifier working from mechanism, not as an independent discipline.
- **One structural leak in the prompt.** The prompt says these six variables
  "currently contribute nothing" and that recovering them is worth doing.
  That tells me the evidence is good; it does not tell me what it says.

---

## How to read these cells

Each cell names **the pattern the mechanism requires**, and the symbol says how
strongly it requires it:

| Symbol | Meaning in this document |
| ------ | ------------------------ |
| `++` | The mechanism requires the named pattern. Its absence counts heavily against the hypothesis. |
| `+`  | The mechanism expects the named pattern. Its absence is a real cost. |
| `0`  | The mechanism is genuinely indifferent; no pattern is named, and the variable can neither support nor damage the hypothesis. |
| `-`  | The mechanism expects the named pattern to be **absent**; observing it counts against. |
| `--` | The named pattern is strongly contrary and would count heavily against. |

Every cell that is not `0` also names its own falsifier, introduced by *Counts
against*. That clause is the prediction's teeth, and it should be carried into
the matrix with the symbol — a symbol without it is the vagueness this exercise
is meant to remove.

Where a hypothesis's honest expectation is "no pattern at all", I have written
that as the expectation (e.g. "no regional concentration; distribution
proportional to Roman bronze use") rather than as a `0`, because it is
falsifiable and a `0` is not.

---

## A note on the mass arithmetic

The EV002 thresholds below are not guesses; they come from the geometry, so
that a threshold can be argued with rather than merely disbelieved.

A regular dodecahedron of edge *a* has surface area 20.65·*a*², and its
face-to-face width is 2.227·*a*. An object 60 mm across the faces therefore has
*a* ≈ 26.9 mm and about 150 cm² of surface, of which twelve apertures remove
roughly 20 cm². Leaded copper alloy runs about 8.7 g/cm³. So:

| Wall | Shell mass at 60 mm across | Twenty knobs | Total |
| ---- | -------------------------- | ------------ | ----- |
| 1.5 mm | ~165 g | ~55 g | **~220 g** |
| 2.5 mm | ~275 g | ~55 g | **~330 g** |
| 4 mm | ~430 g | ~60 g | **~490 g** |

Two consequences run through the whole variable. First, mass at this size is
dominated by wall thickness, so **EV002 is largely a restatement of EV001 size
and EV003 wall thickness** and should not be scored as if it were independent
evidence — a warning for whoever loads these. Second, a light object of this
form is difficult to cast: the knobs alone are roughly 55 g. Any hypothesis
requiring a light object is therefore requiring something the construction
resists, and that is a real prediction, not a hedge.

---

## EV002 Mass

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `+` | Heavy: above about 300 g, implying a wall of 3 mm or more; and tightly clustered within a size class. Counts against: a majority below 150 g, or masses spread continuously with no modal value. | A socket that takes rod thrust needs several millimetres of metal that will not split at the aperture edge. And nodes of a repeated frame are interchangeable parts cast to a pattern, so a kit's nodes should weigh nearly the same as each other. |
| H002 Rangefinder | `0` | No constraint beyond being holdable — anything under about 1 kg will serve, which the whole plausible size range satisfies. | The metrology lives entirely in the aperture diameters and the distance between opposed faces. Weight enters nowhere in the calculation, and no observable mass in this corpus could refute the hypothesis. This is a cost of H002, not a strength: EV002 cannot support it. |
| H003 Ritual object | `0` | Any mass whatever. | Roman religious metalwork runs from 5 g votive miniatures to life-size statuary. "The form itself carries the meaning" sets no weight, and I can construct no threshold that a proponent would accept as binding. Recorded as a genuine indifference and therefore as a place where this hypothesis cannot be tested. |
| H004 Candlestick | `+` | At least about 200 g, and the heavier the better. Counts against: a substantial fraction under 100 g. | A holder must outweigh what it holds and survive a knock without tipping; a terracotta lamp with fuel, or a wax candle, is itself 50–150 g and sits above the holder's centre of mass. A holder lighter than its load is a fire. |
| H005 Textile tool | `+` | Hand-tool range, roughly 50–350 g. Counts against: a modal mass above about 500 g. | The tool is manipulated continuously in one hand while the other works the yarn; above half a kilo the hand tires within a working session and the craft would have adopted a lighter form. |
| H006 Astronomical instrument | `0` | No constraint. | Angular measurement depends on sight-line geometry and on the observer's steadiness, not on the instrument's weight. If the mechanism required the object to stand unsupported through a timed observation, mass would matter; as stated it is a hand-held sight, and any holdable weight serves. |
| H007 Military equipment | `+` | Under about 500 g, and — the more testable half — tightly clustered with a clear modal value. Counts against: masses spread over an order of magnitude with no mode. | Issued kit is weight-rationed on the march, and it is made to pattern in state or contracted workshops. Standardisation is the sharper prediction: an army does not issue an object whose weight varies fivefold between examples. |
| H008 Portable shrine component | `+` | Under about 400 g; no lower bound. Counts against: a modal mass above 600 g. | "Portable" is in the hypothesis. The whole assemblage must be liftable and carried between rooms, on journeys or in procession. Miniaturisation is normal in domestic cult, so lightness is permitted but weight is not. |
| H009 Tent apex fitting | `+` | Heavy: above about 300 g with a wall of 3 mm or more, and clustered, since tent equipment is issued to a pattern. Counts against: a thin-walled majority under 200 g. | The apex hub carries the compression of every rafter plus wind loading, and the socket wall is what fails first. A 1.5 mm shell splits at the aperture under rafter thrust. |
| H010 Parasol crown | `++` | Light: below about 150 g. Counts heavily against: a modal mass above 250 g. | The crown sits at the top of a pole held aloft, where its weight acts through the pole's whole length on the carrier's wrist — a gram there costs more than a gram anywhere else in the assembly. This is why surviving canopy fittings are thin sheet, not castings. A cast shell with twenty solid knobs is the wrong construction for the job, and the arithmetic above says the knobs alone use a third of the budget. |
| H011 Archery ranging aid | `+` | Under about 250 g. Counts against: a modal mass above 400 g. | The archer holds the object up in one hand while the bow occupies the other, and the arm must stay steady for the sighting to mean anything. Hand-held sighting aids used at the moment of shooting sit well under a quarter-kilo or they are not used twice. |
| H012 Spool-knitting frame | `+` | Roughly 50–350 g. Counts against: a majority below 40 g, too light to resist yarn tension without being dragged about, or above 500 g, too heavy to turn through a working session. | The object is held and rotated continuously, and its weight must sit between what the yarn can pull and what the hand can carry. |
| H013 Rope-laying top | `+` | Moderate to heavy, above about 200 g, with the mass distributed outward — thick walls and substantial knobs rather than a thin shell. Counts against: a light thin-walled majority. | Rotational inertia is functional here: the spun object must carry itself evenly through the lay, and a low-inertia body stalls and gives an uneven twist. The strands also bear on the knobs under tension, which the knobs must have the section to take. |
| H014 Wax bulla former | `+` | At least about 150 g. Counts against: a light thin-shelled majority under 100 g. | The metal body has to chill the wax pressed into it so the sealing sets and releases with a crisp edge; a shell with little thermal mass equilibrates with the wax and gives a soft impression that sticks. The body must also not flex under thumb pressure while the wax is worked. |

---

## EV025 Site type

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `+` | Sites with substantial standing structures using the same frame repeatedly: forts and fortresses, public buildings, villas, workshops. Counts against: a thin spread across all site types with no concentration where Roman construction was heaviest. | A component of buildings is lost where buildings are built, repaired and demolished. Sites with no substantial structures have no use for a structural node. |
| H002 Rangefinder | `+` | Contexts of surveying and land organisation: forts and fortresses (the army did the surveying), newly founded colonies, and sites tied to roads, aqueducts and centuriated land. Counts against: dominance of small rural farmsteads with no engineering role. | Distance-measuring is done where land is being laid out, not where it is merely being farmed. |
| H003 Ritual object | `++` | Temples, shrines, sanctuaries, sacred springs and cemeteries prominent among contexted finds — on the order of a quarter or more. Counts heavily against: near-absence from cult sites while ordinary settlement dominates. | If the form itself carries the meaning, the object belongs where meaning was transacted. A cult object that never reaches a cult site has no positive evidence of its own and survives only as the residue left when other hypotheses fail — which is not evidence. |
| H004 Candlestick | `+` | Ordinary domestic occupation of every kind — town houses, villas, farmsteads, fort barracks — in rough proportion to how much of each has been excavated, with no concentration in any single type. Counts against: concentration at one site type, especially a non-residential one. | Artificial light is a universal domestic need with no institutional sponsor, so a lighting fitting has no reason to prefer any one kind of settlement. |
| H005 Textile tool | `+` | Houses, villa working ranges and vici; textile work is a household activity in every kind of settlement. Counts against: concentration at exclusively military sites with no attached civil settlement. | Household crafts are lost in households. |
| H006 Astronomical instrument | `+` | Urban and elite contexts, temples with a calendrical role, and places of learning; Mediterranean towns rather than frontier installations. Counts against: dominance of small rural sites and frontier forts. | Celestial measurement requires someone with a reason to measure and the arithmetic to use the result. A farmstead already has the naked-eye calendar it needs and no use for an instrument. |
| H007 Military equipment | `++` | Forts, fortresses, marching camps and frontier installations should dominate; permanent civilian settlement should be marginal. Counts heavily against: a majority from villas, farms and towns with no garrison. | Issued equipment is lost where it is issued and used. |
| H008 Portable shrine component | `+` | Private houses and villas — the rooms and niches of household cult — and graves. Not public sanctuaries, whose apparatus differs in scale and ownership. Counts against: concentration at public temples, which supports H003 instead, or at military sites. | Domestic cult happens in domestic space, and its equipment stays with the household that owns it. |
| H009 Tent apex fitting | `++` | Marching camps, campaign camps, forts and fortresses. Counts heavily against: a majority from civilian rural settlement, where nobody lives under a rafter tent. | Tents are pitched, struck and lost where armies move. A tent fitting from a villa has no way into the ground. |
| H010 Parasol crown | `+` | Towns, elite town houses, villas, and elite graves — settings with both an owner of status and an attendant to carry the canopy. Counts against: dominance of forts and rural farmsteads. | A carried canopy is a display object; it needs an audience and a servant, neither of which a frontier fort or a farm provides. |
| H011 Archery ranging aid | `++` | Forts and installations garrisoned by archer units (sagittarii), and their shooting ranges — not the army in general. Counts heavily against: a spread across military sites with no relation to archer garrisons, or dominance of civilian settlement. | The mechanism is specific to the bow, so it must predict the units that shot bows. If it can only predict "military", it is H007 under another name and adds nothing. |
| H012 Spool-knitting frame | `+` | Ordinary settlement of every kind — farmsteads, vici, town houses, villas, and the civil settlements attached to forts — with rural and small-town contexts at least as common as high-status ones. Counts against: concentration at temples, or at exclusively military sites with no attached civil settlement. | Cord and braid are household production. The tool belongs where households worked, and it is cheap enough to be lost anywhere people lived. |
| H013 Rope-laying top | `+` | Sites where cordage is made or consumed in bulk: ports, river harbours, military supply bases, and farms with substantial cordage needs. Counts against: absence from waterfront and supply contexts combined with dominance of ordinary domestic sites. | Rope is laid where rope is needed in quantity; a domestic scatter with no waterfront signal describes a household tool, not a rope-walk. |
| H014 Wax bulla former | `+` | Places where goods and documents were sealed: fort headquarters and strongrooms, town administrative buildings, villa estate centres, ports and customs posts. Counts against: dominance of contexts with no administrative or storage function. | Sealing is an administrative act performed where goods are dispatched and records are kept. |

---

## EV026 Roman province

The falsifiable content of this variable is the **shape** of the distribution,
not the identity of any one province. Three shapes are in play, and they
separate the hypotheses cleanly: *proportional to Roman population and bronze
use* (universal-need mechanisms), *proportional to a specific institution's
footprint* (army, archer units, administration), and *a single contiguous
cultural block with sharp edges* (a craft tradition spread by imitation).

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `+` | Every province where Romans built in timber and metal, roughly proportional to the amount of Roman construction, with Italy and the Mediterranean core well represented. Counts against: confinement to a small contiguous group of provinces. | A structural solution is not a fashion. Carpenters everywhere face the same joint, and Italy — the densest Roman building in the Empire — cannot be empty of a Roman building component. |
| H002 Rangefinder | `+` | Empire-wide, tilted towards provinces organised or reorganised under Roman survey: the frontier commands and the colonial foundations. Italy, heavily centuriated Africa, and the eastern provinces should all be represented. Counts against: absence from Africa and the east. | Roman surveying was an imperial practice with a written literature and a trained profession. An instrument of it does not stop at a regional boundary. |
| H003 Ritual object | `+` | Empire-wide, proportional to Roman bronze use, because the mechanism as stated contains nothing regional. Counts against: confinement to a few neighbouring provinces. | The hypothesis says the form carries the meaning; it says nothing about whose form it is. A regionally confined distribution would not confirm H003 but replace it with a narrower hypothesis naming a specific regional cult — a different claim, with different and more testable predictions. Recording that here so the substitution cannot be made silently later. |
| H004 Candlestick | `+` | Empire-wide, proportional to settlement, with the Mediterranean core — the densest lamp use in the Empire — the best represented of all. Counts against: a north-western distribution with the Mediterranean provinces empty. | Artificial light is universal. A lamp fitting confined to one corner of the Empire implies that corner had a lighting problem nobody else had, and the hypothesis offers no such problem. |
| H005 Textile tool | `+` | Empire-wide, with at most a tilt towards the wool-producing north-western and Danubian provinces. Counts against: very little, and that is the point — this hypothesis is generic enough to absorb almost any distribution, which is a weakness to be recorded rather than repaired. | Textile working happens wherever people wear clothes. Without naming the technique, the hypothesis cannot name a region. |
| H006 Astronomical instrument | `+` | Best represented in the provinces with an astronomical tradition — Italy, Greece, Asia, Syria, and above all Egypt. Counts heavily against: concentration in the north-western provinces with Egypt and the east empty. | Roman astronomy was a Greek and Alexandrian science. An instrument for it that is absent where the science was practised, and common where it was not, has its geography exactly backwards — and no diffusion story repairs that, since instruments travel from the tradition outward, not the reverse. |
| H007 Military equipment | `++` | The distribution should follow the army: the Rhine, but equally the Danube (Pannonia, Moesia, Dacia), Britannia, and the eastern and African commands — Syria, Cappadocia, Arabia, Numidia, Egypt. Counts heavily against: a north-western concentration with the eastern and African garrisons empty. | Roughly half the army served away from the north-west. Issued equipment is issued across the army, so a "military" object that never reaches half the military is not military issue; at best it is a regional habit that happens to occur near soldiers. |
| H008 Portable shrine component | `+` | Empire-wide, proportional to Roman-style domestic housing, with the Italian and Mediterranean provinces — where household cult is best documented and best excavated — well represented. Counts against: Mediterranean absence. | The lararium is a Roman domestic institution that travelled with Roman-style housing everywhere. |
| H009 Tent apex fitting | `+` | Where armies campaigned and camped, which again means the eastern and African frontiers as well as the north-western ones. Counts against: a regional block that does not match the army's deployment. | Same logic as H007, one notch weaker: a proponent can fairly argue that one command's workshops supplied a regional tent pattern, so a partial match is survivable where for H007 it is not. |
| H010 Parasol crown | `+` | Mediterranean and eastern provinces — Italy, Greece, Asia, Syria, Egypt, Africa — where the sun makes shade worth carrying and the parasol is an attested convention of status. Counts heavily against: concentration in the cloudy north-western provinces. | The mechanism needs sun strong enough to shade against and a display convention that reads as rank. Northern Europe supplies neither. |
| H011 Archery ranging aid | `+` | Provinces where archer units were raised or stationed: Syria, Commagene, Thrace, and the frontier provinces where those units were posted. Counts against: a distribution showing no relation to the posting of archer units. | Specialist equipment follows the specialists. If the geography of the objects and the geography of the archers are unrelated, the mechanism has no carrier. |
| H012 Spool-knitting frame | `+` | A single contiguous block of neighbouring provinces sharing a craft tradition, with edges that follow cultural rather than administrative boundaries, and near-absence outside it. Counts against: a thin Empire-wide scatter roughly proportional to population. | A craft tool with no state distributor spreads by imitation between neighbouring workshops and households, so its footprint is a region, not an empire. Note that the mechanism predicts contiguity and sharp edges, not the identity of the region: naming the region would be recall on my part, not derivation, and the test should be run on the shape. |
| H013 Rope-laying top | `+` | Maritime and riverine provinces and their ports; cordage is made in bulk where ships, harbours and river transport are. Counts against: an inland distribution with the great maritime provinces empty. | Bulk rope demand is a waterfront phenomenon. A rope tool that avoids water has lost its market. |
| H014 Wax bulla former | `+` | Empire-wide, proportional to administrative and commercial density, with Italy and the eastern provinces best represented. Counts against: absence from the east and from Egypt, where sealing practice is both densest and best preserved. | Sealing is an imperial administrative habit, densest where documents and dispatched goods are densest. |

---

## EV027 Associated finds

Five hypotheses (H001, H009, H010, H011, H014) describe the object as **one
part of a larger assembly**. For those, this variable is close to decisive: an
assembly cannot be evidenced by one part, and across roughly 130 objects the
other parts had to be somewhere.

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `++` | Other examples of the same object in the same context, plus the rods or tubes that seated in the apertures, plus other structural metalwork: brackets, collars, cramps, large nails. Counts heavily against: single finds with no second example and no rod, tube or ferrule anywhere in any assemblage. | One frame needs many nodes and as many rods. If the frame existed, its other parts existed in greater numbers than the nodes and should survive more often, not less. |
| H002 Rangefinder | `++` | Surveying and measuring equipment: groma fittings, plumb-bobs, folding rules, dividers, standardised weights; and the writing kit that records a result — styli, inkwells, wax tablets. Counts heavily against: no measuring and no recording equipment in any well-recorded assemblage. | A measurement nobody writes down is not a measurement. Instruments travel with the means of using their output, and Roman surveying was a documented, bureaucratic activity. |
| H003 Ritual object | `+` | Cult apparatus: figurines, miniature altars, incense burners, votive plaques, deliberately placed coin, structured animal bone. Counts against: consistent association with kitchen, craft and workshop refuse and nothing cultic. | Cult objects are used alongside other cult objects and deposited with them. |
| H004 Candlestick | `++` | Lamps, lamp fragments, candle-holders or lampstands in the same context — and, decisively, soot, charring or wax residue on the object itself. Counts heavily against: no lighting equipment in the associated assemblages and no burning or wax on any example. | Fire leaves residue on the metal that holds it. A lamp support that never touched a flame is a lamp support that was never used as one, and the residue test needs no context at all to run. |
| H005 Textile tool | `+` | Textile equipment: spindle whorls, loom weights, needles, shears, distaffs; and fibre or yarn traces where preservation allows. Counts against: no textile equipment in any assemblage. | Textile tools are used together and stored together in the same part of a house. |
| H006 Astronomical instrument | `+` | Other calendrical or astronomical apparatus: sundials and their gnomons, portable dials, celestial imagery; failing that, at least writing equipment. Counts heavily against: no dial, no gnomon and no writing kit anywhere in the corpus's assemblages. | Celestial observation is worthless unless the result is timed against something and recorded. The rest of that apparatus is more durable than the object itself. |
| H007 Military equipment | `++` | Military kit: weapons and their fittings, armour, belt and harness fittings, and the coinage of the military zone. Counts heavily against: assemblages that are consistently civilian in character. | Issued equipment is lost among other issued equipment, in the deposits of places where equipment is worn daily. |
| H008 Portable shrine component | `+` | Domestic devotional equipment: figurines, miniature altars, lamps, in house contexts; or grave goods of personal devotion. Counts against: purely utilitarian assemblages with no devotional item. | A shrine is a set, not a single object, and its parts stay together in the room that houses them. |
| H009 Tent apex fitting | `++` | The rest of the tent and its camp: pegs, guy-line fittings, rope, leather panels, and the equipment struck alongside it. Counts heavily against: no tent peg, rope or leather in any associated assemblage. | Tents are struck, packed and abandoned as units, so their metal parts enter the ground together. Tent pegs are commoner than apex hubs by an order of magnitude and are readily recognised. |
| H010 Parasol crown | `+` | The rest of the canopy: pole ferrules and collars, rib fittings, hinges; and, since the object is display, elite dress items and personal ornament nearby. Counts against: no ferrule, rib fitting or hinge anywhere in the corpus. | A canopy needs a pole shod at both ends and ribs attached at the crown. A proponent may fairly answer that ribs and pole were cane and wood, and that weakens this test — but a metal collar or hinge is still required somewhere across 130 objects, and its complete absence has no innocent explanation. |
| H011 Archery ranging aid | `++` | Archery equipment: arrowheads, composite-bow laths and nocks, quiver mounts, and the kit of the units that shot. Counts heavily against: no archery equipment in any assemblage. | A ranging aid is carried with the bow it ranges for, and arrowheads are among the commonest and most recognisable military finds there are. Their absence cannot be blamed on preservation. |
| H012 Spool-knitting frame | `+` | Household textile and cord equipment: spindle whorls, needles, shears; cord, braid or fibre in or on the object where preservation allows; and use-wear — polish inside the apertures and on the knob necks. Counts against: no textile item in any assemblage and no wear on knobs or aperture edges. | Yarn under tension turning over an edge thousands of times leaves that edge polished. The wear prediction is the strong half: it is a property of the object, testable without any context at all. |
| H013 Rope-laying top | `+` | Cordage, hemp or flax processing debris, and the fittings of a rope-walk or harbour: ships' fittings, blocks, anchors. Counts against: no cordage-related material anywhere in the corpus. | Rope-laying is a workshop process with its own waste stream and its own site furniture. |
| H014 Wax bulla former | `++` | Sealing equipment and its products: seal boxes, sealings and bullae, styli, wax spatulae, writing tablets, and the locks and keys of the containers being sealed. Counts heavily against: no seal box, sealing or stylus in any assemblage. | The former is one step in a chain whose other steps — the seal box, the sealing itself — are commoner, more durable and better recognised than the former. If the chain existed, its other links should be the easier find. |

---

## EV028 Stratigraphy

This variable discriminates along one axis above all: **structured deposition
versus casual loss**. That makes it cheap to score and unusually consequential
— a corpus dominated by hoards and graves damages eleven utilitarian
hypotheses at once, and a corpus dominated by occupation debris damages H003
and H008. I have written each cell so that whichever way the corpus falls, some
rows lose.

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `+` | In situ within structural collapse or demolition, or in scrap and foundry deposits with the rest of a dismantled frame; and more than one example per context. Counts against: predominance of single finds in graves and coin hoards, which a building component has no route into. | A building component enters the ground when the building falls or is stripped, and it does so alongside its neighbours. |
| H002 Rangefinder | `+` | Curated-object contexts: the graves of the people who used it, deliberate deposits, or loss in occupation deposits at the site being surveyed. Counts against: predominance of rubbish and casual-discard deposits. | A precision instrument is valuable, kept and maintained; such objects are more often retained, buried with an owner or hidden than swept into a midden. |
| H003 Ritual object | `++` | Deliberate, structured deposition: graves, votive pits and shafts, wells, springs, foundation deposits, temple deposits — placed rather than dropped, and preferably complete and undamaged. Counts heavily against: predominance of casual loss in occupation debris and rubbish. | Ritual objects enter the ground by ritual acts. Structured deposition is the only depositional signature this hypothesis can claim as its own; without it, "ritual" is a label applied after the fact rather than a prediction. |
| H004 Candlestick | `+` | Occupation floors and destruction layers of rooms that were lit — where a lamp stood when the building burned or was abandoned. Counts against: predominance of graves and hoards. | Lighting equipment is in use in rooms and is caught there by fire and collapse. |
| H005 Textile tool | `+` | Domestic occupation deposits and workshop floors; possibly the graves of women, where textile equipment is a recognised grave-good category. Counts against: hoards and votive shafts. | Household tools are lost and discarded in households. |
| H006 Astronomical instrument | `+` | Curated contexts as for H002 — the graves of practitioners, or occupation deposits at the observing place. Counts against: rubbish and casual loss. | An instrument that took skill to make and skill to use is not treated as expendable. |
| H007 Military equipment | `+` | Fort occupation and destruction layers, ditch and rampart fills, barrack floors, and garrison rubbish. Counts against: predominance of structured deposits and graves. | Roman military equipment enters the ground overwhelmingly by loss and discard; the army's dead were not buried with their issued kit in most of the Empire and most of the period. |
| H008 Portable shrine component | `+` | Within houses, in or near the room or niche of household cult; or as a grave good. Counts against: rubbish deposits and industrial contexts. | Devotional furniture stays in the place of devotion until the household ends, and is then buried, hidden or abandoned in place. |
| H009 Tent apex fitting | `+` | Camp and fort deposits: abandonment and demolition layers, ditch fills, the discard of struck camps, and loss along routes of march. Counts against: graves and hoards. | Tent equipment is lost when tents are struck in haste, and abandoned when a camp is given up. |
| H010 Parasol crown | `+` | Elite graves, where a status object accompanies its owner, and destruction or abandonment deposits in elite housing. Counts against: rubbish deposits and military ditch fills. | Display objects are curated in life and frequently buried with the person whose status they displayed. |
| H011 Archery ranging aid | `+` | Fort occupation deposits and the vicinity of ranges; loss in use. Counts against: predominance of structured deposits. | Field equipment is dropped where it is used. |
| H012 Spool-knitting frame | `+` | Domestic occupation deposits — house floors, yards, household rubbish — and casual loss. Counts against: predominance of graves, hoards and votive deposits. If the object turns up chiefly in hoards alongside coin and scrap, it was being valued as metal rather than used as a tool, and this hypothesis must explain why a cheap household implement was worth hoarding. | A working tool of no great value is dropped, swept out and lost; it is not buried with ceremony, and it is not worth hiding. |
| H013 Rope-laying top | `+` | Workshop and waterfront deposits, and occupation debris where rope was laid. Counts against: graves and votive deposits. | Process equipment stays at the place of the process and is discarded there. |
| H014 Wax bulla former | `+` | Occupation deposits of rooms with an administrative function, close to where documents and goods were handled; loss and discard. Counts against: graves and votive shafts. | Office equipment is lost in offices. |

---

## EV029 Dating

The mechanisms split into two chronological classes, and this is where the
variable earns its Very High power:

- **Universal need** (H001, H003, H004, H005, H013, H014, and largely H008) —
  the need exists throughout the Roman period, so the objects should too. A
  narrow window refutes these.
- **Bounded institution or tradition** (H002, H006, H007, H009, H010, H011,
  H012) — the need exists only while the institution or fashion does, so a
  bounded window is required, and it must be *the right* window.

A single observed date range therefore cannot satisfy both classes. Whatever
the corpus shows, roughly half these rows must lose.

| Hypothesis | Prediction | What specifically is expected | Mechanical reason |
| ---------- | ---------- | ----------------------------- | ----------------- |
| H001 Structural connector | `+` | The whole span of Roman building, 1st to 5th century AD, with no strong peak, and the earliest examples contemporary with the earliest Roman construction in the region concerned. Counts against: a window narrower than about two centuries, or a start centuries after Roman building began there. | A structural solution that works is adopted when the problem first arises and kept while the building tradition lasts. Joints do not go out of fashion. |
| H002 Rangefinder | `+` | 1st century BC to 3rd century AD, densest in the age of colonial foundation, centuriation and frontier engineering, with examples from the late Republic and the Augustan period. Counts against: an exclusively 2nd–4th century range, which post-dates the great age of Roman land survey. | Instruments appear with the practice that needs them. Roman survey was at its most intense when land was first being divided, not two centuries later. |
| H003 Ritual object | `+` | A long span — three centuries or more — with formal antecedents before the Roman period and some continuity into late antiquity. Counts against: a sharply bounded window of a century or two with nothing before and nothing after. | Cult forms are conservative: they are inherited, they outlive the fashions around them, and they leave ancestors. A form that appears from nothing and vanishes completely is behaving like a technology, not like a symbol. |
| H004 Candlestick | `+` | The entire Roman period, 1st to 5th century AD, in proportion to occupation. Counts against: any bounded window. | Nobody stopped needing light, and no lighting technology change in this period would abolish a holder of this kind while leaving lamps in use. |
| H005 Textile tool | `+` | The entire Roman period. Counts against: a bounded window. | Textile production is continuous and universal; a generic textile tool has no reason to begin or end. |
| H006 Astronomical instrument | `+` | 1st century BC to 4th century AD, with the earliest examples in the provinces with the oldest astronomy. Counts heavily against: a range beginning in the 2nd century AD in the north-west, centuries after Greek and Alexandrian astronomy was already mature and instrumented. | Instruments diffuse outward from the tradition that invents them, and later at the periphery than at the centre. A late peripheral start with no Mediterranean ancestry inverts that. |
| H007 Military equipment | `+` | Tied to the army's presence: earliest in the conquest and occupation phase of each region, running 1st to 4th century AD. Counts against: a range that begins long after the army arrived and ends while the army was still there. | Issued equipment appears when the issuing institution arrives and disappears when it leaves or re-equips. Its chronology should track garrisons, not calendars. |
| H008 Portable shrine component | `+` | 1st to 4th century AD, densest in the 1st–3rd when Roman-style domestic cult is best attested. Counts against: a range confined to late antiquity. | Household cult tracks Roman-style domestic architecture and the household forms that go with it. |
| H009 Tent apex fitting | `+` | Concentrated in the periods of active campaigning and tented occupation, 1st to 3rd century AD, earliest where armies first camped. Counts against: a predominantly late range, when the army was largely in permanent quarters. | Tents matter most to a field army. A tent fitting peaking after the army stopped campaigning under canvas has no occasion for use. |
| H010 Parasol crown | `+` | Whenever the Mediterranean convention of the carried canopy was in force — on present reasoning 1st century BC to 3rd century AD. Counts against: a range confined to the later Empire in the northern provinces. | Fashions in display have dates, and this one belongs to the Mediterranean elite culture that produced it. |
| H011 Archery ranging aid | `+` | Tied to the deployment of auxiliary archer units, 1st to 3rd century AD. Counts against: a chronology unrelated to those deployments. | Specialist equipment exists while the specialists do. |
| H012 Spool-knitting frame | `++` | A bounded window with a beginning and an end, on the order of 150 to 350 years, nothing before the invention, and increasing standardisation followed by disappearance. Counts heavily against: an even spread across the whole Roman period, or examples earlier than the local craft tradition can account for. | A craft invention has a first maker and a last practitioner. Unlike a universal need, it is not obliged to exist at all times, and a diffused technique that stops being taught stops being made. The bounded window is the strong claim here, and it is the claim that distinguishes H012 from H013. |
| H013 Rope-laying top | `+` | A long span, with the technique present before and after the Roman period. Counts against: a bounded window of a century or two, which would mean rope-laying began and ended in Roman north-western Europe. | Rope has been laid since prehistory and the process did not change in the Roman period. A rope tool with a two-century life is a rope tool nobody needed before or after, which the mechanism cannot supply a reason for. |
| H014 Wax bulla former | `+` | The whole span of Roman sealing practice, 1st to 4th century AD at least, and ideally beyond it at both ends. Counts against: a bounded window, since sealing neither began nor ended with Rome. | Sealing is a continuous administrative technique with continuous demand. |

---

## Declaration

**Did you consult any of the forbidden sources?**

**No.** In full: I read the prompt, listed `docs/`, read the first 45 lines of
my own earlier blind matrix `docs/A3a_BLIND_MATRIX_H012.md` for format, and
grepped the hardening plan for the string `A5` to learn where this file
belonged. That grep returned six lines, two of which say that these variables
carry good evidence — a statement about evidence quality, not about any
observation. No results document, no report, no table, no CSV, no
`build_db.py`, no web search. All 84 cells above were written before anything
else was opened.

**Which hypotheses were hardest to specify, and why?**

1. **H003 ritual object** and **H007 military equipment** are the hardest,
   for the same reason: neither is a mechanism, both are categories. "The form
   itself carries the meaning" and "unspecified military function" do not
   entail anything about mass, and only barely about province. Two of H003's
   six cells are honest `0`s, which is the correct answer and also a verdict:
   a hypothesis that cannot be constrained by the best-quantified evidence in
   the corpus is not competing on equal terms with one that can. The temptation
   was to invent constraints for them so the row would look respectable; I have
   not.
2. **H002, H006 and H011** are three sighting hypotheses that differ only in
   who is doing the sighting. Left as "an instrument", they would produce three
   identical rows and no discrimination. I have forced them apart on the
   variables where their *users* differ — province and associated finds — and
   left them identical where their *physics* is identical (mass, where all
   three are honest zeros or near-zeros). If they still score alike, that is a
   real finding about the hypothesis set, not a failure of specification.
3. **H005 generic textile tool** resisted specification everywhere. It is
   H012 with the mechanism removed, and it accordingly predicts almost nothing
   that H012 does not predict better. Its EV026 cell is close to unfalsifiable
   and I have said so rather than dressing it up.
4. **H014's mass cell** needed an argument I had to construct rather than
   recall — the thermal-mass one. It is the cell I am least confident in.

**Which predictions do you expect to be most decisive, and why?**

Written now, before any evidence is consulted:

1. **EV027 for H001, H009, H011 and H014.** Four hypotheses make the object
   one part of a multi-part assembly whose other parts are commoner, more
   durable and more recognisable than the object itself — rods, tent pegs,
   arrowheads, seal boxes. Across roughly 130 objects, the consistent absence
   of any of those would be close to fatal, and would be fatal to four
   hypotheses on a single line of evidence. I expect this to be the single
   most destructive cell-group in the matrix.
2. **EV026 for H006 and H007.** H006 predicts a Mediterranean and Egyptian
   distribution; H007 predicts one that follows the whole army, including the
   eastern and African commands. Both are refutable by the same observation,
   and neither has a repair that does not amount to abandoning the mechanism.
3. **EV029 for H012 against H013.** These two are mechanically close cousins
   — yarn or strand worked over the knobs — and dating separates them
   cleanly and in opposite directions: H012 *requires* a bounded window, H013
   *requires* a long one. Whatever the corpus shows, one of them loses. This
   is the cleanest single discriminating test in the whole set, and it does not
   depend on context quality at all.
4. **EV002 for H010.** The arithmetic in the note above says a cast shell of
   this form cannot easily come in under 150 g, because the knobs alone are
   about a third of that budget. If the corpus is heavy, H010 fails on the
   physics of its own construction.
5. **EV028 as a whole.** The structured-deposition axis fires against
   everything at once in one direction or the other. It is the cheapest
   variable here to score and the broadest in effect.

**What I expect to fail (recorded so it cannot be claimed afterwards)**

- I expect **H010's mass prediction to fail**, for the reason above.
- I expect the **universal-distribution predictions (H004, H006, H014,
  and H003's Empire-wide cell) to be the ones the province variable breaks**,
  if the distribution turns out to be regional. If it does, note that H003 can
  be rescued only by replacing it with a specific regional-cult hypothesis —
  that substitution is a new hypothesis needing new predictions, and it must
  not be scored as though the original had passed.
- I expect **EV027 to be sparse**. Associated finds are the first thing lost
  from antiquarian and metal-detector discoveries, and a Very High power
  variable recorded for only a small minority of objects cannot carry Very
  High weight. If the contexted subset is small, the honest move is to
  down-weight EV027 and EV028 by coverage rather than to score 130 objects'
  worth of confidence off twenty objects' worth of data. The same caution
  applies to EV025 and EV029.
- I expect **EV002 to be partly redundant with EV001 and EV003**, for the
  arithmetic reason set out above, and it should be deduplicated against them
  rather than scored as independent.

**A prediction I would not be willing to lose is not a prediction.** Every
non-zero cell above names its own falsifier, and I have not softened one on
suspicion that it will fail — the four I expect to fail are listed by name
immediately above, which is the only protection against quietly adjusting them
later.
