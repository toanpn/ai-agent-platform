using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Data;
using AgentPlatform.API.Models;

namespace AgentPlatform.API.Services
{
    public class FileService : IFileService
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;
        private readonly IAgentRuntimeClient _runtimeClient;
        private readonly ILogger<FileService> _logger;
        private readonly string _basePath;

        public FileService(ApplicationDbContext context, IConfiguration configuration, IAgentRuntimeClient runtimeClient, ILogger<FileService> logger)
        {
            _context = context;
            _configuration = configuration;
            _runtimeClient = runtimeClient;
            _logger = logger;
            
            // Get the base path from configuration
            var configuredPath = _configuration["FileStorage:BasePath"] ?? "./uploads";
            
            // Convert relative path to absolute path to ensure consistency
            _basePath = Path.IsPathRooted(configuredPath) 
                ? configuredPath 
                : Path.GetFullPath(configuredPath);
            
            _logger.LogInformation("File storage base path resolved to: {BasePath}", _basePath);
            
            // Ensure upload directory exists
            try
            {
                Directory.CreateDirectory(_basePath);
                _logger.LogInformation("Upload directory created/verified: {BasePath}", _basePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create upload directory: {BasePath}", _basePath);
                throw;
            }
        }

        public async Task<string> UploadFileAsync(IFormFile file, int agentId, int userId)
        {
            if (file == null || file.Length == 0)
            {
                throw new ArgumentException("File is required");
            }

            var maxSizeMB = int.Parse(_configuration["FileStorage:MaxFileSizeMB"] ?? "100");
            var fileSizeMB = file.Length / (1024.0 * 1024.0);
            
            _logger.LogInformation("Uploading file: {FileName}, Size: {FileSizeMB:F2}MB, Max allowed: {MaxSizeMB}MB", 
                file.FileName, fileSizeMB, maxSizeMB);
            
            if (file.Length > maxSizeMB * 1024 * 1024)
            {
                var errorMessage = $"File size ({fileSizeMB:F2}MB) exceeds maximum allowed size of {maxSizeMB}MB";
                _logger.LogWarning("File upload rejected: {Error}", errorMessage);
                throw new ArgumentException(errorMessage);
            }

            // Check if agent exists and belongs to user
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                throw new KeyNotFoundException("Agent not found");
            }

            var fileName = Path.GetFileNameWithoutExtension(file.FileName);
            var extension = Path.GetExtension(file.FileName);
            var uniqueFileName = $"{fileName}_{Guid.NewGuid()}{extension}";
            var filePath = Path.Combine(_basePath, uniqueFileName);

            _logger.LogInformation("Uploading file: {OriginalFileName} -> {FilePath}", file.FileName, filePath);

            try
            {
                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await file.CopyToAsync(stream);
                }
                _logger.LogInformation("File successfully saved to: {FilePath}", filePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to save file to: {FilePath}. Directory exists: {DirectoryExists}", 
                    filePath, Directory.Exists(_basePath));
                throw;
            }

            var agentFile = new AgentFile
            {
                AgentId = agentId,
                FileName = file.FileName,
                FilePath = filePath,
                ContentType = file.ContentType,
                FileSize = file.Length,
                UploadedById = userId,
                CreatedAt = DateTime.UtcNow,
                IsIndexed = false // Initially not indexed
            };

            _context.AgentFiles.Add(agentFile);
            await _context.SaveChangesAsync();

            // Automatically start indexing the file
            try
            {
                await IndexFileAsync(agentFile.Id);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to index file {FileId} during upload", agentFile.Id);
                // Don't throw here - the file was uploaded successfully, indexing can be retried
            }

