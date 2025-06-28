namespace AgentPlatform.API.Models
{
    public class AgentManagementConfig
    {
        public const string SectionName = "AgentManagement";
        
        public string AgentsJsonPath { get; set; } = "../AgentPlatform.Core/agents.json";
    }
} 