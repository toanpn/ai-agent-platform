# Technical Specification: File Indexing Service

## 1. Overview

This document outlines the technical design for the File Indexing Service, a core component of the AI Agent Platform. Its purpose is to process and index documents uploaded by various departments, making them searchable for Retrieval-Augmented Generation (RAG) by their respective AI agents.

This service will handle file ingestion, text extraction, chunking, embedding generation, and storage of both vector embeddings and their associated metadata. The design ensures multi-tenancy, allowing for secure data segregation between departments.

## 2. System Architecture

The indexing pipeline is designed as an asynchronous, multi-cloud workflow to ensure scalability and resilience. The architecture uses AWS S3 for storage and Google Cloud Platform (GCP) for compute and AI services, with a direct API call to trigger the indexing process.

```plaintext
+-----------------+      +-------------------+      +-----------------+
|   Agent Mgmt    |----->|  File Upload API  |----->|     AWS S3      |
|      UI         |      | (.NET on Cloud Run)|      |   (Raw Files)   |
+-----------------+      +---------+---------+      +-----------------+
                                    |
                                    | (Direct API Call)
                                    v
+-----------------------+      +------------------+      +-------------------+
| Vertex AI Vector      |<-+---| Embedding API    |<-----| Indexing Service  |
| Search (Embeddings)   |  |   | (Vertex AI)      |      | (.NET Cloud Function)|
+-----------------------+  |   +------------------+      +-------------------+
                           |                                |
                           +--------------------------------+
                                                            |
                                                            v
                                                      +-------------------+
                                                      | BigQuery          |
                                                      | (Chunk Metadata)  |
                                                      +-------------------+
```

### Components:
-   **File Upload API**: A REST API endpoint, built with **.NET**, running on Google Cloud Run, for handling file uploads.
-   **AWS S3**: Stores the original, raw files uploaded by departments.
-   **Indexing Service**: A **.NET** Google Cloud Function that exposes an HTTP endpoint. It is called directly by the **File Upload API** after a file is successfully uploaded. It orchestrates the text extraction, chunking, and embedding process.
-   **Vertex AI Embedding API**: Generates vector embeddings from text chunks.
-   **Vertex AI Vector Search**: A managed vector database for storing and performing high-speed semantic searches on the embeddings.
-   **BigQuery**: Stores metadata for each text chunk, including its content, source file, and departmental ownership.

## 3. Data Models

### 3.1. AWS S3
Files will be stored with a clear prefix structure to ensure logical separation.
-   **Object Path**: `s3://[BUCKET_NAME]/[department_id]/[file_id]/[original_filename]`
-   **S3 Metadata**:
    -   `file_id`: A unique UUID for the document.
    -   `department_id`: The identifier for the department that owns the file.
    -   `uploader_user_id`: The ID of the user who uploaded the file.

### 3.2. BigQuery Metadata
A central table will store the content and metadata of each chunk.
-   **Table**: `document_chunks`
-   **Schema**:
    -   `chunk_id` (STRING, Primary Key): Unique identifier for the chunk (UUID).
    -   `file_id` (STRING, Foreign Key): Identifier of the source file.
    -   `department_id` (STRING, Indexed): Department that owns this data.
    -   `chunk_text` (STRING): The raw text content of the chunk.
    -   `chunk_token_count` (INTEGER): The number of tokens in the chunk.
    -   `embedding_model_version` (STRING): The version of the embedding model used (e.g., `text-embedding-004`).
    -   `created_at` (TIMESTAMP): Timestamp of when the chunk was created.

### 3.3. Vertex AI Vector Search
The index will store the vector embeddings.
-   **Vector ID**: The `chunk_id` from the BigQuery table.
-   **Vector Dimensions**: Depends on the embedding model (e.g., 768 for `text-embedding-004`).
-   **Namespaces/Restrictions**: The index will be configured to use `department_id` as a "restriction" (namespace), enabling strict data isolation during search queries.

## 4. API Endpoints

The primary interaction with the indexing service is for file upload.

