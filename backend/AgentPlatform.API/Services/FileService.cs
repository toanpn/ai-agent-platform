using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Data;
using AgentPlatform.API.Models;

namespace AgentPlatform.API.Services
{
    public class FileService : IFileService
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;
        private readonly string _basePath;

        public FileService(ApplicationDbContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;
            _basePath = _configuration["FileStorage:BasePath"] ?? "./uploads";
            
            // Ensure upload directory exists
            Directory.CreateDirectory(_basePath);
        }

        public async Task<string> UploadFileAsync(IFormFile file, int agentId, int userId)
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

            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            var agentFile = new AgentFile
            {
                AgentId = agentId,
                FileName = file.FileName,
                FilePath = filePath,
                ContentType = file.ContentType,
                FileSize = file.Length,
                UploadedById = userId,
                CreatedAt = DateTime.UtcNow
            };

            _context.AgentFiles.Add(agentFile);
            await _context.SaveChangesAsync();

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

            // Delete physical file
            if (File.Exists(file.FilePath))
            {
                File.Delete(file.FilePath);
            }

            _context.AgentFiles.Remove(file);
            await _context.SaveChangesAsync();

            return true;
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
                .FirstOrDefaultAsync(f => f.Id == fileId);

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