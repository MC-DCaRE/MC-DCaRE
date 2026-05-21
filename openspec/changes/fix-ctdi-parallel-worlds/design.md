## Context

The CTDI phantom Jinja2 templates (`CTDIphantom_16.j2`, `CTDIphantom_32.j2`) already define all 5 chamber plugs as `Material="Air"` with `isParallel="True"` and individual `ParallelWorldName` values. The headsourcecode template declares `LayeredMassGeometryWorlds = 5`. The scorer section uses `{% for position in plug_positions %}` to create 15 scorers (TLE, DTM, DTW × 5 positions).

But `CtdiMode._generate_plug_files()` calls `build_sub_context(config, plug_position=position)` 5 times with a single plug name, then concatenates headsource + phantom per plug into 5 separate files. The context provides `plug_position` (singular string) but the template expects `plug_positions` (plural list), so the scorer loop silently produces zero iterations.

## Goals / Non-Goals

**Goals:**
- Single TOPAS run scoring all 5 plugs simultaneously via parallel worlds
- Correctly rendered scorer section (15 scorers per phantom file)
- Align `SimulationType.CTDI` value across enum, orchestrator, and template
- Maintain backward-compatible output file naming (ChamberPlugCentre_tle.csv, etc.)

**Non-Goals:**
- Changing phantom geometry or physics
- Modifying the CTDI post-processing calculator
- Altering DICOM mode behavior

## Decisions

1. **Single phantom render**: `build_sub_context` provides `plug_positions` as a list of all 5 position names. No material swapping needed (all plugs are Air in the template).

2. **Single combined file**: Headsource + phantom rendered into one file (e.g., `ctdi_simulation.txt`). One TOPAS run produces all 15 output CSVs.

3. **Enum alignment**: Change `SimulationType.CTDI` from `"CTDI validation"` to `"CTDI"`. Update GUI combo box to display `"CTDI validation"` as label while using `"CTDI"` as value. Add a `label` property to the enum if needed for GUI display.

4. **Remove `_generate_plug_files`**: Replace with a single render in `execute()` or `prepare_run()`. The headsourcecode + phantom are concatenated once.

## Risks / Trade-offs

- **Risk**: TOPAS LayeredMassGeometry may have memory overhead with 5 parallel worlds. Mitigation: this is the standard TOPAS approach for multi-region scoring; it's well-documented.
- **Risk**: CTDI calculator expects specific CSV file naming (`ChamberPlugTop_dtw.csv`). Output naming must remain identical. The scorer `OutputFile` settings in the template already use the correct names.
- **Trade-off**: Single run means no per-plug TOPAS logs. All plug scoring shares one log file. Acceptable since the current 5 logs are redundant.
