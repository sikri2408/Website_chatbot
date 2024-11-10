#Config --> main.py
PERSIST_DIRECTORY = 'chroma_db_websites/'
port_no = 8080
host_name = "127.0.0.1"

#Config --> streamlit_ui.py
CHAT_API_URL = f"http://{host_name}:{port_no}/api/v1/chat"

#Config --> index_service.py
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

from dotenv import load_dotenv
load_dotenv()
import os
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# API Authentication
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")  # For managing API keys
API_KEY_EXPIRY_DAYS = 90  # For key rotation
