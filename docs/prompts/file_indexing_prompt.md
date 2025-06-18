# Purpose
Implement a backend service that enables semantic indexing of user-uploaded documents (technical specifications, PDFs, DOCX, HTML, etc.) to support fast and relevant knowledge retrieval by AI agents. This pipeline transforms documents into vector representations for semantic search and context injection into LLMs.

# Key Steps

1. **File Storage**  
   - Users upload documents through a frontend or API  
   - Files are stored in **AWS S3** (object storage)

2. **Text Extraction & Chunking**  
   - Backend service extracts raw text from uploaded files  
   - Text is split into manageable chunks (~300–500 tokens per chunk)  
   - Each chunk includes metadata such as `user_id`, `file_id`, `chunk_id`

3. **Embedding Generation**  
   - Each chunk is converted into a vector using **Vertex AI Embedding API**  
   - Embeddings are used for downstream semantic search

4. **Vector Indexing**  
   - Embedding vectors are stored in **Vertex AI Vector Search**  
   - Supports high-speed, semantic top-K retrieval

5. **Metadata Storage**  
   - Metadata for each chunk is stored in **BigQuery** (e.g., file info, timestamps, ownership)  
   - Enables traceability, filtering, and auditability

6. **Search Runtime Flow**  
   - When an AI agent receives a user query:  
     - Query is embedded using the same embedding model  
     - Top-K relevant document chunks are retrieved from the vector index  
     - These chunks are passed as context to **Gemini 1.5 Pro** (or another LLM) for generating a response

# Tech Stack
- **AWS S3** – File storage (PDF, DOCX, etc.)
- **Vertex AI Embedding API** – Text-to-vector conversion
- **Vertex AI Vector Search** – Semantic vector index and retrieval
- **BigQuery** – Chunk metadata storage
- **.NET (C#)** or **Python (FastAPI / Flask)** – Backend implementation
- **Langchain** (optional for Python) – For managing the RAG pipeline and agent logic
