using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using BCrypt.Net;
using AutoMapper;

namespace AgentPlatform.API.Services
{
    public class UserService : IUserService
    {
        private readonly ApplicationDbContext _context;
        private readonly IJwtService _jwtService;
        private readonly IMapper _mapper;

        public UserService(ApplicationDbContext context, IJwtService jwtService, IMapper mapper)
        {
            _context = context;
            _jwtService = jwtService;
            _mapper = mapper;
        }

        public async Task<AuthResponseDto?> AuthenticateAsync(LoginRequestDto loginRequest)
        {
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == loginRequest.Email && u.IsActive);

            if (user == null || !BCrypt.Net.BCrypt.Verify(loginRequest.Password, user.PasswordHash))
            {
                return null;
            }

            var token = _jwtService.GenerateToken(user);
            var userDto = _mapper.Map<UserDto>(user);

            return new AuthResponseDto
            {
                Token = token,
                ExpiresAt = _jwtService.GetTokenExpiration(),
                User = userDto
            };
        }

        public async Task<AuthResponseDto?> RegisterAsync(RegisterRequestDto registerRequest)
        {
            if (await _context.Users.AnyAsync(u => u.Email == registerRequest.Email))
            {
                return null; // User already exists
            }

            var user = new User
            {
                Email = registerRequest.Email,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(registerRequest.Password),
                FirstName = registerRequest.FirstName,
                LastName = registerRequest.LastName,
                Department = registerRequest.Department,
                CreatedAt = DateTime.UtcNow
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            var token = _jwtService.GenerateToken(user);
            var userDto = _mapper.Map<UserDto>(user);

            return new AuthResponseDto
            {
                Token = token,
                ExpiresAt = _jwtService.GetTokenExpiration(),
                User = userDto
            };
        }

        public async Task<User?> GetUserByIdAsync(int userId)
        {
            return await _context.Users
                .FirstOrDefaultAsync(u => u.Id == userId && u.IsActive);
        }

        public async Task<User?> GetUserByEmailAsync(string email)
        {
            return await _context.Users
                .FirstOrDefaultAsync(u => u.Email == email && u.IsActive);
        }
    }
} 