### `POST /api/v1/departments/{department_id}/files`
-   **Description**: Uploads a file for a specific department to be indexed. The call is asynchronous.
-   **Authentication**: The request must be authenticated, and the caller authorized to act on behalf of the `{department_id}`.
-   **Request Body**: `multipart/form-data` containing the file.
-   **Success Response** (`202 Accepted`):
    ```json
    {
      "file_id": "a8e7e1e4-6c8a-4959-9a74-1b072e528574",
      "filename": "HR_Leave_Policy_2024.pdf",
      "status": "processing",
      "status_check_url": "/api/v1/files/a8e7e1e4-6c8a-4959-9a74-1b072e528574/status"
    }
    ```

### `GET /api/v1/files/{file_id}/status`
-   **Description**: Checks the indexing status of a previously uploaded file.
-   **Success Response** (`200 OK`):
    ```json
    {
      "file_id": "a8e7e1e4-6c8a-4959-9a74-1b072e528574",
      "status": "completed", // or "processing", "failed"
      "message": "File indexed successfully. 15 chunks created.",
      "error_details": null // or details on failure
    }
    ```

## 5. Detailed Indexing Workflow

1.  **Upload**: A user from a department (e.g., HR) uploads a document (`HR_Leave_Policy_2024.pdf`) via the Agent Management UI.
2.  **API Call**: The UI makes a `POST` request to `/api/v1/departments/hr/files`.
3.  **Initial Storage**: The API backend generates a `file_id`, stores the file in **AWS S3** at `hr/[file_id]/HR_Leave_Policy_2024.pdf`, and returns a `202 Accepted` response.
4.  **Trigger**: After the file is successfully uploaded to S3, the **File Upload API** makes a direct, asynchronous HTTP POST request to the **Indexing Service** endpoint, passing along necessary metadata like the `file_id`, `department_id`, and the S3 object path.
5.  **Text Extraction**: The service downloads the file from **AWS S3**. It uses **.NET libraries** (e.g., `PdfPig` for PDF, `Open-XML-SDK` for DOCX) to parse the document and extract its raw text content.
6.  **Chunking**: The extracted text is split into manageable, overlapping chunks of approximately 300-500 tokens each. This can be implemented using custom text manipulation logic in .NET. Each chunk is assigned a unique `chunk_id`.
7.  **Embedding & Storage**: For each chunk, the service performs the following in a batch process:
    a.  Calls the **Vertex AI Embedding API** to generate a vector embedding.
    b.  Upserts the embedding into the **Vertex AI Vector Search** index, using `chunk_id` as the vector's ID and `department_id` as the restriction key.
    c.  Inserts a corresponding record into the **BigQuery** `document_chunks` table with the chunk's text and metadata.
8.  **Status Update**: After all chunks are processed, the file's overall status is updated (e.g., in a separate Firestore or BigQuery table) to "completed" or "failed".

## 6. Error Handling and Resilience

The system must be resilient to failures at various stages. The status check endpoint (`/api/v1/files/{file_id}/status`) is the primary way for users to be informed of the outcome.

-   **Upload Failure**: The File Upload API will reject files that don't meet validation criteria (e.g., size, type) with a `4xx` status code. Network interruptions during upload will be handled by the client.
-   **Indexing Service Failure**:
    -   **Transient Errors**: Issues like temporary network problems when accessing S3 or transient errors from Vertex AI APIs should be handled with a retry mechanism (e.g., exponential backoff).
    -   **Permanent Errors**: If a file is corrupt, in an unsupported format, or cannot be parsed, the error is considered permanent.
-   **Failure Protocol**:
    1.  **Retry**: For transient errors, the service will retry the operation up to 3 times.
    2.  **Log and Report**: If retries fail or the error is permanent, the service will:
        a.  Log the detailed error in Google Cloud Logging.
        b.  Update the file's status to `"failed"`.
        c.  Store a user-friendly error message in the `error_details` field (e.g., "Failed to parse the provided DOCX file. It may be corrupt or in an unsupported format.").
    3.  **Dead-Letter Queue**: For critical, unhandled exceptions within the Indexing Service, a dead-letter topic/queue in Google Pub/Sub can be configured to capture the failed event for manual inspection.

