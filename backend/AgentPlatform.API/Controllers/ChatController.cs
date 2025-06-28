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

        /// <summary>
        /// Send a message to the agent system and receive an enhanced response
        /// </summary>
        /// <param name="request">The message request containing the message text and optional session/agent information</param>
        /// <returns>
        /// Enhanced chat response with comprehensive information including:
        /// - Main response from the appropriate agent
        /// - List of agents used during execution
        /// - List of tools used during execution  
        /// - Complete list of available sub-agents in the master agent system
        /// - List of available tools with descriptions
        /// - Detailed execution steps showing the agent routing and tool usage
        /// - Session information and metadata
        /// </returns>
        /// <response code="200">Returns the enhanced chat response with execution details, list of available sub-agents, and tools</response>
        /// <response code="400">If the request is invalid</response>
        /// <response code="500">If there's an error processing the message</response>
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

        [HttpGet("history/search")]
        public async Task<ActionResult<ChatHistoryDto>> SearchChatHistory(
            [FromQuery] string query,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var userId = GetUserId();
            var history = await _chatService.SearchChatHistoryAsync(userId, query, page, pageSize);
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

        [HttpPost("enhance-prompt")]
        public async Task<ActionResult<PromptEnhancementResponseDto>> EnhancePrompt([FromBody] EnhancePromptRequestDto request)
        {
            var enhancedPrompt = await _chatService.EnhancePromptAsync(request.Message);
            if (enhancedPrompt == null)
            {
                return BadRequest("Failed to enhance prompt.");
            }

            return Ok(new { enhancedPrompt });
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