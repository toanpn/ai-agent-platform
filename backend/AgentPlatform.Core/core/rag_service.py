"""
RAG Service Module

This module provides Retrieval-Augmented Generation (RAG) functionality using ChromaDB
and Google VertexAI embeddings. It handles document processing, embedding generation,
vector storage, and retrieval for the agent system.
"""

import os
import uuid
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import tempfile
import asyncio

# Core dependencies
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Google Cloud imports
from google.auth import default
from google.oauth2 import service_account
import google.auth

# LangChain imports
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader, 
    UnstructuredExcelLoader,
    TextLoader,
    WebBaseLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Document processing
import pypdf
from docx import Document as DocxDocument
import openpyxl
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles processing of various document types."""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.doc': self._process_docx,  # Treating .doc as .docx for now
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.txt': self._process_text,
            '.md': self._process_text,
        }
    
    def can_process(self, file_path: str) -> bool:
        """Check if file format is supported."""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def process_file(self, file_path: str, metadata: Optional[Dict] = None) -> List[Document]:
        """Process a file and return LangChain documents."""
        file_suffix = Path(file_path).suffix.lower()
        
        if not self.can_process(file_path):
            raise ValueError(f"Unsupported file format: {file_suffix}")
        
        try:
            documents = self.supported_formats[file_suffix](file_path)
            
            # Add metadata to all documents
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Add file metadata
            file_metadata = {
                'source': file_path,
                'file_type': file_suffix,
                'processed_at': str(uuid.uuid4())
            }
            
            for doc in documents:
                doc.metadata.update(file_metadata)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def process_web_url(self, url: str, metadata: Optional[Dict] = None) -> List[Document]:
        """Process web content using WebBaseLoader."""
        try:
            loader = WebBaseLoader([url])
            documents = loader.load()
            
            # Add metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Add web metadata
            web_metadata = {
                'source': url,
                'content_type': 'web',
                'processed_at': str(uuid.uuid4())
            }
            
            for doc in documents:
                doc.metadata.update(web_metadata)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            raise
    
    def _process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF files."""
        loader = PyPDFLoader(file_path)
        return loader.load()
    
    def _process_docx(self, file_path: str) -> List[Document]:
        """Process DOCX files."""
        loader = Docx2txtLoader(file_path)
        return loader.load()
    
    def _process_excel(self, file_path: str) -> List[Document]:
        """Process Excel files."""
        loader = UnstructuredExcelLoader(file_path)
        return loader.load()
    
    def _process_text(self, file_path: str) -> List[Document]:
        """Process text files (txt, md)."""
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()


