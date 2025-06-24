using System.Text.Json.Serialization;

namespace AgentPlatform.API.DTOs
{
    public class PromptEnhancementResponseDto
    {
        [JsonPropertyName("assigned_agents")]
        public List<string> AssignedAgents { get; set; } = [];
        [JsonPropertyName("key_details_extracted")]
        public string KeyDetailsExtracted { get; set; } = string.Empty;
        [JsonPropertyName("original_user_query")]
        public string OriginalUserQuery { get; set; } = string.Empty;
        [JsonPropertyName("summary")]
        public string Summary { get; set; } = string.Empty;
        [JsonPropertyName("user_facing_prompt")]
        public string UserFacingPrompt { get; set; } = string.Empty;
    }
} 