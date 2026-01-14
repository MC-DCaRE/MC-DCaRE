# Config File Implementation - Executive Summary

## Overview

This document provides a high-level summary of the config file support implementation plan for MC-DCaRE. For detailed specifications, see [`config_file_implementation_plan.md`](config_file_implementation_plan.md).

## Problem Statement

The current MC-DCaRE application has several architectural limitations:

1. **No Config File Support**: All parameters must be entered through the GUI
2. **Tight Coupling**: GUI, runtime, and editing logic are tightly coupled
3. **No Validation**: Parameters are only validated in the GUI
4. **Hard to Automate**: No programmatic way to configure simulations
5. **Poor Reusability**: Configuration logic is scattered across modules

## Solution Overview

Implement a configuration file system that:

- Supports YAML and JSON formats
- Provides type-safe configuration using Pydantic
- Maintains backward compatibility with existing GUI
- Enables programmatic configuration
- Follows SOLID principles, YAGNI, DRY, and DDD

## Key Benefits

| Benefit | Description |
|---------|-------------|
| **Automation** | Configure simulations without GUI interaction |
| **Reusability** | Save and share configuration templates |
| **Validation** | Comprehensive validation before simulation runs |
| **Type Safety** | Pydantic ensures correct data types |
| **Documentation** | Self-documenting configuration files |
| **Backward Compatible** | Existing GUI workflow unchanged |

## Architecture Highlights

### SOLID Principles Applied

- **Single Responsibility**: Each module handles one concern
- **Open/Closed**: Extensible without modifying existing code
- **Liskov Substitution**: Config sources are interchangeable
- **Interface Segregation**: Focused interfaces for different consumers
- **Dependency Inversion**: Depend on abstractions (config interfaces)

### Domain-Driven Design

Four bounded contexts:
1. **Simulation Configuration**: Runtime parameters
2. **Imaging Configuration**: kV, exposure, rotation
3. **DICOM Configuration**: Patient data, isocenter
4. **CTDI Configuration**: Phantom type, couch settings

### DRY Implementation

- Reuse [`defaultvalues.py`](../src/defaultvalues.py) as Pydantic defaults
- Extract validation logic from GUI to models
- Share string parsing logic
- Consolidate imaging mode mappings

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Deliverables**:
- Pydantic domain models
- Config loader (YAML/JSON)
- Config validator
- Default values module
- Unit tests

**Files Created**:
- [`src/mc_dcare/core/configuration/base.py`](../src/mc_dcare/core/configuration/base.py)
- [`src/mc_dcare/core/configuration/models.py`](../src/mc_dcare/core/configuration/models.py)
- [`src/mc_dcare/core/configuration/loader.py`](../src/mc_dcare/core/configuration/loader.py)
- [`src/mc_dcare/core/configuration/validator.py`](../src/mc_dcare/core/configuration/validator.py)
- [`src/mc_dcare/core/configuration/defaults.py`](../src/mc_dcare/core/configuration/defaults.py)

**No Breaking Changes**: Existing code unchanged

### Phase 2: Integration (Week 2)
**Deliverables**:
- Config file loading in GUI
- Config file saving from GUI
- Runtime handler integration
- Edits handler integration
- Integration tests

**Files Modified**:
- [`topas_gui.py`](../topas_gui.py) - Add Load/Save buttons
- [`runtime_handler.py`](../src/runtime_handler.py) - Accept config objects
- [`edits_handler.py`](../src/edits_handler.py) - Accept config objects

**No Breaking Changes**: GUI workflow unchanged, config loading optional

### Phase 3: Refactoring (Week 3)
**Deliverables**:
- Backward compatibility adapter
- Deprecation warnings
- Refactored defaultvalues.py
- Updated documentation

**Files Created**:
- [`src/mc_dcare/core/configuration/adapters.py`](../src/mc_dcare/core/configuration/adapters.py)

**Files Modified**:
- [`src/defaultvalues.py`](../src/defaultvalues.py) - Add deprecation notice

**No Breaking Changes**: Adapter layer maintains compatibility

### Phase 4: Documentation & CLI (Week 4)
**Deliverables**:
- User guide
- API documentation
- Config file examples
- CLI tool
- Updated README

**Files Created**:
- [`docs/config_file_guide.md`](config_file_guide.md)
- [`docs/api/configuration.md`](api/configuration.md)
- [`examples/config/dicom_example.yaml`](../examples/config/dicom_example.yaml)
- [`examples/config/ctdi_example.yaml`](../examples/config/ctdi_example.yaml)
- [`src/mc_dcare/cli/config_cli.py`](../src/mc_dcare/cli/config_cli.py)

**No Breaking Changes**: Documentation and CLI additions only

