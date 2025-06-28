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

        [HttpGet("tools-json")]
        [AllowAnonymous]
        public async Task<ActionResult> GetToolsJson()
        {
            try
            {
                var toolsJson = await _toolService.GetToolsJsonContentAsync();
                return Content(toolsJson, "application/json");
            }
            catch (FileNotFoundException ex)
            {
                return NotFound(new { 
                    message = "Tools JSON file not found",
                    details = ex.Message,
                    suggestion = "Please ensure the AgentPlatform.Core toolkit/tools.json file exists and is accessible",
                    timestamp = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { 
                    message = $"Error reading tools JSON: {ex.Message}",
                    timestamp = DateTime.UtcNow
                });
            }
        }
    }
}