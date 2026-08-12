#!/bin/bash
# Don't use set -e — continue even if one replay fails
ROOT="/home/bchcphysics/Github/MC-DCaRE"
GRID="$ROOT/test_voxel_output/mrcp_am/mrcp_am_voxels_fine.npy"
DICOM_DIR="$ROOT/data/P145/voxelized/MRCP_AM_5mm/dicom"
INCLUDE_DIR="$ROOT/src/boilerplates/TOPAS_includeFiles"

# Format: name|phsp_dir|isoZ|metadata_dir
COMBOS=(
  "125hf_abdomen|phsp_125hf|200|phsp_125hf"
  "125hf_thorax|phsp_125hf|460|phsp_125hf"
  "125hf_spine|phsp_125hf|300|phsp_125hf"
  "140hf_pelvis|phsp_140hf|0|phsp_140hf"
  "80ff_body|phsp_80ff|200|phsp_80ff"
  "80ff_head|phsp_80ff|795|phsp_80ff"
  "100ff_head|phsp_100ff|795|phsp_100ff"
  "100hf_neck|phsp_100hf|600|phsp_100hf"
  "100hf_body|phsp_100hf|200|phsp_100hf"
  "125ff_pelvis|phsp_125ff|0|phsp_125ff"
  "125ff_abdomen|phsp_125ff|200|phsp_125ff"
  "125ff_thorax|phsp_125ff|460|phsp_125ff"
  "125ff_extremity|phsp_125ff|-200|phsp_125ff"
)

TOPAS="/opt/topas/TOPAS/OpenTOPAS-install/bin/topas"
count=0
total=${#COMBOS[@]}

for combo in "${COMBOS[@]}"; do
  IFS='|' read -r name phsp_dir isoZ meta_dir <<< "$combo"
  count=$((count + 1))
  rf="$ROOT/runfolder/replay_${name}"
  echo ""
  echo "================================================================"
  echo "  [$count/$total] $name (isocenter Z=${isoZ}mm)"
  echo "================================================================"

  # Create runfolder
  rm -rf "$rf"
  mkdir -p "$rf"

  # Copy filtered phase space + header
  cp "$ROOT/runfolder/$phsp_dir/phase_space/beam_exit_phsp_filtered.phsp" "$rf/"
  cp "$ROOT/runfolder/$phsp_dir/phase_space/beam_exit_phsp_filtered.header" "$rf/"

  # Copy required files
  cp "$INCLUDE_DIR/Muen.dat" "$rf/"
  cp "$INCLUDE_DIR/HUtoMaterialSchneider.txt" "$rf/"
  cp "$ROOT/runfolder/$meta_dir/phase_space/simulation_metadata.yaml" "$rf/simulation_metadata.yaml"

  # Set n_scorer_active = N_scoring × R × M for phase-space replay normalization
  # N_scoring=5M (total_histories), R=36 (sequential times), M=5 (PhaseSpaceMultipleUse)
  python3 -c "
import yaml
path = '$rf/simulation_metadata.yaml'
with open(path) as f:
    m = yaml.safe_load(f)
m['n_scorer_active_histories'] = 5000000 * 36 * 5
with open(path, 'w') as f:
    yaml.dump(m, f, default_flow_style=False)
"

  # Generate replay parameter file
  cat > "$rf/phantom_replay.txt" << PARAM
# Phantom Replay: $name (isocenter Z=${isoZ}mm)
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
s:So/beam/PhaseSpaceFileName = "beam_exit_phsp_filtered"
s:So/beam/Component = "Rotation"
i:So/beam/PhaseSpaceMultipleUse = 5

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
s:Ge/Patient/DicomDirectory = "$DICOM_DIR"
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
  echo "Running TOPAS..."
  cd "$rf"
  $TOPAS phantom_replay.txt > topas_output.log 2>&1
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "  ERROR: TOPAS exit code $exit_code. Check topas_output.log"
  else
    echo "  Exit code: 0 (success)"
  fi
  
  # Verify outputs
  dtm_size=$(wc -l < organ_dose.csv 2>/dev/null || echo "0")
  tle_size=$(wc -l < organ_dose_tle.csv 2>/dev/null || echo "0")
  echo "  DTM CSV: $dtm_size lines, TLE CSV: $tle_size lines"

  cd "$ROOT"
done

echo ""
echo "================================================================"
echo "  ALL $total REPLAYS COMPLETE"
echo "================================================================"
