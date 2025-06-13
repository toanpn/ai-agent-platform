using System.ComponentModel.DataAnnotations;

namespace AgentPlatform.API.DTOs
{
    public class CreateAgentRequestDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;
        
        [Required]
        public string Department { get; set; } = string.Empty;
        
        public string? Description { get; set; }
        
        public string? Instructions { get; set; }
    }

    public class UpdateAgentRequestDto
    {
        public string? Name { get; set; }
        
        public string? Department { get; set; }
        
        public string? Description { get; set; }
        
        public string? Instructions { get; set; }
        
        public bool? IsActive { get; set; }
    }

    public class AgentDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Department { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Instructions { get; set; }
        public bool IsActive { get; set; }
        public bool IsMainRouter { get; set; }
        public UserDto CreatedBy { get; set; } = null!;
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public List<AgentFileDto> Files { get; set; } = new();
        public List<AgentFunctionDto> Functions { get; set; } = new();
    }

    public class AgentFileDto
    {
        public int Id { get; set; }
        public string FileName { get; set; } = string.Empty;
        public string? ContentType { get; set; }
        public long FileSize { get; set; }
        public bool IsIndexed { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class AgentFunctionDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Schema { get; set; }
        public string? EndpointUrl { get; set; }
        public string? HttpMethod { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class CreateAgentFunctionRequestDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;
        
        public string? Description { get; set; }
        
        public string? Schema { get; set; }
        
        [Required]
        public string EndpointUrl { get; set; } = string.Empty;
        
        public string HttpMethod { get; set; } = "POST";
        
        public string? Headers { get; set; }
    }
}