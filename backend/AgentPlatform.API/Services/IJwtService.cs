using AgentPlatform.API.Models;

namespace AgentPlatform.API.Services
{
    public interface IJwtService
    {
        string GenerateToken(User user);
        DateTime GetTokenExpiration();
    }
} 