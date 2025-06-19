using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using AgentPlatform.API.Services;

namespace AgentPlatform.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class FileController : ControllerBase
    {
        private readonly IFileService _fileService;

        public FileController(IFileService fileService)
        {
            _fileService = fileService;
        }

        [HttpPost("upload/{agentId}")]
        public async Task<ActionResult> UploadFile(int agentId, IFormFile file)
        {
            var userId = GetUserId();
            var result = await _fileService.UploadFileAsync(file, agentId, userId);
            
            var response = new 
            {
                file_id = result.FileId,
                filename = file.FileName,
                status = "processing",
                status_check_url = $"/api/file/status/{result.FileId}"
            };

            return Accepted(response);
        }

        [HttpGet("status/{fileId}")]
        public ActionResult GetFileStatus(string fileId)
        {
            // TODO: Implement status check logic
            // This would typically involve checking a database or a cache
            // to get the current indexing status of the file.
            var response = new 
            {
                file_id = fileId,
                status = "completed", // or "processing", "failed"
                message = "File indexed successfully. 15 chunks created.",
                error_details = (string)null!
            };
            return Ok(response);
        }

        [HttpDelete("{fileId}")]
        public async Task<ActionResult> DeleteFile(string fileId)
        {
            var userId = GetUserId();
            var success = await _fileService.DeleteFileAsync(fileId, userId);
            
            if (!success)
            {
                return NotFound();
            }

            return NoContent();
        }

        [HttpGet("{fileId}/download")]
        public async Task<ActionResult> DownloadFile(string fileId)
        {
            var userId = GetUserId();
            var stream = await _fileService.GetFileStreamAsync(fileId, userId);
            
            if (stream == null)
            {
                return NotFound();
            }

            // In a real S3 implementation, you would probably want to return a pre-signed URL
            // instead of streaming the file through the server.
            return File(stream, "application/octet-stream");
        }

        [HttpPost("{fileId}/index")]
        public async Task<ActionResult> IndexFile(string fileId)
        {
            var success = await _fileService.IndexFileAsync(fileId);
            
            if (!success)
            {
                return NotFound();
            }

            return Ok();
        }

        private int GetUserId()
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier);
            if (userIdClaim == null)
            {
                throw new UnauthorizedAccessException("Invalid user ID");
            }
            return int.Parse(userIdClaim.Value);
        }
    }
} 