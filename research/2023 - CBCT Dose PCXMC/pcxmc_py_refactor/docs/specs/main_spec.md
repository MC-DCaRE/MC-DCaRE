# Main Module Specification

## Overview
The main module provides the command-line interface (CLI) for running PCXMC simulations directly from the terminal.

## Function: main

### Purpose
Entry point for CLI usage of the PCXMC simulation system.

### Function Signature
```python
def main():
```

### CLI Usage
```bash
python -m src.main [CONFIG_FILE]
```

### Parameters (via command line)
- **CONFIG_FILE** (str, optional): Path to configuration file
  - Default: "configs/demo_config.yaml"
  - Supports: .yaml, .yml, .m files

### Workflow
1. **Parse Arguments**: Extract configuration file path from command line
2. **Load Configuration**: Use ConfigLoader to load and validate configuration
3. **Initialize Simulation**: Create PCXMC runner instance
4. **Run Simulation**: Execute dose calculation
5. **Display Results**: Print summary statistics
6. **Save Output**: Save results to file (if configured)

### Error Handling
- **FileNotFoundError**: Display user-friendly error for missing config file
- **ValueError**: Display validation errors with helpful suggestions
- **ImportError**: Handle missing dependencies gracefully
- **KeyboardInterrupt**: Clean exit on Ctrl+C

### Exit Codes
- **0**: Success
- **1**: Configuration error
- **2**: File not found
- **3**: Validation error
- **4**: Runtime error

### Usage Examples

```bash
# Basic usage with default config
python -m src.main

# Custom configuration file
python -m src.main configs/custom_config.yaml

# With full path
python -m src.main /path/to/config.yaml

# Help information
python -m src.main --help
```

### Integration Points
- **ConfigLoader**: For configuration loading and validation
- **PCXMC Runner**: For actual simulation execution
- **Logging**: For progress reporting and debugging

### Dependencies
- **argparse**: For command-line argument parsing
- **sys**: For exit codes and system interaction
- **pathlib**: For path handling
