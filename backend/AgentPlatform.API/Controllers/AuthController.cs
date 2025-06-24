using Microsoft.AspNetCore.Mvc;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Services;

namespace AgentPlatform.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IUserService _userService;

        public AuthController(IUserService userService)
        {
            _userService = userService;
        }

        [HttpPost("login")]
        public async Task<ActionResult<AuthResponseDto>> Login([FromBody] LoginRequestDto loginRequest)
        {
            var response = await _userService.AuthenticateAsync(loginRequest);
            
            if (response == null)
            {
                return Unauthorized(new { message = "Invalid email or password" });
            }

            return Ok(response);
        }

        [HttpPost("register")]
        public async Task<ActionResult<AuthResponseDto>> Register([FromBody] RegisterRequestDto registerRequest)
        {
            var response = await _userService.RegisterAsync(registerRequest);
            
            if (response == null)
            {
                return BadRequest(new { message = "User with this email already exists" });
            }

            return CreatedAtAction(nameof(Register), response);
        }

        [HttpPost("external-login")]
        public async Task<ActionResult<AuthResponseDto>> ExternalLogin([FromBody] ExternalAuthDto externalAuth)
        {
            var response = await _userService.ExternalLoginAsync(externalAuth);
            
            if (response == null)
            {
                return Unauthorized(new { message = "Invalid external authentication" });
            }

            return Ok(response);
        }
    }
} 