using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Data;
using AgentPlatform.API.Models;

namespace AgentPlatform.API.Services
{
    public class FileService : IFileService
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;
        private readonly IFileStorageService _fileStorageService;

        public FileService(ApplicationDbContext context, IConfiguration configuration, IFileStorageService fileStorageService)
        {
            _context = context;
            _configuration = configuration;
            _fileStorageService = fileStorageService;
        }

        public async Task<FileUploadResult> UploadFileAsync(IFormFile file, int agentId, int userId)
        {
            if (file == null || file.Length == 0)
            {
                throw new ArgumentException("File is required");
            }

            var maxSizeMB = int.Parse(_configuration["FileStorage:MaxFileSizeMB"] ?? "50");
            if (file.Length > maxSizeMB * 1024 * 1024)
            {
                throw new ArgumentException($"File size exceeds maximum allowed size of {maxSizeMB}MB");
            }

            var uploadResult = await _fileStorageService.UploadFileAsync(file, agentId, userId);

            var agentFile = new AgentFile
            {
                FileId = uploadResult.FileId,
                AgentId = agentId,   
                FileName = file.FileName,
                FilePath = uploadResult.FilePath,
                ContentType = file.ContentType,
                FileSize = file.Length,
                UploadedById = userId,
                CreatedAt = DateTime.UtcNow
            };

            _context.AgentFiles.Add(agentFile);
            await _context.SaveChangesAsync();

            return uploadResult;
        }

        public async Task<bool> DeleteFileAsync(string fileId, int userId)
        {
            // parse file id
            if (!Guid.TryParse(fileId, out var fileIdGuid))
            {
                return false;
            }

            // The userId check here is simplified. In a real app, you'd have more robust authorization.
            var file = await _context.AgentFiles
                .FirstOrDefaultAsync(f => f.FileId == fileIdGuid && f.Agent.CreatedById == userId);

            if (file == null)
            {
                return false;
            } 

            // This part will need to be updated to use IFileStorageService to delete from S3
            // For now, it's out of scope of the current task
            if (File.Exists(file.FilePath))
            {
                File.Delete(file.FilePath);
            }

            _context.AgentFiles.Remove(file);
            await _context.SaveChangesAsync();

            return true;
        }

        public async Task<Stream?> GetFileStreamAsync(string fileId, int userId)
        {
            // parse file id
            if (!Guid.TryParse(fileId, out var fileIdGuid))
            {
                return null;
            }

            // The userId check here is simplified. In a real app, you'd have more robust authorization.
            var file = await _context.AgentFiles
                .FirstOrDefaultAsync(f => f.FileId == fileIdGuid && f.UploadedById == userId);

            if (file == null)
            {
                return null;
            }

            // This part will need to be updated to use IFileStorageService to download from S3
            // For now, it's out of scope of the current task
            if (!File.Exists(file.FilePath))
            {
                return null;
            }

            return new FileStream(file.FilePath, FileMode.Open, FileAccess.Read);
        }

        public async Task<bool> IndexFileAsync(string fileId)
        {
            if (!Guid.TryParse(fileId, out var fileIdGuid))
            {
                return false;
            }

            // parse file id
            var file = await _context.AgentFiles
                .FirstOrDefaultAsync(f => f.FileId == fileIdGuid);

            if (file == null)
            {
                return false;
            }

            // TODO: Implement actual file indexing for RAG
            // This would typically involve:
            // 1. Reading file content
            // 2. Chunking the content
            // 3. Creating embeddings
            // 4. Storing in vector database

            file.IsIndexed = true;
            await _context.SaveChangesAsync();

            return true;
        }
    }
} 