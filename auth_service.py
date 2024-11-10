from typing import Optional
import secrets
import hmac
from datetime import datetime, timedelta
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel

class APIKey(BaseModel):
    key: str
    client_id: str
    created_at: datetime
    is_active: bool = True

class AuthService:
    def __init__(self):
        # In-memory storage for API keys. In production, use a database
        self._api_keys: dict[str, APIKey] = {}
        
    def create_api_key(self, client_id: str) -> APIKey:
        """Create a new API key for a client."""
        key = secrets.token_urlsafe(32)
        api_key = APIKey(
            key=key,
            client_id=client_id,
            created_at=datetime.utcnow()
        )
        self._api_keys[key] = api_key
        return api_key
    
    def validate_api_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key and return the associated API key object."""
        api_key = self._api_keys.get(key)
        if api_key and api_key.is_active:
            return api_key
        return None
    
    def deactivate_api_key(self, key: str) -> bool:
        """Deactivate an API key."""
        if key in self._api_keys:
            self._api_keys[key].is_active = False
            return True
        return False
    
    def list_api_keys(self, client_id: Optional[str] = None) -> list[APIKey]:
        """List all API keys or filter by client_id."""
        if client_id:
            return [k for k in self._api_keys.values() if k.client_id == client_id]
        return list(self._api_keys.values())

# FastAPI security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Create global auth service instance
auth_service = AuthService()

async def get_api_key(api_key_header: str = Security(api_key_header)) -> APIKey:
    """Dependency for validating API keys in FastAPI routes."""
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="No API key provided"
        )
    
    api_key = auth_service.validate_api_key(api_key_header)
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Invalid or inactive API key"
        )
    
    return api_key