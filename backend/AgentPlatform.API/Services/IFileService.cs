namespace AgentPlatform.API.Services
{
    public interface IFileService
    {
        Task<string> UploadFileAsync(IFormFile file, int agentId, int userId);
        Task<bool> DeleteFileAsync(int fileId, int userId);
        Task<Stream?> GetFileStreamAsync(int fileId, int userId);
        Task<bool> IndexFileAsync(int fileId);
        Task<bool> ReindexAgentFilesAsync(int agentId, int userId);
    }
}