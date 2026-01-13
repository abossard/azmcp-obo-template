#!/bin/bash
# Validation script for the Graph MCP Server deployment

set -e

echo "=== Validating Graph MCP Server ==="
echo ""

# Validate Python server
echo "1. Validating Python server..."
cd graph-mcp-server
python validate_server.py
echo ""

# Validate Bicep modules
echo "2. Validating Bicep modules..."
cd ../infra

echo "   Validating aca-graph-mcp.bicep..."
az bicep build --file modules/aca-graph-mcp.bicep
echo "   ✓ aca-graph-mcp.bicep is valid"

echo "   Validating aca-infrastructure.bicep..."
az bicep build --file modules/aca-infrastructure.bicep
echo "   ✓ aca-infrastructure.bicep is valid"

echo ""
echo "Note: main.bicep validation may fail in offline environments due to"
echo "Microsoft Graph extension dependency in entra-app.bicep. This is"
echo "expected and does not affect deployment when network is available."
echo ""

echo "=== Validation Complete ==="
