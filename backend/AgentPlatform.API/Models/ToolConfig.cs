using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class ToolConfig
    {
        public int Id { get; set; }

        public string ToolName { get; set; } = string.Empty;

        public int AgentId { get; set; }

        [ForeignKey("AgentId")]
        public Agent Agent { get; set; } = null!;

        public string ConfigSchema { get; set; } = string.Empty; // JSON schema as a string

        public DateTime CreatedAt { get; set; }

        public DateTime UpdatedAt { get; set; }
    }
}