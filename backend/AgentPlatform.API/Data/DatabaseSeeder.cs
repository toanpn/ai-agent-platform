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

            // Create agents based on agents.json structure
            var agents = new List<Agent>
            {
                new Agent
                {
                    Name = "IT_Support_Agent",
                    Department = "IT",
                    Description = "Useful for resolving technical support requests, troubleshooting software and hardware issues, and handling Jira-related problems. The input must be a complete question.",
                    Instructions = "You are an IT support specialist. Help users with technical issues, troubleshoot problems, and create Jira tickets when needed.",
                    ToolsArray = new[] { "jira_ticket_creator", "it_knowledge_base_search" },
                    LlmModelName = "gemini-2.0-flash",
                    LlmTemperature = 0.0,
                    IsActive = true,
                    IsMainRouter = false,
                    CreatedById = adminUser.Id,
                    CreatedAt = DateTime.UtcNow
                },
                new Agent
                {
                    Name = "HR_Agent",
                    Department = "HR", 
                    Description = "Useful for questions about HR policies, leave procedures, and recruitment information. The input must be a complete question.",
                    Instructions = "You are an HR assistant. Help employees with HR policies, leave requests, and recruitment-related questions.",
                    ToolsArray = new[] { "policy_document_search", "leave_request_tool" },
                    LlmModelName = "gemini-2.0-flash",
                    LlmTemperature = 0.7,
                    IsActive = true,
                    IsMainRouter = false,
                    CreatedById = adminUser.Id,
                    CreatedAt = DateTime.UtcNow
                },
                new Agent
                {
                    Name = "Search_Agent",
                    Department = "General",
                    Description = "Useful for searching for general information on the Internet using Google search. Use this agent when you need to find current information, news, guides, or answers to general questions that require web search.",
                    Instructions = "You are a search specialist. Use Google search to find current information, news, guides, and answers to general questions.",
                    ToolsArray = new[] { "google_search" },
                    LlmModelName = "gemini-2.0-flash",
                    LlmTemperature = 0.5,
                    IsActive = true,
                    IsMainRouter = false,
                    CreatedById = adminUser.Id,
                    CreatedAt = DateTime.UtcNow
                },
                new Agent
                {
                    Name = "Personal_Assistant_Agent",
                    Department = "General",
                    Description = "Useful for personal assistance tasks like checking calendar events, weather information, and scheduling. Use this agent when users need help with daily planning, meeting schedules, or weather updates.",
                    Instructions = "You are a personal assistant. Help users with calendar management, weather information, and daily planning tasks.",
                    ToolsArray = new[] { "check_calendar", "check_weather" },
                    LlmModelName = "gemini-2.0-flash",
                    LlmTemperature = 0.3,
                    IsActive = true,
                    IsMainRouter = false,
                    CreatedById = adminUser.Id,
                    CreatedAt = DateTime.UtcNow
                },
                new Agent
                {
                    Name = "General_Utility_Agent",
                    Department = "General",
                    Description = "A versatile agent that can handle various utility tasks including web searches, calendar checks, and weather information. Use this as a fallback when other agents don't match the request.",
                    Instructions = "You are a versatile utility agent. Handle various tasks including web searches, calendar management, and weather information as a fallback option.",
                    ToolsArray = new[] { "google_search", "check_calendar", "check_weather" },
                    LlmModelName = "gemini-2.0-flash",
                    LlmTemperature = 0.4,
                    IsActive = true,
                    IsMainRouter = true, // Set this as main router
                    CreatedById = adminUser.Id,
                    CreatedAt = DateTime.UtcNow
                }
            };

            context.Agents.AddRange(agents);
            await context.SaveChangesAsync();

            // Keep the ADK-powered agent with multi-tool capabilities for demonstration
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
                ToolsArray = new[] { "adk_search", "adk_http_request", "adk_workflow" },
                LlmModelName = "gemini-2.0-flash",
                LlmTemperature = 0.2,
                IsActive = true,
                IsMainRouter = false,
                CreatedById = adminUser.Id,
                CreatedAt = DateTime.UtcNow
            };

            context.Agents.Add(adkAgent);
            await context.SaveChangesAsync();

            // Add ADK functions for the ADK agent
            await AddAdkFunctions(context, adkAgent.Id);

            // Seed available tools
            await AddTools(context);
        }

        private static async Task AddTools(ApplicationDbContext context)
        {
            var toolNames = new Dictionary<string, string>
                {
                    { "jira_ticket_creator", "Creates a Jira ticket for technical support issues." },
                    { "it_knowledge_base_search", "Searches the IT knowledge base for solutions." },
                    { "policy_document_search", "Searches for HR policy documents." },
                    { "leave_request_tool", "Handles leave requests and procedures." },
                    { "google_search", "Performs a Google search for general information." },
                    { "check_calendar", "Checks for calendar events and schedules." },
                    { "check_weather", "Checks the current weather information." },
                    { "adk_search", "Advanced web search using Google ADK." },
                    { "adk_http_request", "Makes HTTP requests to external APIs." },
                    { "adk_workflow", "Executes multi-agent workflows." }
                };

            var tools = toolNames.Select(t => new Tool { Name = t.Key, Description = t.Value }).ToList();
            context.Tools.AddRange(tools);
            await context.SaveChangesAsync();
        }

        private static async Task AddAdkFunctions(ApplicationDbContext context, int agentId)
        {
            var functions = new List<AgentFunction>
            {
                new AgentFunction
                {
                    AgentId = agentId,
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
                },
                new AgentFunction
                {
                    AgentId = agentId,
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
                },
                new AgentFunction
                {
                    AgentId = agentId,
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
                }
            };

            context.AgentFunctions.AddRange(functions);
            await context.SaveChangesAsync();
        }
    }
} 