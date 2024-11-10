import streamlit as st
import requests
import json
from typing import List, Dict
from config import CHAT_API_URL
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

def format_message(role: str, content: str) -> Dict[str, str]:
    """Format message for API request"""
    return {"role": role, "content": content}

def get_chat_response(query: str, chat_history: List[Dict[str, str]]) -> tuple:
    """Get response from API"""
    try:
        response = requests.post(
            CHAT_API_URL,
            json={
                "query": query,
                "chat_history": chat_history
            }
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error communicating with API: {str(e)}"

# Main title
st.title("💬 RAG Chat Interface")
st.divider()

# Chat interface
chat_container = st.container()
with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            # Display sources if available
            if "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for source in message["sources"]:
                        st.write(f"- {source}")

# User input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat
    st.session_state.messages.append(format_message("user", prompt))
    with st.chat_message("user"):
        st.write(prompt)

    # Prepare chat history
    chat_history = [
        msg for msg in st.session_state.messages 
        if msg["role"] in ["user", "assistant"]
    ]

    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data, error = get_chat_response(prompt, chat_history)
            
            if error:
                st.error(error)
            else:
                # Display response
                st.write(response_data["response"])
                
                # Display sources if available
                if response_data.get("sources"):
                    with st.expander("View Sources"):
                        for source in response_data["sources"]:
                            st.write(f"- {source}")
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "sources": response_data.get("sources", [])
                })

# Add a sidebar with instructions
with st.sidebar:
    st.title("ℹ️ About")
    st.markdown("""
    This is a RAG (Retrieval-Augmented Generation) chat interface.
    
    **Features:**
    - Chat with the AI about indexed content
    - View sources for responses
    - Persistent chat history during session
    
    **Usage:**
    1. Type your question in the chat input
    2. Press Enter to send
    3. View the AI's response and sources
    """)
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()