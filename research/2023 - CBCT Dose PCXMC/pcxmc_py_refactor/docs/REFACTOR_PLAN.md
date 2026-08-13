# PCXMC MATLAB to Python Refactoring Plan

## Status: In Progress
**Last Updated**: 2025-08-13 14:57 (Sydney Time)

## 1. Project Structure
- [x] Create documentation directory
- [x] Create source code structure
- [ ] Initialize test framework

## 2. Core Module Conversion
| Module              | MATLAB Source        | Python Target     | Status     |
|---------------------|----------------------|-------------------|------------|
| Angle Handling      | WrapTo360.m         | utils.py          | In Progress|
| Geometry Operations | findIntersections.m | geometry.py       | Planned    |
| Field Calculations  | subField*.m         | fields.py         | Planned    |
| Scaling             | resScale.m          | scaling.py        | Planned    |
| Main Workflow       | Main.m              | main.py           | Planned    |

## 3. Configuration System
- [ ] Define YAML schema
- [ ] Implement config loader
- [ ] Validate against MATLAB test cases

## 4. Testing Strategy
- [ ] Setup pytest
- [ ] Create golden master tests
- [ ] Implement geometry unit tests

## 5. Validation
- [ ] Compare MATLAB/Python outputs
- [ ] Verify PCXMC input compatibility

## 6. Implementation Notes
- Starting with utility functions (WrapTo360.m → utils.py)
- Will maintain MATLAB compatibility for PCXMC input format
- Using numpy for numerical operations
- Using matplotlib for plotting (if needed)
