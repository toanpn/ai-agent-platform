using Amazon.S3;
using Amazon.S3.Model;

namespace AgentPlatform.API.Services
{
    public class S3FileStorageService : IFileStorageService
    {
        private readonly IAmazonS3 _s3Client;
        private readonly string _bucketName;
        private readonly IConfiguration _configuration;

        public S3FileStorageService(IAmazonS3 s3Client, IConfiguration configuration)
        {
            _s3Client = s3Client;
            _configuration = configuration;
            _bucketName = _configuration["AWS:S3:BucketName"] ?? throw new InvalidOperationException("S3 bucket name is not configured.");
        }

        public async Task<FileUploadResult> UploadFileAsync(IFormFile file, int agentId, int uploaderUserId)
        {
            var fileId = Guid.NewGuid();
            var originalFilename = file.FileName;
            var objectKey = $"{agentId}/{fileId}/{originalFilename}";

            await using var stream = file.OpenReadStream();

            var putRequest = new PutObjectRequest
            {
                BucketName = _bucketName,
                Key = objectKey,
                InputStream = stream,
                ContentType = file.ContentType,
                Metadata =
                {
                    ["file_id"] = fileId.ToString(),
                    ["agent_id"] = agentId.ToString(),
                    ["uploaded_by_user_id"] = uploaderUserId.ToString()
                }
            };

            await _s3Client.PutObjectAsync(putRequest);

            // In a real application, you might want to return a full S3 URI or just the key
            return new FileUploadResult
            {
                FileId = fileId,
                FilePath = objectKey 
            };
        }
    }
} 