using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class AgentFunction
    {
        public int Id { get; set; }
        
        public int AgentId { get; set; }
        
        [ForeignKey("AgentId")]
        public Agent Agent { get; set; } = null!;
        
        [Required]
        public string Name { get; set; } = string.Empty;
        
        public string? Description { get; set; }
        
        public string? Schema { get; set; } // JSON schema for function parameters
        
        public string? EndpointUrl { get; set; }
        
        public string? HttpMethod { get; set; } = "POST";
        
        public string? Headers { get; set; } // JSON for HTTP headers
        
        public bool IsActive { get; set; } = true;
        
        public DateTime CreatedAt { get; set; }
        
        public DateTime? UpdatedAt { get; set; }
    }
} 