            return filePath;
        }

        public async Task<bool> DeleteFileAsync(int fileId, int userId)
        {
            var file = await _context.AgentFiles
                .Include(f => f.Agent)
                .FirstOrDefaultAsync(f => f.Id == fileId && f.Agent.CreatedById == userId);

            if (file == null)
            {
                return false;
            }

            try
            {
                // If the file was indexed, we should clean up the RAG data
                if (file.IsIndexed)
                {
                    _logger.LogInformation("Cleaning up RAG data for file {FileId} from agent {AgentId}", fileId, file.AgentId);
                    
                    // Note: The Python backend's delete endpoint is per-agent, not per-file
                    // This would delete all documents for the agent, which might not be desired
                    // For now, we'll just log this - you might want to implement a more granular deletion
                    _logger.LogWarning("File {FileId} was indexed but RAG cleanup is not implemented for individual files", fileId);
                }

                // Delete physical file
                if (File.Exists(file.FilePath))
                {
                    File.Delete(file.FilePath);
                    _logger.LogInformation("Physical file deleted: {FilePath}", file.FilePath);
                }

                // Remove from database
                _context.AgentFiles.Remove(file);
                await _context.SaveChangesAsync();

                _logger.LogInformation("File {FileId} successfully deleted", fileId);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting file {FileId}: {Error}", fileId, ex.Message);
                return false;
            }
        }

        public async Task<Stream?> GetFileStreamAsync(int fileId, int userId)
        {
            var file = await _context.AgentFiles
                .Include(f => f.Agent)
                .FirstOrDefaultAsync(f => f.Id == fileId && f.Agent.CreatedById == userId);

            if (file == null || !File.Exists(file.FilePath))
            {
                return null;
            }

            return new FileStream(file.FilePath, FileMode.Open, FileAccess.Read);
        }

        public async Task<bool> IndexFileAsync(int fileId)
        {
            var file = await _context.AgentFiles
                .Include(f => f.Agent)
                .FirstOrDefaultAsync(f => f.Id == fileId);

            if (file == null)
            {
                _logger.LogWarning("File not found for indexing: {FileId}", fileId);
                return false;
            }

            if (!File.Exists(file.FilePath))
            {
                _logger.LogError("Physical file not found for indexing: {FilePath}. Directory exists: {DirectoryExists}", 
                    file.FilePath, Directory.Exists(Path.GetDirectoryName(file.FilePath)));
                return false;
            }

            if (file.IsIndexed)
            {
                _logger.LogInformation("File {FileId} is already indexed", fileId);
                return true;
            }

            try
            {
                _logger.LogInformation("Starting RAG indexing for file {FileId} ({FileName}) for agent {AgentId}", 
                    fileId, file.FileName, file.AgentId);

                // Prepare metadata for the Python backend
                var metadata = new Dictionary<string, object>
                {
                    ["file_id"] = fileId,
                    ["original_filename"] = file.FileName,
                    ["content_type"] = file.ContentType,
                    ["file_size"] = file.FileSize,
                    ["uploaded_by"] = file.UploadedById,
                    ["uploaded_at"] = file.CreatedAt.ToString("O") // ISO 8601 format
                };

                // Send file to Python backend for RAG processing
                var uploadResult = await _runtimeClient.UploadFileForProcessingAsync(
                    file.FilePath, 
                    file.AgentId, 
                    metadata);

                if (uploadResult?.Success == true)
                {
                    // Update the database record
                    file.IsIndexed = true;
                    
                    // Store additional indexing information if available
                    if (uploadResult.Result != null)
                    {
                        _logger.LogInformation("Successfully indexed file {FileId} with {ChunksCreated} chunks. Document ID: {DocumentId}", 
                            fileId, uploadResult.Result.ChunksCreated, uploadResult.Result.DocumentId);
                        
                        // You could add a property to store the document ID if needed
                        // file.DocumentId = uploadResult.Result.DocumentId;
                    }
                    
                    await _context.SaveChangesAsync();
                    
                    _logger.LogInformation("File {FileId} successfully indexed and database updated", fileId);
                    return true;
                }
                else
                {
                    var errorMessage = uploadResult?.Error ?? "Unknown error during file processing";
                    _logger.LogError("Failed to index file {FileId}: {Error}", fileId, errorMessage);
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error indexing file {FileId}: {Error}", fileId, ex.Message);
                return false;
            }
        }

        public async Task<bool> ReindexAgentFilesAsync(int agentId, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                _logger.LogWarning("Agent not found for re-indexing: {AgentId}", agentId);
                return false;
            }

            try
            {
                _logger.LogInformation("Starting re-indexing for agent {AgentId}", agentId);

                // First, clear existing documents for this agent in the RAG system
                var clearResult = await _runtimeClient.DeleteAgentDocumentsAsync(agentId.ToString());
                if (!clearResult)
                {
                    _logger.LogWarning("Failed to clear existing documents for agent {AgentId}", agentId);
                }

                // Get all files for this agent
                var agentFiles = await _context.AgentFiles
                    .Where(f => f.AgentId == agentId)
                    .ToListAsync();

                if (!agentFiles.Any())
                {
                    _logger.LogInformation("No files found for agent {AgentId}", agentId);
                    return true;
                }

                // Reset indexing status
                foreach (var file in agentFiles)
                {
                    file.IsIndexed = false;
                }
                await _context.SaveChangesAsync();

                // Re-index all files
                var indexedCount = 0;
                foreach (var file in agentFiles)
                {
                    try
                    {
                        if (await IndexFileAsync(file.Id))
                        {
                            indexedCount++;
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Failed to re-index file {FileId} during agent re-indexing", file.Id);
                    }
                }

                _logger.LogInformation("Re-indexing completed for agent {AgentId}. Successfully indexed {IndexedCount}/{TotalCount} files", 
                    agentId, indexedCount, agentFiles.Count);

                return indexedCount > 0;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during agent re-indexing for agent {AgentId}: {Error}", agentId, ex.Message);
                return false;
            }
        }
    }
} 