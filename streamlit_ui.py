import streamlit as st
import requests
import json
from typing import List, Dict
from config import CHAT_API_URL, API_KEY, API_CLIENT_ID
import warnings
warnings.filterwarnings('ignore')

# Configure page settings
st.set_page_config(
    page_title="RAG Chat Interface",
    page_icon="💬",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"

def format_message(role: str, content: str) -> Dict[str, str]:
    """Format message for API request"""
    return {"role": role, "content": content}

# Update existing functions to include client_id
def get_chat_response(query: str, chat_history: List[Dict[str, str]], api_key: str, client_id: str) -> tuple:
    """Get response from API with authentication"""
    try:
        response = requests.post(
            CHAT_API_URL,
            json={
                "query": query,
                "chat_history": chat_history
            },
            headers={
                "X-API-Key": api_key,
                "X-Client-ID": client_id
            }
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        if response.status_code == 403:
            st.session_state.is_authenticated = False
            return None, "Authentication failed. Please check your credentials."
        return None, f"Error communicating with API: {str(e)}"

def submit_url(url: str, force_update: bool = False, api_key: str = None, client_id: str = None) -> tuple:
    """Submit URL to be indexed"""
    try:
        response = requests.post(
            f"{CHAT_API_URL.rsplit('/', 1)[0]}/index",
            json={
                "url": url,
                "force_update": force_update
            },
            headers={
                "X-API-Key": api_key,
                "X-Client-ID": client_id
            }
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        if response.status_code == 403:
            st.session_state.is_authenticated = False
            return None, "Authentication failed. Please check your credentials."
        return None, f"Error submitting URL: {str(e)}"

# Update session state initialization
if "client_id" not in st.session_state:
    st.session_state.client_id = None


# Update sidebar authentication
with st.sidebar:
    st.title("🔐 Authentication")
    
    if not st.session_state.is_authenticated:
        client_id = st.text_input("Enter Client ID", type="password")
        api_key = st.text_input("Enter API Key", type="password")
        
        if st.button("Login"):
            if api_key == API_KEY and client_id == API_CLIENT_ID:
                st.session_state.api_key = api_key
                st.session_state.client_id = client_id
                st.session_state.is_authenticated = True
                st.success("Successfully authenticated!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    else:
        st.success("Authenticated ✅")
        if st.button("Logout"):
            st.session_state.api_key = None
            st.session_state.is_authenticated = False
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
     # Navigation menu (only shown when authenticated)
    if st.session_state.is_authenticated:
        st.title("📍 Navigation")
        nav_col1, nav_col2 = st.columns(2)
        
        with nav_col1:
            if st.button("💬 Chat Interface", 
                        type="primary" if st.session_state.current_page == "chat" else "secondary",
                        use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        
        with nav_col2:
            if st.button("🔗 Add URL", 
                        type="primary" if st.session_state.current_page == "url" else "secondary",
                        use_container_width=True):
                st.session_state.current_page = "url"
                st.rerun()
        
        st.divider()
    
    # About section
    st.title("ℹ️ About")
    st.markdown("""
    This is a RAG (Retrieval-Augmented Generation) chat interface.
    
    **Features:**
    - Secure API key authentication
    - Chat with the AI about indexed content
    - View sources for responses
    - Persistent chat history during session
    """)
    
    if st.session_state.is_authenticated:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

# Main content area
if st.session_state.is_authenticated:
    if st.session_state.current_page == "chat":
        # Chat Interface
        st.title("💬 RAG Chat Interface")
        st.divider()

        chat_container = st.container()
        with chat_container:
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if "sources" in message and message["sources"]:
                        with st.expander("View Sources"):
                            for source in message["sources"]:
                                st.write(f"- {source}")

        # User input
        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append(format_message("user", prompt))
            with st.chat_message("user"):
                st.write(prompt)

            chat_history = [
                msg for msg in st.session_state.messages 
                if msg["role"] in ["user", "assistant"]
            ]

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response_data, error = get_chat_response(
                        prompt, 
                        chat_history,
                        st.session_state.api_key,
                        st.session_state.client_id
                    )
                    
                    if error:
                        st.error(error)
                    else:
                        st.write(response_data["response"])
                        
                        if response_data.get("sources"):
                            with st.expander("View Sources"):
                                for source in response_data["sources"]:
                                    st.write(f"- {source}")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_data["response"],
                            "sources": response_data.get("sources", [])
                        })
    
    else:
        # URL Submission Interface
        st.title("🔗 Add URL to Knowledge Base")
        st.divider()
        
        with st.form("url_submission_form"):
            url = st.text_input("Enter URL to index", 
                              placeholder="https://example.com/article")
            force_update = st.checkbox("Force update if URL already exists")
            
            submitted = st.form_submit_button("Submit URL")
            if submitted:
                if url:
                    with st.spinner("Processing URL..."):
                        result, error = submit_url(
                            url, 
                            force_update,
                            st.session_state.api_key,
                             st.session_state.client_id
                        )
                        if error:
                            st.error(error)
                        else:
                            st.success(result["message"])
                else:
                    st.warning("Please enter a URL")
        
        # URL Submission Tips
        with st.expander("URL Submission Tips"):
            st.markdown("""
            **Guidelines for submitting URLs:**
            - Enter complete URLs including the protocol (http:// or https://)
            - Ensure the webpage is publicly accessible
            - Check if the content is relevant to your knowledge base
            - Use 'Force update' if you want to refresh existing content
            
            **Supported content types:**
            - Blog posts
            - Articles
            - Documentation
            - Research papers
            - Technical guides
            """)

else:
    st.title("🔐 Authentication Required")
    st.info("Please authenticate using the sidebar to access the interface.")