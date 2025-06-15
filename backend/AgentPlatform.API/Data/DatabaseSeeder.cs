using AgentPlatform.API.Models;
using BCrypt.Net;

namespace AgentPlatform.API.Data
{
    public static class DatabaseSeeder
    {
        public static async Task SeedAsync(ApplicationDbContext context)
        {
            // Ensure database is created
            await context.Database.EnsureCreatedAsync();

            // Check if we already have users
            if (context.Users.Any())
            {
                return; // Database has been seeded
            }

            // Create default admin user
            var adminUser = new User
            {
                Email = "admin@kiotviet.com",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
                FirstName = "Admin",
                LastName = "User",
                Department = "IT",
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            };

            context.Users.Add(adminUser);
            await context.SaveChangesAsync();

            // Create default demo agent
            var demoAgent = new Agent
            {
                Name = "Demo Assistant",
                Department = "General",
                Description = "A general-purpose AI assistant for demonstration purposes",
                Instructions = "You are a helpful AI assistant. Respond to user queries politely and informatively.",
                IsActive = true,
                IsMainRouter = true,
                CreatedById = adminUser.Id,
                CreatedAt = DateTime.UtcNow
            };

            context.Agents.Add(demoAgent);
            await context.SaveChangesAsync();
        }
    }
} 