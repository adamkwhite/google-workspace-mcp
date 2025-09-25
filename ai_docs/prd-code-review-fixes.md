# PRD: Code Review Fixes for Day-of-Week Enhancement

## Product Overview

Fix critical code quality issues identified in the pragmatic code review for the day-of-week calendar enhancement feature before merging to main branch.

## Problem Statement

The day-of-week enhancement PR contains several code quality issues that need resolution:
1. Import path anti-pattern using runtime sys.path manipulation
2. Test file located in wrong directory (src/utils/ instead of tests/)
3. Missing type annotations reducing IDE support and documentation

## Functional Requirements

### FR1: Fix Import Path Anti-Pattern
- **Description**: Replace runtime sys.path manipulation in `src/tools/calendar.py` with proper Python package imports
- **Current State**: Uses `sys.path.append()` to import from utils directory
- **Target State**: Uses standard Python import patterns with proper package structure
- **Acceptance Criteria**:
  - Remove sys.path manipulation code
  - Create proper `__init__.py` files for package structure
  - Use standard import: `from src.utils.date_helpers import add_computed_fields`
  - Import works in all contexts (development, testing, packaging)

### FR2: Move Test File to Correct Location
- **Description**: Move `src/utils/test_date_helpers.py` to proper `tests/` directory
- **Current State**: Test file located alongside source code in utils directory
- **Target State**: Test file in `tests/test_date_helpers.py` following standard Python conventions
- **Acceptance Criteria**:
  - File moved to `tests/test_date_helpers.py`
  - Import paths updated to work from new location
  - All 35 unit tests continue to pass
  - Test discovery works with pytest

### FR3: Add Missing Type Annotations
- **Description**: Complete type annotations for all functions in `src/utils/date_helpers.py`
- **Current State**: Some functions lack complete type hints
- **Target State**: Full type coverage for better IDE support and documentation
- **Acceptance Criteria**:
  - Import necessary typing modules (Dict, Any, Optional, Union)
  - Add return type annotations for all functions
  - Add parameter type annotations where missing
  - Type checker (mypy) passes without errors

## Technical Requirements

### TR1: Maintain Backward Compatibility
- All existing functionality must continue to work
- No changes to public API or response formats
- All existing tests must continue to pass

### TR2: No Runtime Performance Impact
- Import changes must not affect server startup time
- Date helper functions maintain same performance characteristics

### TR3: Testing Requirements
- All existing unit tests (35) must pass after changes
- Integration tests (3) must continue to work
- Add verification that imports work correctly in different contexts

## User Stories

### US1: As a Developer
**Story**: As a developer working on this codebase, I want proper Python import patterns so that the code works reliably across different execution environments (development, testing, CI/CD, packaging).

**Acceptance Criteria**:
- Code can be imported and used from any valid Python context
- No runtime sys.path manipulation required
- Standard Python tooling (IDEs, linters, type checkers) work correctly

### US2: As a Maintainer
**Story**: As a code maintainer, I want test files in the standard location so that they are discoverable by testing tools and follow Python conventions.

**Acceptance Criteria**:
- Tests are discoverable by pytest from project root
- Test file location follows standard Python project structure
- Test coverage tools can find and analyze test files correctly

### US3: As a Developer Using IDEs
**Story**: As a developer using modern IDEs and type checkers, I want complete type annotations so that I get proper autocompletion, error detection, and documentation.

**Acceptance Criteria**:
- IDE provides accurate autocompletion for all functions
- Type checker catches type-related errors before runtime
- Function signatures are self-documenting through type hints

## Success Metrics

- ✅ All 35 unit tests pass after changes
- ✅ All 3 integration tests pass after changes
- ✅ Import statements work without sys.path manipulation
- ✅ Code passes type checking with mypy
- ✅ pytest discovers and runs all tests from standard location

## Dependencies

- Existing day-of-week enhancement feature (already implemented)
- Python package structure understanding
- pytest testing framework
- mypy type checker (optional but recommended)

## Timeline

**Target**: Complete before merging PR to main branch
**Effort**: ~2-3 hours of development work
**Priority**: HIGH - blocks PR merge