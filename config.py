# config.py
from dotenv import load_dotenv
load_dotenv()
import os

# Server settings
PERSIST_DIRECTORY = 'chroma_db_websites/'
port_no = 8080
host_name = "0.0.0.0"

# API URLs
API_BASE_URL = f"http://{host_name}:{port_no}/api/v1"
CHAT_API_URL = f"{API_BASE_URL}/chat"

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# API keys 
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
API_CLIENT_ID = os.getenv("API_CLIENT_ID", "future_path")
API_KEY = os.getenv("API_KEY", "1234")  # Change this or use env var