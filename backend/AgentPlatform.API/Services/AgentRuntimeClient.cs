using System.Text;
using System.Text.Json;
using AgentPlatform.Shared.Models;

namespace AgentPlatform.API.Services
{
    public class AgentRuntimeClient : IAgentRuntimeClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<AgentRuntimeClient> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public AgentRuntimeClient(HttpClient httpClient, IConfiguration configuration, ILogger<AgentRuntimeClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
            
            var baseUrl = configuration["AgentRuntime:BaseUrl"] ?? "http://localhost:5001";
            _httpClient.BaseAddress = new Uri(baseUrl);
            
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };
        }

        public async Task<AgentRuntimeResponse> SendMessageAsync(AgentRuntimeRequest request)
        {
            try
            {
                _logger.LogInformation("Sending request to runtime service at {BaseUrl}", _httpClient.BaseAddress);
                
                var json = JsonSerializer.Serialize(request, _jsonOptions);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                _logger.LogDebug("Request payload: {Request}", json);
                
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                var response = await _httpClient.PostAsync("/api/chat", content);
                stopwatch.Stop();
                
                _logger.LogInformation("Runtime service responded in {ElapsedMs}ms with status {StatusCode}", 
                    stopwatch.ElapsedMilliseconds, response.StatusCode);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Runtime service returned error: {StatusCode}, Content: {Content}", 
                        response.StatusCode, errorContent);
                    
                    return new AgentRuntimeResponse
                    {
                        Success = false,
                        Error = $"Runtime service returned error: {response.StatusCode}",
                        Response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
                    };
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                
                // The Python backend returns a different structure, so we need to parse it correctly
                using var document = JsonDocument.Parse(responseJson);
                var root = document.RootElement;
                
                var result = new AgentRuntimeResponse
                {
                    Success = root.TryGetProperty("success", out var successProp) && successProp.GetBoolean(),
                    Response = GetStringProperty(root, "response") ?? "",
                    AgentName = GetStringProperty(root, "agentName") ?? "MasterAgent",
                    SessionId = GetStringProperty(root, "sessionId"),
                    Error = GetNestedStringProperty(root, "metadata", "error"),
                    
                    // Parse enhanced fields
                    AgentsUsed = GetStringArray(root, "agents_used"),
                    ToolsUsed = GetStringArray(root, "tools_used"),
                    AvailableAgents = ParseAvailableAgents(root),
                    AvailableTools = ParseAvailableTools(root),
                    ExecutionDetails = ParseExecutionDetails(root),
                    Metadata = ParseMetadata(root)
                };
                
                _logger.LogInformation("Successfully parsed runtime response with {AgentsUsed} agents used and {ToolsUsed} tools used", 
                    result.AgentsUsed.Count, result.ToolsUsed.Count);
                
                return result;
            }
            catch (TaskCanceledException ex) when (ex.InnerException is TimeoutException)
            {
                _logger.LogError("Request to runtime service timed out after {Timeout}ms", _httpClient.Timeout.TotalMilliseconds);
                return new AgentRuntimeResponse
                {
                    Success = false,
                    Error = $"Request timed out after {_httpClient.Timeout.TotalSeconds} seconds",
                    Response = "The request is taking longer than expected. Please try again or contact support if the issue persists."
                };
            }
            catch (TaskCanceledException ex)
            {
                _logger.LogError(ex, "Request to runtime service was canceled");
                return new AgentRuntimeResponse
                {
                    Success = false,
                    Error = "Request was canceled",
                    Response = "The request was canceled. Please try again."
                };
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "HTTP error communicating with runtime service at {BaseUrl}", _httpClient.BaseAddress);
                return new AgentRuntimeResponse
                {
                    Success = false,
                    Error = $"HTTP error: {ex.Message}",
                    Response = "I apologize, but I'm having trouble connecting to the agent service. Please try again later."
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error communicating with runtime service");
                return new AgentRuntimeResponse
                {
                    Success = false,
                    Error = ex.Message,
                    Response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
                };
            }
        }

        private AvailableAgents ParseAvailableAgents(JsonElement root)
        {
            if (!root.TryGetProperty("available_agents", out var availableAgentsProp))
                return new AvailableAgents();

            var result = new AvailableAgents
            {
                TotalAgents = availableAgentsProp.TryGetProperty("total_agents", out var totalProp) && totalProp.ValueKind == JsonValueKind.Number ? totalProp.GetInt32() : 0,
                Agents = new List<AgentInfo>()
            };

            if (availableAgentsProp.TryGetProperty("agents", out var agentsArrayProp) && agentsArrayProp.ValueKind == JsonValueKind.Array)
            {
                result.Agents = agentsArrayProp.EnumerateArray()
                    .Select(agent => new AgentInfo
                    {
                        Name = GetStringProperty(agent, "name") ?? "",
                        Description = GetStringProperty(agent, "description") ?? ""
                    })
                    .ToList();
            }

            return result;
        }

        private List<AvailableTool> ParseAvailableTools(JsonElement root)
        {
            if (!root.TryGetProperty("available_tools", out var availableToolsProp) || availableToolsProp.ValueKind != JsonValueKind.Array)
                return new List<AvailableTool>();

            return availableToolsProp.EnumerateArray()
                .Select(tool => new AvailableTool
                {
                    Name = GetStringProperty(tool, "name") ?? "",
                    Description = GetStringProperty(tool, "description") ?? ""
                })
                .ToList();
        }

        private ExecutionDetails ParseExecutionDetails(JsonElement root)
        {
            if (!root.TryGetProperty("execution_details", out var executionDetailsProp))
                return new ExecutionDetails();

            var result = new ExecutionDetails
            {
                TotalSteps = executionDetailsProp.TryGetProperty("total_steps", out var totalStepsProp) && totalStepsProp.ValueKind == JsonValueKind.Number ? totalStepsProp.GetInt32() : 0,
                ExecutionSteps = new List<ExecutionStep>()
            };

            if (executionDetailsProp.TryGetProperty("execution_steps", out var stepsArrayProp) && stepsArrayProp.ValueKind == JsonValueKind.Array)
            {
                result.ExecutionSteps = stepsArrayProp.EnumerateArray()
                    .Select(step => new ExecutionStep
                    {
                        ToolName = GetStringProperty(step, "tool_name") ?? "",
                        ToolInput = GetStringProperty(step, "tool_input") ?? "",
                        Observation = GetStringProperty(step, "observation") ?? ""
                    })
                    .ToList();
            }

            return result;
        }

        private Dictionary<string, object> ParseMetadata(JsonElement root)
        {
            var metadata = new Dictionary<string, object>();

            if (root.TryGetProperty("metadata", out var metadataProp) && metadataProp.ValueKind == JsonValueKind.Object)
            {
                foreach (var property in metadataProp.EnumerateObject())
                {
                    metadata[property.Name] = property.Value.ValueKind switch
                    {
                        JsonValueKind.String => property.Value.GetString() ?? "",
                        JsonValueKind.Number => property.Value.GetDouble(),
                        JsonValueKind.True => true,
                        JsonValueKind.False => false,
                        JsonValueKind.Null => null,
                        _ => property.Value.ToString()
                    };
                }
            }

            return metadata;
        }

        private string GetStringProperty(JsonElement root, string propertyName)
        {
            if (root.TryGetProperty(propertyName, out var property))
            {
                return property.ValueKind switch
                {
                    JsonValueKind.String => property.GetString(),
                    JsonValueKind.Null => null,
                    JsonValueKind.Number => property.GetDouble().ToString(),
                    JsonValueKind.True => "true",
                    JsonValueKind.False => "false",
                    _ => property.ToString()
                };
            }
            return null;
        }

        private string GetNestedStringProperty(JsonElement root, string parentPropertyName, string childPropertyName)
        {
            if (root.TryGetProperty(parentPropertyName, out var parentProperty) &&
                parentProperty.ValueKind == JsonValueKind.Object &&
                parentProperty.TryGetProperty(childPropertyName, out var childProperty))
            {
                return childProperty.ValueKind switch
                {
                    JsonValueKind.String => childProperty.GetString(),
                    JsonValueKind.Null => null,
                    JsonValueKind.Number => childProperty.GetDouble().ToString(),
                    JsonValueKind.True => "true",
                    JsonValueKind.False => "false",
                    _ => childProperty.ToString()
                };
            }
            return null;
        }

        private List<string> GetStringArray(JsonElement root, string propertyName)
        {
            if (root.TryGetProperty(propertyName, out var arrayProp) && arrayProp.ValueKind == JsonValueKind.Array)
            {
                return arrayProp.EnumerateArray()
                    .Where(item => item.ValueKind == JsonValueKind.String)
                    .Select(item => item.GetString())
                    .Where(item => item != null)
                    .ToList();
            }
            return new List<string>();
        }

        public async Task<bool> IsHealthyAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/health");
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Health check failed for runtime service");
                return false;
            }
        }
    }
} 