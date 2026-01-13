"""
Microsoft Graph API client for mail operations

Following design principles:
- Data: Message models (immutable data structures)
- Calculations: Data transformations (pure functions)
- Actions: API calls (side effects)
"""

import logging
from typing import Optional, List
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


# Data models (immutable data structures)
@dataclass(frozen=True)
class EmailAddress:
    """Represents an email address"""
    address: str
    name: Optional[str] = None


@dataclass(frozen=True)
class MessagePreview:
    """
    Preview of an email message.
    
    Contains subject, recipients, cc, and body preview for quick scanning.
    """
    id: str
    subject: str
    from_address: EmailAddress
    to_recipients: List[EmailAddress]
    cc_recipients: List[EmailAddress]
    body_preview: str
    received_datetime: str
    is_read: bool
    has_attachments: bool


@dataclass(frozen=True)
class MessageFull:
    """Complete email message with full body"""
    id: str
    subject: str
    from_address: EmailAddress
    to_recipients: List[EmailAddress]
    cc_recipients: List[EmailAddress]
    bcc_recipients: List[EmailAddress]
    body_content: str
    body_content_type: str
    received_datetime: str
    sent_datetime: Optional[str]
    is_read: bool
    has_attachments: bool
    importance: str


@dataclass(frozen=True)
class DraftMessage:
    """Draft message structure"""
    id: Optional[str]
    subject: str
    to_recipients: List[EmailAddress]
    cc_recipients: List[EmailAddress]
    bcc_recipients: List[EmailAddress]
    body_content: str
    body_content_type: str


# Calculations (pure functions for data transformation)
def parse_email_address(data: dict) -> EmailAddress:
    """Parse email address from Graph API response - pure function"""
    email_data = data.get("emailAddress", {})
    return EmailAddress(
        address=email_data.get("address", ""),
        name=email_data.get("name")
    )


def parse_message_preview(data: dict) -> MessagePreview:
    """
    Parse message preview from Graph API response.
    
    Pure function - transforms data without side effects.
    """
    from_data = data.get("from", {})
    to_data = data.get("toRecipients", [])
    cc_data = data.get("ccRecipients", [])
    
    return MessagePreview(
        id=data.get("id", ""),
        subject=data.get("subject", ""),
        from_address=parse_email_address(from_data),
        to_recipients=[parse_email_address(r) for r in to_data],
        cc_recipients=[parse_email_address(r) for r in cc_data],
        body_preview=data.get("bodyPreview", "")[:200],  # First 200 chars
        received_datetime=data.get("receivedDateTime", ""),
        is_read=data.get("isRead", False),
        has_attachments=data.get("hasAttachments", False)
    )


def parse_message_full(data: dict) -> MessageFull:
    """Parse full message from Graph API response - pure function"""
    from_data = data.get("from", {})
    to_data = data.get("toRecipients", [])
    cc_data = data.get("ccRecipients", [])
    bcc_data = data.get("bccRecipients", [])
    body_data = data.get("body", {})
    
    return MessageFull(
        id=data.get("id", ""),
        subject=data.get("subject", ""),
        from_address=parse_email_address(from_data),
        to_recipients=[parse_email_address(r) for r in to_data],
        cc_recipients=[parse_email_address(r) for r in cc_data],
        bcc_recipients=[parse_email_address(r) for r in bcc_data],
        body_content=body_data.get("content", ""),
        body_content_type=body_data.get("contentType", "text"),
        received_datetime=data.get("receivedDateTime", ""),
        sent_datetime=data.get("sentDateTime"),
        is_read=data.get("isRead", False),
        has_attachments=data.get("hasAttachments", False),
        importance=data.get("importance", "normal")
    )


def create_draft_payload(draft: DraftMessage) -> dict:
    """
    Create Graph API payload from draft message.
    
    Pure function - data transformation only.
    """
    return {
        "subject": draft.subject,
        "toRecipients": [
            {"emailAddress": {"address": r.address, "name": r.name}}
            for r in draft.to_recipients
        ],
        "ccRecipients": [
            {"emailAddress": {"address": r.address, "name": r.name}}
            for r in draft.cc_recipients
        ],
        "bccRecipients": [
            {"emailAddress": {"address": r.address, "name": r.name}}
            for r in draft.bcc_recipients
        ],
        "body": {
            "contentType": draft.body_content_type,
            "content": draft.body_content
        }
    }


