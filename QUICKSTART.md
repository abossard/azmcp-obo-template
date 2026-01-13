# Quick Start Guide - Graph Mail MCP Server

## Overview

This repository now includes a **Graph Mail MCP Server** for Microsoft Graph API mail operations alongside the Azure MCP Server.

## What's New

### Graph Mail MCP Server
A custom MCP server providing email management tools:
- 📧 **List Recent Emails** - Preview inbox with subject, recipients, CC, and body preview
- 📄 **Get Full Email** - Retrieve complete email content
- ✏️ **Create Draft** - Compose new email drafts
- 🔄 **Update Draft** - Edit existing drafts

### Key Features
- ✅ On-Behalf-Of (OBO) authentication flow
- ✅ Deploys alongside Azure MCP Server (shared infrastructure)
- ✅ Follows Grokking Simplicity design principles
- ✅ Follows A Philosophy of Software Design principles
- ✅ Comprehensive logging throughout

## Quick Deploy

### Prerequisites
- Azure subscription with Owner permissions
- Azure CLI and Azure Developer CLI (azd)
- Docker (for building the container image)
- Azure Container Registry

### Steps

1. **Build and push the container image:**
   ```bash
   ACR_NAME="your-acr-name"
   az acr login --name $ACR_NAME
   
   cd graph-mcp-server
   docker build -t ${ACR_NAME}.azurecr.io/graph-mail-mcp-server:latest .
   docker push ${ACR_NAME}.azurecr.io/graph-mail-mcp-server:latest
   ```

2. **Deploy with azd:**
   ```bash
   cd ..
   azd up --parameter deployGraphMcpServer=true \
          --parameter graphMcpContainerRegistry="${ACR_NAME}.azurecr.io" \
          --parameter graphMcpContainerImage="graph-mail-mcp-server:latest"
   ```

3. **Configure Graph API permissions:**
   ```bash
   SERVER_APP_ID=$(azd env get-values | grep ENTRA_APP_SERVER_CLIENT_ID | cut -d'=' -f2)
   
   # Add Mail.Read and Mail.ReadWrite permissions
   az ad app permission add --id $SERVER_APP_ID \
     --api 00000003-0000-0000-c000-000000000000 \
     --api-permissions 810c84a8-4a9e-49e6-bf7d-12d183f40d01=Scope
   
   az ad app permission add --id $SERVER_APP_ID \
     --api 00000003-0000-0000-c000-000000000000 \
     --api-permissions e2a3a72e-5f79-4c64-b1b1-878b674786c9=Scope
   
   # Grant admin consent
   az ad app permission admin-consent --id $SERVER_APP_ID
   ```

4. **Get your server URLs:**
   ```bash
   azd env get-values | grep CONTAINER_APP_URL
   ```

## Validation

Run comprehensive validation before deploying:

```bash
./validate.sh
```

This validates:
- ✓ Python syntax for all files
- ✓ Design principles adherence
- ✓ Bicep module compilation
- ✓ Required files and dependencies

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment instructions
- **[graph-mcp-server/README.md](graph-mcp-server/README.md)** - Server documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical overview
- **[EntraIdConfig.md](EntraIdConfig.md)** - API permissions configuration
- **[Usage.md](Usage.md)** - How to use the MCP servers

## Architecture

```
┌─────────────────────────────────────────────────┐
│     Container Apps Environment                   │
│                                                  │
│  ┌──────────────────┐  ┌───────────────────┐   │
│  │ Azure MCP Server │  │ Graph Mail MCP     │   │
│  │ (Storage Tools)  │  │ (Mail Tools)       │   │
│  └──────────────────┘  └───────────────────┘   │
│                                                  │
│         Shared Managed Identity                 │
│         Shared App Insights                     │
└─────────────────────────────────────────────────┘
```

## Files Created

### Python MCP Server
- `graph-mcp-server/src/` - Server implementation (6 files)
- `graph-mcp-server/Dockerfile` - Container definition
- `graph-mcp-server/requirements.txt` - Dependencies
- `graph-mcp-server/validate_server.py` - Validation tests

### Infrastructure
- `infra/modules/aca-graph-mcp.bicep` - Container App deployment

### Documentation
- `DEPLOYMENT.md` - Deployment guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `validate.sh` - Validation script

## Support

For issues or questions:
1. Check [Troubleshooting.md](Troubleshooting.md)
2. Review [KnownIssues.md](KnownIssues.md)
3. Open an issue in the repository

## Next Steps

1. **Test locally** - Use MCP Inspector to test tools
2. **Deploy to Azure** - Follow deployment guide
3. **Connect clients** - Use with Copilot Studio or Foundry
4. **Monitor** - Check Application Insights for telemetry

---

See individual documentation files for detailed information.
