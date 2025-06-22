using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using AutoMapper;
using Microsoft.EntityFrameworkCore;

namespace AgentPlatform.API.Services
{
    public class ToolService : IToolService
    {
        private readonly ApplicationDbContext _context;
        private readonly IMapper _mapper;

        public ToolService(ApplicationDbContext context, IMapper mapper)
        {
            _context = context;
            _mapper = mapper;
        }

        public async Task<List<ToolDto>> GetToolsAsync()
        {
            var tools = await _context.Tools.ToListAsync();
            return _mapper.Map<List<ToolDto>>(tools);
        }
    }
} 