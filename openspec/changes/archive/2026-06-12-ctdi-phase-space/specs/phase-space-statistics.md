## phase-space-statistics

### Requirement
Beam characterization statistics must be extractable from `.phsp` files for analysis of post-filtration beam properties.

### Specification
- `PhaseSpaceAnalyzer` class in `src/services/phase_space_analyzer.py`.
- Reads TOPAS Binary format `.phsp` files.
- Computes and returns a structured dict with:
  - `particle_count: int` — total particles in file
  - `survival_fraction: float` — particle_count / original_histories (from metadata)
  - `mean_energy_keV: float` — mean of energy distribution
  - `std_energy_keV: float` — standard deviation of energy distribution
  - `energy_spectrum: Dict` — histogram with `bin_edges` and `counts` (default 100 bins, configurable)
  - `spatial_x: Dict` — histogram of x positions
  - `spatial_y: Dict` — histogram of y positions
  - `angular_dx: Dict` — histogram of x direction cosines
  - `angular_dy: Dict` — histogram of y direction cosines
  - `particle_types: Dict[str, int]` — count by particle type
  - `file_size_mb: float`
- Optional: saves matplotlib summary plots (energy spectrum, spatial map, angular distribution) to the runfolder.
- Accepts `metadata_path: str` parameter to read original histories for survival fraction calculation.

### Acceptance Criteria
- Given a valid Binary `.phsp` file, `PhaseSpaceAnalyzer.analyze()` returns all listed statistics without error.
- Energy spectrum histogram has correct bin counts that sum to `particle_count`.
- `survival_fraction` is correctly computed when metadata is provided.
- The analyzer handles files with only gamma particles (kV imaging case).