## 7. Updating and Deleting Documents

The lifecycle of a document extends beyond its initial creation.

### 7.1. Updating a Document
To update a document, the client will re-upload it. This is effectively a "delete and re-index" operation from the system's perspective.
1.  A user uploads a new version of an existing file. A recommended approach is to call the `DELETE` endpoint first, and then the `POST` endpoint to upload the new version.
2.  Alternatively, the `POST /api/v1/departments/{department_id}/files` endpoint could be made idempotent or support an `update` flag, triggering the deletion of the old `file_id`'s data before proceeding with the new indexing flow. The first approach is simpler to implement.

### 7.2. Deleting a Document
A dedicated endpoint will be required to handle document deletion.

#### `DELETE /api/v1/files/{file_id}`
-   **Description**: Triggers the permanent deletion of a file and its associated indexed data.
-   **Success Response**: `204 No Content`.

The deletion process involves:
1.  **Triggering Deletion**: The API call initiates an asynchronous background process (e.g., another Cloud Function).
2.  **Finding Chunks**: The process queries BigQuery to retrieve all `chunk_id`s associated with the given `file_id`.
3.  **Deleting Vectors**: It deletes the corresponding vectors from the Vertex AI Vector Search index in a batch operation using the `chunk_id`s.
4.  **Deleting Metadata**: It deletes the chunk metadata records from the BigQuery `document_chunks` table.
5.  **Deleting Raw File**: Finally, it deletes the original file from the AWS S3 bucket.

## 8. Chunking Strategy

The quality of the search results heavily depends on the chunking strategy.

-   **Chunk Size**: 300-500 tokens is a good starting point. This is small enough to ensure the retrieved chunks are highly relevant to the query, but large enough to contain meaningful semantic context.
-   **Chunk Overlap**: An overlap of approximately 50-100 tokens between consecutive chunks is crucial. This ensures that semantic context is not lost at chunk boundaries. For example, a sentence that is split across two chunks will be fully contained in at least one of them due to the overlap.
-   **Splitting Logic**: The service will employ a hierarchical splitting strategy:
    1.  First, attempt to split the extracted text by semantic units like paragraphs or sections.
    2.  If a resulting section is still larger than the token limit, it will be recursively split into smaller chunks based on sentence boundaries.
    3.  If a single sentence exceeds the token limit, it will be split by a fixed token count as a last resort.
-   **Future Enhancements**: The system can be improved by adding document-specific chunking logic. For example, for a Markdown or HTML document, it could preserve header context within each chunk derived from that section.

## 9. Search and Retrieval Flow (Runtime)

1.  **Query**: A user asks an HR agent, "How many vacation days do I get?"
2.  **Embedding**: The Main Router Agent forwards the query to the HR Agent. The HR Agent embeds the query ("How many vacation days do I get?") using the same Vertex AI model.
3.  **Semantic Search**: The agent queries the Vertex AI Vector Search index with the new vector.
4.  **Filtering**: The query **must** include a `restriction` for `department_id: 'hr'`. This is a critical step to ensure it only searches within HR's documents.
5.  **Retrieval**: The vector search returns the IDs (e.g., top 5 `chunk_id`s) of the most relevant text chunks.
6.  **Context Augmentation**: The agent fetches the full text of these chunks from BigQuery using their `chunk_id`s.
7.  **Generation**: The retrieved text chunks are injected into a prompt as context for the LLM (Gemini 1.5 Pro), which then generates a precise answer based on the provided leave policy documents.

## 10. Technology Stack Summary

-   **Backend**: **.NET (C#)**
-   **Compute**: Google Cloud Run (API) & Google Cloud Functions (Indexing)
-   **File Storage**: **AWS S3**
-   **Vector Embeddings**: Vertex AI Embedding API
-   **Vector Store**: Vertex AI Vector Search
-   **Metadata Store**: Google BigQuery
-   **Libraries**: **.NET libraries for document parsing (e.g., `PdfPig`, `Open-XML-SDK`)**.
