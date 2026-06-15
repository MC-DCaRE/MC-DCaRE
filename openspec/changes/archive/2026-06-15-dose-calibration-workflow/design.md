# Design: Dose Calibration Workflow

## Overview

Four new/modified components:

1. **`calibration.yaml`** — data file (no code, just schema)
2. **`CalibrationService`** — new service in `src/services/calibration.py`
3. **Simulation metadata** — modified `SpectrumGenerator` output + backward-compatible reader in `CTDICalculator`
4. **Cleanup** — remove stale copy, fix comment

## Component Design

### 1. calibration.yaml

Location: project root. Schema enforced with frozen dataclasses (matching `src/models/` convention) and YAML round-tripping via a `from_yaml()` classmethod.

```yaml
machine: "TrueBeam-SN1234"
date_calibrated: "2026-06-10"
calibrations:
  - kV: 80
    fan_mode: "Full Fan"
    reference_mAs: 100
    measured_ctdi_w_mGy: null
    dcf: null
  - kV: 100
    fan_mode: "Full Fan"
    reference_mAs: 150
    measured_ctdi_w_mGy: null
    dcf: null
  # ... 6 entries total
```

Dataclass model (`src/models/calibration.py`):

```python
@dataclass(frozen=True)
class CalibrationEntry:
    kV: int
    fan_mode: str
    reference_mAs: float
    measured_ctdi_w_mGy: Optional[float]
    dcf: Optional[float]

@dataclass(frozen=True)
class MachineCalibration:
    machine: str
    date_calibrated: str
    calibrations: List[CalibrationEntry]
```

Loading: `MachineCalibration.from_yaml(path)` classmethod. Raises if duplicate `(kV, fan_mode)` entries found.

### 2. CalibrationService

Location: `src/services/calibration.py`

```python
class CalibrationService:
    def __init__(self, calibration_path: Path):
        """Load calibration.yaml."""
    
    def compute_dcf(self, kV: int, fan_mode: str, simulated_ctdi_w_Gy: float, measured_ctdi_w_mGy: float) -> float:
        """Compute DCF = (measured_mGy * 1e-3) / simulated_Gy. Write back to calibration.yaml."""
    
    def lookup_dcf(self, kV: int, fan_mode: str) -> Optional[float]:
        """Lookup DCF for (kV, fan_mode). Returns None if not calibrated."""
    
    def apply(self, runfolder: Path, kV: int, fan_mode: str, target_mAs: Optional[float] = None) -> List[Dict]:
        """Full pipeline: CTDICalculator → apply DCF → optional mAs scaling.
        
        CTDICalculator returns CTDI_w already scaled by the combined calibration
        factor from head_calibration_factor.txt (norm_factor × mAs × dcf_used).
        Since dcf_used is always 1.0, CTDI_w = D_raw × norm_factor × sim_mAs.
        This method then applies the empirical DCF and optional mAs ratio.
        
        1. Read simulation_metadata.yaml from runfolder for simulation mAs
        2. Run CTDICalculator (produces dose at sim_mAs, with dcf_used=1.0)
        3. Lookup DCF(kV, fan_mode)
        4. If target_mAs provided and differs from simulation mAs, scale by ratio
        5. Return calibrated results
        """
```

**mAs scaling logic**:
```python
if target_mAs is not None and target_mAs != sim_mAs:
    mAs_ratio = target_mAs / sim_mAs
    result["CTDI_w_calibrated"] = result["CTDI_w"] * dcf * mAs_ratio
else:
    result["CTDI_w_calibrated"] = result["CTDI_w"] * dcf
```

**DCF computation**:
```python
reference_Gy = measured_ctdi_w_mGy * 1e-3
dcf = reference_Gy / simulated_ctdi_w_Gy
```

### 3. Simulation Metadata

**SpectrumGenerator changes**:

Currently writes `head_calibration_factor.txt` with unstructured content. Change to write `simulation_metadata.yaml`:

```yaml
norm_factor: 1.270680e+16     # 4πr² × fluence(1 mAs) / N_total
mAs: 100                       # simulation mAs
total_histories: 100000000     # sequential_times × histories
dcf_used: 1.0                  # always 1.0, post-hoc calibration
spekpy:
  kvp: 120
  th: 14
  dk: 0.2                     # keV energy bin width
  z: 0.1                      # cm, focus-to-reference distance
  mas: 100
  version: "2.0.1"
fan_mode: "Full Fan"
seed: 42
threads: 4
timestamp: "2026-06-10T14:30:00"
```

Also keep writing `head_calibration_factor.txt` with backward-compatible format for existing CTDICalculator. The file contains the same combined factor as before, computed as `norm_factor × mAs × dcf_used`.

**CTDICalculator changes**:

Add backward-compatible reading: try `simulation_metadata.yaml` first, fall back to `head_calibration_factor.txt` if not found. No behavior change for existing runfolders.

### 4. Cleanup

**Remove NbParticlesInTime.txt copy**: Delete line 85 from `src/modes/base.py`:
```python
# Remove this line:
shutil.copy(os.path.join(include_dir, "NbParticlesInTime.txt"), rundatadir)
```

**Fix dk comment**: In `src/spectrum_generator.py` lines 41-43, change:
```python
# SpekPy energy bin width: dk=0.2 keV (finer spectral resolution than default 0.5 keV).
# No inherent filtration is applied in SpekPy; filtration is modeled in TOPAS geometry
# (0.7 mm Ti beam hardening filter, bowtie filter).
```

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `calibration.yaml` | Create | Per-machine calibration data file (project root) |
| `src/models/calibration.py` | Create | Dataclass models for calibration data |
| `src/services/calibration.py` | Create | CalibrationService |
| `src/spectrum_generator.py` | Modify | Write `simulation_metadata.yaml`, fix dk comment |
| `src/modes/base.py` | Modify | Remove NbParticlesInTime.txt copy, add `simulation_metadata.yaml` copy to runfolder |
| `src/services/ctdi_calculator.py` | Modify | Add backward-compatible metadata reader |
| `tests/unit/test_calibration.py` | Create | Tests for CalibrationService |
| `tests/unit/test_spectrum_generator.py` | Modify | Update for new metadata output |
| `tests/unit/test_base_mode.py` | Modify | Remove NbParticlesInTime assertions |

## Key Design Decisions

1. **Post-hoc DCF only** — simulation always runs with DCF=1.0, calibration applied after. Enables re-calibration without re-running TOPAS.

2. **Backward compatible** — keep writing `head_calibration_factor.txt` alongside new `simulation_metadata.yaml`. CTDICalculator reads new format first, falls back to old.

3. **calibration.yaml entries are filled in-place** — `compute_dcf()` finds the matching `(kV, fan_mode)` entry (keyed by these two fields, no separate ID), fills in `dcf` and `measured_ctdi_w_mGy`, and writes the file back. Entries start with null values and get filled as measurements are taken. No new entries are appended after initial creation.

4. **CalibrationService owns the pipeline** — `apply()` method chains CTDICalculator → DCF lookup → mAs scaling. Callers don't need to know the decomposition.

5. **Frozen dataclasses in `src/models/`** — follows existing project convention for domain value objects, with YAML round-tripping via `from_yaml()` classmethod.
