---

Document ID: RDORP-005
Title: Data Dictionary
Version: 0.1.0
Status: Draft
Project: Roman Dodecahedron Open Research Project (RDORP)
License: CC BY 4.0
Created: 2026-08-07
Last Updated: 2026-08-07

Related Documents:

* RDORP-001 Project Charter
* RDORP-003 Research Method
* RDORP-004 Database Schema

---

# Data Dictionary

## 1. Purpose

This document defines every field used in the RDORP master specimen database.

Its objectives are to:

* ensure consistent data entry;
* eliminate ambiguity;
* define validation rules;
* establish controlled vocabularies;
* support CSV, SQLite, JSON, and future database exports.

---

# 2. General Conventions

## Character Encoding

* UTF-8

## Decimal Separator

* `.` (period)

Example:

```text
18.5
```

## Date Format

ISO 8601

```text
YYYY-MM-DD
```

If only the year is known:

```text
YYYY
```

---

# 3. Null Values

Unknown values must remain empty.

Never use:

* 0
* N/A
* Unknown
* ?
* *

---

# 4. Units

| Quantity    | Unit                    |
| ----------- | ----------------------- |
| Length      | mm                      |
| Weight      | g                       |
| Coordinates | Decimal Degrees (WGS84) |
| Dates       | ISO 8601                |

---

# 5. Field Definitions

## Identification

| Field                 | Type    | Required | Description                      | Example     |
| --------------------- | ------- | -------- | -------------------------------- | ----------- |
| SpecimenID            | String  | Yes      | Permanent RDORP identifier       | RD-0001     |
| GuggenbergerNumber    | Integer | No       | Guggenberger catalogue number    | 27          |
| NouwenNumber          | Integer | No       | Nouwen catalogue number          | 18          |
| OtherCatalogueNumbers | String  | No       | Additional published identifiers | CAT-15      |
| MuseumInventoryNumber | String  | No       | Museum inventory number          | 1924.0411.1 |

---

## Discovery

| Field                  | Type    | Required | Description                       |
| ---------------------- | ------- | -------- | --------------------------------- |
| Findspot               | String  | Yes      | Published archaeological findspot |
| ModernMunicipality     | String  | No       | Present-day municipality          |
| AdministrativeRegion   | String  | No       | Region, county or province        |
| Country                | String  | Yes      | Modern country                    |
| RomanProvince          | String  | No       | Roman administrative province     |
| Latitude               | Decimal | No       | WGS84 latitude                    |
| Longitude              | Decimal | No       | WGS84 longitude                   |
| DiscoveryYear          | Integer | No       | Year of discovery                 |
| DiscoveryDate          | Date    | No       | Exact discovery date              |
| DiscoveryCircumstances | String  | No       | Description of discovery          |

---

## Archaeological Context

| Field              | Type    | Required | Description            |
| ------------------ | ------- | -------- | ---------------------- |
| ContextCategory    | Enum    | No       | Controlled vocabulary  |
| ContextDescription | Text    | No       | Published context      |
| AssociatedFinds    | Text    | No       | Objects found together |
| DatingFrom         | Integer | No       | Earliest proposed date |
| DatingTo           | Integer | No       | Latest proposed date   |
| DatingMethod       | String  | No       | Method used for dating |

Allowed ContextCategory values:

* Military
* Civilian
* Villa
* Temple
* Grave
* Hoard
* River
* Settlement
* Unknown

---

## Museum

| Field         | Type    | Required |
| ------------- | ------- | -------- |
| MuseumName    | String  | No       |
| MuseumCity    | String  | No       |
| MuseumCountry | String  | No       |
| Collection    | String  | No       |
| PublicDisplay | Boolean | No       |

---

## Physical Description

| Field               | Type   | Required |
| ------------------- | ------ | -------- |
| Material            | Enum   | No       |
| ManufacturingMethod | String | No       |
| PreservationState   | Enum   | No       |
| CorrosionState      | String | No       |
| Repairs             | Text   | No       |
| Damage              | Text   | No       |

Material vocabulary:

* Bronze
* Copper Alloy
* Brass
* Unknown

PreservationState:

* Complete
* Nearly Complete
* Fragmentary
* Reconstructed

---

## Measurements

All measurements are recorded in millimetres unless otherwise stated.

| Field             | Type    |
| ----------------- | ------- |
| HeightMM          | Decimal |
| WidthMM           | Decimal |
| MaximumDiameterMM | Decimal |
| MinimumDiameterMM | Decimal |
| WallThicknessMM   | Decimal |
| WeightG           | Decimal |
| KnobDiameterMM    | Decimal |

---

## Face Measurements

Each face opening is recorded individually.

| Field            |
| ---------------- |
| Face01DiameterMM |
| Face02DiameterMM |
| Face03DiameterMM |
| Face04DiameterMM |
| Face05DiameterMM |
| Face06DiameterMM |
| Face07DiameterMM |
| Face08DiameterMM |
| Face09DiameterMM |
| Face10DiameterMM |
| Face11DiameterMM |
| Face12DiameterMM |

Face numbering follows the RDORP Geometry Specification.

---

## Decoration

| Field                   | Type    |
| ----------------------- | ------- |
| DecorationType          | String  |
| DecorationDescription   | Text    |
| NumberOfConcentricRings | Integer |
| SurfaceFinish           | String  |

---

## Wear

Observed evidence only.

| Field           | Type    |
| --------------- | ------- |
| WearPresent     | Boolean |
| WearDescription | Text    |
| MechanicalWear  | Boolean |
| Abrasion        | Boolean |
| RopeWear        | Boolean |
| ToolMarks       | Boolean |

Interpretations of wear are not stored here.

---

## Documentation

| Field                | Type    |
| -------------------- | ------- |
| PhotographAvailable  | Boolean |
| DrawingAvailable     | Boolean |
| ThreeDModelAvailable | Boolean |
| CTScanAvailable      | Boolean |
| LaserScanAvailable   | Boolean |

---

## References

| Field               | Type   |
| ------------------- | ------ |
| PrimaryReference    | String |
| SecondaryReferences | Text   |
| MuseumURL           | String |
| PublicationURL      | String |
| DOI                 | String |

---

## Data Quality

| Field            | Type   |
| ---------------- | ------ |
| SourceConfidence | Enum   |
| LastVerified     | Date   |
| VerifiedBy       | String |
| Notes            | Text   |

Confidence Levels:

| Grade | Meaning                                               |
| ----- | ----------------------------------------------------- |
| A     | Direct measurement from primary archaeological source |
| B     | Official museum documentation                         |
| C     | Peer-reviewed secondary publication                   |
| D     | Derived from photographs or illustrations             |
| E     | Unverified or uncertain information                   |

---

# 6. Validation Rules

* `SpecimenID` must be unique.
* Coordinates must use WGS84 decimal degrees.
* Measurements must be positive values.
* Dates must follow ISO 8601.
* Enumeration fields must use only approved values.
* Empty fields represent unknown information.

---

# 7. Future Compatibility

New fields may be added in future versions provided they:

1. do not alter the meaning of existing fields;
2. remain backward compatible;
3. are documented in this Data Dictionary;
4. receive corresponding validation rules.

---

# 8. Revision History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 0.1.0   | 2026-08-07 | Initial data dictionary. |
