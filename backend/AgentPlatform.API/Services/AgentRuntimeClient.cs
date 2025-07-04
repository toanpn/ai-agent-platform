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

    // DTO for summarization request
    public class SummarizationRequest
    {
        [JsonPropertyName("messages")]
        public List<MessageHistory> Messages { get; set; } = new();
    }

    // DTO for summarization response
    public class SummarizationResponse
    {
        [JsonPropertyName("summary")]
        public string Summary { get; set; } = string.Empty;
    }

    // DTOs for RAG operations
    public class PythonRagUploadResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }
        
        [JsonPropertyName("result")]
        public PythonRagUploadResult? Result { get; set; }
        
        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }

    public class PythonRagUploadResult
    {
        [JsonPropertyName("document_id")]
        public string DocumentId { get; set; } = string.Empty;
        
        [JsonPropertyName("chunks_created")]
        public int ChunksCreated { get; set; }
        
        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; } = string.Empty;
        
        [JsonPropertyName("file_name")]
        public string FileName { get; set; } = string.Empty;
        
        [JsonPropertyName("file_size")]
        public long FileSize { get; set; }
        
        [JsonPropertyName("processed_at")]
        public string ProcessedAt { get; set; } = string.Empty;
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

        public async Task<string?> GetSessionSummaryAsync(List<MessageHistory> messages)
        {
            try
            {
                _logger.LogInformation("Sending request to runtime service for session summary");

                var request = new SummarizationRequest { Messages = messages };
                var json = JsonSerializer.Serialize(request, _jsonOptions);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                _logger.LogDebug("Summarization request payload: {Request}", json);

                var response = await _httpClient.PostAsync("/v1/chat/summarize", content);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Runtime service returned error on summarization: {StatusCode}, Content: {Content}",
                        response.StatusCode, errorContent);
                    return null;
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Raw summarization response: {Response}", responseJson);

                var summarizationResponse = JsonSerializer.Deserialize<SummarizationResponse>(responseJson, _jsonOptions);

                return summarizationResponse?.Summary;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error getting session summary from runtime service");
                return null;
            }
        }

        public async Task<RagUploadResponse?> UploadFileForProcessingAsync(string filePath, int agentId, Dictionary<string, object>? metadata = null)
        {
            try
            {
                _logger.LogInformation("Uploading file {FilePath} for agent {AgentId} to runtime service", filePath, agentId);

                if (!File.Exists(filePath))
                {
                    _logger.LogError("File not found: {FilePath}", filePath);
                    return new RagUploadResponse
                    {
                        Success = false,
                        Error = "File not found"
                    };
                }

                using var formContent = new MultipartFormDataContent();
                
                // Add file
                var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(filePath));
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                formContent.Add(fileContent, "file", Path.GetFileName(filePath));
                
                // Add agent_id
                formContent.Add(new StringContent(agentId.ToString()), "agent_id");
                
                // Add metadata if provided
                if (metadata != null && metadata.Count > 0)
                {
                    var metadataJson = JsonSerializer.Serialize(metadata, _jsonOptions);
                    formContent.Add(new StringContent(metadataJson), "metadata");
                }

                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                var response = await _httpClient.PostAsync("/api/rag/upload", formContent);
                stopwatch.Stop();

                _logger.LogInformation("RAG upload completed in {ElapsedMs}ms with status {StatusCode}", 
                    stopwatch.ElapsedMilliseconds, response.StatusCode);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Runtime service returned error on RAG upload: {StatusCode}, Content: {Content}", 
                        response.StatusCode, errorContent);
                    return new RagUploadResponse
                    {
                        Success = false,
                        Error = $"Runtime service returned error: {response.StatusCode}"
                    };
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("RAG upload response: {Response}", responseJson);

                var pythonResponse = JsonSerializer.Deserialize<PythonRagUploadResponse>(responseJson, _jsonOptions);
                
                if (pythonResponse == null)
                {
                    _logger.LogError("Failed to deserialize RAG upload response");
                    return new RagUploadResponse
                    {
                        Success = false,
                        Error = "Failed to parse response from runtime service"
                    };
                }

                // Map Python response to our DTO
                var result = new RagUploadResponse
                {
                    Success = pythonResponse.Success,
                    Error = pythonResponse.Error,
                    Result = pythonResponse.Result != null ? new RagUploadResult
                    {
                        DocumentId = pythonResponse.Result.DocumentId,
                        ChunksCreated = pythonResponse.Result.ChunksCreated,
                        AgentId = pythonResponse.Result.AgentId,
                        FileName = pythonResponse.Result.FileName,
                        FileSize = pythonResponse.Result.FileSize,
                        ProcessedAt = pythonResponse.Result.ProcessedAt
                    } : null
                };

                _logger.LogInformation("Successfully uploaded and processed file {FileName} with {ChunksCreated} chunks", 
                    result.Result?.FileName, result.Result?.ChunksCreated);

                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error uploading file to runtime service");
                return new RagUploadResponse
                {
                    Success = false,
                    Error = ex.Message
                };
            }
        }

        public async Task<bool> DeleteAgentDocumentsAsync(string agentId)
        {
            try
            {
                _logger.LogInformation("Deleting documents for agent {AgentId} from runtime service", agentId);

                var response = await _httpClient.DeleteAsync($"/api/rag/agent/{agentId}/documents");

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Runtime service returned error on document deletion: {StatusCode}, Content: {Content}", 
                        response.StatusCode, errorContent);
                    return false;
                }

                _logger.LogInformation("Successfully deleted documents for agent {AgentId}", agentId);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error deleting agent documents from runtime service");
                return false;
            }
        }

        public async Task<AgentSyncResponse?> SyncAgentsAsync(List<AgentJsonDto> agents)
        {
            try
            {
                _logger.LogInformation("Syncing {AgentCount} agents to Agent Core", agents.Count);
                
                var requestData = new { agents = agents };
                var json = JsonSerializer.Serialize(requestData, _jsonOptions);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                _logger.LogDebug("Agent sync payload: {Request}", json);
                
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                var response = await _httpClient.PostAsync("/api/agents/sync", content);
                stopwatch.Stop();
                
                _logger.LogInformation("Agent sync responded in {ElapsedMs}ms with status {StatusCode}", 
                    stopwatch.ElapsedMilliseconds, response.StatusCode);
                
                var responseJson = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Agent sync response: {Response}", responseJson);
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError("Agent sync failed: {StatusCode}, Content: {Content}", 
                        response.StatusCode, responseJson);
                    
                    // Try to parse error from response
                    try
                    {
                        var errorResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                        var errorMessage = errorResponse?.ContainsKey("error") == true 
                            ? errorResponse["error"].ToString() 
                            : "Unknown error";
                            
                        return new AgentSyncResponse
                        {
                            Success = false,
                            Error = errorMessage,
                            Message = $"HTTP {response.StatusCode}: {errorMessage}"
                        };
                    }
                    catch
                    {
                        return new AgentSyncResponse
                        {
                            Success = false,
                            Error = $"HTTP {response.StatusCode}",
                            Message = "Failed to sync agents to Agent Core"
                        };
                    }
                }
                
                // Parse successful response
                try
                {
                    var syncResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                    
                    var success = syncResponse?.ContainsKey("success") == true && 
                                 syncResponse["success"] is JsonElement successElement && 
                                 successElement.ValueKind == JsonValueKind.True;
                    
                    var message = syncResponse?.ContainsKey("message") == true 
                        ? syncResponse["message"].ToString() 
                        : "Agents synced successfully";
                        
                    var agentsSynced = 0;
                    var agentsLoaded = 0;
                    
                    if (syncResponse?.ContainsKey("agents_synced") == true && 
                        syncResponse["agents_synced"] is JsonElement syncedElement && 
                        syncedElement.ValueKind == JsonValueKind.Number)
                    {
                        agentsSynced = syncedElement.GetInt32();
                    }
                    
                    if (syncResponse?.ContainsKey("agents_loaded") == true && 
                        syncResponse["agents_loaded"] is JsonElement loadedElement && 
                        loadedElement.ValueKind == JsonValueKind.Number)
                    {
                        agentsLoaded = loadedElement.GetInt32();
                    }
                    
                    return new AgentSyncResponse
                    {
                        Success = success,
                        Message = message,
                        AgentsSynced = agentsSynced,
                        AgentsLoaded = agentsLoaded
                    };
                }
                catch (JsonException ex)
                {
                    _logger.LogError(ex, "Failed to parse agent sync response: {Response}", responseJson);
                    return new AgentSyncResponse
                    {
                        Success = false,
                        Error = "Failed to parse response",
                        Message = "Invalid response format from Agent Core"
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Exception occurred while syncing agents");
                return new AgentSyncResponse
                {
                    Success = false,
                    Error = ex.Message,
                    Message = "Exception occurred during agent sync"
                };
            }
        }

        public async Task<ToolsResponse?> GetToolsAsync()
        {
            try
            {
                _logger.LogInformation("Getting tools from Agent Core");
                
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                var response = await _httpClient.GetAsync("/api/tools");
                stopwatch.Stop();
                
                _logger.LogInformation("Tools request responded in {ElapsedMs}ms with status {StatusCode}", 
                    stopwatch.ElapsedMilliseconds, response.StatusCode);
                
                var responseJson = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Tools response: {Response}", responseJson);
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError("Tools request failed: {StatusCode}, Content: {Content}", 
                        response.StatusCode, responseJson);
                    
                    // Try to parse error from response
                    try
                    {
                        var errorResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                        var errorMessage = errorResponse?.ContainsKey("error") == true 
                            ? errorResponse["error"].ToString() 
                            : "Unknown error";
                            
                        return new ToolsResponse
                        {
                            Success = false,
                            Error = errorMessage
                        };
                    }
                    catch
                    {
                        return new ToolsResponse
                        {
                            Success = false,
                            Error = $"HTTP {response.StatusCode}"
                        };
                    }
                }
                
                // Parse successful response
                try
                {
                    var toolsResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                    
                    var success = toolsResponse?.ContainsKey("success") == true && 
                                 toolsResponse["success"] is JsonElement successElement && 
                                 successElement.ValueKind == JsonValueKind.True;
                    
                    var toolsData = new List<ToolInfo>();
                    var totalTools = 0;
                    
                    if (toolsResponse?.ContainsKey("data") == true && 
                        toolsResponse["data"] is JsonElement dataElement && 
                        dataElement.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var toolElement in dataElement.EnumerateArray())
                        {
                            var toolInfo = new ToolInfo();
                            
                            if (toolElement.TryGetProperty("id", out var idProp))
                                toolInfo.Id = idProp.GetString() ?? string.Empty;
                            
                            if (toolElement.TryGetProperty("name", out var nameProp))
                                toolInfo.Name = nameProp.GetString() ?? string.Empty;
                            
                            if (toolElement.TryGetProperty("description", out var descProp))
                                toolInfo.Description = descProp.GetString();
                            
                            if (toolElement.TryGetProperty("file", out var fileProp))
                                toolInfo.File = fileProp.GetString();
                            
                            if (toolElement.TryGetProperty("parameters", out var paramsProp))
                            {
                                try
                                {
                                    toolInfo.Parameters = JsonSerializer.Deserialize<Dictionary<string, object>>(paramsProp.GetRawText(), _jsonOptions);
                                }
                                catch
                                {
                                    toolInfo.Parameters = new Dictionary<string, object>();
                                }
                            }
                            
                            toolsData.Add(toolInfo);
                        }
                    }
                    
                    if (toolsResponse?.ContainsKey("total_tools") == true && 
                        toolsResponse["total_tools"] is JsonElement totalElement && 
                        totalElement.ValueKind == JsonValueKind.Number)
                    {
                        totalTools = totalElement.GetInt32();
                    }
                    
                    return new ToolsResponse
                    {
                        Success = success,
                        Data = toolsData,
                        TotalTools = totalTools
                    };
                }
                catch (JsonException ex)
                {
                    _logger.LogError(ex, "Failed to parse tools response: {Response}", responseJson);
                    return new ToolsResponse
                    {
                        Success = false,
                        Error = "Failed to parse response"
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Exception occurred while getting tools");
                return new ToolsResponse
                {
                    Success = false,
                    Error = ex.Message
                };
            }
        }
    }
} 