using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using AutoMapper;
using Google.Apis.Auth;

namespace AgentPlatform.API.Services
{
    public class UserService : IUserService
    {
        private readonly ApplicationDbContext _context;
        private readonly IJwtService _jwtService;
        private readonly IMapper _mapper;
        private readonly IConfiguration _configuration;

        public UserService(ApplicationDbContext context, IJwtService jwtService, IMapper mapper, IConfiguration configuration)
        {
            _context = context;
            _jwtService = jwtService;
            _mapper = mapper;
            _configuration = configuration;
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

        public async Task<AuthResponseDto?> ExternalLoginAsync(ExternalAuthDto externalAuth)
        {
            try
            {
                var settings = new GoogleJsonWebSignature.ValidationSettings()
                {
                    Audience = [_configuration["Authentication:Google:ClientId"]]
                };

                var payload = await GoogleJsonWebSignature.ValidateAsync(externalAuth.IdToken, settings);

                // Find existing user by email
                var user = await GetUserByEmailAsync(payload.Email);

                if (user == null)
                {
                    // Create a new user if they don't exist
                    user = new User
                    {
                        Email = payload.Email,
                        PasswordHash = string.Empty, // External users don't have passwords
                        FirstName = payload.GivenName,
                        LastName = payload.FamilyName,
                        CreatedAt = DateTime.UtcNow,
                        IsActive = true
                    };

                    _context.Users.Add(user);
                    await _context.SaveChangesAsync();
                }

                // Generate application-specific JWT
                var token = _jwtService.GenerateToken(user);
                var userDto = _mapper.Map<UserDto>(user);

                return new AuthResponseDto
                {
                    Token = token,
                    ExpiresAt = _jwtService.GetTokenExpiration(),
                    User = userDto
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"External login error: {ex.Message}");
                return null;
            }
        }
    }
} 