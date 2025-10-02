"""
Authentication Middleware for API Key validation
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from services.database import APIKey, get_db


security = HTTPBearer(auto_error=False)


async def verify_api_key(request: Request) -> str:
    """
    Verify API key from X-API-Key header
    
    Returns:
        app_name if valid
    
    Raises:
        HTTPException: If API key is invalid
    """
    # Get API key from header
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header."
        )
    
    # Validate API key
    db: Session = next(get_db())
    try:
        api_key_obj = db.query(APIKey).filter(
            APIKey.api_key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not api_key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check expiration
        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )
        
        # Update last used timestamp
        api_key_obj.last_used_at = datetime.utcnow()
        db.commit()
        
        return api_key_obj.app_name
        
    finally:
        db.close()


async def get_current_app_name(request: Request) -> str:
    """Dependency to get current app name from API key"""
    return await verify_api_key(request)

