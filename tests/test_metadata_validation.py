"""Unit tests for metadata validation in calendar tools."""

from unittest.mock import Mock, patch

import pytest

from tools.calendar import GoogleCalendarTools


class TestMetadataValidation:
    """Test cases for _validate_metadata method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth_manager = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth_manager)

    def test_validate_empty_metadata_returns_empty_dict(self):
        """Test that empty metadata returns empty dict."""
        result = self.calendar_tools._validate_metadata({})
        assert result == {}

    def test_validate_none_metadata_returns_empty_dict(self):
        """Test that None metadata returns empty dict."""
        result = self.calendar_tools._validate_metadata(None)
        assert result == {}

    def test_validate_metadata_not_dict_raises_error(self):
        """Test that non-dict metadata raises ValueError."""
        with pytest.raises(ValueError, match="metadata must be a dictionary"):
            self.calendar_tools._validate_metadata("not a dict")

    # chat_title validation tests
    def test_validate_chat_title_valid(self):
        """Test valid chat_title passes validation."""
        metadata = {"chat_title": "Team Planning Meeting"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Team Planning Meeting"

    def test_validate_chat_title_with_html_escapes(self):
        """Test chat_title with HTML is escaped."""
        metadata = {"chat_title": "<script>alert('xss')</script>"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert (
            result["chat_title"]
            == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        )

    def test_validate_chat_title_with_special_chars_escapes(self):
        """Test chat_title with special characters is escaped."""
        metadata = {"chat_title": "Q&A Session: What's Next?"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Q&amp;A Session: What&#x27;s Next?"

    def test_validate_chat_title_strips_whitespace(self):
        """Test chat_title strips leading/trailing whitespace."""
        metadata = {"chat_title": "  Meeting  "}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Meeting"

    def test_validate_chat_title_empty_string_raises_error(self):
        """Test empty chat_title raises ValueError."""
        with pytest.raises(ValueError, match="chat_title cannot be empty"):
            self.calendar_tools._validate_metadata({"chat_title": ""})

    def test_validate_chat_title_whitespace_only_raises_error(self):
        """Test whitespace-only chat_title raises ValueError."""
        with pytest.raises(ValueError, match="chat_title cannot be empty"):
            self.calendar_tools._validate_metadata({"chat_title": "   "})

    def test_validate_chat_title_too_long_raises_error(self):
        """Test chat_title over 200 chars raises ValueError."""
        long_title = "A" * 201
        with pytest.raises(
            ValueError, match="chat_title must be 200 characters or less"
        ):
            self.calendar_tools._validate_metadata({"chat_title": long_title})

    def test_validate_chat_title_exactly_200_chars_passes(self):
        """Test chat_title with exactly 200 chars passes."""
        title = "A" * 200
        result = self.calendar_tools._validate_metadata({"chat_title": title})
        assert len(result["chat_title"]) == 200

    def test_validate_chat_title_not_string_raises_error(self):
        """Test non-string chat_title raises ValueError."""
        with pytest.raises(ValueError, match="chat_title must be a string"):
            self.calendar_tools._validate_metadata({"chat_title": 123})

    # chat_url validation tests
    def test_validate_chat_url_valid_claude_ai(self):
        """Test valid claude.ai URL passes validation."""
        metadata = {"chat_url": "https://claude.ai/chat/abc123"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_url"] == "https://claude.ai/chat/abc123"

    def test_validate_chat_url_valid_subdomain(self):
        """Test valid claude.ai subdomain URL passes validation."""
        metadata = {"chat_url": "https://app.claude.ai/chat/abc123"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_url"] == "https://app.claude.ai/chat/abc123"

    def test_validate_chat_url_strips_whitespace(self):
        """Test chat_url strips leading/trailing whitespace."""
        metadata = {"chat_url": "  https://claude.ai/chat/123  "}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_url"] == "https://claude.ai/chat/123"

    def test_validate_chat_url_http_raises_error(self):
        """Test HTTP (non-HTTPS) URL raises ValueError."""
        with pytest.raises(ValueError, match="chat_url must use HTTPS protocol"):
            self.calendar_tools._validate_metadata(
                {"chat_url": "http://claude.ai/chat/123"}
            )

    def test_validate_chat_url_wrong_domain_raises_error(self):
        """Test URL from wrong domain raises ValueError."""
        with pytest.raises(ValueError, match="chat_url must be from claude.ai domain"):
            self.calendar_tools._validate_metadata(
                {"chat_url": "https://example.com/chat/123"}
            )

    def test_validate_chat_url_empty_string_raises_error(self):
        """Test empty chat_url raises ValueError."""
        with pytest.raises(ValueError, match="chat_url cannot be empty"):
            self.calendar_tools._validate_metadata({"chat_url": ""})

    def test_validate_chat_url_invalid_format_raises_error(self):
        """Test invalid URL format raises ValueError."""
        with pytest.raises(ValueError, match="chat_url must use HTTPS protocol"):
            self.calendar_tools._validate_metadata({"chat_url": "not a url"})

    def test_validate_chat_url_not_string_raises_error(self):
        """Test non-string chat_url raises ValueError."""
        with pytest.raises(ValueError, match="chat_url must be a string"):
            self.calendar_tools._validate_metadata({"chat_url": 123})

    # project_name validation tests
    def test_validate_project_name_valid(self):
        """Test valid project_name passes validation."""
        metadata = {"project_name": "Q4 Planning"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["project_name"] == "Q4 Planning"

    def test_validate_project_name_with_html_escapes(self):
        """Test project_name with HTML is escaped."""
        metadata = {"project_name": "<b>Important</b> Project"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["project_name"] == "&lt;b&gt;Important&lt;/b&gt; Project"

    def test_validate_project_name_strips_whitespace(self):
        """Test project_name strips leading/trailing whitespace."""
        metadata = {"project_name": "  Project  "}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["project_name"] == "Project"

    def test_validate_project_name_empty_string_raises_error(self):
        """Test empty project_name raises ValueError."""
        with pytest.raises(ValueError, match="project_name cannot be empty"):
            self.calendar_tools._validate_metadata({"project_name": ""})

    def test_validate_project_name_too_long_raises_error(self):
        """Test project_name over 100 chars raises ValueError."""
        long_name = "A" * 101
        with pytest.raises(
            ValueError, match="project_name must be 100 characters or less"
        ):
            self.calendar_tools._validate_metadata({"project_name": long_name})

    def test_validate_project_name_exactly_100_chars_passes(self):
        """Test project_name with exactly 100 chars passes."""
        name = "A" * 100
        result = self.calendar_tools._validate_metadata({"project_name": name})
        assert len(result["project_name"]) == 100

    def test_validate_project_name_not_string_raises_error(self):
        """Test non-string project_name raises ValueError."""
        with pytest.raises(ValueError, match="project_name must be a string"):
            self.calendar_tools._validate_metadata({"project_name": 123})

    # created_date validation tests
    def test_validate_created_date_valid_format(self):
        """Test valid ISO date format passes validation."""
        metadata = {"created_date": "2025-09-28"}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["created_date"] == "2025-09-28"

    def test_validate_created_date_strips_whitespace(self):
        """Test created_date strips leading/trailing whitespace."""
        metadata = {"created_date": "  2025-09-28  "}
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["created_date"] == "2025-09-28"

    def test_validate_created_date_with_time_raises_error(self):
        """Test ISO datetime (with time) raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata(
                {"created_date": "2025-09-28T10:00:00"}
            )

    def test_validate_created_date_invalid_format_raises_error(self):
        """Test invalid date format raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "09/28/2025"})

    def test_validate_created_date_invalid_date_raises_error(self):
        """Test invalid date (e.g., Feb 31) raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-02-31"})

    def test_validate_created_date_feb_30_raises_error(self):
        """Test February 30 raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-02-30"})

    def test_validate_created_date_month_13_raises_error(self):
        """Test month 13 raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-13-01"})

    def test_validate_created_date_april_31_raises_error(self):
        """Test April 31 raises ValueError (April only has 30 days)."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-04-31"})

    def test_validate_created_date_non_leap_year_feb_29_raises_error(self):
        """Test Feb 29 in non-leap year raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-02-29"})

    def test_validate_created_date_leap_year_feb_29_passes(self):
        """Test Feb 29 in leap year (2024) passes validation."""
        result = self.calendar_tools._validate_metadata({"created_date": "2024-02-29"})
        assert result["created_date"] == "2024-02-29"

    def test_validate_created_date_day_zero_raises_error(self):
        """Test day 0 raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-01-00"})

    def test_validate_created_date_month_zero_raises_error(self):
        """Test month 0 raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-00-15"})

    def test_validate_created_date_negative_day_raises_error(self):
        """Test negative day raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025-01--05"})

    def test_validate_created_date_negative_month_raises_error(self):
        """Test negative month raises ValueError."""
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools._validate_metadata({"created_date": "2025--01-15"})

    def test_validate_created_date_empty_string_raises_error(self):
        """Test empty created_date raises ValueError."""
        with pytest.raises(ValueError, match="created_date cannot be empty"):
            self.calendar_tools._validate_metadata({"created_date": ""})

    def test_validate_created_date_not_string_raises_error(self):
        """Test non-string created_date raises ValueError."""
        with pytest.raises(ValueError, match="created_date must be a string"):
            self.calendar_tools._validate_metadata({"created_date": 20250928})

    # Combined field validation tests
    def test_validate_all_fields_valid(self):
        """Test all valid fields pass validation."""
        metadata = {
            "chat_title": "Team Meeting",
            "chat_url": "https://claude.ai/chat/abc123",
            "project_name": "Q4 Planning",
            "created_date": "2025-09-28",
        }
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Team Meeting"
        assert result["chat_url"] == "https://claude.ai/chat/abc123"
        assert result["project_name"] == "Q4 Planning"
        assert result["created_date"] == "2025-09-28"

    def test_validate_partial_metadata_valid(self):
        """Test partial metadata with only some fields passes."""
        metadata = {
            "chat_title": "Meeting",
            "project_name": "Project",
        }
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Meeting"
        assert result["project_name"] == "Project"
        assert "chat_url" not in result
        assert "created_date" not in result

    def test_validate_unknown_fields_ignored(self):
        """Test unknown fields are ignored (not included in output)."""
        metadata = {
            "chat_title": "Meeting",
            "unknown_field": "value",
        }
        result = self.calendar_tools._validate_metadata(metadata)
        assert result["chat_title"] == "Meeting"
        assert "unknown_field" not in result


class TestFormatMetadata:
    """Test cases for _format_metadata method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth_manager = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth_manager)

    def test_format_empty_metadata_returns_empty_string(self):
        """Test that empty metadata dict returns empty string."""
        result = self.calendar_tools._format_metadata({})
        assert result == ""

    def test_format_metadata_all_none_values_returns_empty_string(self):
        """Test that metadata with all None values returns empty string."""
        metadata = {
            "created_date": None,
            "project_name": None,
            "chat_title": None,
            "chat_url": None,
        }
        result = self.calendar_tools._format_metadata(metadata)
        assert result == ""

    def test_format_metadata_all_empty_strings_returns_empty_string(self):
        """Test that metadata with all empty strings returns empty string."""
        metadata = {
            "created_date": "",
            "project_name": "",
            "chat_title": "",
            "chat_url": "",
        }
        result = self.calendar_tools._format_metadata(metadata)
        assert result == ""

    def test_format_metadata_with_one_field_formats_correctly(self):
        """Test that metadata with one field formats correctly."""
        metadata = {"chat_title": "Test Chat"}
        result = self.calendar_tools._format_metadata(metadata)
        assert "\n\n---\n📋 Context:\n" in result
        assert "Chat: Test Chat" in result
        assert "Created:" not in result
        assert "Project:" not in result

    def test_format_metadata_with_all_fields_formats_correctly(self):
        """Test that metadata with all fields formats correctly."""
        metadata = {
            "created_date": "2025-09-28",
            "project_name": "Test Project",
            "chat_title": "Test Chat",
            "chat_url": "https://claude.ai/chat/test123",
        }
        result = self.calendar_tools._format_metadata(metadata)
        assert "\n\n---\n📋 Context:\n" in result
        assert "Created: 2025-09-28" in result
        assert "Project: Test Project" in result
        assert "Chat: Test Chat" in result
        assert "URL: https://claude.ai/chat/test123" in result


