#!/bin/bash
# Per-protocol phase space scoring + phantom replay
# Each protocol gets its own phase space (correct collimator field)
ROOT="/home/bchcphysics/Github/MC-DCaRE"
TOPAS="/opt/topas/TOPAS/OpenTOPAS-install/bin/topas"
INCLUDE_DIR="$ROOT/src/boilerplates/TOPAS_includeFiles"
DICOM_DIR="$ROOT/data/P145/voxelized/MRCP_AM_5mm/dicom"
M_REUSE=2

# protocol_name|exposure_mAs|isocenter_Z
PROTOCOLS=(
  "Image Gently|100.2|200"
  "Head|150.3|795"
  "Short Thorax|210|460"
  "Spotlight|750|200"
  "Thorax|268.5|460"
  "Pelvis|1074|0"
  "Pelvis Large|1700.5|0"
  "4D Spotlight|750|460"
  "4D Thorax|270|460"
  "Abdomen|1080|200"
  "Abdo Spotlight|750|200"
  "Breast 360|270|460"
  "Extremity Spotlight|750|-200"
  "Head and Shoulders|150|600"
  "Head SRS|150|795"
  "Paediatric Body|150|200"
  "Paediatric Head|100|795"
  "Pelvis Spotlight|751.5|0"
  "SBRT Spine|270|300"
  "Thorax Spotlight|750|460"
)

# ===== PHASE 1: Score all phase spaces =====
echo "========================================================"
echo "  PHASE 1: Scoring 20 phase spaces (~30s each)"
echo "========================================================"

