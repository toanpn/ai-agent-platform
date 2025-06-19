namespace AgentPlatform.API.Services
{
    public interface IFileService
    {
        Task<FileUploadResult> UploadFileAsync(IFormFile file, int agentId, int userId);
        Task<bool> DeleteFileAsync(string fileId, int userId);
        Task<Stream?> GetFileStreamAsync(string fileId, int userId);
        Task<bool> IndexFileAsync(string fileId);
    }
}