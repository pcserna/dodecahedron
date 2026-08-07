---

Document ID: RDORP-004
Title: Database Schema
Version: 0.1.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-07
Last Updated: 2026-08-07
Related Documents:

* RDORP-001 Project Charter
* RDORP-003 Research Method

---

# Database Schema

## 1. Purpose

This document defines the logical database structure used by the Roman Dodecahedron Open Research Project (RDORP).

The master dataset follows a simple rule:

> **One physical artifact = One primary database record**

All observations associated with a specimen are stored in that record. Additional datasets (images, references, experiments, analyses) reference the specimen using its permanent identifier.

---

# 2. Primary Identifier

Each artifact receives a permanent internal identifier.

Format:

```
RD-0001
RD-0002
RD-0003
...
```

This identifier never changes, regardless of museum inventory changes or future publications.

---

# 3. Record Structure

Each record consists of the following sections:

## A. Identification

* SpecimenID
* GuggenbergerNumber
* NouwenNumber
* OtherCatalogueNumbers
* MuseumInventoryNumber

---

## B. Discovery

* Findspot
* ModernMunicipality
* AdministrativeRegion
* Country
* RomanProvince
* Latitude
* Longitude
* DiscoveryYear
* DiscoveryDate
* DiscoveryCircumstances

---

## C. Archaeological Context

* ContextCategory
* ContextDescription
* AssociatedFinds
* DatingFrom
* DatingTo
* DatingMethod

---

## D. Current Location

* MuseumName
* MuseumCity
* MuseumCountry
* Collection
* StorageStatus
* PublicDisplay

---

## E. Physical Description

* Material
* ManufacturingMethod
* PreservationState
* CorrosionState
* Repairs
* Damage

---

## F. Measurements

All dimensions are stored in millimetres unless otherwise stated.

Fields include:

* HeightMM
* WidthMM
* MaximumDiameterMM
* MinimumDiameterMM
* WallThicknessMM
* WeightG
* KnobDiameterMM

---

## G. Faces

The master record contains twelve face measurements.

```
Face01DiameterMM
Face02DiameterMM
...
Face12DiameterMM
```

If the orientation is unknown, the numbering follows the project's standard face-ordering convention (defined separately in the Geometry Specification).

---

## H. Decoration

* DecorationType
* DecorationDescription
* NumberOfConcentricRings
* CastingDecoration
* SurfaceFinish

---

## I. Wear

* WearPresent
* WearDescription
* MechanicalWear
* Abrasion
* RopeWear
* ToolMarks

Observed wear only.

Interpretations belong elsewhere.

---

## J. Documentation

* PhotographAvailable
* DrawingAvailable
* ThreeDModelAvailable
* CTScanAvailable
* LaserScanAvailable

---

## K. References

* PrimaryReference
* SecondaryReferences
* MuseumURL
* PublicationURL
* DOI

---

## L. Data Quality

Every record contains:

* SourceConfidence
* LastVerified
* VerifiedBy
* Notes

---

# 4. Units

Standard units:

| Property    | Unit                      |
| ----------- | ------------------------- |
| Length      | mm                        |
| Mass        | g                         |
| Coordinates | WGS84 decimal degrees     |
| Dates       | ISO 8601 where applicable |

---

# 5. Null Values

Unknown values remain NULL.

Unknown must never be replaced by:

* 0
* N/A
* Estimated values
* Dummy values

---

# 6. Controlled Vocabulary

Where practical, controlled vocabularies should be used.

Examples include:

ContextCategory

* Military
* Civilian
* Villa
* Temple
* Grave
* Hoard
* River
* Unknown

Material

* Bronze
* Copper Alloy
* Unknown

PreservationState

* Complete
* Fragmentary
* Reconstructed

---

# 7. Versioning

Records are never overwritten.

Corrections generate a new revision while preserving previous values and documenting:

* date
* editor
* reason
* source

---

# 8. Future Extensions

The schema is intentionally extensible.

Future datasets may include:

* metallurgy
* isotope analysis
* XRF
* CT measurements
* finite element analysis
* experimental archaeology
* graph topology
* GIS layers

These datasets should reference SpecimenID rather than altering the primary record.

---

# 9. Design Principles

The schema follows five principles:

1. One artifact = one record.
2. Observations before interpretations.
3. Stable identifiers.
4. Source traceability.
5. Forward compatibility.

---

# 10. Revision History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 0.1.0   | 2026-08-07 | Initial database schema. |
