"""
MCP Server implementation for Graph API mail operations

Implements MCP protocol tools for mail management with OBO authentication.
"""

import logging
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import Config
from .auth import OBOAuthenticator, extract_bearer_token, AuthenticationError
from .graph_client import GraphMailClient, DraftMessage, EmailAddress

logger = logging.getLogger(__name__)


# Tool definitions (data - immutable)
TOOLS: list[Tool] = [
    Tool(
        name="mail_list_recent",
        description=(
            "List recent emails in the user's inbox. "
            "Returns subject, sender, recipients, CC, and a preview of the body (first 200 characters). "
            "This helps identify emails that may require a personal response and are addressed directly to the user."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "top": {
                    "type": "integer",
                    "description": "Number of messages to retrieve (default: 25, max: 50)",
                    "default": 25,
                    "minimum": 1,
                    "maximum": 50
                },
                "unread_only": {
                    "type": "boolean",
                    "description": "Only return unread messages",
                    "default": False
                }
            }
        }
    ),
    Tool(
        name="mail_get_full",
        description=(
            "Get the complete details of a specific email message, including the full body content. "
            "Use this after identifying a message of interest from mail_list_recent."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "The ID of the message to retrieve"
                }
            },
            "required": ["message_id"]
        }
    ),
    Tool(
        name="mail_create_draft",
        description=(
            "Create a new email draft with rich formatting support. "
            "The draft is saved in the user's mailbox and can be edited or sent later.\n\n"
            "**HTML FORMATTING TIPS:**\n"
            "- Use body_type='html' for rich formatting (recommended for professional emails)\n"
            "- For HTML emails, use <br> for line breaks, NOT \\n\n"
            "- Common tags: <b>bold</b>, <i>italic</i>, <u>underline</u>\n"
            "- Lists: <ul><li>item</li></ul> (bullets) or <ol><li>item</li></ol> (numbered)\n"
            "- Links: <a href='url'>text</a>\n"
            "- Tables: <table><tr><td>cell</td></tr></table> (great for structured data)\n"
            "- Use inline CSS only: <span style='color: #0066cc;'>colored text</span>\n"
            "- Structure: <p>paragraph</p> for proper spacing\n\n"
            "**BEST PRACTICES:**\n"
            "- Start with greeting: <p>Dear [Name],</p>\n"
            "- Use paragraphs for readability\n"
            "- End with signature: <p>Best regards,<br>[Your Name]</p>\n"
            "- Keep HTML simple for best email client compatibility\n\n"
            "See EMAIL_FORMATTING_GUIDE.md for detailed examples and patterns."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Email subject line"
                },
                "to_recipients": {
                    "type": "array",
                    "description": "List of To recipients",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string", "description": "Email address"},
                            "name": {"type": "string", "description": "Display name (optional)"}
                        },
                        "required": ["address"]
                    }
                },
                "cc_recipients": {
                    "type": "array",
                    "description": "List of CC recipients (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "name": {"type": "string"}
                        },
                        "required": ["address"]
                    },
                    "default": []
                },
                "bcc_recipients": {
                    "type": "array",
                    "description": "List of BCC recipients (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "name": {"type": "string"}
                        },
                        "required": ["address"]
                    },
                    "default": []
                },
                "body": {
                    "type": "string",
                    "description": (
                        "Email body content. When body_type is 'html', use HTML tags for formatting. "
                        "Examples: <b>bold</b>, <br> for line breaks, <p>paragraph</p>, "
                        "<ul><li>bullet</li></ul>, <a href='url'>link</a>. "
                        "Use inline CSS for styling. See EMAIL_FORMATTING_GUIDE.md for examples."
                    )
                },
                "body_type": {
                    "type": "string",
                    "description": (
                        "Body content type: 'text' for plain text (use \\n for line breaks) or "
                        "'html' for rich formatting (use <br>, <p>, <b>, etc.). "
                        "HTML is recommended for professional emails. Default: 'text'"
                    ),
                    "enum": ["text", "html"],
                    "default": "text"
                }
            },
            "required": ["subject", "to_recipients", "body"]
        }
    ),
    Tool(
        name="mail_update_draft",
        description=(
            "Update an existing email draft with rich formatting support. "
            "You can modify any field including subject, recipients, and body content.\n\n"
            "**HTML FORMATTING TIPS:**\n"
            "- Use body_type='html' for rich formatting (recommended)\n"
            "- For HTML emails, use <br> for line breaks, NOT \\n\n"
            "- Common tags: <b>bold</b>, <i>italic</i>, <u>underline</u>\n"
            "- Lists: <ul><li>item</li></ul> or <ol><li>item</li></ol>\n"
            "- Links: <a href='url'>text</a>\n"
            "- Use inline CSS: <span style='color: blue;'>text</span>\n\n"
            "See EMAIL_FORMATTING_GUIDE.md for detailed examples."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "The ID of the draft message to update"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line"
                },
                "to_recipients": {
                    "type": "array",
                    "description": "List of To recipients",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "name": {"type": "string"}
                        },
                        "required": ["address"]
                    }
                },
                "cc_recipients": {
                    "type": "array",
                    "description": "List of CC recipients (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "name": {"type": "string"}
                        },
                        "required": ["address"]
                    },
                    "default": []
                },
                "bcc_recipients": {
                    "type": "array",
                    "description": "List of BCC recipients (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "string"},
                            "name": {"type": "string"}
                        },
                        "required": ["address"]
                    },
                    "default": []
                },
                "body": {
                    "type": "string",
                    "description": (
                        "Email body content. When body_type is 'html', use HTML tags for formatting. "
                        "Examples: <b>bold</b>, <br> for line breaks, <p>paragraph</p>, "
                        "<ul><li>bullet</li></ul>, <a href='url'>link</a>. "
                        "Use inline CSS for styling. See EMAIL_FORMATTING_GUIDE.md for examples."
                    )
                },
                "body_type": {
                    "type": "string",
                    "description": (
                        "Body content type: 'text' for plain text (use \\n for line breaks) or "
                        "'html' for rich formatting (use <br>, <p>, <b>, etc.). "
                        "HTML is recommended for professional emails. Default: 'text'"
                    ),
                    "enum": ["text", "html"],
                    "default": "text"
                }
            },
            "required": ["message_id", "subject", "to_recipients", "body"]
        }
    )
]


