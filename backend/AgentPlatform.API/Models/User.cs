using System.ComponentModel.DataAnnotations;

namespace AgentPlatform.API.Models
{
    public class User
    {
        public int Id { get; set; }
        
        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;
        
        [Required]
        public string PasswordHash { get; set; } = string.Empty;
        
        public string? FirstName { get; set; }
        
        public string? LastName { get; set; }
        
        public string? Department { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        public DateTime CreatedAt { get; set; }
        
        public DateTime? UpdatedAt { get; set; }

        public Guid SecurityStamp { get; set; } = Guid.NewGuid();
    }
} 