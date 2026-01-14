#!/bin/bash
# Test runner script for Graph MCP Server
# Can use either uv (recommended) or pip

set -e

echo "=== Graph MCP Server - Test Runner ==="
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    
    # Run end-to-end tests
    echo "Running end-to-end blackbox tests..."
    uv run python test_e2e.py
    
    echo ""
    echo "Running unit tests..."
    uv run python test_server.py
else
    echo "uv not found, using pip..."
    echo "Note: Install uv for faster package management: https://github.com/astral-sh/uv"
    echo ""
    
    # Check if dependencies are installed
    python -c "import mcp" 2>/dev/null || {
        echo "Dependencies not installed. Installing..."
        pip install -r requirements.txt
    }
    
    # Run end-to-end tests
    echo "Running end-to-end blackbox tests..."
    python test_e2e.py
    
    echo ""
    echo "Running unit tests..."
    python test_server.py
fi

echo ""
echo "=== All tests passed! ==="