# Calculations (pure functions)
def parse_recipients(recipients_data: list[dict]) -> list[EmailAddress]:
    """Parse recipients from tool input - pure function"""
    return [
        EmailAddress(
            address=r["address"],
            name=r.get("name")
        )
        for r in recipients_data
    ]


def format_message_preview(msg) -> str:
    """Format message preview for display - pure function"""
    to_list = ", ".join([r.address for r in msg.to_recipients])
    cc_list = ", ".join([r.address for r in msg.cc_recipients]) if msg.cc_recipients else "None"
    
    return f"""Message ID: {msg.id}
Subject: {msg.subject}
From: {msg.from_address.name or msg.from_address.address} <{msg.from_address.address}>
To: {to_list}
CC: {cc_list}
Received: {msg.received_datetime}
Read: {msg.is_read}
Has Attachments: {msg.has_attachments}

Body Preview:
{msg.body_preview}
---
"""


def format_message_full(msg) -> str:
    """Format full message for display - pure function"""
    to_list = ", ".join([r.address for r in msg.to_recipients])
    cc_list = ", ".join([r.address for r in msg.cc_recipients]) if msg.cc_recipients else "None"
    bcc_list = ", ".join([r.address for r in msg.bcc_recipients]) if msg.bcc_recipients else "None"
    
    return f"""Message ID: {msg.id}
Subject: {msg.subject}
From: {msg.from_address.name or msg.from_address.address} <{msg.from_address.address}>
To: {to_list}
CC: {cc_list}
BCC: {bcc_list}
Received: {msg.received_datetime}
Sent: {msg.sent_datetime or 'N/A'}
Read: {msg.is_read}
Has Attachments: {msg.has_attachments}
Importance: {msg.importance}

Body ({msg.body_content_type}):
{msg.body_content}
"""