class RAGService:
    """Main RAG service class that orchestrates document processing, embedding, and retrieval."""
    
    def __init__(self, 
                 collection_name: str = "agent_knowledge_base",
                 embedding_model: str = "text-multilingual-embedding-002",
                 persist_directory: Optional[str] = None):
        """
        Initialize RAG service.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: VertexAI embedding model name
            persist_directory: Directory to persist ChromaDB data (defaults to CHROMA_DB_PATH env var or /tmp/chroma_db)
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Set persist directory with environment variable support
        if persist_directory:
            self.persist_directory = persist_directory
        else:
            self.persist_directory = os.getenv('CHROMA_DB_PATH', '/tmp/chroma_db')
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize embedding function
        self._init_embeddings()
        
        # Initialize ChromaDB
        self._init_chromadb()
    
    def _init_embeddings(self):
        """Initialize VertexAI embeddings."""
        try:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
            
            # Set up Google Cloud credentials - check multiple possible paths
            credentials = None
            
            # List of possible credential file paths (local and Docker)
            possible_paths = []
            if credentials_path:
                possible_paths.append(credentials_path)
            
            # Add common paths for both local and Docker environments
            possible_paths.extend([
                '/app/gcp-credentials.json',  # Docker path
                './gcp-credentials.json',     # Local relative path
                'gcp-credentials.json',       # Current directory
                '../gcp-credentials.json',    # Parent directory (if running from subdirectory)
                os.path.join(os.path.dirname(__file__), '../../../gcp-credentials.json')  # From core/ to project root
            ])
            
            # Try each path until we find a valid credentials file
            credentials_found = False
            for path in possible_paths:
                if path and os.path.exists(path):
                    try:
                        logger.info(f"✅ Loading service account credentials from: {path}")
                        credentials = service_account.Credentials.from_service_account_file(path)
                        logger.info(f"✅ Service account loaded: {credentials.service_account_email}")
                        credentials_found = True
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load credentials from {path}: {e}")
                        continue
            
            # If no service account file found, try default credentials
            if not credentials_found:
                logger.info("🔄 No service account file found, attempting to use default credentials")
                try:
                    credentials, project = default()
                    if project:
                        project_id = project
                    logger.info(f"✅ Default credentials loaded for project: {project_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load default credentials: {e}")
                    raise ValueError("No valid Google Cloud credentials found")
            
            # Initialize VertexAI embeddings with explicit credentials
            self.embeddings = VertexAIEmbeddings(
                model_name=self.embedding_model,
                project=project_id,
                location=location,
                credentials=credentials
            )
            logger.info(f"✅ VertexAI embeddings initialized with model: {self.embedding_model} (project: {project_id}, location: {location})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize VertexAI embeddings: {e}")
            # Fallback to ChromaDB default embeddings if VertexAI fails
            logger.warning("⚠️ Falling back to default embeddings")
            self.embeddings = None
    
    def _init_chromadb(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Determine embedding function based on VertexAI availability
            if self.embeddings:
                # Create custom embedding function using service account credentials
                class VertexAIServiceAccountEmbeddingFunction:
                    def __init__(self, langchain_embeddings, model_name):
                        self.embeddings = langchain_embeddings
                        self._name = f"vertex_ai_service_account_{model_name}"
                    
                    def name(self):
                        return self._name
                    
                    def __call__(self, input):
                        # Handle both single string and list of strings
                        if isinstance(input, str):
                            return self.embeddings.embed_query(input)
                        elif isinstance(input, list):
                            return self.embeddings.embed_documents(input)
                        else:
                            raise ValueError(f"Unsupported input type: {type(input)}")
                
                embedding_function = VertexAIServiceAccountEmbeddingFunction(self.embeddings, self.embedding_model)
                embedding_type = "google_vertex_service_account"
            else:
                # Use default embedding function
                embedding_function = embedding_functions.DefaultEmbeddingFunction()
                embedding_type = "default"
            
            # Check if collection exists and handle embedding function conflicts
            try:
                existing_collections = [col.name for col in self.client.list_collections()]
                if self.collection_name in existing_collections:
                    try:
                        # Try to get existing collection
                        self.collection = self.client.get_collection(
                            name=self.collection_name,
                            embedding_function=embedding_function
                        )
                        logger.info(f"✅ Retrieved existing ChromaDB collection: {self.collection_name}")
                    except Exception as e:
                        # If there's an embedding function conflict, recreate the collection
                        if "embedding function" in str(e).lower() or "conflict" in str(e).lower():
                            logger.warning(f"⚠️ Embedding function conflict detected: {e}")
                            logger.info(f"🔄 Recreating collection with {embedding_type} embedding function...")
                            
                            # Delete existing collection
                            self.client.delete_collection(name=self.collection_name)
                            logger.info(f"🗑️ Deleted existing collection: {self.collection_name}")
                            
                            # Create new collection with correct embedding function
                            self.collection = self.client.create_collection(
                                name=self.collection_name,
                                embedding_function=embedding_function
                            )
                            logger.info(f"✅ Created new ChromaDB collection with {embedding_type} embeddings: {self.collection_name}")
                        else:
                            raise e
                else:
                    # Collection doesn't exist, create it
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        embedding_function=embedding_function
                    )
                    logger.info(f"✅ Created new ChromaDB collection with {embedding_type} embeddings: {self.collection_name}")
            
            except Exception as e:
                logger.error(f"❌ Error with ChromaDB collection operations: {e}")
                # Final fallback - try to create collection directly
                try:
                    self.collection = self.client.create_collection(
                        name=f"{self.collection_name}_{embedding_type}",
                        embedding_function=embedding_function
                    )
                    logger.info(f"✅ Created fallback ChromaDB collection: {self.collection_name}_{embedding_type}")
                except Exception as create_error:
                    logger.error(f"❌ Failed to create collection as fallback: {create_error}")
                    raise create_error
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            raise
    
    def add_document(self, file_path: str, agent_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add a document to the knowledge base.
        
        Args:
            file_path: Path to the document file
            agent_id: ID of the agent this document belongs to
            metadata: Additional metadata for the document
            
        Returns:
            Dict with processing results
        """
        try:
            # Prepare metadata
            doc_metadata = metadata or {}
            if agent_id:
                doc_metadata['agent_id'] = agent_id
            
            doc_metadata.update({
                'upload_timestamp': str(uuid.uuid4()),
                'file_name': Path(file_path).name
            })
            
            # Process document
            documents = self.document_processor.process_file(file_path, doc_metadata)
            
            # Split documents into chunks
            chunks = []
            for doc in documents:
                doc_chunks = self.text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
            
            if not chunks:
                raise ValueError("No content extracted from document")
            
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_texts = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_metadata['upload_timestamp']}_{i}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk.page_content)
                chunk_metadatas.append(chunk.metadata)
            
            # Add to ChromaDB
            self.collection.add(
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            result = {
                'status': 'success',
                'document_id': doc_metadata['upload_timestamp'],
                'chunks_created': len(chunks),
                'file_name': doc_metadata['file_name'],
                'agent_id': agent_id
            }
            
            logger.info(f"✅ Successfully processed document: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error adding document {file_path}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file_name': Path(file_path).name
            }
    
    def add_web_content(self, url: str, agent_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add web content to the knowledge base.
        
        Args:
            url: URL to process
            agent_id: ID of the agent this content belongs to
            metadata: Additional metadata
            
        Returns:
            Dict with processing results
        """
        try:
            # Prepare metadata
            doc_metadata = metadata or {}
            if agent_id:
                doc_metadata['agent_id'] = agent_id
            
            doc_metadata.update({
                'upload_timestamp': str(uuid.uuid4()),
                'source_url': url
            })
            
            # Process web content
            documents = self.document_processor.process_web_url(url, doc_metadata)
            
            # Split documents into chunks
            chunks = []
            for doc in documents:
                doc_chunks = self.text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
            
            if not chunks:
                raise ValueError("No content extracted from URL")
            
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_texts = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_metadata['upload_timestamp']}_{i}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk.page_content)
                chunk_metadatas.append(chunk.metadata)
            
            # Add to ChromaDB
            self.collection.add(
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            result = {
                'status': 'success',
                'document_id': doc_metadata['upload_timestamp'],
                'chunks_created': len(chunks),
                'source_url': url,
                'agent_id': agent_id
            }
            
            logger.info(f"✅ Successfully processed web content: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error adding web content {url}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'source_url': url
            }
    
    def search_knowledge(self, query: str, agent_id: Optional[str] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            agent_id: Filter by specific agent ID
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Prepare where clause for filtering by agent_id
            where_clause = {}
            if agent_id:
                where_clause['agent_id'] = agent_id
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result_item = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'id': results['ids'][0][i] if results['ids'] else None
                    }
                    formatted_results.append(result_item)
            
            logger.info(f"✅ Knowledge search completed: {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching knowledge base: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collection."""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def delete_agent_documents(self, agent_id: str) -> Dict[str, Any]:
        """Delete all documents for a specific agent."""
        try:
            # Get all documents for the agent
            results = self.collection.get(where={'agent_id': agent_id})
            
            if results['ids']:
                # Delete the documents
                self.collection.delete(ids=results['ids'])
                
                return {
                    'status': 'success',
                    'deleted_chunks': len(results['ids']),
                    'agent_id': agent_id
                }
            else:
                return {
                    'status': 'success',
                    'deleted_chunks': 0,
                    'agent_id': agent_id,
                    'message': 'No documents found for agent'
                }
                
        except Exception as e:
            logger.error(f"❌ Error deleting agent documents: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'agent_id': agent_id
            } 