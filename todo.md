# Google Workspace MCP - Todo List

## Cornell Numbering System
Format: [Category].[Priority].[Sequence]
- Categories: AUTH, CAL, GMAIL, DOCS, SHEETS, SLIDES, CORE, TEST, DEPLOY
- Priority: 1 (High), 2 (Medium), 3 (Low)
- Sequence: Sequential within category/priority

## Current Sprint Tasks

### Phase 1: Foundation & Integration ✓
- [x] CORE.1.1 - Create project structure following CLAUDE.md template
- [x] CORE.1.2 - Set up virtual environment and dependencies
- [x] AUTH.1.1 - Implement unified OAuth2 authentication
- [x] AUTH.1.2 - Add all necessary scopes for Google Workspace
- [x] CAL.1.1 - Migrate calendar functionality from calendar-mcp
- [x] CAL.1.2 - Create calendar tools module
- [x] GMAIL.1.1 - Implement Gmail tools module
- [x] GMAIL.1.2 - Add send, search, and draft functionality
- [x] DOCS.1.1 - Create basic Google Docs creation tool
- [x] CORE.1.3 - Update server.py with all tools

### Phase 2: Core Features (In Progress)
- [ ] SHEETS.1.1 - Implement create_google_sheet tool
- [ ] SHEETS.1.2 - Add data population functionality
- [ ] SHEETS.1.3 - Support headers and basic formatting
- [ ] SHEETS.2.1 - Write unit tests for sheets operations
- [ ] SLIDES.1.1 - Implement create_google_presentation tool
- [ ] SLIDES.1.2 - Add slide creation with layouts
- [ ] SLIDES.1.3 - Support text content insertion
- [ ] SLIDES.2.1 - Write unit tests for slides operations

### Phase 3: Testing & Deployment
- [ ] TEST.1.1 - Create unit tests for calendar tools
- [ ] TEST.1.2 - Create unit tests for Gmail tools
- [ ] TEST.1.3 - Integration tests for all tools
- [ ] DEPLOY.1.1 - Create unified Claude Desktop configuration
- [ ] DEPLOY.1.2 - Test end-to-end with Claude
- [ ] DOCS.2.1 - Update README with full usage examples
- [ ] DOCS.2.2 - Create migration guide from separate MCPs

### Phase 4: Enhancement
- [ ] CAL.2.1 - Add find_free_time functionality
- [ ] CAL.2.2 - Support recurring events
- [ ] GMAIL.2.1 - Add attachment support
- [ ] GMAIL.2.2 - Implement label management
- [ ] DOCS.2.1 - Add document formatting options
- [ ] SHEETS.2.2 - Add multiple sheet support
- [ ] SLIDES.2.1 - Add image insertion capability
- [ ] CORE.2.1 - Implement retry logic for API failures
- [ ] CORE.2.2 - Add comprehensive logging
- [ ] AUTH.2.1 - Support service accounts (Workspace)

## Backlog

### Features
- [ ] DOCS.3.1 - Document templates support
- [ ] SHEETS.3.1 - Formula support
- [ ] SLIDES.3.1 - Presentation templates
- [ ] CORE.3.1 - Batch operations
- [ ] CORE.3.2 - Update existing documents
- [ ] CORE.3.3 - Document search functionality

### Quality
- [ ] TEST.2.1 - Achieve 80% test coverage
- [ ] TEST.2.2 - Add performance benchmarks
- [ ] DOCS.3.1 - API documentation
- [ ] DOCS.3.2 - Troubleshooting guide

### Infrastructure
- [ ] DEPLOY.2.1 - Docker containerization
- [ ] DEPLOY.2.2 - GitHub Actions CI/CD
- [ ] DEPLOY.3.1 - PyPI package publication

## Completed Tasks
- [x] Project initialization
- [x] OAuth2 authentication implementation
- [x] Google Docs basic functionality
- [x] Unit test framework setup
- [x] Documentation structure

## Notes
- Focus on Gmail account support (most users)
- Service account support is lower priority
- Each tool should be independently testable
- Maintain consistent error handling patterns
- Follow Google API best practices
