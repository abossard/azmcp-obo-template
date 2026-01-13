# Graph API Mail MCP Server

A Model Context Protocol (MCP) server that provides Microsoft Graph API mail operations with On-Behalf-Of (OBO) authentication flow.

## Features

This MCP server provides the following tools for email management:

### 1. `mail_list_recent`
List recent emails in the user's inbox with preview information:
- Subject
- Sender (From)
- Recipients (To)
- CC recipients
- Body preview (first 200 characters)
- Received date/time
- Read status
- Attachment indicator

This tool is designed to help identify emails that may require a personal response and are addressed directly to the user.

**Parameters:**
- `top` (optional): Number of messages to retrieve (default: 25, max: 50)
- `unread_only` (optional): Only return unread messages (default: false)

### 2. `mail_get_full`
Get the complete details of a specific email message, including the full body content.

**Parameters:**
- `message_id` (required): The ID of the message to retrieve

### 3. `mail_create_draft`
Create a new email draft in the user's mailbox.

**Parameters:**
- `subject` (required): Email subject line
- `to_recipients` (required): Array of recipient objects with `address` and optional `name`
- `cc_recipients` (optional): Array of CC recipient objects
- `bcc_recipients` (optional): Array of BCC recipient objects
- `body` (required): Email body content
- `body_type` (optional): Content type - "text" or "html" (default: "text")

### 4. `mail_update_draft`
Update an existing email draft.

**Parameters:**
- `message_id` (required): The ID of the draft to update
- `subject` (required): Updated subject line
- `to_recipients` (required): Updated To recipients
- `cc_recipients` (optional): Updated CC recipients
- `bcc_recipients` (optional): Updated BCC recipients
- `body` (required): Updated body content
- `body_type` (optional): Content type - "text" or "html"

## Design Principles

This server follows two key software design philosophies:

### Grokking Simplicity
- **Actions, Calculations, and Data**: Code is organized into pure functions (calculations), side effects (actions), and data structures
- **Immutability**: Data structures are immutable using Python's `@dataclass(frozen=True)`
- **Separation of Concerns**: Authentication, API calls, and data transformation are cleanly separated

### A Philosophy of Software Design
- **Deep modules with shallow interfaces**: Complex functionality is hidden behind simple, clear APIs
- **Information hiding**: Internal implementation details are encapsulated
- **Minimize complexity**: Code is structured to reduce cognitive load

## Architecture

```
graph-mcp-server/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration (data)
│   ├── auth.py              # OBO authentication (actions + calculations)
│   ├── graph_client.py      # Graph API client (data models + actions)
│   └── server.py            # MCP server implementation
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
└── .env.example            # Environment configuration template
```

## Authentication Flow

This server uses the On-Behalf-Of (OBO) flow:

1. Client authenticates user and obtains access token for the MCP server
2. Client calls MCP tool with user's access token in metadata
3. MCP server extracts user token and exchanges it for a Graph API token
4. MCP server calls Graph API on behalf of the user
5. Results are returned to the client

## Required Permissions

The server app registration needs the following delegated Microsoft Graph API permissions:

- `Mail.Read` - Read user mail
- `Mail.ReadWrite` - Read and write user mail (for drafts)

Admin consent is required for these permissions.

## Logging

The server implements comprehensive logging at multiple levels:

- **INFO**: Normal operations (tool calls, API requests, successful operations)
- **WARNING**: Potential issues (missing configuration)
- **ERROR**: Failures (authentication errors, API errors)

All log messages include structured context using the `extra` parameter for better observability.

## Environment Variables

See `.env.example` for required configuration:

- `AZURE_AD_TENANT_ID`: Your Azure AD tenant ID
- `AZURE_AD_CLIENT_ID`: The server app registration client ID
- `AZURE_AD_INSTANCE`: Azure AD authority URL
- `AZURE_AD_CLIENT_SECRET`: Client secret (for local testing only)
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Optional Application Insights connection

**Production Note**: Use Federated Identity Credential instead of client secrets for production deployments.

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Run the server:
```bash
python -m src.server
```

## Docker Deployment

Build the container:
```bash
docker build -t graph-mail-mcp-server .
```

Run the container:
```bash
docker run -p 8080:8080 \
  -e AZURE_AD_TENANT_ID=your-tenant-id \
  -e AZURE_AD_CLIENT_ID=your-client-id \
  -e AZURE_AD_INSTANCE=https://login.microsoftonline.com/your-tenant-id \
  graph-mail-mcp-server
```

## Integration with Azure Container Apps

This server can be deployed alongside the existing Azure MCP Server as an alternative endpoint. See the main repository documentation for infrastructure deployment instructions.

## Security Considerations

1. **Never commit secrets** to version control
2. **Use Federated Identity Credentials** in production instead of client secrets
3. **Validate all inputs** before processing
4. **Log security events** appropriately without exposing sensitive data
5. **Apply principle of least privilege** for API permissions

## Testing

The server can be tested using:
- MCP Inspector (for development)
- Custom MCP clients (see `/client` directory in main repository)
- Copilot Studio agents with custom connectors
- Microsoft Foundry agents

## License

See LICENSE.md in the main repository.
