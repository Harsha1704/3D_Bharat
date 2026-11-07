import logging
from typing import Optional
from fastapi import Header, HTTPException, status

from app.core.config import settings

logger = logging.getLogger("3d_bharat.security")


def verify_write_access(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> bool:
    """
    Access control dependency for write, upload, update, and delete endpoints.
    
    Security rules:
    1. In production (ENVIRONMENT == 'production'):
       - If PRESERVATION_WRITE_API_KEY is not configured: write operations are locked (503 Service Unavailable).
       - If configured: requests must provide matching X-API-Key or Bearer token (401 Unauthorized on mismatch).
    2. In development/staging:
       - If PRESERVATION_WRITE_API_KEY is configured: enforces matching key.
       - If not configured: allows local write access with a security audit warning.
    """
    expected_key = settings.PRESERVATION_WRITE_API_KEY

    # Check Bearer token if provided
    provided_key = x_api_key
    if not provided_key and authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided_key = parts[1]

    # Production gate
    if settings.ENVIRONMENT.lower() == "production":
        if not expected_key:
            logger.error("Production deployment blocker: PRESERVATION_WRITE_API_KEY is not configured. Write endpoints are disabled.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Preservation write endpoints are disabled in production until PRESERVATION_WRITE_API_KEY is configured.",
            )
        if not provided_key or provided_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key for preservation write operations.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return True

    # Development / Staging gate
    if expected_key:
        if not provided_key or provided_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key for preservation write operations.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return True

    # Development mode without key: allowed with warning log
    logger.debug("Development mode: write operation executed without authentication key.")
    return True
