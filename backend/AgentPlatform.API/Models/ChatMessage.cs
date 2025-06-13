using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class ChatMessage
    {
        public int Id { get; set; }
        
        public int ChatSessionId { get; set; }
        
        [ForeignKey("ChatSessionId")]
        public ChatSession ChatSession { get; set; } = null!;
        
        [Required]
        public string Content { get; set; } = string.Empty;
        
        [Required]
        public string Role { get; set; } = string.Empty; // "user", "assistant", "system"
        
        public string? AgentName { get; set; }
        
        public string? Metadata { get; set; } // JSON for additional data
        
        public DateTime CreatedAt { get; set; }
    }
} 