using AgentPlatform.API.Common;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AgentPlatform.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class ToolController : ControllerBase
    {
        public ToolController()
        {
        }

        [HttpGet]
        public IActionResult GetTools()
        {
            var tools = ToolConst.Tools();
            return Ok(tools);
        }
    }
}