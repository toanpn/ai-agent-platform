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


            // Create ADK-powered agent with multi-tool capabilities
            var adkAgent = new Agent
            {
                Name = "ADK Assistant",
                Department = "AI Research",
                Description = "An advanced AI assistant powered by Google ADK with multi-tool capabilities and workflow orchestration",
                Instructions = @"You are an advanced AI assistant powered by Google's Agent Development Kit (ADK). 
You have access to multiple tools and can orchestrate complex workflows:
- Use built-in SearchTool for web searches
- Leverage HttpTool for API interactions
- Coordinate multi-step tasks using sequential or parallel workflows
- Provide comprehensive research and analysis capabilities

Always explain your reasoning and cite sources when providing information. 
You can break down complex requests into multiple tool calls and synthesize results.",
                IsActive = true,
                IsMainRouter = false,
                CreatedById = adminUser.Id,
                CreatedAt = DateTime.UtcNow
            };

            context.Agents.Add(adkAgent);
            await context.SaveChangesAsync();

            // Add ADK SearchTool function
            var adkSearchFunction = new AgentFunction
            {
                AgentId = adkAgent.Id,
                Name = "adk_search",
                Description = "Advanced web search using Google ADK's built-in SearchTool with enhanced capabilities",
                Schema = @"{
                    ""type"": ""object"",
                    ""properties"": {
                        ""query"": {""type"": ""string"", ""description"": ""Search query text""},
                        ""max_results"": {""type"": ""integer"", ""description"": ""Maximum number of results to return (1-20)"", ""default"": 10},
                        ""include_snippets"": {""type"": ""boolean"", ""description"": ""Include content snippets in results"", ""default"": true},
                        ""filter_domains"": {""type"": ""array"", ""items"": {""type"": ""string""}, ""description"": ""Optional domain filters""}
                    },
                    ""required"": [""query""]
                }",
                EndpointUrl = null,
                HttpMethod = "POST",
                Headers = null,
                IsActive = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            context.AgentFunctions.Add(adkSearchFunction);

            // Add ADK HttpTool function for API interactions
            var adkHttpFunction = new AgentFunction
            {
                AgentId = adkAgent.Id,
                Name = "adk_http_request",
                Description = "Make HTTP requests to external APIs using ADK's HttpTool",
                Schema = @"{
                    ""type"": ""object"",
                    ""properties"": {
                        ""url"": {""type"": ""string"", ""description"": ""Target URL for the HTTP request""},
                        ""method"": {""type"": ""string"", ""enum"": [""GET"", ""POST"", ""PUT"", ""DELETE""], ""default"": ""GET""},
                        ""headers"": {""type"": ""object"", ""description"": ""HTTP headers as key-value pairs""},
                        ""body"": {""type"": ""object"", ""description"": ""Request body for POST/PUT requests""},
                        ""timeout"": {""type"": ""integer"", ""description"": ""Request timeout in seconds"", ""default"": 30}
                    },
                    ""required"": [""url""]
                }",
                EndpointUrl = null,
                HttpMethod = "POST",
                Headers = null,
                IsActive = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            context.AgentFunctions.Add(adkHttpFunction);

            // Add ADK Workflow orchestration function
            var adkWorkflowFunction = new AgentFunction
            {
                AgentId = adkAgent.Id,
                Name = "adk_workflow",
                Description = "Execute multi-agent workflows (sequential, parallel, or loop) using ADK orchestration",
                Schema = @"{
                    ""type"": ""object"",
                    ""properties"": {
                        ""workflow_type"": {""type"": ""string"", ""enum"": [""sequential"", ""parallel"", ""loop""], ""description"": ""Type of workflow to execute""},
                        ""agents"": {""type"": ""array"", ""items"": {""type"": ""string""}, ""description"": ""List of agent names to include in workflow""},
                        ""task"": {""type"": ""string"", ""description"": ""Task description for the workflow""},
                        ""max_iterations"": {""type"": ""integer"", ""description"": ""Maximum iterations for loop workflows"", ""default"": 3}
                    },
                    ""required"": [""workflow_type"", ""agents"", ""task""]
                }",
                EndpointUrl = null,
                HttpMethod = "POST",
                Headers = null,
                IsActive = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            context.AgentFunctions.Add(adkWorkflowFunction);
            await context.SaveChangesAsync();
        }
    }
} 