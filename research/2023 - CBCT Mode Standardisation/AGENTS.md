# 2023 - CBCT Mode Standardisation

Clinical CBCT-mode parameter standardisation across five Varian TrueBeam linacs (2023). The authoritative source for the per-mode acquisition parameters, CTDI, and PCXMC effective doses used throughout MC-DCaRE.

## Directory map

```
2023 - CBCT Mode Standardisation/
├── TrueBeamCBCTmodes.xlsx          Master table (5 sheets, see below)
├── TrueBeam CBCT modes and doses 4.1.pdf  Printout of TB4.1 sheet
├── TrueBeamCBCTmodes.pdf          Earlier printout
├── CST/Done/                       Site screenshots: Chris O'Brien Lifehouse
├── OBK/Done/                       Site screenshots: Orange (OBK)
├── PL CBCT modes LA3/Done/         Site screenshots: PowL (Linac 3)
├── PL CBCT modes LA4/Done/         Site screenshots: PowL (Linac 4)
└── PL CBCT Modes LA5/Done/         Site screenshots: PowL (Linac 5)
```

The five site folders contain PNG screenshots of each CBCT mode's acquisition page from the TrueBeam service/console UI (kV, mA, ms, frames/s, blade positions, trajectory). These are the raw evidence that the mode parameters in the master table are correct per machine. They are not processed further.

## Master table: `TrueBeamCBCTmodes.xlsx`

Five sheets, progressively cleaned:

| Sheet | Date | Content |
|---|---|---|
| `Original` | 2023 | Per-linac matrix (LA3/LA4/LA5/CST/OBK) × ~30 modes; CTDI in cGy; Dose Factor (mGy/100mAs). Header caveat: "Only trust dose factor for Stds, otherwise it might just be copied over not measured." |
| `Updated (Change as actioned)` | 2023 | Edited original |
| `Proposed Final` | 24/04/2024 | Cleaned standardisation |
| `For printing Apr25` | Apr 2025 | Final per-mode params + CTDI (cGy) + **PCXMC E (mSv)** |
| `TB4.1 July25` | Jul 2025 | TB 4.1 upgrade: mAs/frame split out, **CTDI now in mGy** (10× cGy values) |

Footer note on `TB4.1 July25`: *"Effective Dose mSv estimates from PCXMC calculations for generic 80 kg/180 cm person, scales with body habitus."* and *"TB 4.1 upgrade combines mA & S single value, CTDI now in mGy."*

## Per-mode parameters (finalized, from `For printing Apr25` / `TB4.1 July25`)

CTDI shown in mGy (TB4.1 convention). Exposure is total mAs. Effective dose is PCXMC, adult 80 kg/180 cm.

| Mode | kV | Exposure (mAs) | CTDI (mGy) | E (mSv) | Fan | Trajectory |
|---|---|---|---|---|---|---|
| Head | 100 | 150 | 3.171 | 0.5 | Full | Half |
| Head SRS | 100 | 540 | 11.331 | 1.8 | Full | Half |
| Head and Shoulders | 125 | 270 | 3.974 | 0.3 | – | – |
| Thorax | 125 | 270 | 3.974 | 1.3 | Half | Full |
| Thorax Spotlight | 125 | 150 | 2.465 | 0.7 | Full | Half |
| 4D Thorax | 125 | 672 | 9.934 | 3.3 | Half | Full |
| Abdomen | 125 | 720 | 10.597 | 2.8 | Half | Full |
| Abdo Spotlight | 125 | 400 | 6.573 | 1.2 | Full | Half |
| Pelvis | 125 | 1080 | 15.895 | 4.2 | Half | Full |
| Pelvis Large | 140 | 1688 | 37.071 | (blank) | Half | Full |
| Pelvis Spotlight | 125 | 750 | 12.325 | 2.2 | Full | Half |
| 4D Spotlight | 125 | 374 | 6.127 | 1.6 | Full | Half |
| Breast 360 | 125 | 90 | 1.325 | 0.2 | Half | Full |
| Extremity Spotlight | 100 | 150 | 3.171 | 0.5 | Full | Half |
| SBRT Spine | 125 | 360 | 5.298 | 1.7 | Full | Full |
| Image Gently | 80 | 100 | 0.942 | (blank) | Full | Half |
| Pediatric Head | 80 | 50 | 0.471 | (blank) | Full | Half |
| Paediatric Body | 80 | 100 | 0.942 | (blank) | Full | Half |

## How MC-DCaRE uses this

- The 13 standard + custom CBCT modes here are the basis of the 47 imaging presets in `src/models/imaging_mode.py` (each mode × CW/CCW direction, plus 7 kV-kV planar pairs).
- `effective_dose_references` in `calibration.yaml` (Pelvis 4.2, Thorax 1.3, Head 0.5, etc.) is copied verbatim from this table's PCXMC column.
- `measured_ctdi_w_mGy` calibration entries are derived from this table's CTDI column.
- Effective-dose blanks (Image Gently, Pelvis Large, paediatric) indicate PCXMC was never run for those modes — a gap MC-DCaRE's full-MC path can fill.
