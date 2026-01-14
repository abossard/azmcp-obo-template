"""
End-to-End Blackbox Tests for Graph Mail MCP Server

These tests validate the entire data flow from input to output without
requiring external dependencies (Graph API, MSAL). They focus on:
1. Pure calculation functions (parsing, formatting, transformations)
2. End-to-end data flows through the system
3. Edge cases and error handling
4. Blackbox testing approach - tests behavior, not implementation
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph_client import (
    EmailAddress, MessagePreview, MessageFull, DraftMessage,
    parse_email_address, parse_message_preview, parse_message_full,
    create_draft_payload
)
from src.server import parse_recipients, format_message_preview, format_message_full
from src.auth import extract_bearer_token, validate_token_response, AuthenticationError


class TestPureCalculations(unittest.TestCase):
    """
    Comprehensive tests for all pure calculation functions.
    These are blackbox tests - we test inputs and outputs, not implementation.
    """
    
    def test_parse_email_address_complete(self):
        """Test parsing email address with all fields"""
        data = {
            "emailAddress": {
                "address": "john.doe@example.com",
                "name": "John Doe"
            }
        }
        result = parse_email_address(data)
        self.assertEqual(result.address, "john.doe@example.com")
        self.assertEqual(result.name, "John Doe")
    
    def test_parse_email_address_minimal(self):
        """Test parsing email address with only address"""
        data = {
            "emailAddress": {
                "address": "minimal@example.com"
            }
        }
        result = parse_email_address(data)
        self.assertEqual(result.address, "minimal@example.com")
        self.assertIsNone(result.name)
    
    def test_parse_email_address_empty(self):
        """Test parsing empty email data"""
        data = {}
        result = parse_email_address(data)
        self.assertEqual(result.address, "")
        self.assertIsNone(result.name)
    
    def test_parse_email_address_missing_emailaddress_key(self):
        """Test parsing when emailAddress key is missing"""
        data = {"someOtherKey": "value"}
        result = parse_email_address(data)
        self.assertEqual(result.address, "")
        self.assertIsNone(result.name)


class TestMessagePreviewParsing(unittest.TestCase):
    """End-to-end tests for message preview parsing"""
    
    def test_parse_message_preview_complete(self):
        """Test parsing a complete message preview"""
        data = {
            "id": "AAMkAGI2TG93AAA=",
            "subject": "Important Meeting Tomorrow",
            "from": {
                "emailAddress": {
                    "address": "boss@company.com",
                    "name": "Boss Manager"
                }
            },
            "toRecipients": [
                {"emailAddress": {"address": "me@company.com", "name": "Me"}},
                {"emailAddress": {"address": "colleague@company.com", "name": "Colleague"}}
            ],
            "ccRecipients": [
                {"emailAddress": {"address": "cc@company.com", "name": "CC Person"}}
            ],
            "bodyPreview": "This is a preview of the email body content that should be truncated at 200 characters. " * 5,
            "receivedDateTime": "2024-01-14T10:30:00Z",
            "isRead": False,
            "hasAttachments": True
        }
        
        result = parse_message_preview(data)
        
        # Verify all fields
        self.assertEqual(result.id, "AAMkAGI2TG93AAA=")
        self.assertEqual(result.subject, "Important Meeting Tomorrow")
        self.assertEqual(result.from_address.address, "boss@company.com")
        self.assertEqual(result.from_address.name, "Boss Manager")
        self.assertEqual(len(result.to_recipients), 2)
        self.assertEqual(result.to_recipients[0].address, "me@company.com")
        self.assertEqual(len(result.cc_recipients), 1)
        self.assertEqual(result.cc_recipients[0].address, "cc@company.com")
        # Body preview should be truncated to 200 chars
        self.assertEqual(len(result.body_preview), 200)
        self.assertEqual(result.received_datetime, "2024-01-14T10:30:00Z")
        self.assertFalse(result.is_read)
        self.assertTrue(result.has_attachments)
    
    def test_parse_message_preview_minimal(self):
        """Test parsing message with minimal fields"""
        data = {
            "id": "msg123",
            "subject": "",
            "from": {},
            "toRecipients": [],
            "ccRecipients": [],
            "bodyPreview": "",
            "receivedDateTime": "",
            "isRead": True,
            "hasAttachments": False
        }
        
        result = parse_message_preview(data)
        
        self.assertEqual(result.id, "msg123")
        self.assertEqual(result.subject, "")
        self.assertEqual(result.from_address.address, "")
        self.assertEqual(len(result.to_recipients), 0)
        self.assertEqual(len(result.cc_recipients), 0)
        self.assertEqual(result.body_preview, "")
        self.assertTrue(result.is_read)
        self.assertFalse(result.has_attachments)
    
    def test_parse_message_preview_body_truncation(self):
        """Test that body preview is truncated at exactly 200 characters"""
        long_body = "A" * 500  # 500 characters
        data = {
            "id": "test",
            "subject": "Test",
            "from": {},
            "toRecipients": [],
            "ccRecipients": [],
            "bodyPreview": long_body,
            "receivedDateTime": "2024-01-01T00:00:00Z",
            "isRead": False,
            "hasAttachments": False
        }
        
        result = parse_message_preview(data)
        self.assertEqual(len(result.body_preview), 200)
        self.assertEqual(result.body_preview, "A" * 200)


class TestMessageFullParsing(unittest.TestCase):
    """End-to-end tests for full message parsing"""
    
    def test_parse_message_full_complete(self):
        """Test parsing a complete full message"""
        data = {
            "id": "msg-full-123",
            "subject": "Quarterly Report",
            "from": {
                "emailAddress": {
                    "address": "sender@company.com",
                    "name": "Sender Name"
                }
            },
            "toRecipients": [
                {"emailAddress": {"address": "to1@company.com", "name": "To One"}},
                {"emailAddress": {"address": "to2@company.com", "name": "To Two"}}
            ],
            "ccRecipients": [
                {"emailAddress": {"address": "cc@company.com"}}
            ],
            "bccRecipients": [
                {"emailAddress": {"address": "bcc@company.com", "name": "BCC Person"}}
            ],
            "body": {
                "content": "This is the full body content of the email with all details.",
                "contentType": "html"
            },
            "receivedDateTime": "2024-01-14T15:30:00Z",
            "sentDateTime": "2024-01-14T15:29:50Z",
            "isRead": True,
            "hasAttachments": False,
            "importance": "high"
        }
        
        result = parse_message_full(data)
        
        self.assertEqual(result.id, "msg-full-123")
        self.assertEqual(result.subject, "Quarterly Report")
        self.assertEqual(result.from_address.address, "sender@company.com")
        self.assertEqual(len(result.to_recipients), 2)
        self.assertEqual(len(result.cc_recipients), 1)
        self.assertEqual(len(result.bcc_recipients), 1)
        self.assertEqual(result.body_content, "This is the full body content of the email with all details.")
        self.assertEqual(result.body_content_type, "html")
        self.assertEqual(result.received_datetime, "2024-01-14T15:30:00Z")
        self.assertEqual(result.sent_datetime, "2024-01-14T15:29:50Z")
        self.assertTrue(result.is_read)
        self.assertFalse(result.has_attachments)
        self.assertEqual(result.importance, "high")
    
    def test_parse_message_full_missing_optional_fields(self):
        """Test parsing message with missing optional fields"""
        data = {
            "id": "msg-minimal",
            "subject": "Test",
            "from": {},
            "toRecipients": [],
            "ccRecipients": [],
            "bccRecipients": [],
            "body": {
                "content": "Body",
                "contentType": "text"
            },
            "receivedDateTime": "2024-01-01T00:00:00Z",
            # sentDateTime is missing
            "isRead": False,
            "hasAttachments": False,
            "importance": "normal"
        }
        
        result = parse_message_full(data)
        
        self.assertEqual(result.id, "msg-minimal")
        self.assertIsNone(result.sent_datetime)
        self.assertEqual(result.importance, "normal")


class TestDraftPayloadCreation(unittest.TestCase):
    """End-to-end tests for draft payload creation"""
    
    def test_create_draft_payload_complete(self):
        """Test creating draft payload with all fields"""
        draft = DraftMessage(
            id=None,
            subject="Draft Email Subject",
            to_recipients=[
                EmailAddress(address="to1@example.com", name="To One"),
                EmailAddress(address="to2@example.com", name="To Two")
            ],
            cc_recipients=[
                EmailAddress(address="cc@example.com", name="CC Person")
            ],
            bcc_recipients=[
                EmailAddress(address="bcc@example.com", name=None)
            ],
            body_content="This is the draft body content.",
            body_content_type="html"
        )
        
        payload = create_draft_payload(draft)
        
        self.assertEqual(payload["subject"], "Draft Email Subject")
        self.assertEqual(len(payload["toRecipients"]), 2)
        self.assertEqual(payload["toRecipients"][0]["emailAddress"]["address"], "to1@example.com")
        self.assertEqual(payload["toRecipients"][0]["emailAddress"]["name"], "To One")
        self.assertEqual(len(payload["ccRecipients"]), 1)
        self.assertEqual(len(payload["bccRecipients"]), 1)
        self.assertEqual(payload["bccRecipients"][0]["emailAddress"]["address"], "bcc@example.com")
        self.assertIsNone(payload["bccRecipients"][0]["emailAddress"]["name"])
        self.assertEqual(payload["body"]["content"], "This is the draft body content.")
        self.assertEqual(payload["body"]["contentType"], "html")
    
    def test_create_draft_payload_minimal(self):
        """Test creating draft payload with minimal fields"""
        draft = DraftMessage(
            id=None,
            subject="Minimal Draft",
            to_recipients=[EmailAddress(address="recipient@example.com", name=None)],
            cc_recipients=[],
            bcc_recipients=[],
            body_content="Minimal body",
            body_content_type="text"
        )
        
        payload = create_draft_payload(draft)
        
        self.assertEqual(payload["subject"], "Minimal Draft")
        self.assertEqual(len(payload["toRecipients"]), 1)
        self.assertEqual(len(payload["ccRecipients"]), 0)
        self.assertEqual(len(payload["bccRecipients"]), 0)
        self.assertEqual(payload["body"]["contentType"], "text")


class TestRecipientsparsing(unittest.TestCase):
    """End-to-end tests for recipient parsing from tool input"""
    
    def test_parse_recipients_complete(self):
        """Test parsing recipients with all fields"""
        data = [
            {"address": "user1@example.com", "name": "User One"},
            {"address": "user2@example.com", "name": "User Two"},
            {"address": "user3@example.com", "name": "User Three"}
        ]
        
        result = parse_recipients(data)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].address, "user1@example.com")
        self.assertEqual(result[0].name, "User One")
        self.assertEqual(result[2].address, "user3@example.com")
    
    def test_parse_recipients_minimal(self):
        """Test parsing recipients with only address"""
        data = [
            {"address": "minimal@example.com"}
        ]
        
        result = parse_recipients(data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].address, "minimal@example.com")
        self.assertIsNone(result[0].name)
    
    def test_parse_recipients_empty_list(self):
        """Test parsing empty recipient list"""
        data = []
        result = parse_recipients(data)
        self.assertEqual(len(result), 0)


class TestMessageFormatting(unittest.TestCase):
    """End-to-end tests for message formatting"""
    
    def test_format_message_preview(self):
        """Test formatting a message preview for display"""
        msg = MessagePreview(
            id="msg-preview-123",
            subject="Test Email",
            from_address=EmailAddress(address="sender@example.com", name="Sender Name"),
            to_recipients=[
                EmailAddress(address="to1@example.com", name="To One"),
                EmailAddress(address="to2@example.com", name=None)
            ],
            cc_recipients=[
                EmailAddress(address="cc@example.com", name="CC Person")
            ],
            body_preview="This is a preview of the email body.",
            received_datetime="2024-01-14T10:00:00Z",
            is_read=False,
            has_attachments=True
        )
        
        result = format_message_preview(msg)
        
        # Verify all important information is in the output
        self.assertIn("msg-preview-123", result)
        self.assertIn("Test Email", result)
        self.assertIn("Sender Name <sender@example.com>", result)
        self.assertIn("to1@example.com, to2@example.com", result)
        self.assertIn("cc@example.com", result)
        self.assertIn("This is a preview of the email body.", result)
        self.assertIn("False", result)  # is_read
        self.assertIn("True", result)   # has_attachments
    
    def test_format_message_preview_no_cc(self):
        """Test formatting message preview with no CC recipients"""
        msg = MessagePreview(
            id="msg-no-cc",
            subject="No CC Email",
            from_address=EmailAddress(address="sender@example.com", name=None),
            to_recipients=[EmailAddress(address="to@example.com", name=None)],
            cc_recipients=[],
            body_preview="Body",
            received_datetime="2024-01-14T10:00:00Z",
            is_read=True,
            has_attachments=False
        )
        
        result = format_message_preview(msg)
        
        self.assertIn("CC: None", result)
        self.assertIn("sender@example.com", result)  # Should use address when name is None
    
    def test_format_message_full(self):
        """Test formatting a full message for display"""
        msg = MessageFull(
            id="msg-full-456",
            subject="Full Email",
            from_address=EmailAddress(address="from@example.com", name="From Person"),
            to_recipients=[EmailAddress(address="to@example.com", name="To Person")],
            cc_recipients=[EmailAddress(address="cc@example.com", name=None)],
            bcc_recipients=[EmailAddress(address="bcc@example.com", name="BCC Person")],
            body_content="This is the full body content of the email.",
            body_content_type="html",
            received_datetime="2024-01-14T12:00:00Z",
            sent_datetime="2024-01-14T11:59:50Z",
            is_read=True,
            has_attachments=False,
            importance="high"
        )
        
        result = format_message_full(msg)
        
        # Verify all fields are present
        self.assertIn("msg-full-456", result)
        self.assertIn("Full Email", result)
        self.assertIn("From Person <from@example.com>", result)
        self.assertIn("to@example.com", result)
        self.assertIn("cc@example.com", result)
        self.assertIn("bcc@example.com", result)
        self.assertIn("This is the full body content of the email.", result)
        self.assertIn("html", result)
        self.assertIn("2024-01-14T11:59:50Z", result)
        self.assertIn("high", result)
    
    def test_format_message_full_no_sent_datetime(self):
        """Test formatting full message with no sent datetime"""
        msg = MessageFull(
            id="msg-no-sent",
            subject="Draft",
            from_address=EmailAddress(address="me@example.com", name=None),
            to_recipients=[],
            cc_recipients=[],
            bcc_recipients=[],
            body_content="Draft body",
            body_content_type="text",
            received_datetime="2024-01-14T12:00:00Z",
            sent_datetime=None,
            is_read=False,
            has_attachments=False,
            importance="normal"
        )
        
        result = format_message_full(msg)
        
        self.assertIn("Sent: N/A", result)
        self.assertIn("BCC: None", result)


class TestAuthenticationCalculations(unittest.TestCase):
    """End-to-end tests for authentication pure functions"""
    
    def test_extract_bearer_token_valid_formats(self):
        """Test extracting bearer token from various valid formats"""
        test_cases = [
            ("Bearer token123", "token123"),
            ("bearer abc456", "abc456"),
            ("BEARER xyz789", "xyz789"),
        ]
        
        for header, expected_token in test_cases:
            with self.subTest(header=header):
                result = extract_bearer_token(header)
                self.assertEqual(result, expected_token)
    
    def test_extract_bearer_token_invalid_formats(self):
        """Test that invalid formats raise AuthenticationError"""
        invalid_cases = [
            None,
            "",
            "NoBearer token123",
            "Bearer",  # Missing token
            "Bearer  ",  # Only whitespace
            "token123",  # Missing Bearer
        ]
        
        for invalid_header in invalid_cases:
            with self.subTest(header=invalid_header):
                with self.assertRaises(AuthenticationError):
                    extract_bearer_token(invalid_header)
    
    def test_validate_token_response_valid(self):
        """Test validating various valid token responses"""
        test_cases = [
            {"access_token": "token1", "expires_in": 3600},
            {"access_token": "token2", "token_type": "Bearer"},
            {"access_token": "token3", "scope": "Mail.Read"},
        ]
        
        for response in test_cases:
            with self.subTest(response=response):
                result = validate_token_response(response)
                self.assertEqual(result, response)
                self.assertIn("access_token", result)
    
    def test_validate_token_response_invalid(self):
        """Test that responses without access_token raise error"""
        invalid_cases = [
            {"error": "invalid_grant"},
            {"error": "invalid_client", "error_description": "Bad client"},
            {},
            {"token": "wrong_key"},  # Has token but wrong key
        ]
        
        for response in invalid_cases:
            with self.subTest(response=response):
                with self.assertRaises(AuthenticationError):
                    validate_token_response(response)


class TestEndToEndDataFlow(unittest.TestCase):
    """
    Blackbox end-to-end tests simulating complete data flows.
    These tests validate the entire transformation pipeline.
    """
    
    def test_email_preview_flow_complete(self):
        """
        Test complete flow: Graph API response → Parse → Format for display
        """
        # Simulate Graph API response
        api_response = {
            "id": "AAMkAGI2TG93AAA=",
            "subject": "Project Update",
            "from": {
                "emailAddress": {
                    "address": "manager@company.com",
                    "name": "Manager"
                }
            },
            "toRecipients": [
                {"emailAddress": {"address": "me@company.com", "name": "Me"}},
                {"emailAddress": {"address": "team@company.com", "name": "Team"}}
            ],
            "ccRecipients": [
                {"emailAddress": {"address": "stakeholder@company.com", "name": "Stakeholder"}}
            ],
            "bodyPreview": "Here are the latest updates on the project...",
            "receivedDateTime": "2024-01-14T09:00:00Z",
            "isRead": False,
            "hasAttachments": True
        }
        
        # Parse the response
        message = parse_message_preview(api_response)
        
        # Verify parsing
        self.assertEqual(message.subject, "Project Update")
        self.assertEqual(len(message.to_recipients), 2)
        
        # Format for display
        formatted = format_message_preview(message)
        
        # Verify formatting contains all key info
        self.assertIn("AAMkAGI2TG93AAA=", formatted)
        self.assertIn("Project Update", formatted)
        self.assertIn("Manager <manager@company.com>", formatted)
        self.assertIn("me@company.com, team@company.com", formatted)
        self.assertIn("stakeholder@company.com", formatted)
        self.assertIn("Here are the latest updates on the project...", formatted)
    
    def test_draft_creation_flow_complete(self):
        """
        Test complete flow: User input → Parse recipients → Create draft → Generate payload
        """
        # Simulate user input for creating a draft
        to_input = [
            {"address": "recipient1@example.com", "name": "Recipient One"},
            {"address": "recipient2@example.com", "name": "Recipient Two"}
        ]
        cc_input = [
            {"address": "cc@example.com", "name": "CC Person"}
        ]
        
        # Parse recipients
        to_recipients = parse_recipients(to_input)
        cc_recipients = parse_recipients(cc_input)
        
        # Create draft message
        draft = DraftMessage(
            id=None,
            subject="New Draft",
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=[],
            body_content="This is the draft body.",
            body_content_type="html"
        )
        
        # Generate payload for Graph API
        payload = create_draft_payload(draft)
        
        # Verify the complete transformation
        self.assertEqual(payload["subject"], "New Draft")
        self.assertEqual(len(payload["toRecipients"]), 2)
        self.assertEqual(payload["toRecipients"][0]["emailAddress"]["address"], "recipient1@example.com")
        self.assertEqual(len(payload["ccRecipients"]), 1)
        self.assertEqual(payload["body"]["content"], "This is the draft body.")
        self.assertEqual(payload["body"]["contentType"], "html")
    
    def test_token_extraction_and_validation_flow(self):
        """
        Test complete authentication flow: Extract token → Validate response
        """
        # Extract token from header
        auth_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        token = extract_bearer_token(auth_header)
        
        self.assertTrue(len(token) > 0)
        self.assertNotIn("Bearer", token)
        
        # Simulate token acquisition response
        token_response = {
            "access_token": "graph_token_abc123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "Mail.Read Mail.ReadWrite"
        }
        
        # Validate response
        validated = validate_token_response(token_response)
        
        self.assertEqual(validated["access_token"], "graph_token_abc123")
        self.assertEqual(validated["expires_in"], 3600)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions"""
    
    def test_very_long_subject_line(self):
        """Test handling of very long subject lines"""
        long_subject = "A" * 1000
        data = {
            "id": "test",
            "subject": long_subject,
            "from": {},
            "toRecipients": [],
            "ccRecipients": [],
            "bodyPreview": "",
            "receivedDateTime": "2024-01-01T00:00:00Z",
            "isRead": False,
            "hasAttachments": False
        }
        
        msg = parse_message_preview(data)
        self.assertEqual(msg.subject, long_subject)  # Should preserve full subject
    
    def test_special_characters_in_email_addresses(self):
        """Test handling of special characters in email addresses"""
        special_chars_email = "user+tag@sub-domain.example.com"
        data = {
            "emailAddress": {
                "address": special_chars_email,
                "name": "User (Name)"
            }
        }
        
        result = parse_email_address(data)
        self.assertEqual(result.address, special_chars_email)
        self.assertEqual(result.name, "User (Name)")
    
    def test_empty_body_preview(self):
        """Test handling of empty body preview"""
        data = {
            "id": "test",
            "subject": "Empty Body",
            "from": {},
            "toRecipients": [],
            "ccRecipients": [],
            "bodyPreview": "",
            "receivedDateTime": "2024-01-01T00:00:00Z",
            "isRead": False,
            "hasAttachments": False
        }
        
        msg = parse_message_preview(data)
        self.assertEqual(msg.body_preview, "")
        
        # Should format without errors
        formatted = format_message_preview(msg)
        self.assertIn("Body Preview:", formatted)
    
    def test_multiple_recipients_same_address(self):
        """Test handling of duplicate recipient addresses"""
        data = [
            {"address": "duplicate@example.com", "name": "First"},
            {"address": "duplicate@example.com", "name": "Second"},
            {"address": "unique@example.com", "name": "Unique"}
        ]
        
        result = parse_recipients(data)
        
        # Should parse all, even duplicates
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].address, "duplicate@example.com")
        self.assertEqual(result[1].address, "duplicate@example.com")


