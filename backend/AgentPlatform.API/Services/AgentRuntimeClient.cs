using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using AgentPlatform.Shared.Models;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    // DTO classes for Python backend response structure
    public class PythonBackendResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }
        
        [JsonPropertyName("response")]
        public string Response { get; set; } = string.Empty;
        
        [JsonPropertyName("agentName")]
        public string AgentName { get; set; } = string.Empty;
        
        [JsonPropertyName("sessionId")]
        public string? SessionId { get; set; }
        
        [JsonPropertyName("error")]
        public string? Error { get; set; }
        
        [JsonPropertyName("agents_used")]
        public List<string> AgentsUsed { get; set; } = new();
        
        [JsonPropertyName("tools_used")]
        public List<string> ToolsUsed { get; set; } = new();
        
        [JsonPropertyName("available_agents")]
        public PythonAvailableAgents AvailableAgents { get; set; } = new();
        
        [JsonPropertyName("available_tools")]
        public List<PythonAvailableTool> AvailableTools { get; set; } = new();
        
        [JsonPropertyName("execution_details")]
        public PythonExecutionDetails ExecutionDetails { get; set; } = new();
        
        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class PythonAvailableAgents
    {
        [JsonPropertyName("total_agents")]
        public int TotalAgents { get; set; }
        
        [JsonPropertyName("agents")]
        public List<PythonAgentInfo> Agents { get; set; } = new();
    }

    public class PythonAgentInfo
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
    }

    public class PythonAvailableTool
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
    }

    public class PythonExecutionDetails
    {
        [JsonPropertyName("total_steps")]
        public int TotalSteps { get; set; }
        
        [JsonPropertyName("execution_steps")]
        public List<PythonExecutionStep> ExecutionSteps { get; set; } = new();
    }

    public class PythonExecutionStep
    {
        [JsonPropertyName("tool_name")]
        public string ToolName { get; set; } = string.Empty;
        
        [JsonPropertyName("tool_input")]
        public JsonElement ToolInput { get; set; }
        
        [JsonPropertyName("observation")]
        public string Observation { get; set; } = string.Empty;
    }

    public class AgentRuntimeClient : IAgentRuntimeClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<AgentRuntimeClient> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public AgentRuntimeClient(HttpClient httpClient, IConfiguration configuration, ILogger<AgentRuntimeClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
            
            var baseUrl = configuration["AgentRuntime:BaseUrl"] ?? "http://localhost:8000";
            _httpClient.BaseAddress = new Uri(baseUrl);
            
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                PropertyNameCaseInsensitive = true,
                MaxDepth = 64,
                DefaultBufferSize = 32768, // Increase buffer size for large content
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping // Handle Unicode properly
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
                
                // Debug logging to see raw response
                _logger.LogDebug("Raw runtime response: {Response}", responseJson);
                
                // Debug: Check raw observation length in JSON
                using var rawDocument = JsonDocument.Parse(responseJson);
                if (rawDocument.RootElement.TryGetProperty("execution_details", out var execDetails) &&
                    execDetails.TryGetProperty("execution_steps", out var steps) &&
                    steps.ValueKind == JsonValueKind.Array)
                {
                    var stepArray = steps.EnumerateArray().ToArray();
                    for (int i = 0; i < stepArray.Length; i++)
                    {
                        if (stepArray[i].TryGetProperty("observation", out var rawObs) && rawObs.ValueKind == JsonValueKind.String)
                        {
                            var rawObsText = rawObs.GetString() ?? "";
                            _logger.LogDebug("Raw observation {Index} length: {Length}", i, rawObsText.Length);
                            _logger.LogDebug("Raw observation {Index} preview: {Preview}", i, rawObsText.Length > 100 ? rawObsText.Substring(0, 100) + "..." : rawObsText);
                        }
                    }
                }
                
                // Use JsonSerializer.Deserialize instead of manual JsonDocument parsing
                var pythonResponse = JsonSerializer.Deserialize<PythonBackendResponse>(responseJson, _jsonOptions);
                
                if (pythonResponse == null)
                {
                    _logger.LogError("Failed to deserialize Python backend response");
                    return new AgentRuntimeResponse
                    {
                        Success = false,
                        Error = "Failed to parse response from runtime service",
                        Response = "I apologize, but I'm having trouble processing the response. Please try again later."
                    };
                }
                
                // Map Python response to our AgentRuntimeResponse
                var result = new AgentRuntimeResponse
                {
                    Success = pythonResponse.Success,
                    Response = pythonResponse.Response,
                    AgentName = pythonResponse.AgentName,
                    SessionId = pythonResponse.SessionId,
                    Error = pythonResponse.Error,
                    AgentsUsed = pythonResponse.AgentsUsed,
                    ToolsUsed = pythonResponse.ToolsUsed,
                    AvailableAgents = new AvailableAgents
                    {
                        TotalAgents = pythonResponse.AvailableAgents.TotalAgents,
                        Agents = pythonResponse.AvailableAgents.Agents.Select(a => new AgentInfo
                        {
                            Name = a.Name,
                            Description = a.Description
                        }).ToList()
                    },
                    AvailableTools = pythonResponse.AvailableTools.Select(t => new AvailableTool
                    {
                        Name = t.Name,
                        Description = t.Description
                    }).ToList(),
                    ExecutionDetails = new ExecutionDetails
                    {
                        TotalSteps = pythonResponse.ExecutionDetails.TotalSteps,
                        ExecutionSteps = pythonResponse.ExecutionDetails.ExecutionSteps.Select(s => new ExecutionStep
                        {
                            ToolName = s.ToolName,
                            ToolInput = s.ToolInput.ValueKind == JsonValueKind.String 
                                ? s.ToolInput.GetString() ?? "" 
                                : s.ToolInput.GetRawText(),
                            Observation = s.Observation
                        }).ToList()
                    },
                    Metadata = pythonResponse.Metadata
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
            catch (JsonException ex)
            {
                _logger.LogError(ex, "Failed to parse JSON response from runtime service");
                return new AgentRuntimeResponse
                {
                    Success = false,
                    Error = $"JSON parsing error: {ex.Message}",
                    Response = "I apologize, but I'm having trouble parsing the response. Please try again later."
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

        public async Task<PromptEnhancementResponseDto?> EnhancePromptAsync(string query)
        {
            try
            {
                var coreApiRequest = new { query };
                var response = await _httpClient.PostAsJsonAsync("/api/enhance-prompt", coreApiRequest);

                if (response.IsSuccessStatusCode)
                {
                    var responseStream = await response.Content.ReadAsStreamAsync();
                    using var jsonDocument = await JsonDocument.ParseAsync(responseStream);
                    var enhancementResponse = jsonDocument.RootElement;
                    if (enhancementResponse.TryGetProperty("enhanced_prompt", out var promptElement))
                    {
                        _logger.LogDebug("Prompt enhancement response: {Response}", promptElement);

                        var result = JsonSerializer.Deserialize<PromptEnhancementResponseDto>(promptElement, _jsonOptions);

                        if (result == null)
                        {
                            _logger.LogWarning("Failed to deserialize prompt enhancement response");
                            return null;
                        }

                        return result;
                    }
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Error from core API service: {StatusCode} - {ErrorContent}", response.StatusCode, errorContent);
                return null;
            
            }
            catch (JsonException ex)
            {
                _logger.LogError(ex, "Failed to parse JSON response from prompt enhancement service");
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error enhancing prompt");
                return null;
            }
        }
    }
} 