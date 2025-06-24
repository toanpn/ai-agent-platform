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
                 persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: VertexAI embedding model name
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        
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
            self.embeddings = VertexAIEmbeddings(
                model_name=self.embedding_model,
                project=os.getenv('GOOGLE_CLOUD_PROJECT'),
                location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            )
            logger.info(f"✅ VertexAI embeddings initialized with model: {self.embedding_model}")
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
            
            # Create or get collection
            if self.embeddings:
                # Use custom VertexAI embeddings
                embedding_function = embedding_functions.GoogleVertexEmbeddingFunction(
                    api_key=os.getenv('GOOGLE_API_KEY'),
                    model_name=self.embedding_model
                )
            else:
                # Use default embedding function
                embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"✅ Retrieved existing ChromaDB collection: {self.collection_name}")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"✅ Created new ChromaDB collection: {self.collection_name}")
            
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