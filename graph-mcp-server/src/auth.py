"""
Authentication module for OBO flow

Separates authentication concerns following design principles:
- Actions: Token acquisition (interacts with external auth service)
- Calculations: Token validation and extraction (pure functions)
"""

import logging
from typing import Optional
from msal import ConfidentialClientApplication, SerializableTokenCache

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


# Calculations (pure functions)
def extract_bearer_token(authorization_header: Optional[str]) -> str:
    """
    Extract bearer token from Authorization header.
    
    Pure function - no side effects, always same output for same input.
    
    Args:
        authorization_header: The Authorization header value
        
    Returns:
        The bearer token string
        
    Raises:
        AuthenticationError: If header is missing or malformed
    """
    if not authorization_header:
        logger.warning("Missing Authorization header")
        raise AuthenticationError("Missing Authorization header")
    
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(
            "Malformed Authorization header",
            extra={"header_parts": len(parts)}
        )
        raise AuthenticationError("Malformed Authorization header")
    
    return parts[1]


def validate_token_response(token_response: dict) -> dict:
    """
    Validate token response from MSAL.
    
    Pure function - validates data structure.
    
    Args:
        token_response: Response from MSAL token acquisition
        
    Returns:
        The validated token response
        
    Raises:
        AuthenticationError: If token response is invalid
    """
    if "access_token" not in token_response:
        error = token_response.get("error", "unknown")
        error_description = token_response.get("error_description", "No description")
        logger.error(
            "Token acquisition failed",
            extra={
                "error": error,
                "error_description": error_description
            }
        )
        raise AuthenticationError(f"Token acquisition failed: {error} - {error_description}")
    
    logger.info("Token validated successfully")
    return token_response


# Actions (side effects - interacts with external services)
class OBOAuthenticator:
    """
    Handles On-Behalf-Of authentication flow.
    
    Deep module - complex authentication logic behind simple interface.
    """
    
    def __init__(self, client_id: str, authority: str, client_credential: str):
        """
        Initialize the authenticator.
        
        Args:
            client_id: Azure AD client ID
            authority: Azure AD authority URL
            client_credential: Client secret or certificate
        """
        self.client_id = client_id
        self.authority = authority
        self.client_credential = client_credential
        
        # Initialize MSAL app
        self.app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_credential,
            authority=authority
        )
        
        logger.info(
            "OBO Authenticator initialized",
            extra={
                "client_id": client_id,
                "authority": authority
            }
        )
    
    def acquire_token_on_behalf_of(self, user_token: str, scopes: list[str]) -> str:
        """
        Acquire token on behalf of user using OBO flow.
        
        Action - performs I/O with external auth service.
        
        Args:
            user_token: The user's access token
            scopes: Requested scopes for the new token
            
        Returns:
            Access token for Microsoft Graph
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        logger.info(
            "Acquiring token via OBO flow",
            extra={"scopes": scopes}
        )
        
        try:
            # Perform OBO token exchange
            result = self.app.acquire_token_on_behalf_of(
                user_assertion=user_token,
                scopes=scopes
            )
            
            # Validate response (calculation)
            validated_result = validate_token_response(result)
            
            logger.info("Token acquired successfully via OBO flow")
            return validated_result["access_token"]
            
        except Exception as e:
            logger.error(
                "OBO token acquisition failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise AuthenticationError(f"OBO flow failed: {str(e)}")