class TestDataImmutability(unittest.TestCase):
    """Verify that all data structures are truly immutable"""
    
    def test_email_address_immutability(self):
        """EmailAddress should be immutable"""
        email = EmailAddress(address="test@example.com", name="Test")
        
        with self.assertRaises(Exception):  # FrozenInstanceError or similar
            email.address = "new@example.com"
    
    def test_message_preview_immutability(self):
        """MessagePreview should be immutable"""
        msg = MessagePreview(
            id="test",
            subject="Test",
            from_address=EmailAddress(address="from@test.com", name=None),
            to_recipients=[],
            cc_recipients=[],
            body_preview="",
            received_datetime="2024-01-01T00:00:00Z",
            is_read=False,
            has_attachments=False
        )
        
        with self.assertRaises(Exception):
            msg.subject = "New Subject"
    
    def test_draft_message_immutability(self):
        """DraftMessage should be immutable"""
        draft = DraftMessage(
            id=None,
            subject="Draft",
            to_recipients=[],
            cc_recipients=[],
            bcc_recipients=[],
            body_content="Body",
            body_content_type="text"
        )
        
        with self.assertRaises(Exception):
            draft.subject = "New Subject"


class TestPureFunctionProperties(unittest.TestCase):
    """
    Verify that calculation functions have pure function properties:
    - Same input always produces same output (deterministic)
    - No side effects
    - Referential transparency
    """
    
    def test_parse_email_address_deterministic(self):
        """parse_email_address should be deterministic"""
        data = {
            "emailAddress": {
                "address": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Call multiple times
        result1 = parse_email_address(data)
        result2 = parse_email_address(data)
        result3 = parse_email_address(data)
        
        # Should produce identical results
        self.assertEqual(result1.address, result2.address)
        self.assertEqual(result2.address, result3.address)
        self.assertEqual(result1.name, result2.name)
    
    def test_create_draft_payload_deterministic(self):
        """create_draft_payload should be deterministic"""
        draft = DraftMessage(
            id=None,
            subject="Test",
            to_recipients=[EmailAddress(address="to@test.com", name="To")],
            cc_recipients=[],
            bcc_recipients=[],
            body_content="Body",
            body_content_type="text"
        )
        
        # Call multiple times
        payload1 = create_draft_payload(draft)
        payload2 = create_draft_payload(draft)
        
        # Should produce identical payloads
        self.assertEqual(payload1, payload2)
    
    def test_format_message_preview_deterministic(self):
        """format_message_preview should be deterministic"""
        msg = MessagePreview(
            id="test",
            subject="Test",
            from_address=EmailAddress(address="from@test.com", name="From"),
            to_recipients=[EmailAddress(address="to@test.com", name="To")],
            cc_recipients=[],
            body_preview="Preview",
            received_datetime="2024-01-01T00:00:00Z",
            is_read=False,
            has_attachments=False
        )
        
        # Call multiple times
        formatted1 = format_message_preview(msg)
        formatted2 = format_message_preview(msg)
        
        # Should produce identical strings
        self.assertEqual(formatted1, formatted2)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
