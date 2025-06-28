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
#pragma warning disable CS8600 // Converting null literal or possible null value to non-nullable type.
                session = await _context.ChatSessions
                    .Include(s => s.Messages)
                    .FirstOrDefaultAsync(s => s.Id == request.SessionId.Value && s.UserId == userId);
#pragma warning restore CS8600 // Converting null literal or possible null value to non-nullable type.

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
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow,
                };
                _context.ChatSessions.Add(session);
                // No need for SaveChangesAsync here, it will be saved with the message
            }

            session.UpdatedAt = DateTime.UtcNow;

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

            // Determine the main response based on execution steps
            string mainResponse = runtimeResponse.Response;
            string? masterAgentThinking = null;
            string agentName = runtimeResponse.AgentName;

            // If there are execution steps, use the observation with the most content as the main response
            // and treat the Master agent's response as thinking
            if (runtimeResponse.ExecutionDetails?.ExecutionSteps?.Any() == true)
            {
                // Find the execution step with the longest/most complete observation
                var bestStep = runtimeResponse.ExecutionDetails.ExecutionSteps
                    .Where(s => !string.IsNullOrEmpty(s.Observation))
                    .OrderByDescending(s => s.Observation.Length)
                    .FirstOrDefault();

                if (bestStep != null)
                {
                    masterAgentThinking = runtimeResponse.Response; // Master agent's response becomes thinking
                    mainResponse = bestStep.Observation; // Best execution step observation becomes main response
                    agentName = bestStep.ToolName; // Use the actual agent name from the execution step
                }
            }

            // Save agent response
            var agentMessage = new ChatMessage
            {
                ChatSessionId = session.Id,
                Content = mainResponse, // Use the determined main response
                Role = "assistant",
                AgentName = agentName, // Use the determined agent name
                CreatedAt = DateTime.UtcNow
            };

            _context.ChatMessages.Add(agentMessage);
            await _context.SaveChangesAsync();

            string? sessionTitle = null;
            // Check if session needs summarization based on user messages
            var userMessageCount = await _context.ChatMessages
                .CountAsync(m => m.ChatSessionId == session.Id && m.Role == "user");

            // Summarize on the first user message, and every 3 user messages thereafter (1, 4, 7, ...)
            if (userMessageCount % 3 == 1)
            {
                var messagesForSummary = await _context.ChatMessages
                    .Where(m => m.ChatSessionId == session.Id)
                    .OrderBy(m => m.CreatedAt)
                    .Select(m => new MessageHistory { Role = m.Role, Content = m.Content })
                    .ToListAsync();

                var summary = await _runtimeClient.GetSessionSummaryAsync(messagesForSummary);
                if (!string.IsNullOrEmpty(summary))
                {
                    session.Title = summary;
                    sessionTitle = summary;
                    // UpdatedAt is already set at the start of the method
                }
            } else if (string.IsNullOrEmpty(session.Title)) {
                // If there's no title yet, just update the timestamp
                session.UpdatedAt = DateTime.UtcNow;
                await _context.SaveChangesAsync();
            }

            await _context.SaveChangesAsync();

            // Map the enhanced runtime response to ChatResponseDto
            return new ChatResponseDto
            {
                Response = mainResponse, // Use the determined main response
                AgentName = agentName, // Use the determined agent name
                SessionId = session.Id,
                SessionTitle = sessionTitle,
                Timestamp = DateTime.UtcNow,
                Success = runtimeResponse.Success,
                Error = runtimeResponse.Error,
                
                // Enhanced fields
                AgentsUsed = runtimeResponse.AgentsUsed,
                ToolsUsed = runtimeResponse.ToolsUsed,
                ExecutionDetails = new ExecutionDetailsDto
                {
                    TotalSteps = runtimeResponse.ExecutionDetails!.TotalSteps,
                    ExecutionSteps = runtimeResponse.ExecutionDetails.ExecutionSteps.Select(s => new ExecutionStepDto
                    {
                        ToolName = s.ToolName,
                        ToolInput = s.ToolInput,
                        Observation = s.Observation
                    }).ToList()
                },
                Metadata = runtimeResponse.Metadata,
                MasterAgentThinking = masterAgentThinking // Add master agent thinking field
            };
        }

        public async Task<ChatHistoryDto> GetChatHistoryAsync(int userId, int page = 1, int pageSize = 10)
        {
            var query = _context.ChatSessions
                .Where(s => s.UserId == userId)
                .OrderByDescending(s => s.UpdatedAt)
                .ThenByDescending(s => s.CreatedAt);

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
                UpdatedAt = s.UpdatedAt,
                Messages = new List<ChatMessageDto>() // Messages are not needed for the history list
            }).ToList();

            return new ChatHistoryDto
            {
                Sessions = sessionDtos,
                TotalCount = totalCount,
                Page = page,
                PageSize = pageSize
            };
        }

        public async Task<ChatHistoryDto> SearchChatHistoryAsync(int userId, string query, int page = 1, int pageSize = 10)
        {
            var queryable = _context.ChatSessions
                .Where(s => s.UserId == userId && (s.Title != null && s.Title.ToLower().Contains(query.ToLower())))
                .OrderByDescending(s => s.UpdatedAt)
                .ThenByDescending(s => s.CreatedAt);
            
            var totalCount = await queryable.CountAsync();
            var sessions = await queryable
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            var sessionDtos = sessions.Select(s => new ChatSessionDto
            {
                Id = s.Id,
                Title = s.Title,
                IsActive = s.IsActive,
                CreatedAt = s.CreatedAt,
                UpdatedAt = s.UpdatedAt,
                Messages = new List<ChatMessageDto>()
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
                UpdatedAt = session.UpdatedAt,
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

        public async Task<PromptEnhancementResponseDto?> EnhancePromptAsync(string query)
        {
            return await _runtimeClient.EnhancePromptAsync(query);
        }
    }
}