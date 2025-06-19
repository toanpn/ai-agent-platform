namespace AgentPlatform.API.Services
{
    public class FileUploadResult
    {
        public Guid FileId { get; set; }
        public string FilePath { get; set; } = string.Empty;
    }

    public interface IFileStorageService
    {
        Task<FileUploadResult> UploadFileAsync(IFormFile file, int agentId, int userId);
    }
} 