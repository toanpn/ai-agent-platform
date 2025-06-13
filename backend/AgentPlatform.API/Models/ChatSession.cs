using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class ChatSession
    {
        public int Id { get; set; }
        
        public int UserId { get; set; }
        
        [ForeignKey("UserId")]
        public User User { get; set; } = null!;
        
        public string? Title { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        public DateTime CreatedAt { get; set; }
        
        public DateTime? UpdatedAt { get; set; }
        
        // Navigation properties
        public ICollection<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
    }
} 