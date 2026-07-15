<!-- Context: simulation/troubleshooting | Priority: high | Version: 1.0 | Updated: 2026-06-12 -->

# Simulation Troubleshooting

**Purpose**: Common issues, error patterns, and resolution strategies for MC-DCaRE simulations.
**Audience**: Simulation agent.

## Configuration Errors

### "No imaging mode found for key"
**Cause:** `rotation_direction` + `imaging_mode` combination not in IMAGING_MODES dictionary.
**Fix:**
1. Check spelling of `imaging_mode` and `rotation_direction`
2. List valid keys: read `src/models/imaging_mode.py` IMAGING_MODES keys
3. If no match, set parameters manually (field sizes, blade openings, voltage)

### "Invalid simulation_type"
**Cause:** `simulation_type` not "CTDI" or "DICOM".
**Fix:** Set to exactly "CTDI" or "DICOM" (case-sensitive).

### Missing required fields
**Cause:** Config YAML incomplete. SimulationConfig dataclass requires certain fields.
**Fix:** Run `uv run python run_simulation.py validate <config>` to identify missing fields. Generate a complete template with `generate-config`.

### Invalid parameter ranges
**Cause:** kVp outside 40-150, phantom_size not "16 cm"/"32 cm", fan_mode not recognized.
**Fix:** Check parameter values against enums in `src/models/enums.py`.

## Execution Errors

### TOPAS binary not found
**Signal:** Process exits immediately, log shows "command not found" or similar.
**Fix:** Check `general.topas_directory` points to the TOPAS executable (not just the directory). Path should end in `/topas`.

### Geant4 data files missing
**Signal:** TOPAS starts but crashes with "G4Data" errors in topas_ctdi.log.
**Fix:** Check `general.g4_data_directory` points to valid Geant4 data directory. Required datasets: G4EMLOW, PhotonEvaporation, etc.

### Geometry overlap errors
**Signal:** Geant4 warnings about overlapping volumes in topas_ctdi.log.
**Fix:** Check field sizes don't exceed phantom geometry. For CTDI, ensure field sizes are compatible with phantom diameter (16 or 32 cm).

### TOPAS hangs / no progress
**Signal:** Process running but no CSV output appearing.
**Fix:**
1. Check `topas_ctdi.log` for progress markers
2. Histories may be very high — check expected runtime
3. TOPAS may be waiting for G4 data — check data paths

## Result Errors

### Zero dose in CSV output
**Cause:** Histories too low, geometry misconfiguration, scorer not in correct volume.
**Fix:**
1. Increase histories (minimum 100k)
2. Verify field sizes cover the phantom center
3. Check blade openings aren't fully closed
4. Verify TOPAS parameter file has correct scorer definitions

### CTDI-w calculation fails
**Signal:** `calculate_ctdiw.py` reports missing CSV files or empty data.
**Fix:**
1. Verify ChamberPlug CSV files exist in runfolder
2. Check CSV files are not empty (TOPAS completed successfully)
3. Confirm scorer naming matches expected pattern: `ChamberPlug{Position}_{scorer}.csv`

### Calibration gives unreasonable DCF
**Signal:** Recommended DCF is very far from 1.0 (>10x or <0.01x).
**Fix:**
1. Check units — measured value should be in mSv (millisievert)
2. Verify simulation used correct kVp and filtration
3. Confirm phantom size matches physical measurement setup
4. Check histories are sufficient for statistical accuracy

### Statistical uncertainty too high
**Signal:** Large variance between repeated runs with same parameters.
**Fix:** Increase histories. Statistical uncertainty scales as 1/sqrt(N). Doubling histories reduces uncertainty by ~30%.

## File System Issues

### Runfolder not created
**Cause:** Output directory permissions or path issues.
**Fix:** Check write permissions in project root. Runfolder created relative to working directory.

### Template rendering fails
**Signal:** Jinja2 UndefinedError or TemplateNotFound.
**Fix:**
1. Verify template files exist in `src/boilerplates/`
2. Check context dict has all required variables for the template
3. Run with `--dry-run` to isolate template rendering from TOPAS execution

### Spectrum generation fails
**Signal:** SpekPy errors during spectrum_generator.py execution.
**Fix:**
1. Check SpekPy is installed: `uv run python -c "import spekpy; print(spekpy.__version__)"`
2. Verify kVp, filtration, anode angle are within SpekPy valid ranges
3. Anode angle typically 7-20 degrees for CT

## Diagnostic Commands

```bash
# Check TOPAS installation
ls -la $(grep topas_directory config.yaml | awk '{print $2}')

# Check Geant4 data
ls $(grep g4_data_directory config.yaml | awk '{print $2}')

# Verify SpekPy
uv run python -c "import spekpy; s=spekpy.Spek(100); print('OK')"

# Inspect generated TOPAS parameter file (dry run)
uv run python run_simulation.py run config.yaml --dry-run
cat runfolder/*/CTDI_all_positions.txt

# Check simulation log for errors
grep -i "error\|fatal\|abort" runfolder/*/simulation.log

# Monitor running TOPAS process
tail -f runfolder/<timestamp>/topas_ctdi.log
```
