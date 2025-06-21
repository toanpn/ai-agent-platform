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
    public class AgentController : ControllerBase
    {
        private readonly IAgentService _agentService;

        public AgentController(IAgentService agentService)
        {
            _agentService = agentService;
        }

        [HttpGet]
        public async Task<ActionResult<List<AgentDto>>> GetAgents()
        {
            var userId = GetUserId();
            var agents = await _agentService.GetAgentsAsync(userId);
            return Ok(agents);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<AgentDto>> GetAgent(int id)
        {
            var userId = GetUserId();
            var agent = await _agentService.GetAgentByIdAsync(id, userId);
            
            if (agent == null)
            {
                return NotFound();
            }

            return Ok(agent);
        }

        [HttpPost]
        public async Task<ActionResult<AgentDto>> CreateAgent([FromBody] CreateAgentRequestDto request)
        {
            var userId = GetUserId();
            var agent = await _agentService.CreateAgentAsync(request, userId);
            return CreatedAtAction(nameof(GetAgent), new { id = agent.Id }, agent);
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<AgentDto>> UpdateAgent(int id, [FromBody] UpdateAgentRequestDto request)
        {
            var userId = GetUserId();
            var agent = await _agentService.UpdateAgentAsync(id, request, userId);
            
            if (agent == null)
            {
                return NotFound();
            }

            return Ok(agent);
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteAgent(int id)
        {
            var userId = GetUserId();
            var success = await _agentService.DeleteAgentAsync(id, userId);
            
            if (!success)
            {
                return NotFound();
            }

            return NoContent();
        }

        [HttpPost("{id}/functions")]
        public async Task<ActionResult> AddFunction(int id, [FromBody] CreateAgentFunctionRequestDto request)
        {
            var userId = GetUserId();
            var success = await _agentService.AddFunctionToAgentAsync(id, request, userId);
            
            if (!success)
            {
                return NotFound();
            }

            return Ok();
        }

        [HttpPost("sync-json")]
        public async Task<ActionResult> SyncAgentsJson()
        {
            await _agentService.SyncAgentsJsonAsync();
            return Ok(new { message = "Agents JSON synchronized successfully" });
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