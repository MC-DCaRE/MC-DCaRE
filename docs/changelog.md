# Changelog

All notable changes to MC-DCaRE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned - Configuration File Support

#### Added
- Configuration file support (YAML and JSON formats)
- Pydantic-based domain models for type-safe configuration
- Config loader with automatic format detection
- Config saver for YAML and JSON formats
- Config validator with comprehensive validation rules
- Config merger for merging user configs with defaults
- Backward compatibility adapter for existing code
- CLI tool for config validation, conversion, and generation
- Comprehensive documentation and examples

#### Changed
- Refactored [`defaultvalues.py`](../src/defaultvalues.py) to use new config system (deprecated)
- Updated [`runtime_handler.py`](../src/runtime_handler.py) to accept config objects
- Updated [`edits_handler.py`](../src/edits_handler.py) to accept config objects
- Added Load/Save config buttons to GUI

#### Deprecated
- Module-level variables in [`defaultvalues.py`](../src/defaultvalues.py) - Use [`src.mc_dcare.core.configuration.models`](../src/mc_dcare/core/configuration/models.py) instead
- Dict-based configuration approach - Use [`MCDCaREConfig`](../src/mc_dcare/core/configuration/models.py) objects instead

#### Removed
- None (backward compatibility maintained)

#### Fixed
- None

#### Security
- None

---

## [0.1.0] - 2024-XX-XX

### Added
- Initial release of MC-DCaRE
- FreeSimpleGUI-based interface for Monte Carlo simulation configuration
- DICOM patient simulation support
- CTDI phantom validation support
- TOPAS/Geant4 integration
- Beam profile generation using spekpy
- Imaging mode presets (Image Gently, Head, Thorax, Pelvis, etc.)
- Fan mode support (Full Fan, Half Fan)
- CBCT and kV-kV imaging modes
- Couch geometry support
- Blade position calculations

---

## Version History Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