# Actions (side effects - API calls)
class GraphMailClient:
    """
    Microsoft Graph API client for mail operations.
    
    Deep module with shallow interface - hides complexity of API calls
    behind simple methods.
    """
    
    def __init__(self, graph_endpoint: str):
        """
        Initialize Graph API client.
        
        Args:
            graph_endpoint: Base URL for Graph API
        """
        self.graph_endpoint = graph_endpoint
        self.client = httpx.Client(timeout=30.0)
        
        logger.info(
            "Graph Mail Client initialized",
            extra={"endpoint": graph_endpoint}
        )
    
    def _make_request(
        self,
        method: str,
        path: str,
        access_token: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """
        Make HTTP request to Graph API.
        
        Internal action - handles all HTTP communication.
        """
        url = f"{self.graph_endpoint}{path}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(
            "Making Graph API request",
            extra={
                "method": method,
                "path": path,
                "has_data": data is not None
            }
        )
        
        try:
            response = self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            
            logger.info(
                "Graph API request successful",
                extra={
                    "status_code": response.status_code,
                    "path": path
                }
            )
            
            return response.json() if response.content else {}
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "Graph API request failed",
                extra={
                    "status_code": e.response.status_code,
                    "path": path,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in Graph API request",
                extra={"path": path, "error": str(e)},
                exc_info=True
            )
            raise
    
    def list_recent_messages(
        self,
        access_token: str,
        top: int = 25,
        filter_unread: bool = False
    ) -> List[MessagePreview]:
        """
        List recent messages with preview information.
        
        Action - fetches data from Graph API.
        
        Args:
            access_token: OAuth access token for Graph API
            top: Number of messages to retrieve (max 50 for performance)
            filter_unread: Only return unread messages
            
        Returns:
            List of message previews
        """
        logger.info(
            "Listing recent messages",
            extra={"top": top, "filter_unread": filter_unread}
        )
        
        params = {
            "$top": min(top, 50),  # Limit to 50 for performance
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,toRecipients,ccRecipients,bodyPreview,receivedDateTime,isRead,hasAttachments"
        }
        
        if filter_unread:
            params["$filter"] = "isRead eq false"
        
        response = self._make_request(
            method="GET",
            path="/me/messages",
            access_token=access_token,
            params=params
        )
        
        messages = response.get("value", [])
        logger.info(f"Retrieved {len(messages)} messages")
        
        # Transform data using pure functions
        return [parse_message_preview(msg) for msg in messages]
    
    def get_message(self, access_token: str, message_id: str) -> MessageFull:
        """
        Get full message details.
        
        Action - fetches data from Graph API.
        
        Args:
            access_token: OAuth access token for Graph API
            message_id: ID of the message to retrieve
            
        Returns:
            Full message details
        """
        logger.info(
            "Getting full message",
            extra={"message_id": message_id}
        )
        
        response = self._make_request(
            method="GET",
            path=f"/me/messages/{message_id}",
            access_token=access_token
        )
        
        logger.info("Message retrieved successfully")
        
        # Transform data using pure function
        return parse_message_full(response)
    
    def create_draft(
        self,
        access_token: str,
        draft: DraftMessage
    ) -> str:
        """
        Create a new draft message.
        
        Action - creates resource via Graph API.
        
        Args:
            access_token: OAuth access token for Graph API
            draft: Draft message to create
            
        Returns:
            ID of the created draft
        """
        logger.info(
            "Creating draft message",
            extra={"subject": draft.subject}
        )
        
        # Transform data using pure function
        payload = create_draft_payload(draft)
        
        response = self._make_request(
            method="POST",
            path="/me/messages",
            access_token=access_token,
            data=payload
        )
        
        draft_id = response.get("id", "")
        logger.info(
            "Draft created successfully",
            extra={"draft_id": draft_id}
        )
        
        return draft_id
    
    def update_draft(
        self,
        access_token: str,
        message_id: str,
        draft: DraftMessage
    ) -> None:
        """
        Update an existing draft message.
        
        Action - updates resource via Graph API.
        
        Args:
            access_token: OAuth access token for Graph API
            message_id: ID of the draft to update
            draft: Updated draft message data
        """
        logger.info(
            "Updating draft message",
            extra={"message_id": message_id, "subject": draft.subject}
        )
        
        # Transform data using pure function
        payload = create_draft_payload(draft)
        
        self._make_request(
            method="PATCH",
            path=f"/me/messages/{message_id}",
            access_token=access_token,
            data=payload
        )
        
        logger.info("Draft updated successfully")
    
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()