for entry in "${PROTOCOLS[@]}"; do
  IFS='|' read -r name mas isoZ <<< "$entry"
  # Create slug for directory naming
  slug=$(echo "$name" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

  echo -n "  Scoring $name... "

  # Generate scoring config
  cat > "$ROOT/score_${slug}.yaml" << YML
general:
  g4_data_directory: /opt/topas/GEANT4/G4DATA
  topas_directory: /opt/topas/TOPAS/OpenTOPAS-install/bin/topas
  seed: '42'
  threads: '20'
  histories: '5000000'
  log_filename: simulation.log
imaging:
  simulation_type: CTDI
  rotation_direction: CBCT Anticlockwise
  imaging_mode: $name
  exposure: '${mas} mAs'
  sequential_times: '1'
ctdi:
  couch_enabled: false
  user_blade_enabled: false
  graphics_enabled: false
  water_chamber_enabled: false
  phase_space_mode: 'score'
YML

  # Run scoring
  cd "$ROOT"
  uv run python run_simulation.py run "score_${slug}.yaml" > /dev/null 2>&1

  # Find and rename output runfolder
  latest=$(ls -td runfolder/2026-* 2>/dev/null | head -1)
  if [ -n "$latest" ] && [ -f "$latest/phase_space/beam_exit_phsp.phsp" ]; then
    rm -rf "runfolder/phsp_${slug}"
    mv "$latest" "runfolder/phsp_${slug}"
    npart=$(grep "Number of Scored" "runfolder/phsp_${slug}/phase_space/beam_exit_phsp.header" | awk '{print $NF}')
    echo "OK ($npart particles)"
  else
    echo "FAILED"
  fi
done

echo ""
echo "========================================================"
echo "  PHASE 2: Running 20 phantom replays"
echo "========================================================"

count=0
total=${#PROTOCOLS[@]}
for entry in "${PROTOCOLS[@]}"; do
  IFS='|' read -r name mas isoZ <<< "$entry"
  slug=$(echo "$name" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
  count=$((count + 1))

  echo ""
  echo "  [$count/$total] $name (Z=${isoZ}mm, ${mas} mAs)"

  # Create replay runfolder
  rf="$ROOT/runfolder/replay_${slug}"
  rm -rf "$rf"
  mkdir -p "$rf"

  # Copy full (unfiltered) phase space — collimator already restricts field
  cp "runfolder/phsp_${slug}/phase_space/beam_exit_phsp.phsp" "$rf/"
  cp "runfolder/phsp_${slug}/phase_space/beam_exit_phsp.header" "$rf/"
  cp "$INCLUDE_DIR/Muen.dat" "$rf/"
  cp "$INCLUDE_DIR/HUtoMaterialSchneider.txt" "$rf/"

  # Copy metadata and set n_scorer_active = N_scoring × R × M
  python3 -c "
import yaml
with open('runfolder/phsp_${slug}/phase_space/simulation_metadata.yaml') as f:
    m = yaml.safe_load(f)
m['n_scorer_active_histories'] = 5000000 * 36 * ${M_REUSE}
with open('$rf/simulation_metadata.yaml', 'w') as f:
    yaml.dump(m, f, default_flow_style=False)
"

  # Generate replay parameter file
  cat > "$rf/phantom_replay.txt" << PARAM
i:Ts/Seed = 42
i:Ts/NumberOfThreads = 20
s:Ts/G4DataDirectory = "/opt/topas/GEANT4/G4DATA"
i:Ts/ShowHistoryCountAtInterval = 500000
d:Ge/World/HLX = 1.2 m
d:Ge/World/HLY = 1.2 m
d:Ge/World/HLZ = 2.0 m
s:Ph/ListName = "Default"
b:Ph/ListProcesses = "False"
s:Ph/Default/Type = "Geant4_Modular"
sv:Ph/Default/Modules = 1 "g4em-standard_opt4"
d:Ph/Default/EMRangeMin = 100. eV
d:Ph/Default/EMRangeMax = 1.0 MeV
s:Ge/Rotation/Type = "Group"
s:Ge/Rotation/Parent = "World"
dc:Ge/Rotation/RotX = 0 deg
dc:Ge/Rotation/RotY = 180 deg
dc:Ge/Rotation/RotZ = Tf/Rotate/Value deg
s:So/beam/Type = "PhaseSpace"
s:So/beam/PhaseSpaceFileName = "beam_exit_phsp"
s:So/beam/Component = "Rotation"
i:So/beam/PhaseSpaceMultipleUse = ${M_REUSE}
i:Tf/NumberOfSequentialTimes = 36
i:Tf/Verbosity = 0
d:Tf/TimelineEnd = 60.0 s
s:Tf/Rotate/Function = "Linear deg"
d:Tf/Rotate/Rate = 6.0 deg/s
d:Tf/Rotate/StartValue = 0 deg
includeFile = HUtoMaterialSchneider.txt
s:Ge/Patient/Parent = "World"
s:Ge/Patient/Material = "G4_WATER"
s:Ge/Patient/Type = "TsDicomPatient"
s:Ge/Patient/ImagingtoMaterialConverter = "Schneider"
s:Ge/Patient/DicomDirectory = "${DICOM_DIR}"
sv:Ge/Patient/DicomModalityTags = 1 "CT"
b:Ge/Patient/IgnoreInconsistentFrameOfReferenceUID = "True"
dc:Ge/IsocenterX = 0.0 mm
dc:Ge/IsocenterY = 0.0 mm
dc:Ge/IsocenterZ = ${isoZ} mm
dc:Ge/Patient/UserTransX = 0.0 mm
dc:Ge/Patient/UserTransY = 0.0 mm
dc:Ge/Patient/UserTransZ = 0.0 mm
d:Ge/Patient/InterX = Ge/IsocenterX + Ge/Patient/UserTransX mm
d:Ge/Patient/InterY = Ge/IsocenterY + Ge/Patient/UserTransY mm
d:Ge/Patient/InterZ = Ge/IsocenterZ + Ge/Patient/UserTransZ mm
dc:Ge/Patient/DicomOriginX = 0.0 mm
dc:Ge/Patient/DicomOriginY = 0.0 mm
dc:Ge/Patient/DicomOriginZ = 0.0 mm
dc:Ge/Patient/TransX = Ge/Patient/DicomOriginX - Ge/Patient/InterX mm
dc:Ge/Patient/TransY = Ge/Patient/DicomOriginY - Ge/Patient/InterY mm
dc:Ge/Patient/TransZ = Ge/Patient/DicomOriginZ - Ge/Patient/InterZ mm
s:Sc/PhantomDose/Quantity = "DoseToMedium"
s:Sc/PhantomDose/Component = "Patient"
s:Sc/PhantomDose/IfOutputFileAlreadyExists = "Overwrite"
s:Sc/PhantomDose/OutputType = "CSV"
s:Sc/PhantomDose/OutputFile = "organ_dose"
sv:Sc/PhantomDose/Report = 1 "Sum"
s:Sc/PhantomTLE/Quantity = "TrackLengthEstimator"
s:Sc/PhantomTLE/InputFile = "Muen.dat"
s:Sc/PhantomTLE/Component = "Patient"
s:Sc/PhantomTLE/IfOutputFileAlreadyExists = "Overwrite"
s:Sc/PhantomTLE/OutputType = "CSV"
s:Sc/PhantomTLE/OutputFile = "organ_dose_tle"
sv:Sc/PhantomTLE/Report = 1 "Sum"
b:Ts/ShowCPUTime = "True"
PARAM

  # Run TOPAS
  echo "    Running TOPAS..."
  cd "$rf"
  $TOPAS phantom_replay.txt > topas_output.log 2>&1
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "    ERROR: TOPAS exit code $exit_code"
  else
    dtm=$(wc -l < organ_dose.csv 2>/dev/null || echo "0")
    tle=$(wc -l < organ_dose_tle.csv 2>/dev/null || echo "0")
    echo "    OK (DTM=$dtm TLE=$tle lines)"
  fi
  cd "$ROOT"
done

echo ""
echo "========================================================"
echo "  ALL $total PROTOCOLS COMPLETE"
echo "========================================================"
