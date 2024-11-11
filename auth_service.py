# auth_service.py
from typing import Optional
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel
from datetime import datetime
from config import API_CLIENT_ID, API_KEY

class APIKey(BaseModel):
    key: str
    client_id: str
    created_at: datetime
    is_active: bool = True

class AuthService:
    def __init__(self):
        # Initialize with static API key from config
        self._api_key = APIKey(
            key=API_KEY,
            client_id=API_CLIENT_ID,
            created_at=datetime.utcnow(),
            is_active=True
        )
    
    def validate_credentials(self, key: str, client_id: str) -> Optional[APIKey]:
        """Validate both the API key and client ID."""
        if (key == self._api_key.key and 
            client_id == self._api_key.client_id and 
            self._api_key.is_active):
            return self._api_key
        return None

# FastAPI security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
client_id_header = APIKeyHeader(name="X-Client-ID", auto_error=False)

# Create global auth service instance
auth_service = AuthService()

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    client_id_header: str = Security(client_id_header)
) -> APIKey:
    """Dependency for validating API keys and client IDs in FastAPI routes."""
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="No API key provided"
        )
    
    if not client_id_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="No client ID provided"
        )
    
    api_key = auth_service.validate_credentials(api_key_header, client_id_header)
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Invalid credentials"
        )
    
    return api_key