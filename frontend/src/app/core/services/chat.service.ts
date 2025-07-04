import { inject, Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { NotificationService } from './notification.service';
import { HashbrownService } from './hashbrown.service';

/**
 * Interface for chat stream response
 */
export interface StreamResponse {
	chunk?: string;
	sessionId?: string;
	done?: boolean;
	error?: string;
}

/**
 * Represents a chat message between the user and assistant
 */
export interface Message {
	/** Unique identifier for the message */
	id: string;

	/** Content of the message */
	text: string;

	/** Who sent the message */
	sender: 'user' | 'assistant' | 'system';

	/** When the message was sent */
	timestamp: Date;

	/** The conversation this message belongs to */
	conversationId: string;

	/** The name of the agent that sent the message (if applicable) */
	agentName?: string;

	// Enhanced response fields
	masterAgentThinking?: string;
	agentsUsed?: string[];
	toolsUsed?: string[];
	executionDetails?: ExecutionDetails;
	metadata?: { [key: string]: unknown };
	error?: string;
}

/**
 * Represents a chat conversation between the user and the AI
 */
export interface Conversation {
	/** Unique identifier for the conversation */
	id: string;

	/** Title of the conversation */
	title: string;

	/** When the conversation was created or last updated */
	timestamp: Date;

	/** Messages in this conversation */
	messages?: Message[];

	/** Whether the conversation is currently loading messages */
	loading?: boolean;
}

/**
 * Backend DTO interfaces corresponding to the ASP.NET Core models. Keeping them
 * at the top-level (outside the service) allows re-use across the file while
 * preventing nested interface declarations that are illegal in TypeScript.
 */
export interface ChatMessageDto {
	id: number;
	content: string;
	role: string;
	agentName?: string;
	createdAt: string;
	metadata?: string;
}

export interface ChatSessionDto {
	id: number;
	title?: string;
	isActive: boolean;
	createdAt: string;
	updatedAt?: string;
	messages?: ChatMessageDto[];
}

export interface ChatResponseDto {
	response: string;
	agentName: string;
	sessionId: number;
	sessionTitle?: string;
	timestamp: string;
	success: boolean;
	error?: string;
	masterAgentThinking?: string;
	agentsUsed: string[];
	toolsUsed: string[];
	executionDetails: ExecutionDetails;
	metadata: { [key: string]: unknown };
}

export interface ChatHistoryDto {
	sessions: ChatSessionDto[];
	totalCount: number;
	page: number;
	pageSize: number;
}

export interface ExecutionStep {
	toolName: string;
	toolInput: string;
	observation: string;
}

export interface ExecutionDetails {
	executionSteps: ExecutionStep[];
	totalSteps: number;
}

export interface PromptEnhancementResponseDto {
	assigned_agents: string[];
	key_details_extracted: string;
	original_user_query: string;
	summary: string;
	user_facing_prompt: string;
}

/**
 * ChatService manages all chat-related operations including loading conversations,
 * sending messages, and managing conversation state. It is a stateless service
 * that acts as a gateway to the backend API.
 */
@Injectable({
	providedIn: 'root',
})
export class ChatService {
	private api = inject(ApiService);
	private hashbrown = inject(HashbrownService);

	/**
	 * Fetch chat history (paginated list of chat sessions) and transform to the
	 * local `Conversation` model expected by the UI components.
	 */
	loadConversations(page: number = 1, pageSize: number = 100): Observable<Conversation[]> {
		const params = new HttpParams().set('page', page).set('pageSize', pageSize);

		return this.api.get<ChatHistoryDto>('/Chat/history', params).pipe(
			map((history) =>
				history.sessions.map<Conversation>((session: ChatSessionDto) => ({
					id: session.id.toString(),
					title: session.title || '',
					timestamp: session.updatedAt ? new Date(session.updatedAt) : new Date(session.createdAt),
				})),
			),
		);
	}

	/**
	 * Search for conversations by a query term.
	 */
	searchConversations(query: string, page: number = 1, pageSize: number = 100): Observable<Conversation[]> {
		const params = new HttpParams()
			.set('query', query)
			.set('page', page)
			.set('pageSize', pageSize);

		return this.api.get<ChatHistoryDto>('/Chat/history/search', params).pipe(
			map((history) =>
				history.sessions.map<Conversation>((session: ChatSessionDto) => ({
					id: session.id.toString(),
					title: session.title || '',
					timestamp: session.updatedAt ? new Date(session.updatedAt) : new Date(session.createdAt),
				})),
			),
		);
	}

	/**
	 * Retrieve a single chat session (with messages) and transform into the local
	 * models used by the application.
	 */
	loadChat(conversationId: string): Observable<Conversation> {
		return this.api.get<ChatSessionDto>(`/Chat/sessions/${conversationId}`).pipe(
			map((session) => {
				const conversation: Conversation = {
					id: session.id.toString(),
					title: session.title || '',
					timestamp: session.updatedAt ? new Date(session.updatedAt) : new Date(session.createdAt),
					messages: (session.messages || []).map((m: ChatMessageDto) => this.mapMessageDto(m, session.id)),
				};
				return conversation;
			}),
		);
	}

	/**
	 * Send a message and get a streaming response.
	 * @param text - The message text to send.
	 * @param agentName - The name of the agent to use.
	 * @param conversationId - The ID of the conversation.
	 * @returns An observable of the streaming response.
	 */
	sendMessage(text: string, agentName: string, conversationId?: string): Observable<StreamResponse> {
		return this.hashbrown.streamChat({
			message: text,
			sessionId: conversationId,
			agentId: agentName,
		});
	}

	/**
	 * Send a message without streaming.
	 * @param text The message text to send.
	 * @param agentName The name of the agent to use.
	 * @param conversationId The ID of the conversation.
	 * @returns An observable of the response message.
	 */
	sendMessageNonStreaming(
		text: string,
		agentName?: string,
		conversationId?: string,
	): Observable<ChatResponseDto> {
		return this.api.post<ChatResponseDto>('/Chat/message', {
			message: text,
			sessionId: conversationId,
			agentName,
		});
	}

	/**
	 * Deletes a conversation by its ID.
	 * @param conversationId The ID of the conversation to delete.
	 * @returns An observable that completes when the deletion is successful.
	 */
	deleteConversation(conversationId: string): Observable<void> {
		return this.api.delete<void>(`/Chat/sessions/${conversationId}`);
	}

	/**
	 * Enhance a prompt using the prompt enhancement API.
	 * @param message The message text to enhance.
	 * @returns An observable of the enhanced prompt.
	 */
	enhancePrompt(message: string): Observable<PromptEnhancementResponseDto> {
		return this.api.post<{ enhancedPrompt: PromptEnhancementResponseDto }>('/Chat/enhance-prompt', {
			message: message,
		}).pipe(
			map(response => response.enhancedPrompt)
		);
	}

	/**
	 * Helper method to convert the backend ChatMessageDto into the local `Message` model.
	 */
	private mapMessageDto(dto: ChatMessageDto, conversationId: number | string): Message {
		const message: Message = {
			id: dto.id.toString(),
			text: dto.content,
			sender: dto.role === 'user' ? 'user' : 'assistant',
			timestamp: new Date(dto.createdAt),
			conversationId: conversationId.toString(),
			agentName: dto.agentName,
		};

		// Parse metadata if available for assistant messages
		if (dto.metadata && dto.role === 'assistant') {
			try {
				const metadata = JSON.parse(dto.metadata);
				message.masterAgentThinking = metadata.masterAgentThinking;
				message.agentsUsed = metadata.agentsUsed;
				message.toolsUsed = metadata.toolsUsed;
				message.executionDetails = metadata.executionDetails;
				message.metadata = metadata.metadata;
			} catch (error) {
				console.warn('Failed to parse message metadata:', error);
			}
		}

		return message;
	}
}
