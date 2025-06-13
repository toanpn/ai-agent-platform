using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AgentPlatform.API.Models
{
    public class AgentFile
    {
        public int Id { get; set; }
        
        public int AgentId { get; set; }
        
        [ForeignKey("AgentId")]
        public Agent Agent { get; set; } = null!;
        
        [Required]
        public string FileName { get; set; } = string.Empty;
        
        [Required]
        public string FilePath { get; set; } = string.Empty;
        
        public string? ContentType { get; set; }
        
        public long FileSize { get; set; }
        
        public bool IsIndexed { get; set; } = false;
        
        public int UploadedById { get; set; }
        
        [ForeignKey("UploadedById")]
        public User UploadedBy { get; set; } = null!;
        
        public DateTime CreatedAt { get; set; }
    }
}