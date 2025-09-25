# Tasks: Day-of-Week Calendar Enhancement

## Relevant Files

- `src/utils/date_helpers.py` - New utility module for timezone-aware datetime parsing and day-of-week calculations
- `src/utils/test_date_helpers.py` - Unit tests for date helper functions
- `src/tools/calendar.py` - Existing calendar tools that need enhancement with computed fields
- `tests/test_calendar_enhanced.py` - New comprehensive tests for enhanced calendar functionality
- `README.md` - Documentation updates for new computed fields in calendar responses

### Notes

- Unit tests should be placed alongside the code files they are testing
- Use `pytest tests/` to run all tests, or `pytest tests/test_calendar_enhanced.py` for specific tests
- The enhancement maintains backward compatibility by adding new `computed` fields without modifying existing response structure
- All datetime calculations should use Python's `zoneinfo` for proper timezone handling including DST transitions

## Tasks

- [ ] 1.0 Create Date Utility Infrastructure
  - [ ] 1.1 Create `src/utils/date_helpers.py` with timezone-aware parsing functions
  - [ ] 1.2 Implement `parse_calendar_datetime()` function to parse ISO datetime strings with timezone
  - [ ] 1.3 Implement `get_day_of_week()` function that returns day name (e.g., "Saturday")
  - [ ] 1.4 Implement `get_date_string()` function that returns YYYY-MM-DD format
  - [ ] 1.5 Implement `calculate_duration()` function for human-readable duration strings
  - [ ] 1.6 Implement `spans_multiple_days()` function to detect multi-day events
  - [ ] 1.7 Add proper error handling for invalid datetime formats and timezones
  - [ ] 1.8 Create comprehensive unit tests in `src/utils/test_date_helpers.py`

- [ ] 2.0 Enhance Calendar Event Response Format
  - [ ] 2.1 Design the `computed` field structure with all required properties
  - [ ] 2.2 Create `add_computed_fields()` helper function in calendar.py
  - [ ] 2.3 Ensure computed fields handle edge cases (midnight boundaries, DST transitions)
  - [ ] 2.4 Add validation to ensure computed fields match the original datetime data
  - [ ] 2.5 Test computed field generation with various timezone combinations

- [ ] 3.0 Update Calendar Tool Methods
  - [ ] 3.1 Modify `list_events()` method to include computed fields in response
  - [ ] 3.2 Modify `create_event()` method to return computed fields in created event response
  - [ ] 3.3 Modify `update_event()` method to return computed fields in updated event response
  - [ ] 3.4 Import and integrate `date_helpers` module in calendar.py
  - [ ] 3.5 Update event formatting logic to call `add_computed_fields()` for all events
  - [ ] 3.6 Verify backward compatibility - existing response fields remain unchanged

- [ ] 4.0 Add Comprehensive Testing
  - [ ] 4.1 Create `tests/test_calendar_enhanced.py` for integration testing
  - [ ] 4.2 Test day-of-week accuracy across multiple timezones (EST, PST, UTC, etc.)
  - [ ] 4.3 Test edge cases: events at midnight, DST transitions, leap years
  - [ ] 4.4 Test multi-day events and duration calculations
  - [ ] 4.5 Test error handling for malformed datetime strings
  - [ ] 4.6 Test backward compatibility - verify existing response structure intact
  - [ ] 4.7 Add performance tests for computed field generation with large event lists
  - [ ] 4.8 Test with real calendar data to validate accuracy

- [ ] 5.0 Validation and Documentation
  - [ ] 5.1 Update README.md with examples of new computed fields in calendar responses
  - [ ] 5.2 Add code comments explaining the computed field logic
  - [ ] 5.3 Run full test suite to ensure no regressions
  - [ ] 5.4 Test the MCP server end-to-end with enhanced calendar responses
  - [ ] 5.5 Verify Claude can successfully use day-of-week information without calculation errors
  - [ ] 5.6 Create example calendar responses showing before/after format