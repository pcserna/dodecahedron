# Roman Dodecahedron Open Research Database (RDORD)

## Overview

The **Roman Dodecahedron Open Research Database (RDORD)** is an open, evidence-based research project dedicated to collecting, organizing, analyzing, and preserving all available information about Roman dodecahedra.

The project does **not** promote a single interpretation of these artifacts. Instead, it provides a structured research platform where competing hypotheses can be evaluated against archaeological, geometrical, engineering, statistical, and experimental evidence.

The repository is designed to support archaeologists, historians, engineers, data scientists, experimental archaeologists, and 3D modelers.

---

# Objectives

The project aims to:

* Build the most comprehensive database of known Roman dodecahedra.
* Preserve references to primary archaeological sources.
* Standardize measurements and metadata.
* Document the geometry of every known specimen.
* Record archaeological context and provenance.
* Support statistical and computational analysis.
* Enable reproducible experimental archaeology.
* Provide accurate 3D reconstructions.
* Create an open research platform for future studies.

---

# Research Philosophy

The project follows several fundamental principles:

* Evidence before interpretation.
* Every data point must be traceable to its source.
* Unknown values remain unknown.
* Assumptions are never stored as facts.
* Every hypothesis must be testable.
* The database should remain reusable for future research.

---

# Repository Structure

```text
dodecahedron/

├── README.md
├── LICENSE
├── .gitignore
│
├── 01_Database/
│   ├── Specimens.csv
│   ├── Specimens.xlsx
│   ├── Specimens.sqlite
│   └── Schema/
│
├── 02_Literature/
│   ├── Bibliography.md
│   ├── Notes/
│   └── References/
│
├── 03_Images/
│
├── 04_3D/
│   ├── Blender/
│   ├── STL/
│   ├── OBJ/
│   └── GLB/
│
├── 05_Geometry/
│
├── 06_Engineering/
│
├── 07_Experimental_Archaeology/
│
├── 08_Statistics/
│
├── 09_AI_Analysis/
│
├── 10_GIS/
│
└── docs/
```

---

# Database Design

The primary dataset follows the principle:

**One specimen = One record**

Each record contains all currently available information for a single Roman dodecahedron.

Typical fields include:

* Internal ID
* Catalogue numbers
* Findspot
* Country
* Roman province
* Geographic coordinates
* Discovery date
* Archaeological context
* Current museum
* Inventory number
* Material
* Dimensions
* Weight
* Wall thickness
* Decoration
* Hole diameters
* Wear traces
* Associated finds
* References
* Source reliability

Unknown information is intentionally left blank.

---

# Data Sources

The project uses publicly available and academically reliable sources, including:

* Museum collections
* Archaeological excavation reports
* Peer-reviewed publications
* Published catalogues
* Academic books
* Conference proceedings
* Official heritage organizations

Every record should reference one or more original sources whenever possible.

---

# Source Reliability

Each data field should include a confidence level.

| Grade | Description                                      |
| ----- | ------------------------------------------------ |
| A     | Direct archaeological measurement                |
| B     | Museum documentation                             |
| C     | Peer-reviewed secondary publication              |
| D     | Estimated from published photographs or drawings |
| E     | Unverified claim                                 |

---

# Research Areas

The repository supports research in:

* Archaeology
* Roman history
* Geometry
* Topology
* Engineering
* Materials science
* Manufacturing techniques
* Experimental archaeology
* Digital humanities
* Data science
* Artificial intelligence

---

# Working Hypotheses

The repository intentionally remains neutral.

Possible hypotheses include, but are not limited to:

* Measuring instrument
* Ritual object
* Military equipment
* Portable shrine
* Structural connector
* Modular construction node
* Wagon component
* Tent component
* Textile tool
* Astronomical instrument

No hypothesis is treated as established fact.

---

# Experimental Archaeology

The repository includes experimental results whenever available.

Potential experiments include:

* Structural assembly
* Wooden rod connections
* Rope fastening
* Mechanical loading
* Wear analysis
* 3D printing
* Material testing
* Field reconstruction

All experiments should be reproducible and fully documented.

---

# 3D Models

Whenever possible, each specimen should include:

* Parametric reconstruction
* Blender source
* STL
* OBJ
* GLB

Every model should document the measurements and assumptions used during reconstruction.

---

# AI and Computational Analysis

After the database reaches sufficient completeness, computational methods may be applied, including:

* Cluster analysis
* Principal Component Analysis (PCA)
* Graph analysis
* Pattern recognition
* Bayesian comparison
* Similarity analysis
* Statistical classification

AI-generated conclusions should always be explainable and traceable to the underlying data.

---

# Contributing

Contributions are welcome.

Contributors should:

* Cite original sources.
* Avoid speculation.
* Clearly distinguish observations from interpretations.
* Preserve source references.
* Document any assumptions.
* Follow the repository data schema.

---

# Long-Term Vision

The long-term objective is to create the world's most comprehensive open research resource on Roman dodecahedra.

Rather than advocating a single explanation, the project aims to provide a transparent, extensible, and evidence-based platform that enables researchers to evaluate competing hypotheses using the same high-quality dataset.

---

# License

The repository structure, database schema, and original project documentation may be distributed under an open-source license selected by the project maintainers.

Please respect the copyright and licensing terms of museums, publishers, and image providers when contributing external material.