## File Structure

```
src/mc_dcare/core/configuration/
├── __init__.py              # Package exports
├── base.py                  # Abstract base classes
├── models.py                # Pydantic domain models
├── loader.py                # Config file loading
├── saver.py                 # Config file saving
├── validator.py             # Validation logic
├── merger.py                # Config merging
├── defaults.py              # Default values
└── adapters.py              # Backward compatibility
```

## Example Config File

```yaml
# DICOM simulation configuration
simulation_type: "DICOM"

simulation:
  g4_data_directory: "/path/to/G4Data"
  topas_directory: "/path/to/topas/bin/topas"
  seed: 9
  threads: 4
  histories: 100000

imaging:
  mode: "Head"
  fan_mode: "Full Fan"
  rotation_direction: "CBCT Clockwise"
  start_angle: 0.0
  voltage: 100.0
  exposure: 100.0

dicom:
  directory: "/path/to/dicom"
  rp_file: "/path/to/RTPlan.dcm"
  translation_x: "0. mm"
  translation_y: "0. mm"
  translation_z: "0. mm"
  rotation_yaw: "0. deg"
  isocenter_x: "0. mm"
  isocenter_y: "0. mm"
  isocenter_z: "0. mm"
```

## Usage Examples

### Load Config in Python

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader

config = ConfigLoader.load_from_file("my_config.yaml")
print(config.simulation.histories)  # 100000
```

### Save Config in Python

```python
from src.mc_dcare.core.configuration.saver import ConfigSaver
from src.mc_dcare.core.configuration.models import MCDCaREConfig

config = MCDCaREConfig(simulation={'histories': 50000})
ConfigSaver.save_to_file(config, "output.yaml")
```

### Validate Config via CLI

```bash
python -m src.mc_dcare.cli.config_cli validate my_config.yaml
```

### Generate Default Config

```bash
python -m src.mc_dcare.cli.config_cli generate default.yaml --type dicom
```

## Testing Strategy

- **Unit Tests**: 90%+ coverage for config module
- **Integration Tests**: 80%+ coverage for GUI integration
- **System Tests**: End-to-end workflow coverage
- **Backward Compatibility**: All existing tests pass

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing GUI workflow | Adapter layer maintains compatibility |
| Pydantic learning curve | Clear documentation and examples |
| Performance overhead | Validation only on load/save, no runtime overhead |
| Complex migration | Phased approach with clear documentation |

## Success Criteria

- [ ] All unit tests pass (90%+ coverage)
- [ ] All integration tests pass (80%+ coverage)
- [ ] GUI load/save working
- [ ] Runtime handler using config objects
- [ ] No regressions in existing functionality
- [ ] Backward compatibility maintained
- [ ] Documentation complete
- [ ] CLI functional

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Foundation | Week 1 | Planned |
| Phase 2: Integration | Week 2 | Planned |
| Phase 3: Refactoring | Week 3 | Planned |
| Phase 4: Documentation | Week 4 | Planned |

**Total Duration**: 4 weeks

## Dependencies

- `pydantic`: Data validation and settings management
- `pyyaml`: YAML support
- (No additional dependencies for JSON)

## Migration Path

1. **Phase 1**: New config system exists alongside old code
2. **Phase 2**: GUI uses new config system (optional for users)
3. **Phase 3**: Adapter layer bridges old and new
4. **Phase 4**: Deprecation warnings added
5. **Future**: Old code removed (after transition period)

## What's NOT Included (YAGNI)

- Config file versioning/migration
- Remote config loading
- Config file encryption
- GUI state persistence
- Config file diffing tools
- Config history tracking

These features can be added in future iterations if needed.

## Documentation

- [`config_file_implementation_plan.md`](config_file_implementation_plan.md) - Detailed implementation plan
- [`config_architecture_overview.md`](config_architecture_overview.md) - Architecture diagrams and design decisions
- [`config_implementation_quickref.md`](config_implementation_quickref.md) - Quick reference for developers
- [`changelog.md`](changelog.md) - Change log

## Next Steps

1. Review this implementation plan
2. Approve the phased approach
3. Switch to Code mode to begin Phase 1 implementation
4. Create unit tests as each module is implemented
5. Integrate with GUI in Phase 2
6. Maintain backward compatibility in Phase 3
7. Complete documentation in Phase 4

## Questions?

For questions about this implementation plan, refer to:

1. [`config_file_implementation_plan.md`](config_file_implementation_plan.md) - Detailed specifications
2. [`config_architecture_overview.md`](config_architecture_overview.md) - Architecture details
3. [`config_implementation_quickref.md`](config_implementation_quickref.md) - Quick reference

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-09  
**Status**: Ready for Review
