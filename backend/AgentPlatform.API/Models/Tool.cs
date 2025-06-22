using System.ComponentModel.DataAnnotations;

namespace AgentPlatform.API.Models
{
    public class Tool
    {
        public int Id { get; set; }

        [Required]
        public string Name { get; set; } = string.Empty;

        public string? Description { get; set; }
    }
} 