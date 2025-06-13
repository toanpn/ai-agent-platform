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
                .ForMember(dest => dest.Functions, opt => opt.MapFrom(src => src.Functions));
            
            CreateMap<AgentFile, AgentFileDto>();
            
            CreateMap<AgentFunction, AgentFunctionDto>();
            
            CreateMap<ChatMessage, ChatMessageDto>();
            
            CreateMap<ChatSession, ChatSessionDto>()
                .ForMember(dest => dest.Messages, opt => opt.MapFrom(src => src.Messages));
        }
    }
} 