from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List, Tuple, Dict, Any
import re
import warnings
warnings.filterwarnings('ignore')

from config import OPENAI_API_KEY
from index_service import VectorStoreManager

class RAGService:
    def __init__(self, persist_directory: str):
        self.vector_store_manager = VectorStoreManager(persist_directory)
        
    def get_context_retriever_chain(self):
        """Create a context-aware retriever chain."""
        llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        
        retriever = self.vector_store_manager.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.6,
            }
        )
        
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Given the above conversation, generate a focused and specific search query to find the most relevant information. Avoid broad or generic queries.")
        ])
        
        return create_history_aware_retriever(llm, retriever, prompt)

    def get_conversational_rag_chain(self, retriever_chain):
        """Create a conversational RAG chain."""
        llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions based STRICTLY on the provided context. 

            Instructions for providing answers:
            1. Only answer what is explicitly supported by the context
            2. If the context doesn't contain information to answer the question, respond with "I couldn't find any information in the provided context to answer your question."
            3. Do not make assumptions or include external knowledge
            4. If the context only partially answers the question, only provide what is supported by the context and mention that only partial information was found
            5. Use citation numbers [1] ONLY when directly quoting or referencing specific information from a source
            6. Use each citation number only ONCE in your response - do not repeat citations
            7. Make sure each citation actually corresponds to information from that source
            8. If multiple sources contain the same information, use only the most relevant source

            Context:
            {context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        
        stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever_chain, stuff_documents_chain)

    @staticmethod
    def extract_citations(text: str) -> List[int]:
        """Extract unique citation numbers from text in order of appearance."""
        citations = re.findall(r'\[(\d+)\]', text)
        return [int(c) for c in dict.fromkeys(citations)]

    def format_response_with_citations(self, response_text: str, source_documents: List) -> Tuple[str, List[str]]:
        """Format response with deduplicated citations and return response text and sources."""
        no_info_message = "I couldn't find any information in the provided context to answer your question."
        if response_text.strip() == no_info_message:
            return response_text, []

        used_citations = self.extract_citations(response_text)
        
        if not used_citations:
            return response_text, []
            
        sources = []
        urls_seen = set()
        
        for citation_num in used_citations:
            if citation_num <= len(source_documents):
                doc = source_documents[citation_num - 1]
                if 'url' in doc.metadata:
                    url = doc.metadata['url']
                    if url not in urls_seen:
                        sources.append(url)
                        urls_seen.add(url)
        
        return response_text, sources

    def url_exists(self, url: str) -> bool:
        """Check if a URL is already indexed."""
        url_hash = self.vector_store_manager.get_url_hash(url)
        return self.vector_store_manager.url_already_exists(url_hash)

    def process_url(self, url: str, force_update: bool = False) -> bool:
        """Process and index a URL."""
        return self.vector_store_manager.process_url(url, force_update)

    def get_response(self, query: str, chat_history: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        """Get response for a query with chat history."""
        # Convert chat history to LangChain message format
        formatted_history = []
        for msg in chat_history:
            if msg["role"].lower() == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # Get response using RAG chain
        retriever_chain = self.get_context_retriever_chain()
        conversation_rag_chain = self.get_conversational_rag_chain(retriever_chain)
        
        response = conversation_rag_chain.invoke({
            "chat_history": formatted_history,
            "input": query
        })
        
        # Format response and extract sources
        return self.format_response_with_citations(
            response['answer'],
            response['context']
        )

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        return self.vector_store_manager.print_collection_stats()