class TestUpdateEventValidation:
    """Test cases for update_event metadata validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth_manager = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth_manager)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_with_valid_metadata(self, mock_build):
        """Test update_event validates metadata correctly."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock the get() call to return existing event
        existing_event = {
            "id": "event-123",
            "summary": "Old Title",
            "description": "Old description",
            "start": {"dateTime": "2025-09-28T10:00:00", "timeZone": "America/Toronto"},
            "end": {"dateTime": "2025-09-28T11:00:00", "timeZone": "America/Toronto"},
        }
        mock_service.events().get().execute.return_value = existing_event

        # Mock the update() call
        updated_event = existing_event.copy()
        updated_event["description"] = (
            "Old description\n\n---\n📋 Context:\n"
            "Created: 2025-09-28\nProject: Q4 Planning\n"
            "Chat: Team Meeting\nURL: https://claude.ai/chat/abc123\n"
        )
        mock_service.events().update().execute.return_value = updated_event

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "created_date": "2025-09-28",
                "project_name": "Q4 Planning",
                "chat_title": "Team Meeting",
                "chat_url": "https://claude.ai/chat/abc123",
            },
        }

        self.calendar_tools.update_event(params)

        # Verify metadata was validated and added
        update_call = mock_service.events().update.call_args
        assert "📋 Context:" in update_call.kwargs["body"]["description"]
        assert "Created: 2025-09-28" in update_call.kwargs["body"]["description"]

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_rejects_xss_in_metadata(self, mock_build):
        """Test update_event prevents XSS attacks in metadata."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
        }
        mock_service.events().get().execute.return_value = existing_event

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "chat_title": "<script>alert('xss')</script>",
            },
        }

        # Should not raise - but XSS should be escaped
        self.calendar_tools.update_event(params)

        # Verify XSS was escaped
        update_call = mock_service.events().update.call_args
        description = update_call.kwargs["body"]["description"]
        assert "&lt;script&gt;" in description
        assert "<script>" not in description

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_rejects_malicious_url(self, mock_build):
        """Test update_event prevents malicious URLs in metadata."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
        }
        mock_service.events().get().execute.return_value = existing_event

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "chat_url": "https://evil.com/phishing",
            },
        }

        # Should raise ValueError for malicious URL
        with pytest.raises(ValueError, match="chat_url must be from claude.ai domain"):
            self.calendar_tools.update_event(params)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_rejects_http_url(self, mock_build):
        """Test update_event enforces HTTPS for URLs."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
        }
        mock_service.events().get().execute.return_value = existing_event

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "chat_url": "http://claude.ai/chat/abc",
            },
        }

        # Should raise ValueError for HTTP URL
        with pytest.raises(ValueError, match="chat_url must use HTTPS protocol"):
            self.calendar_tools.update_event(params)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_with_invalid_date(self, mock_build):
        """Test update_event validates date format."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
        }
        mock_service.events().get().execute.return_value = existing_event

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "created_date": "09/28/2025",  # Invalid format
            },
        }

        # Should raise ValueError for invalid date format
        with pytest.raises(
            ValueError, match="created_date must be in ISO format \\(YYYY-MM-DD\\)"
        ):
            self.calendar_tools.update_event(params)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_repeated_updates_no_double_escaping(self, mock_build):
        """Test that repeated metadata updates don't cause double-escaping."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Initial event
        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
            "description": "Original description",
        }
        mock_service.events().get().execute.return_value = existing_event

        # First update with metadata containing special chars
        params_first = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "chat_title": "Q&A Session",
            },
        }

        # Mock first update response
        first_updated = existing_event.copy()
        first_updated["description"] = (
            "Original description\n\n---\n📋 Context:\nChat: Q&amp;A Session\n"
        )
        mock_service.events().update().execute.return_value = first_updated

        self.calendar_tools.update_event(params_first)

        # Second update - simulate getting the already-updated event
        mock_service.events().get().execute.return_value = first_updated

        # Second update with same metadata
        params_second = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "chat_title": "Q&A Session",  # Raw input again
            },
        }

        self.calendar_tools.update_event(params_second)

        # Verify second update call
        second_update_call = mock_service.events().update.call_args_list[1]
        description = second_update_call.kwargs["body"]["description"]

        # Should have Q&amp;A only once, not Q&amp;amp;A
        assert description.count("Q&amp;A") == 1
        assert "Q&amp;amp;A" not in description
        # Original description should still be present
        assert "Original description" in description

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_replaces_old_metadata(self, mock_build):
        """Test that updating metadata replaces old metadata section."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Event with existing metadata
        existing_event = {
            "id": "event-123",
            "summary": "Event",
            "start": {"dateTime": "2025-09-28T10:00:00"},
            "end": {"dateTime": "2025-09-28T11:00:00"},
            "description": (
                "User notes here\n\n---\n📋 Context:\n"
                "Created: 2025-09-01\n"
                "Project: Old Project\n"
                "Chat: Old Chat\n"
            ),
        }
        mock_service.events().get().execute.return_value = existing_event

        # Update with completely different metadata
        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "metadata": {
                "created_date": "2025-09-28",
                "project_name": "New Project",
                "chat_title": "New Chat",
                "chat_url": "https://claude.ai/chat/new123",
            },
        }

        self.calendar_tools.update_event(params)

        # Verify update call
        update_call = mock_service.events().update.call_args
        description = update_call.kwargs["body"]["description"]

        # User notes should be preserved
        assert "User notes here" in description
        # Old metadata should be gone
        assert "Old Project" not in description
        assert "Old Chat" not in description
        assert "2025-09-01" not in description
        # New metadata should be present
        assert "New Project" in description
        assert "New Chat" in description
        assert "2025-09-28" in description
        assert "https://claude.ai/chat/new123" in description