class GraphMailMCPServer:
    """
    MCP Server for Graph API mail operations.
    
    Handles tool execution with proper OBO authentication.
    """
    
    def __init__(self, config: Config):
        """Initialize the MCP server"""
        self.config = config
        self.server = Server("graph-mail-mcp")
        
        # Initialize clients (actions)
        # Note: In production, use federated identity credential instead of client secret
        client_secret = os.getenv("AZURE_AD_CLIENT_SECRET", "")
        if not client_secret:
            logger.warning("AZURE_AD_CLIENT_SECRET not set - authentication may fail")
        
        self.authenticator = OBOAuthenticator(
            client_id=config.AZURE_AD_CLIENT_ID,
            authority=config.AZURE_AD_AUTHORITY,
            client_credential=client_secret
        )
        
        self.graph_client = GraphMailClient(
            graph_endpoint=config.GRAPH_API_ENDPOINT
        )
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Graph Mail MCP Server initialized")
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            logger.info("Listing tools")
            return TOOLS
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict, meta: dict) -> Sequence[TextContent]:
            """Execute a tool"""
            logger.info(
                "Tool called",
                extra={
                    "tool": name,
                    "has_meta": bool(meta)
                }
            )
            
            try:
                # Extract user token from meta (OBO flow)
                auth_header = meta.get("authorization")
                user_token = extract_bearer_token(auth_header)
                
                # Acquire Graph token via OBO
                graph_token = self.authenticator.acquire_token_on_behalf_of(
                    user_token=user_token,
                    scopes=self.config.GRAPH_API_SCOPES
                )
                
                # Execute tool
                if name == "mail_list_recent":
                    return await self._handle_list_recent(graph_token, arguments)
                elif name == "mail_get_full":
                    return await self._handle_get_full(graph_token, arguments)
                elif name == "mail_create_draft":
                    return await self._handle_create_draft(graph_token, arguments)
                elif name == "mail_update_draft":
                    return await self._handle_update_draft(graph_token, arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                return [TextContent(type="text", text=f"Authentication failed: {str(e)}")]
            except Exception as e:
                logger.error(f"Tool execution error: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_list_recent(self, graph_token: str, args: dict) -> Sequence[TextContent]:
        """Handle mail_list_recent tool"""
        top = args.get("top", 25)
        unread_only = args.get("unread_only", False)
        
        logger.info(f"Listing recent messages: top={top}, unread_only={unread_only}")
        
        messages = self.graph_client.list_recent_messages(
            access_token=graph_token,
            top=top,
            filter_unread=unread_only
        )
        
        if not messages:
            return [TextContent(type="text", text="No messages found.")]
        
        # Format messages using pure function
        formatted = "\n".join([format_message_preview(msg) for msg in messages])
        result = f"Found {len(messages)} message(s):\n\n{formatted}"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_get_full(self, graph_token: str, args: dict) -> Sequence[TextContent]:
        """Handle mail_get_full tool"""
        message_id = args["message_id"]
        
        logger.info(f"Getting full message: {message_id}")
        
        message = self.graph_client.get_message(
            access_token=graph_token,
            message_id=message_id
        )
        
        # Format message using pure function
        formatted = format_message_full(message)
        
        return [TextContent(type="text", text=formatted)]
    
    async def _handle_create_draft(self, graph_token: str, args: dict) -> Sequence[TextContent]:
        """Handle mail_create_draft tool"""
        logger.info(f"Creating draft: {args.get('subject')}")
        
        # Parse recipients using pure function
        to_recipients = parse_recipients(args["to_recipients"])
        cc_recipients = parse_recipients(args.get("cc_recipients", []))
        bcc_recipients = parse_recipients(args.get("bcc_recipients", []))
        
        draft = DraftMessage(
            id=None,
            subject=args["subject"],
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            body_content=args["body"],
            body_content_type=args.get("body_type", "text")
        )
        
        draft_id = self.graph_client.create_draft(
            access_token=graph_token,
            draft=draft
        )
        
        result = f"Draft created successfully.\nDraft ID: {draft_id}"
        return [TextContent(type="text", text=result)]
    
    async def _handle_update_draft(self, graph_token: str, args: dict) -> Sequence[TextContent]:
        """Handle mail_update_draft tool"""
        message_id = args["message_id"]
        logger.info(f"Updating draft: {message_id}")
        
        # Parse recipients using pure function
        to_recipients = parse_recipients(args["to_recipients"])
        cc_recipients = parse_recipients(args.get("cc_recipients", []))
        bcc_recipients = parse_recipients(args.get("bcc_recipients", []))
        
        draft = DraftMessage(
            id=message_id,
            subject=args["subject"],
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            body_content=args["body"],
            body_content_type=args.get("body_type", "text")
        )
        
        self.graph_client.update_draft(
            access_token=graph_token,
            message_id=message_id,
            draft=draft
        )
        
        result = f"Draft updated successfully.\nDraft ID: {message_id}"
        return [TextContent(type="text", text=result)]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Graph Mail MCP Server")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# Entry point
import os


async def main():
    """Main entry point"""
    # Load configuration
    config = Config.from_env()
    
    # Create and run server
    server = GraphMailMCPServer(config)
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
