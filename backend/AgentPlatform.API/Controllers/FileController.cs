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
        public async Task<ActionResult<string>> UploadFile(int agentId, IFormFile file)
        {
            var userId = GetUserId();
            var filePath = await _fileService.UploadFileAsync(file, agentId, userId);
            return Ok(new { filePath });
        }

        [HttpDelete("{fileId}")]
        public async Task<ActionResult> DeleteFile(int fileId)
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
        public async Task<ActionResult> DownloadFile(int fileId)
        {
            var userId = GetUserId();
            var stream = await _fileService.GetFileStreamAsync(fileId, userId);
            
            if (stream == null)
            {
                return NotFound();
            }

            return File(stream, "application/octet-stream");
        }

        [HttpPost("{fileId}/index")]
        public async Task<ActionResult> IndexFile(int fileId)
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
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out var userId))
            {
                throw new UnauthorizedAccessException("Invalid user ID");
            }
            return userId;
        }
    }
} 