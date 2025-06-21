using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class Agent
    {
        public int Id { get; set; }
        
        [Required]
        public string Name { get; set; } = string.Empty;
        
        [Required]
        public string Department { get; set; } = string.Empty;
        
        public string? Description { get; set; }
        
        public string? Instructions { get; set; }
        
        // Tools field - stored as pipe-separated string for database compatibility
        public string? Tools { get; set; }
        
        // LLM Configuration fields
        public string? LlmModelName { get; set; }
        
        public double? LlmTemperature { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        public bool IsMainRouter { get; set; } = false;
        
        public int CreatedById { get; set; }
        
        [ForeignKey("CreatedById")]
        public User CreatedBy { get; set; } = null!;
        
        public DateTime CreatedAt { get; set; }
        
        public DateTime? UpdatedAt { get; set; }
        
        // Navigation properties
        public ICollection<AgentFile> Files { get; set; } = new List<AgentFile>();
        
        public ICollection<AgentFunction> Functions { get; set; } = new List<AgentFunction>();
        
        // Helper methods to work with Tools as array
        [NotMapped]
        public string[] ToolsArray
        {
            get => string.IsNullOrEmpty(Tools) ? Array.Empty<string>() : Tools.Split('|', StringSplitOptions.RemoveEmptyEntries);
            set => Tools = value != null && value.Length > 0 ? string.Join('|', value) : null;
        }
    }
} 