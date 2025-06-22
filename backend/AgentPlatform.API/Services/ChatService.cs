using Microsoft.EntityFrameworkCore;
using AutoMapper;
using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using AgentPlatform.Shared.Models;

namespace AgentPlatform.API.Services
{
    public class ChatService : IChatService
    {
        private readonly ApplicationDbContext _context;
        private readonly IAgentRuntimeClient _runtimeClient;
        private readonly IMapper _mapper;

        public ChatService(ApplicationDbContext context, IAgentRuntimeClient runtimeClient, IMapper mapper)
        {
            _context = context;
            _runtimeClient = runtimeClient;
            _mapper = mapper;
        }

        public async Task<ChatResponseDto> SendMessageAsync(int userId, SendMessageRequestDto request)
        {
            // Get or create chat session
            ChatSession session;
            if (request.SessionId.HasValue)
            {
                session = await _context.ChatSessions
                    .Include(s => s.Messages)
                    .FirstOrDefaultAsync(s => s.Id == request.SessionId.Value && s.UserId == userId);
                
                if (session == null)
                {
                    throw new KeyNotFoundException("Chat session not found");
                }
            }
            else
            {
                session = new ChatSession
                {
                    UserId = userId,
                    CreatedAt = DateTime.UtcNow
                };
                _context.ChatSessions.Add(session);
                await _context.SaveChangesAsync();
            }

            // Save user message
            var userMessage = new ChatMessage
            {
                ChatSessionId = session.Id,
                Content = request.Message,
                Role = "user",
                CreatedAt = DateTime.UtcNow
            };

            _context.ChatMessages.Add(userMessage);

            // Prepare history for runtime
            var history = session.Messages
                .OrderBy(m => m.CreatedAt)
                .Select(m => new MessageHistory
                {
                    Role = m.Role,
                    Content = m.Content,
                    AgentName = m.AgentName,
                    Timestamp = m.CreatedAt
                })
                .ToList();

            // Add current message to history
            history.Add(new MessageHistory
            {
                Role = "user",
                Content = request.Message,
                Timestamp = DateTime.UtcNow
            });

            // Send to runtime
            var runtimeRequest = new AgentRuntimeRequest
            {
                Message = request.Message,
                UserId = userId.ToString(),
                SessionId = session.Id.ToString(),
                AgentName = request.AgentName,
                History = history
            };

            var runtimeResponse = await _runtimeClient.SendMessageAsync(runtimeRequest);

            // Save agent response
            var agentMessage = new ChatMessage
            {
                ChatSessionId = session.Id,
                Content = runtimeResponse.Response,
                Role = "assistant",
                AgentName = runtimeResponse.AgentName,
                CreatedAt = DateTime.UtcNow
            };

            _context.ChatMessages.Add(agentMessage);
            await _context.SaveChangesAsync();

            // Map the enhanced runtime response to ChatResponseDto
            return new ChatResponseDto
            {
                Response = runtimeResponse.Response,
                AgentName = runtimeResponse.AgentName,
                SessionId = session.Id,
                Timestamp = DateTime.UtcNow,
                Success = runtimeResponse.Success,
                Error = runtimeResponse.Error,
                
                // Enhanced fields
                AgentsUsed = runtimeResponse.AgentsUsed,
                ToolsUsed = runtimeResponse.ToolsUsed,
                AvailableAgents = new AvailableAgentsDto
                {
                    TotalAgents = runtimeResponse.AvailableAgents.TotalAgents,
                    Agents = runtimeResponse.AvailableAgents.Agents.Select(a => new AgentInfoDto
                    {
                        Name = a.Name,
                        Description = a.Description
                    }).ToList()
                },
                AvailableTools = runtimeResponse.AvailableTools.Select(t => new AvailableToolDto
                {
                    Name = t.Name,
                    Description = t.Description
                }).ToList(),
                ExecutionDetails = new ExecutionDetailsDto
                {
                    TotalSteps = runtimeResponse.ExecutionDetails.TotalSteps,
                    ExecutionSteps = runtimeResponse.ExecutionDetails.ExecutionSteps.Select(s => new ExecutionStepDto
                    {
                        ToolName = s.ToolName,
                        ToolInput = s.ToolInput,
                        Observation = s.Observation
                    }).ToList()
                },
                Metadata = runtimeResponse.Metadata
            };
        }

        public async Task<ChatHistoryDto> GetChatHistoryAsync(int userId, int page = 1, int pageSize = 10)
        {
            var query = _context.ChatSessions
                .Where(s => s.UserId == userId)
                .Include(s => s.Messages.OrderBy(m => m.CreatedAt))
                .OrderByDescending(s => s.CreatedAt);

            var totalCount = await query.CountAsync();
            var sessions = await query
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            var sessionDtos = sessions.Select(s => new ChatSessionDto
            {
                Id = s.Id,
                Title = s.Title,
                IsActive = s.IsActive,
                CreatedAt = s.CreatedAt,
                Messages = s.Messages.Select(m => new ChatMessageDto
                {
                    Id = m.Id,
                    Content = m.Content,
                    Role = m.Role,
                    AgentName = m.AgentName,
                    CreatedAt = m.CreatedAt
                }).ToList()
            }).ToList();

            return new ChatHistoryDto
            {
                Sessions = sessionDtos,
                TotalCount = totalCount,
                Page = page,
                PageSize = pageSize
            };
        }

        public async Task<ChatSessionDto?> GetChatSessionAsync(int userId, int sessionId)
        {
            var session = await _context.ChatSessions
                .Include(s => s.Messages.OrderBy(m => m.CreatedAt))
                .FirstOrDefaultAsync(s => s.Id == sessionId && s.UserId == userId);

            if (session == null)
            {
                return null;
            }

            return new ChatSessionDto
            {
                Id = session.Id,
                Title = session.Title,
                IsActive = session.IsActive,
                CreatedAt = session.CreatedAt,
                Messages = session.Messages.Select(m => new ChatMessageDto
                {
                    Id = m.Id,
                    Content = m.Content,
                    Role = m.Role,
                    AgentName = m.AgentName,
                    CreatedAt = m.CreatedAt
                }).ToList()
            };
        }

        public async Task<bool> DeleteChatSessionAsync(int userId, int sessionId)
        {
            var session = await _context.ChatSessions
                .FirstOrDefaultAsync(s => s.Id == sessionId && s.UserId == userId);

            if (session == null)
            {
                return false;
            }

            _context.ChatSessions.Remove(session);
            await _context.SaveChangesAsync();
            return true;
        }
    }
}