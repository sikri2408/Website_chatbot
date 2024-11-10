from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from rag_service import RAGService
from config import PERSIST_DIRECTORY, port_no, host_name
from auth_service import auth_service, get_api_key, APIKey
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime

app = FastAPI()
rag_service = RAGService(PERSIST_DIRECTORY)

# Existing model definitions...
class URLInput(BaseModel):
    url: HttpUrl
    force_update: bool = False

class URLResponse(BaseModel):
    status: str
    message: str
    was_indexed: bool

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    query: str
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None

class CreateAPIKeyRequest(BaseModel):
    client_id: str

class CreateAPIKeyResponse(BaseModel):
    key: str
    client_id: str
    created_at: datetime

@app.post("/api/v1/auth/keys", response_model=CreateAPIKeyResponse)
async def create_api_key(request: CreateAPIKeyRequest):
    """Create a new API key for a client."""
    api_key = auth_service.create_api_key(request.client_id)
    return api_key

@app.get("/api/v1/auth/keys")
async def list_api_keys(client_id: Optional[str] = None, api_key: APIKey = Depends(get_api_key)):
    """List all API keys or filter by client_id."""
    return auth_service.list_api_keys(client_id)

@app.delete("/api/v1/auth/keys/{key}")
async def deactivate_api_key(key: str, api_key: APIKey = Depends(get_api_key)):
    """Deactivate an API key."""
    if auth_service.deactivate_api_key(key):
        return {"status": "success", "message": "API key deactivated"}
    raise HTTPException(status_code=404, detail="API key not found")

# Modified existing endpoints to require authentication
@app.post("/api/v1/index", response_model=URLResponse)
async def index_url(url_input: URLInput, api_key: APIKey = Depends(get_api_key)):
    """Index a new URL or update an existing one in the vector store."""
    try:
        url_str = str(url_input.url)
        url_exists = rag_service.url_exists(url_str)
        
        if url_exists and not url_input.force_update:
            return URLResponse(
                status="skipped",
                message=f"URL {url_str} is already indexed. Use force_update=true to reindex.",
                was_indexed=False
            )
        
        success = rag_service.process_url(
            url_str,
            force_update=url_input.force_update
        )
        
        if success:
            action = "updated" if url_exists else "indexed"
            return URLResponse(
                status="success",
                message=f"Successfully {action} {url_str}",
                was_indexed=True
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to process URL")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat")
async def chat(chat_input: ChatInput, api_key: APIKey = Depends(get_api_key)):
    """Process a chat query and return response with sources."""
    try:
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_input.chat_history
        ]
        
        response_text, sources = rag_service.get_response(
            chat_input.query,
            chat_history
        )
        
        return ChatResponse(response=response_text, sources=sources)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats(api_key: APIKey = Depends(get_api_key)):
    """Get statistics about the vector store collection."""
    try:
        return rag_service.get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host_name, port=port_no)