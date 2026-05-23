## Why

CTDI phantom templates were redesigned to use TOPAS Parallel Worlds (Layered Mass Geometry) for simultaneous scoring of all 5 chamber plug positions, but the mode code (`CtdiMode`) still generates 5 separate parameter files and runs 5 sequential TOPAS processes. Two bugs result:

1. **Broken scoring**: The template scorer section uses `{% for position in plug_positions %}` but the context provides only `plug_position` (singular). Jinja2 silently skips the undefined loop, so all 15 scorers are omitted from rendered output. Simulations run but produce no dose data.

2. **5x unnecessary runs**: The parallel worlds design enables a single TOPAS run scoring all plugs simultaneously. The current 5-run approach is 5x slower for no benefit.

Additionally, `SimulationType.CTDI` has value `"CTDI validation"` but the headsourcecode template checks `{% if simulation_type == 'CTDI' %}`. This works only because `CtdiMode.build_main_context()` hardcodes `"CTDI"`, bypassing the enum. The string should be aligned.

## What Changes

- Fix CTDI mode to render a single phantom file with all 5 plugs scored via parallel worlds
- Provide `plug_positions` (plural list) in the template context instead of `plug_position` (singular)
- Remove the `_generate_plug_files` 5-file generation loop
- Change `CtdiMode.execute()` to a single TOPAS run
- Align `SimulationType.CTDI` enum value with template expectation
- Update `SimulationRunner.run_ctdi` signature for single-run mode

## Capabilities

### Modified Capabilities
- `ctdi-simulation`: Single-run parallel worlds replaces 5-run sequential approach

## Impact

- `src/modes/ctdi_mode.py` — context builder, file generation, execute method
- `src/models/enums.py` — `SimulationType.CTDI` value
- `src/boilerplates/headsourcecode_boilerplate.j2` — LayeredMassGeometry conditional
- `src/simulation_runner.py` — `run_ctdi` signature
- `tests/unit/test_ctdi_mode.py` — updated tests
- `tests/unit/shared.py` — updated context constants
