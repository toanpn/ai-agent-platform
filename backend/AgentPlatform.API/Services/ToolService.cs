using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public class ToolService : IToolService
    {
        private readonly IAgentRuntimeClient _agentRuntimeClient;
        private readonly ILogger<ToolService> _logger;

        public ToolService(IAgentRuntimeClient agentRuntimeClient, ILogger<ToolService> logger)
        {
            _agentRuntimeClient = agentRuntimeClient;
            _logger = logger;
        }

        public async Task<List<ToolDto>> GetToolsAsync()
        {
            try
            {
                _logger.LogInformation("Getting tools from Agent Core via HTTP API");

                // Get tools from Agent Core via HTTP API
                var toolsResponse = await _agentRuntimeClient.GetToolsAsync();

                if (toolsResponse?.Success == true)
                {
                    _logger.LogInformation("✅ Successfully retrieved {Count} tools from Agent Core", toolsResponse.Data.Count);

                    // Convert ToolInfo to ToolDto
                    var toolDtos = toolsResponse.Data.Select(tool => new ToolDto
                    {
                        Id = tool.Id,
                        Name = tool.Name,
                        Description = tool.Description,
                        File = tool.File,
                        Parameters = tool.Parameters?.ToDictionary(
                            kv => kv.Key,
                            kv => ConvertToToolParameterDto(kv.Value)
                        )
                    }).ToList();

                    return toolDtos;
                }
                else
                {
                    var errorMessage = toolsResponse?.Error ?? "Unknown error occurred";
                    _logger.LogError("❌ Failed to get tools from Agent Core: {Error}", errorMessage);
                    
                    // Return empty list instead of throwing exception to maintain backward compatibility
                    return new List<ToolDto>();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Error getting tools from Agent Core via HTTP API");
                
                // Return empty list instead of throwing exception to maintain backward compatibility
                return new List<ToolDto>();
            }
        }

        private static ToolParameterDto ConvertToToolParameterDto(object parameter)
        {
            // Handle parameter conversion from JSON object to ToolParameterDto
            if (parameter is Dictionary<string, object> paramDict)
            {
                return new ToolParameterDto
                {
                    Type = paramDict.TryGetValue("type", out var type) ? type?.ToString() : null,
                    Description = paramDict.TryGetValue("description", out var desc) ? desc?.ToString() : null,
                    Required = paramDict.TryGetValue("required", out var req) && Convert.ToBoolean(req),
                    Default = paramDict.TryGetValue("default", out var def) ? def : null,
                    IsCredential = paramDict.TryGetValue("is_credential", out var cred) && Convert.ToBoolean(cred)
                };
            }

            return new ToolParameterDto();
        }
    }
} 