using AutoMapper;
using AgentPlatform.API.Models;
using AgentPlatform.API.DTOs;
using System.Text.Json;

namespace AgentPlatform.API.Mapping
{
    public class ToolConfigsValueResolver : IValueResolver<Agent, AgentJsonDto, object?>
    {
        public object? Resolve(Agent source, AgentJsonDto destination, object? destMember, ResolutionContext context)
        {
            if (string.IsNullOrEmpty(source.ToolConfigs))
                return null;
            
            try
            {
                return JsonSerializer.Deserialize<object>(source.ToolConfigs);
            }
            catch
            {
                return null;
            }
        }
    }

    public class MappingProfile : Profile
    {
        public MappingProfile()
        {
            CreateMap<User, UserDto>();
            
            CreateMap<Agent, AgentDto>()
                .ForMember(dest => dest.CreatedBy, opt => opt.MapFrom(src => src.CreatedBy))
                .ForMember(dest => dest.Files, opt => opt.MapFrom(src => src.Files))
                .ForMember(dest => dest.Functions, opt => opt.MapFrom(src => src.Functions))
                .ForMember(dest => dest.Tools, opt => opt.MapFrom(src => src.ToolsArray))
                .ForMember(dest => dest.ToolConfigs, opt => opt.MapFrom(src => src.ToolConfigs))
                .ForMember(dest => dest.LlmConfig, opt => opt.MapFrom(src => 
                    src.LlmModelName != null || src.LlmTemperature != null 
                        ? new LlmConfigDto { ModelName = src.LlmModelName, Temperature = src.LlmTemperature }
                        : null));
            
            CreateMap<AgentFile, AgentFileDto>();
            
            CreateMap<AgentFunction, AgentFunctionDto>();
            
            CreateMap<ChatMessage, ChatMessageDto>();
            
            CreateMap<ChatSession, ChatSessionDto>()
                .ForMember(dest => dest.Messages, opt => opt.MapFrom(src => src.Messages));
                
            // Mapping for agents.json synchronization
            CreateMap<Agent, AgentJsonDto>()
                .ForMember(dest => dest.AgentName, opt => opt.MapFrom(src => src.Name))
                .ForMember(dest => dest.Tools, opt => opt.MapFrom(src => src.ToolsArray))
                .ForMember(dest => dest.ToolConfigs, opt => opt.MapFrom<ToolConfigsValueResolver>())
                .ForMember(dest => dest.LlmConfig, opt => opt.MapFrom(src => 
                    src.LlmModelName != null || src.LlmTemperature != null 
                        ? new LlmConfigDto { ModelName = src.LlmModelName, Temperature = src.LlmTemperature }
                        : null));
        }
    }
} 