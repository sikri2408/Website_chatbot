#Config --> main.py
PERSIST_DIRECTORY = 'chroma_db_websites/'
port_no = 8080
host_name = "127.0.0.1"

#Config --> streamlit_ui.py
CHAT_API_URL = f"http://{host_name}:{port_no}/api/v1/chat"

#Config --> index_service.py
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

#KEYS
OPENAI_API_KEY = "your_api_key"