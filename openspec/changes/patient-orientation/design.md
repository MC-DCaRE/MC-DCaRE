## Context

The TOPAS `Ge/Rotation/RotY` line currently uses a hardcoded patient yaw:
```
dc:Ge/Rotation/RotY= 180. deg + Ge/patrotation/yaw
```

Where `Ge/patrotation/yaw` is hardcoded to `0 deg`. TOPAS supports `RotX`, `RotY`, `RotZ` for full 3-axis rotation. For DICOM patient simulations, pitch (anterior-posterior tilt) and roll (lateral tilt) are needed alongside yaw (axial rotation) to model real patient setup.

Current:
```
World
  Rotation (RotY = 180 + yaw, RotZ = time feature)
    BeamPosition
    Collimators
```

Proposed:
```
World
  Rotation (RotX = pitch, RotY = 180 + yaw, RotZ = roll + time feature)
    BeamPosition
    Collimators
```

## Goals / Non-Goals

**Goals:**
- Add pitch and roll rotation support to DICOM mode
- All three rotations configurable via YAML and GUI
- Backward compatible (defaults to 0 deg for all)

**Non-Goals:**
- Applying rotations in CTDI mode (phantom is stationary)
- Changing the rotation rate or time feature behavior
- Adding non-cardinal rotation angles

## Decisions

1. **Three separate config fields**: `patient_pitch`, `patient_roll`, `patient_yaw` as `Quantity` objects (after config-modernization). Default `0 deg`.

2. **Template variables**: `{{ patient_pitch }}`, `{{ patient_roll }}`, `{{ patient_yaw }}` in headsourcecode template. The `Ge/Rotation/RotZ` line combines roll with time feature: `Tf/Rotate/Value + {{ patient_roll }}`.

3. **DICOM mode only**: Rotations only applied when `simulation_type == 'DICOM'`. CTDI mode phantom is stationary.

## Risks / Trade-offs

- **Risk**: Combining roll with time-feature rotation on RotZ could cause unexpected beam paths. Mitigation: verify with dry-run that beam trajectory is correct for non-zero roll values.
- **Risk**: Sign convention for pitch/roll/yaw must match IEC patient coordinate system (X=Left, Y=Posterior, Z=Head). Mitigation: document sign convention in template comments.
