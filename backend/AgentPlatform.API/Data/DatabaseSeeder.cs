using AgentPlatform.API.Models;
using BCrypt.Net;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System;
using Microsoft.EntityFrameworkCore;
using System.Text.Json.Serialization;

namespace AgentPlatform.API.Data
{
    public static class DatabaseSeeder
    {
        private class AgentJson
        {
            [JsonPropertyName("agent_name")]
            public string Name { get; set; }

            [JsonPropertyName("description")]
            public string Description { get; set; }

            [JsonPropertyName("tools")]
            public string[] Tools { get; set; }

            [JsonPropertyName("tool_configs")]
            public JsonElement ToolConfigs { get; set; }

            [JsonPropertyName("llm_config")]
            public LlmConfigJson LlmConfig { get; set; }
        }

        private class LlmConfigJson
        {
            [JsonPropertyName("model_name")]
            public string ModelName { get; set; }

            [JsonPropertyName("temperature")]
            public double Temperature { get; set; }
        }

        private class ToolJson
        {
            [JsonPropertyName("name")]
            public string Name { get; set; }

            [JsonPropertyName("description")]
            public string Description { get; set; }
        }

        public static async Task SeedAsync(ApplicationDbContext context)
        {
            // Ensure database is created
            await context.Database.EnsureCreatedAsync();

            // Seed User
            var adminUser = await SeedUser(context);

            // Seed Agents
            await SeedAgents(context, adminUser);
        }

        private static async Task<User> SeedUser(ApplicationDbContext context)
        {
            if (await context.Users.AnyAsync())
            {
                return await context.Users.FirstAsync(u => u.Email == "admin@kiotviet.com");
            }

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
            return adminUser;
        }

        private static async Task SeedAgents(ApplicationDbContext context, User adminUser)
        {
            if (await context.Agents.AnyAsync())
            {
                return; // Agents have been seeded
            }

            var agentsJsonPath = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "AgentPlatform.Core", "agents.json");
            if (!File.Exists(agentsJsonPath))
            {
                // Handle case where file doesn't exist, maybe log an error
                return;
            }

            var agentsJson = await File.ReadAllTextAsync(agentsJsonPath);
            var agentList = JsonSerializer.Deserialize<List<AgentJson>>(agentsJson);

            if (agentList != null)
            {
                foreach (var agentDef in agentList)
                {
                    var agent = new Agent
                    {
                        Name = agentDef.Name,
                        Description = agentDef.Description,
                        Instructions = agentDef.Description, // Using description as instruction
                        ToolsArray = agentDef.Tools,
                        LlmModelName = agentDef.LlmConfig.ModelName,
                        LlmTemperature = agentDef.LlmConfig.Temperature,
                        ToolConfigs = agentDef.ToolConfigs.GetRawText(),
                        IsActive = true,
                        IsMainRouter = false, // Set a default, can be adjusted if logic is provided
                        CreatedById = adminUser.Id,
                        CreatedAt = DateTime.UtcNow,
                        Department = GetDepartmentFromName(agentDef.Name)
                    };
                    context.Agents.Add(agent);
                }
                await context.SaveChangesAsync();
            }
        }

        private static string GetDepartmentFromName(string agentName)
        {
            if (string.IsNullOrEmpty(agentName)) return "General";
            
            var parts = agentName.Split('_');
            if (parts.Length > 1)
            {
                return parts[0];
            }
            return "General";
        }
    }
} 