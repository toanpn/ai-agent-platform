using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using AgentPlatform.API.Services;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class ToolController : ControllerBase
    {
        private readonly IToolService _toolService;

        public ToolController(IToolService toolService)
        {
            _toolService = toolService;
        }

        [HttpGet]
        public async Task<ActionResult<List<ToolDto>>> GetTools()
        {
            var tools = await _toolService.GetToolsAsync();
            return Ok(tools);
        }
    }
}