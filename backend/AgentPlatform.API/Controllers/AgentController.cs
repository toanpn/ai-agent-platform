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
        private readonly IToolService _toolService;

        public AgentController(IAgentService agentService, IToolService toolService)
        {
            _agentService = agentService;
            _toolService = toolService;
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
        
        [HttpPost("{id}/tools")]
        public async Task<ActionResult> SetTools(int id, [FromBody] SetToolsRequestDto request)
        {
            var userId = GetUserId();
            var success = await _agentService.SetAgentToolsAsync(id, request.Tools, userId);
            if (!success)
            {
                return NotFound();
            }

            return Ok(new { message = "Tools have been set successfully" });
        }

        [HttpGet("{id}/tools")]
        public async Task<ActionResult<List<string>>> GetTools(int id)
        {
            var userId = GetUserId();
            var tools = await _agentService.GetAgentToolsAsync(id, userId);
            if (tools == null)
            {
                return NotFound();
            }
            return Ok(tools);
        }

        [HttpGet("{agentId}/tools/config")]
        public async Task<IActionResult> GetToolConfigs(int agentId)
        {
            var userId = GetUserId();
            var toolConfigs = await _toolService.GetAgentToolConfigsAsync(agentId, userId);
            return Ok(toolConfigs);
        }

        [HttpPost("{agentId}/tools/config")]
        public async Task<IActionResult> AddToolConfig(int agentId, [FromBody] CreateToolConfigDto toolConfigDto)
        {
            if (agentId != toolConfigDto.AgentId)
            {
                return BadRequest("Agent ID in URL must match Agent ID in body.");
            }
            var userId = GetUserId();
            var newToolConfig = await _toolService.AddToolConfigAsync(toolConfigDto, userId);
            // Returning a 201 Created with a route to get the single resource is a bit tricky here
            // because we don't have a "GetToolConfig(id)" endpoint on this controller.
            // Returning the object is a pragmatic choice.
            return Created($"api/agents/{agentId}/tools/config", newToolConfig);
        }

        [HttpPut("{agentId}/tools/config/{configId}")]
        public async Task<IActionResult> UpdateToolConfig(int agentId, int configId, [FromBody] UpdateToolConfigDto toolConfigDto)
        {
            var userId = GetUserId();
            var success = await _toolService.UpdateToolConfigAsync(configId, toolConfigDto, agentId, userId);
            if (!success)
            {
                return NotFound();
            }
            return NoContent();
        }

        [HttpDelete("{agentId}/tools/config/{configId}")]
        public async Task<IActionResult> DeleteToolConfig(int agentId, int configId)
        {
            var userId = GetUserId();
            var success = await _toolService.DeleteToolConfigAsync(configId, agentId, userId);
            if (!success)
            {
                return NotFound();
            }
            return NoContent();
        }
    }
} 