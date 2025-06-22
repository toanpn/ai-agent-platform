using AutoMapper;
using AgentPlatform.API.Models;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Mapping
{
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
                .ForMember(dest => dest.LlmConfig, opt => opt.MapFrom(src => 
                    src.LlmModelName != null || src.LlmTemperature != null 
                        ? new LlmConfigDto { ModelName = src.LlmModelName, Temperature = src.LlmTemperature }
                        : null));
            
            CreateMap<AgentFile, AgentFileDto>();
            
            CreateMap<AgentFunction, AgentFunctionDto>();
            
            CreateMap<Tool, ToolDto>();
            
            CreateMap<ChatMessage, ChatMessageDto>();
            
            CreateMap<ChatSession, ChatSessionDto>()
                .ForMember(dest => dest.Messages, opt => opt.MapFrom(src => src.Messages));
                
            // Mapping for agents.json synchronization
            CreateMap<Agent, AgentJsonDto>()
                .ForMember(dest => dest.AgentName, opt => opt.MapFrom(src => src.Name))
                .ForMember(dest => dest.Tools, opt => opt.MapFrom(src => src.ToolsArray))
                .ForMember(dest => dest.LlmConfig, opt => opt.MapFrom(src => 
                    src.LlmModelName != null || src.LlmTemperature != null 
                        ? new LlmConfigDto { ModelName = src.LlmModelName, Temperature = src.LlmTemperature }
                        : null));
        }
    }
} 