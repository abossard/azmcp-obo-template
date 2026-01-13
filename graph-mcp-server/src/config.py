"""
Graph API Mail MCP Server

This module implements an MCP server for Microsoft Graph API mail operations
using On-Behalf-Of (OBO) authentication flow.

Design Philosophy:
- Grokking Simplicity: Separating Actions, Calculations, and Data
- A Philosophy of Software Design: Deep modules with shallow interfaces
"""

import os
import logging
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration data (immutable)
class Config:
    """Configuration data - pure data, no behavior"""
    AZURE_AD_TENANT_ID: str
    AZURE_AD_CLIENT_ID: str
    AZURE_AD_AUTHORITY: str
    GRAPH_API_ENDPOINT: str = "https://graph.microsoft.com/v1.0"
    GRAPH_API_SCOPES: list[str] = ["https://graph.microsoft.com/.default"]
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment - Calculation (pure function)"""
        config = cls()
        config.AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID", "")
        config.AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID", "")
        config.AZURE_AD_AUTHORITY = os.getenv(
            "AZURE_AD_INSTANCE",
            f"https://login.microsoftonline.com/{config.AZURE_AD_TENANT_ID}"
        )
        
        logger.info(
            "Configuration loaded",
            extra={
                "tenant_id": config.AZURE_AD_TENANT_ID,
                "client_id": config.AZURE_AD_CLIENT_ID,
                "authority": config.AZURE_AD_AUTHORITY
            }
        )
        return config
