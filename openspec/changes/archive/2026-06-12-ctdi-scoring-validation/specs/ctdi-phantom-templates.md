## ctdi-phantom-templates

### Requirement
CTDI phantom templates support optional water-filled chamber scoring volumes for sensitivity studies, in addition to existing air chambers.

### Specification
- New config field `ctdi.water_chamber_enabled: bool` (default `false`) in `CtdiConfig`.
- When `true`, the template adds 5 additional parallel world volumes named `ChamberPlug{Position}_water` with `Material="Water"`, same geometry as air chambers.
- 5 additional DTM scorers target the water volumes, outputting to `{Position}_water_dtm.csv`.
- Air chambers and their scorers remain unchanged — both air and water score simultaneously.
- `CTDICalculator._find_chamber_files()` discovers water chamber CSVs when present.
- Water chamber results are labelled `"scorer_type": "dtw_water"` and `"is_primary": false`.

### Acceptance Criteria
- With `water_chamber_enabled=false` (default), template output is identical to current.
- With `water_chamber_enabled=true`, template contains 10 parallel world volumes (5 air + 5 water) and 20 scorers (15 existing + 5 new).
- `CTDICalculator` processes water chamber CSVs and returns results with `"dtw_water"` label.
