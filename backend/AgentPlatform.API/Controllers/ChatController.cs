using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Services;

namespace AgentPlatform.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class ChatController : ControllerBase
    {
        private readonly IChatService _chatService;

        public ChatController(IChatService chatService)
        {
            _chatService = chatService;
        }

        [HttpPost("message")]
        public async Task<ActionResult<ChatResponseDto>> SendMessage([FromBody] SendMessageRequestDto request)
        {
            var userId = GetUserId();
            var response = await _chatService.SendMessageAsync(userId, request);
            return Ok(response);
        }

        [HttpGet("history")]
        public async Task<ActionResult<ChatHistoryDto>> GetChatHistory(
            [FromQuery] int page = 1, 
            [FromQuery] int pageSize = 10)
        {
            var userId = GetUserId();
            var history = await _chatService.GetChatHistoryAsync(userId, page, pageSize);
            return Ok(history);
        }

        [HttpGet("sessions/{sessionId}")]
        public async Task<ActionResult<ChatSessionDto>> GetChatSession(int sessionId)
        {
            var userId = GetUserId();
            var session = await _chatService.GetChatSessionAsync(userId, sessionId);
            
            if (session == null)
            {
                return NotFound();
            }

            return Ok(session);
        }

        [HttpDelete("sessions/{sessionId}")]
        public async Task<ActionResult> DeleteChatSession(int sessionId)
        {
            var userId = GetUserId();
            var success = await _chatService.DeleteChatSessionAsync(userId, sessionId);
            
            if (!success)
            {
                return NotFound();
            }

            return NoContent();
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