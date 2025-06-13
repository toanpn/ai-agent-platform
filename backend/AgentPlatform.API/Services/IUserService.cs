using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;

namespace AgentPlatform.API.Services
{
    public interface IUserService
    {
        Task<AuthResponseDto?> AuthenticateAsync(LoginRequestDto loginRequest);
        Task<AuthResponseDto?> RegisterAsync(RegisterRequestDto registerRequest);
        Task<User?> GetUserByIdAsync(int userId);
        Task<User?> GetUserByEmailAsync(string email);
    }
} 