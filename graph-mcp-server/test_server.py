"""
Unit tests for Graph Mail MCP Server

Tests the core functionality without requiring external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from dataclasses import FrozenInstanceError

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.auth import extract_bearer_token, validate_token_response, AuthenticationError
from src.graph_client import (
    EmailAddress, MessagePreview, parse_email_address, 
    parse_message_preview, create_draft_payload, DraftMessage
)
from src.config import Config


class TestAuthModule(unittest.TestCase):
    """Test authentication module calculations"""
    
    def test_extract_bearer_token_valid(self):
        """Test extracting bearer token from valid header"""
        header = "Bearer abc123token"
        token = extract_bearer_token(header)
        self.assertEqual(token, "abc123token")
    
    def test_extract_bearer_token_missing(self):
        """Test extracting bearer token from missing header"""
        with self.assertRaises(AuthenticationError):
            extract_bearer_token(None)
    
    def test_extract_bearer_token_malformed(self):
        """Test extracting bearer token from malformed header"""
        with self.assertRaises(AuthenticationError):
            extract_bearer_token("InvalidHeader")
    
    def test_validate_token_response_valid(self):
        """Test validating valid token response"""
        response = {"access_token": "token123", "expires_in": 3600}
        validated = validate_token_response(response)
        self.assertEqual(validated["access_token"], "token123")
    
    def test_validate_token_response_invalid(self):
        """Test validating invalid token response"""
        response = {"error": "invalid_grant", "error_description": "Token expired"}
        with self.assertRaises(AuthenticationError):
            validate_token_response(response)


class TestGraphClientDataModels(unittest.TestCase):
    """Test Graph client data models and calculations"""
    
    def test_email_address_creation(self):
        """Test EmailAddress data class"""
        email = EmailAddress(address="test@example.com", name="Test User")
        self.assertEqual(email.address, "test@example.com")
        self.assertEqual(email.name, "Test User")
    
    def test_parse_email_address(self):
        """Test parsing email address from API response"""
        data = {
            "emailAddress": {
                "address": "user@example.com",
                "name": "John Doe"
            }
        }
        email = parse_email_address(data)
        self.assertEqual(email.address, "user@example.com")
        self.assertEqual(email.name, "John Doe")
    
    def test_parse_message_preview(self):
        """Test parsing message preview from API response"""
        data = {
            "id": "msg123",
            "subject": "Test Email",
            "from": {"emailAddress": {"address": "sender@example.com", "name": "Sender"}},
            "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
            "ccRecipients": [],
            "bodyPreview": "This is a test email body preview",
            "receivedDateTime": "2024-01-01T12:00:00Z",
            "isRead": False,
            "hasAttachments": True
        }
        
        msg = parse_message_preview(data)
        self.assertEqual(msg.id, "msg123")
        self.assertEqual(msg.subject, "Test Email")
        self.assertEqual(msg.from_address.address, "sender@example.com")
        self.assertEqual(len(msg.to_recipients), 1)
        self.assertEqual(msg.to_recipients[0].address, "recipient@example.com")
        self.assertFalse(msg.is_read)
        self.assertTrue(msg.has_attachments)
    
    def test_create_draft_payload(self):
        """Test creating draft payload from DraftMessage"""
        draft = DraftMessage(
            id=None,
            subject="Test Draft",
            to_recipients=[EmailAddress(address="to@example.com", name="To User")],
            cc_recipients=[EmailAddress(address="cc@example.com", name=None)],
            bcc_recipients=[],
            body_content="Test body",
            body_content_type="text"
        )
        
        payload = create_draft_payload(draft)
        
        self.assertEqual(payload["subject"], "Test Draft")
        self.assertEqual(len(payload["toRecipients"]), 1)
        self.assertEqual(payload["toRecipients"][0]["emailAddress"]["address"], "to@example.com")
        self.assertEqual(len(payload["ccRecipients"]), 1)
        self.assertEqual(payload["body"]["content"], "Test body")
        self.assertEqual(payload["body"]["contentType"], "text")


class TestConfig(unittest.TestCase):
    """Test configuration module"""
    
    @patch.dict(os.environ, {
        'AZURE_AD_TENANT_ID': 'test-tenant-id',
        'AZURE_AD_CLIENT_ID': 'test-client-id',
        'AZURE_AD_INSTANCE': 'https://login.microsoftonline.com/test-tenant-id'
    })
    def test_config_from_env(self):
        """Test loading configuration from environment"""
        config = Config.from_env()
        self.assertEqual(config.AZURE_AD_TENANT_ID, 'test-tenant-id')
        self.assertEqual(config.AZURE_AD_CLIENT_ID, 'test-client-id')
        self.assertEqual(config.GRAPH_API_ENDPOINT, 'https://graph.microsoft.com/v1.0')


class TestDesignPrinciples(unittest.TestCase):
    """Test adherence to design principles"""
    
    def test_data_immutability(self):
        """Test that data classes are immutable (Grokking Simplicity)"""
        email = EmailAddress(address="test@example.com", name="Test")
        
        # Should not be able to modify frozen dataclass
        with self.assertRaises(FrozenInstanceError):
            email.address = "new@example.com"
    
    def test_calculations_are_pure(self):
        """Test that calculations are pure functions (same input = same output)"""
        data = {
            "emailAddress": {
                "address": "user@example.com",
                "name": "John Doe"
            }
        }
        
        # Call function multiple times
        result1 = parse_email_address(data)
        result2 = parse_email_address(data)
        
        # Should produce identical results
        self.assertEqual(result1.address, result2.address)
        self.assertEqual(result1.name, result2.name)


if __name__ == '__main__':
    unittest.main()
