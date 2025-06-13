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
                var json = JsonSerializer.Serialize(request, _jsonOptions);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/api/chat", content);
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError("Runtime service returned error: {StatusCode}", response.StatusCode);
                    return new AgentRuntimeResponse
                    {
                        Success = false,
                        Error = $"Runtime service returned error: {response.StatusCode}",
                        Response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
                    };
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<AgentRuntimeResponse>(responseJson, _jsonOptions);
                
                return result ?? new AgentRuntimeResponse
                {
                    Success = false,
                    Error = "Failed to deserialize response",
                    Response = "I apologize, but I'm having trouble processing your request right now."
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error communicating with runtime service");
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
    }
} 