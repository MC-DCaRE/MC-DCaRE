<!-- Context: simulation/concepts | Priority: critical | Version: 1.0 | Updated: 2026-06-12 -->

# MC-DCaRE Simulation Concepts

**Purpose**: Core concepts, terminology, and data models for CT Monte Carlo dosimetry.
**Audience**: Simulation agent, developers.

## CTDI (Computed Tomography Dose Index)

CTDI quantifies radiation dose from CT scans using a standardized phantom.

**Phantom types:**
- 16 cm PMMA cylinder — head phantom
- 32 cm PMMA cylinder — body phantom

**5 measurement positions:**
- Centre (1 position)
- Peripheral: Top, Bottom, Left, Right (4 positions)

**CTDI-w (weighted):**
```
CTDI-w = (1/3) x CTDI_centre + (2/3) x CTDI_peripheral_avg
```

**CTDI-vol:** CTDI-w x (pitch / slice thickness). MC-DCaRE simulates axial mode, so CTDI-vol = CTDI-w.

**DLP (Dose-Length Product):** CTDI-vol x scan length.

## TOPAS/Geant4 Monte Carlo

TOPAS (TOol for PArticle Simulation) wraps Geant4 for medical physics. MC-DCaRE generates TOPAS parameter files (.txt) via Jinja2 templates.

**Particle transport:** Photons and electrons through geometry materials (PMMA, air, water, lead, tungsten).

**Parallel Worlds (Layered Mass Geometry):** CTDI mode scores all 5 plug positions simultaneously in a single TOPAS process. Each position occupies its own parallel world with air material.

## Scorer Types

| Scorer | Full Name | Use | Calibration |
|--------|-----------|-----|-------------|
| TLE | Track Length Estimator | Primary, measurement-equivalent | DCF applied |
| DTM | Dose To Medium | Relative comparisons only | Not calibrated |
| DTW | Dose To Water | Relative comparisons only | Not calibrated |
| water_dtm | DTM in water-filled chamber | Optional, when water_chamber_enabled | Not calibrated |

**TLE is designated PRIMARY_SCORER.** All quantitative dose reporting uses TLE values.

## Simulation Modes

### CTDI Mode
- Standardized phantom geometry
- 5 positions scored simultaneously (15 scorers: 3 per position)
- Optional: 5 additional water_dtm scorers
- Single TOPAS process
- Parameters: kVp, filtration, fan mode, phantom size, field size

### DICOM Mode
- Patient-specific geometry from DICOM files
- Single execution with headsource + patient DICOM
- Parameters: DICOM directory, RP file, isocenter shifts, patient orientation

## Imaging Protocols

47 protocols across 21 fields, stored in `src/models/imaging_mode.py` as `IMAGING_MODES` dictionary.

**Resolution:** `rotation_direction` + `imaging_mode` compose to a lookup key. When matched, 15 fields auto-populate: voltage, exposure, field sizes, blade openings, phantom size, rotation parameters, timeline.

**Key protocol examples:**
- "Head" — 100 kV, Full Fan, 16 cm phantom
- "Image Gently" — pediatric protocol
- "Pelvis" — 120 kV, Half Fan, 32 cm phantom
- "Chest" — 120 kV, Full Fan, 32 cm phantom

## X-Ray Spectrum Generation

SpekPy generates polychromatic X-ray spectra. Parameters:
- `anode_voltage` (kV) — tube potential
- `anode_angle` (degrees) — anode target angle
- `total_filtration` (mmAl) — total aluminum-equivalent filtration
- `anode_material` — tungsten by default

Spectrum file written to runfolder as `spectrum.txt`.

## Beam Geometry

**Fan modes:**
- Full Fan — beam covers smaller FOV, used for head/small body
- Half Fan — beam offset, covers larger FOV, used for large body

**Collimator blades:** Field size converted to blade openings via `fieldtobladeopening.py`. User-blade override available when `user_blade_enabled = true`.

**Rotation:** CBCT rotation (clockwise/counter-clockwise), start angle, rotation rate, timeline end.
