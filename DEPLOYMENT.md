# Deploying the Graph Mail MCP Server

This guide explains how to deploy the Graph Mail MCP Server alongside the Azure MCP Server.

## Prerequisites

- All prerequisites from the main [README.md](./README.md)
- Docker (for building the custom container image)
- Azure Container Registry (ACR) or access to push to Microsoft Container Registry

## Deployment Steps

### Option 1: Using Azure Container Registry (Recommended)

#### 1. Build and Push Container Image

First, build and push the Graph MCP Server container image to your Azure Container Registry:

```bash
# Set your ACR name
ACR_NAME="your-acr-name"

# Login to ACR
az acr login --name $ACR_NAME

# Build and push the image
cd graph-mcp-server
docker build -t ${ACR_NAME}.azurecr.io/graph-mail-mcp-server:latest .
docker push ${ACR_NAME}.azurecr.io/graph-mail-mcp-server:latest
```

#### 2. Deploy with azd

Update the deployment to enable the Graph MCP Server and specify your container registry:

```bash
# Set environment variables for deployment
azd env set DEPLOY_GRAPH_MCP_SERVER true
azd env set CONTAINER_REGISTRY "${ACR_NAME}.azurecr.io"
azd env set CONTAINER_IMAGE "graph-mail-mcp-server:latest"

# Deploy
azd up
```

Or use parameters directly:

```bash
azd up --parameter deployGraphMcpServer=true \
       --parameter containerRegistry="${ACR_NAME}.azurecr.io" \
       --parameter containerImage="graph-mail-mcp-server:latest"
```

#### 3. Configure Graph API Permissions

After deployment, add Microsoft Graph API permissions to the server app registration:

```bash
# Get the server app registration ID
SERVER_APP_ID=$(azd env get-values | grep ENTRA_APP_SERVER_CLIENT_ID | cut -d'=' -f2)

# Microsoft Graph API ID
GRAPH_API_ID="00000003-0000-0000-c000-000000000000"

# Mail.Read permission ID
MAIL_READ_ID="810c84a8-4a9e-49e6-bf7d-12d183f40d01"

# Mail.ReadWrite permission ID
MAIL_READWRITE_ID="e2a3a72e-5f79-4c64-b1b1-878b674786c9"

# Add permissions
az ad app permission add --id $SERVER_APP_ID --api $GRAPH_API_ID --api-permissions ${MAIL_READ_ID}=Scope
az ad app permission add --id $SERVER_APP_ID --api $GRAPH_API_ID --api-permissions ${MAIL_READWRITE_ID}=Scope

# Grant admin consent
az ad app permission admin-consent --id $SERVER_APP_ID
```

See [EntraIdConfig.md](./EntraIdConfig.md) for more details on API permissions.

#### 4. Get the Graph MCP Server URL

```bash
azd env get-values | grep GRAPH_MCP_CONTAINER_APP_URL
```

### Option 2: Manual Bicep Deployment

If you prefer to deploy using Bicep directly without azd:

```bash
# Create a resource group
az group create --name myResourceGroup --location eastus

# Deploy with Graph MCP Server enabled
az deployment group create \
  --resource-group myResourceGroup \
  --template-file infra/main.bicep \
  --parameters deployGraphMcpServer=true \
               containerRegistry="${ACR_NAME}.azurecr.io" \
               containerImage="graph-mail-mcp-server:latest" \
               acaName="my-mcp-server" \
               entraAppServerDisplayName="My MCP Server" \
               entraAppClientDisplayName="My MCP Client"
```

## Validation

Run the validation script to ensure all code is valid:

```bash
./validate.sh
```

This validates:
- Python syntax for all source files
- Bicep modules (aca-graph-mcp.bicep, aca-infrastructure.bicep)

## Testing the Graph MCP Server

Once deployed, you can test the Graph MCP Server using:

### 1. MCP Inspector (Development)

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run against the deployed server
mcp-inspector https://your-graph-mcp-url
```

### 2. Custom MCP Client

See the [client/README.md](./client/README.md) for using the C# MCP client.

### 3. Copilot Studio or Foundry Agents

Follow the instructions in [Usage.md](./Usage.md) to connect from Copilot Studio or Foundry, but use the Graph MCP Server URL instead of the Azure MCP Server URL.

## Architecture

When deployed, you will have two Container Apps:

1. **Azure MCP Server** (`CONTAINER_APP_URL`)
   - Provides Azure Storage tools
   - Read-only by default

2. **Graph Mail MCP Server** (`GRAPH_MCP_CONTAINER_APP_URL`)
   - Provides Microsoft Graph mail tools
   - List emails, get full messages, create/update drafts

Both servers:
- Share the same Container Apps Environment
- Use the same Entra app registration (server)
- Use the same user-assigned managed identity for authentication
- Share Application Insights for telemetry

## Security Notes

1. **Never commit container registry credentials** to source control
2. **Use managed identities** for ACR pull access when possible
3. **Review API permissions** carefully - only grant what's needed
4. **Enable Application Insights** for monitoring and security auditing
5. **Regularly update** container images with security patches

## Troubleshooting

### Container fails to start

Check Container App logs:
```bash
az containerapp logs show \
  --name $(azd env get-values | grep GRAPH_MCP_CONTAINER_APP_NAME | cut -d'=' -f2) \
  --resource-group $(azd env get-values | grep AZURE_RESOURCE_GROUP | cut -d'=' -f2)
```

### Authentication errors

Verify the app registration has the required permissions and admin consent has been granted:
```bash
az ad app permission list --id $SERVER_APP_ID
```

### Cannot pull container image

Ensure the Container App has pull access to your ACR:
```bash
# Grant AcrPull role to the managed identity
az role assignment create \
  --assignee $(azd env get-values | grep CONTAINER_APP_MANAGED_IDENTITY_CLIENT_ID | cut -d'=' -f2) \
  --role AcrPull \
  --scope /subscriptions/{subscription-id}/resourceGroups/{acr-resource-group}/providers/Microsoft.ContainerRegistry/registries/${ACR_NAME}
```

## Clean Up

To remove the Graph MCP Server but keep the Azure MCP Server:

```bash
azd env set DEPLOY_GRAPH_MCP_SERVER false
azd up
```

To remove all resources:

```bash
azd down
```

Note: You'll need to manually delete the Entra app registrations from Azure Portal.

## Next Steps

- [Configure custom connector](./Usage.md#calling-tools-from-copilot-studio-agent) for Copilot Studio
- [Review Graph MCP Server documentation](./graph-mcp-server/README.md)
- [Understand OBO flow](./EntraIdConfig.md)
