using System.Security.Claims;
using AgentPlatform.API.Services;
using System.Net;

namespace AgentPlatform.API.Middleware
{
    public class SecurityStampValidatorMiddleware
    {
        private readonly RequestDelegate _next;

        public SecurityStampValidatorMiddleware(RequestDelegate next)
        {
            _next = next;
        }

        public async Task InvokeAsync(HttpContext context, IUserService userService)
        {
            if (context.User.Identity?.IsAuthenticated == true)
            {
                var userIdStr = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
                var securityStampStr = context.User.FindFirst("security_stamp")?.Value;

                if (int.TryParse(userIdStr, out var userId) && Guid.TryParse(securityStampStr, out var tokenSecurityStamp))
                {
                    var user = await userService.GetUserByIdAsync(userId);

                    if (user == null || user.SecurityStamp != tokenSecurityStamp)
                    {
                        context.Response.StatusCode = (int)HttpStatusCode.Unauthorized;
                        await context.Response.WriteAsync("Invalid token.");
                        return;
                    }
                }
            }

            await _next(context);
        }
    }
} 