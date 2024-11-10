import os
import hashlib
from urllib.parse import urlparse
import chromadb
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHUNK_SIZE, CHUNK_OVERLAP, OPENAI_API_KEY
import warnings
warnings.filterwarnings('ignore')

class VectorStoreManager:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.client_settings = chromadb.config.Settings(
            chroma_db_impl='duckdb+parquet',
            persist_directory=persist_directory
        )
        self.embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.vector_store = self.initialize_vector_store()

    def initialize_vector_store(self):
        """Initialize or load the vector store"""
        if os.path.exists(self.persist_directory):
            print(f"Loading existing vector store from {self.persist_directory}...")
        else:
            print(f"Creating new vector store in {self.persist_directory}...")
        
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
            client_settings=self.client_settings
        )

    def get_url_hash(self, url):
        """Create a hash of the URL to use as a unique identifier"""
        return hashlib.md5(url.encode()).hexdigest()

    def url_already_exists(self, url_hash):
        """Check if the URL has already been processed"""
        collection = self.vector_store._collection
        results = collection.get(
            where={"url_hash": url_hash},
            include=["metadatas"]
        )
        return len(results['metadatas']) > 0

    def process_url(self, url, force_update=False):
        """Process a URL and add its contents to the vector store if not already present"""
        url_hash = self.get_url_hash(url)
        
        # Check if URL already exists
        if not force_update and self.url_already_exists(url_hash):
            print(f"URL {url} already exists in the vector store. Skipping...")
            return False
        
        print(f"Processing new URL: {url}")
        
        # Load and process the document
        try:
            loader = WebBaseLoader(url)
            document = loader.load()
            
            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            document_chunks = text_splitter.split_documents(document)
            
            # Add URL metadata to each chunk
            for chunk in document_chunks:
                chunk.metadata.update({
                    "url": url,
                    "url_hash": url_hash,
                    "domain": urlparse(url).netloc
                })
            
            # If updating existing content, remove old entries first
            if force_update:
                print(f"Removing existing content for URL: {url}")
                collection = self.vector_store._collection
                collection.delete(
                    where={"url_hash": url_hash}
                )
            
            # Add documents to the vector store
            self.vector_store.add_documents(document_chunks)
            self.vector_store.persist()
            
            print(f"Successfully processed URL: {url}")
            return True
            
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            return False

    def print_collection_stats(self):
        """Print statistics about the vector store collection"""
        collection = self.vector_store._collection
        
        # Get total count of documents
        count = collection.count()
        print(f"\nCollection Statistics:")
        print(f"Total documents: {count}")
        
        # Get all metadata to analyze URLs
        result = collection.get(include=['metadatas'])
        
        # Get unique URLs
        unique_urls = set(meta['url'] for meta in result['metadatas'] if 'url' in meta)
        print(f"Unique URLs stored: {len(unique_urls)}")
        
        # Print domains
        domains = set(meta['domain'] for meta in result['metadatas'] if 'domain' in meta)
        print(f"Unique domains: {len(domains)}")
        print("Domains:", ", ".join(domains))
        
        # Calculate storage size
        if os.path.exists(self.vector_store._persist_directory):
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(self.vector_store._persist_directory)
                for filename in filenames
            )
            print(f"Total storage size on disk: {total_size / (1024*1024):.2f} MB")
        
        stats_response = f"""\nCollection Statistics:\n
                    Total documents: {count}
                    Unique URLs stored: {len(unique_urls)}
                    Unique domains: {len(domains)}
                    Domains: {', '.join(domains)}
                    Total storage size on disk: {total_size / (1024*1024):.2f} MB"""
        
        return stats_response


# Example usage
if __name__ == "__main__":
    persist_directory = 'chroma_db_websites'
    vector_store_manager = VectorStoreManager(persist_directory)
    
    # Example URLs to process
    urls = ['https://huyenchip.com/2024/07/25/genai-platform.html', 
        'https://lilianweng.github.io/posts/2024-07-07-hallucination/',
        'https://jina.ai/news/what-is-colbert-and-late-interaction-and-why-they-matter-in-search/',
        'https://quoraengineering.quora.com/Building-Embedding-Search-at-Quora'
    
    # Add more URLs as needed
    ]
    
    # Process each URL
    for url in urls:
        vector_store_manager.process_url(url)
    
    # Print statistics
    vector_store_manager.print_collection_stats()