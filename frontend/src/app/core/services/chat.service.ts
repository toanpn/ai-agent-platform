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
	sender: 'user' | 'assistant';

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
}

export interface ChatSessionDto {
	id: number;
	title?: string;
	isActive: boolean;
	createdAt: string;
	messages?: ChatMessageDto[];
}

export interface ChatResponseDto {
	response: string;
	agentName: string;
	sessionId: number;
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
	private notificationService = inject(NotificationService);

	/**
	 * Fetch chat history (paginated list of chat sessions) and transform to the
	 * local `Conversation` model expected by the UI components.
	 */
	loadConversations(page: number = 1, pageSize: number = 50): Observable<Conversation[]> {
		const params = new HttpParams().set('page', page).set('pageSize', pageSize);

		return this.api.get<ChatHistoryDto>('/Chat/history', params).pipe(
			map((history) =>
				history.sessions.map<Conversation>((session: ChatSessionDto) => ({
					id: session.id.toString(),
					title: session.title || `Session ${session.id}`,
					timestamp: new Date(session.createdAt),
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
					title: session.title || `Session ${session.id}`,
					timestamp: new Date(session.createdAt),
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
	 * Helper method to convert the backend ChatMessageDto into the local `Message` model.
	 */
	private mapMessageDto(dto: ChatMessageDto, conversationId: number | string): Message {
		return {
			id: dto.id.toString(),
			text: dto.content,
			sender: dto.role === 'user' ? 'user' : 'assistant',
			timestamp: new Date(dto.createdAt),
			conversationId: conversationId.toString(),
			agentName: dto.agentName,
		};
	}
}
