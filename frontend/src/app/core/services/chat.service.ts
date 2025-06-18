import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { BehaviorSubject, Observable, tap, catchError, throwError } from 'rxjs';
import { NotificationService } from './notification.service';
import { HashbrownService, StreamResponse } from './hashbrown.service';
import { environment } from '../../../environments/environment';

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
 * ChatService manages all chat-related operations including loading conversations,
 * sending messages, and managing conversation state.
 */
@Injectable({
	providedIn: 'root',
})
export class ChatService {
	/** BehaviorSubject storing all user conversations */
	private conversationsSubject = new BehaviorSubject<Conversation[]>([]);

	/** Observable of all user conversations */
	public conversations$ = this.conversationsSubject.asObservable();

	/** BehaviorSubject storing the currently active conversation */
	private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);

	/** Observable of the currently active conversation */
	public activeConversation$ = this.activeConversationSubject.asObservable();

	/** BehaviorSubject storing messages in the active conversation */
	private messagesSubject = new BehaviorSubject<Message[]>([]);

	/** Observable of messages in the active conversation */
	public messages$ = this.messagesSubject.asObservable();

	/** BehaviorSubject for tracking message streaming state */
	private isStreamingSubject = new BehaviorSubject<boolean>(false);

	/** Observable for message streaming state */
	public isStreaming$ = this.isStreamingSubject.asObservable();

	/** Currently selected agent ID */
	private selectedAgentId: string | null = null;

	/**
	 * Creates an instance of ChatService
	 * @param api - Service for API communication
	 * @param notificationService - Service for displaying notifications
	 */
	constructor(
		private api: ApiService,
		private notificationService: NotificationService,
		private hashbrown: HashbrownService,
	) {}

	/**
	 * Set the agent to use for chat
	 * @param agentId - ID of the agent to use
	 */
	selectAgent(agentId: string): void {
		this.selectedAgentId = agentId;
	}

	/**
	 * Load all user conversations from the API
	 * @returns Observable of conversation array
	 */
	loadConversations(): Observable<Conversation[]> {
		return this.api.get<Conversation[]>('/chat/sessions').pipe(
			tap((conversations) => {
				this.conversationsSubject.next(conversations);
			}),
			catchError((error) => {
				this.handleError('Failed to load conversations', error);
				return throwError(() => error);
			}),
		);
	}

	/**
	 * Load a specific conversation and its messages
	 * @param conversationId - ID of the conversation to load
	 * @returns Observable of the loaded conversation
	 */
	loadChat(conversationId: string): Observable<Conversation> {
		return this.api.get<Conversation>(`/chat/sessions/${conversationId}/messages`).pipe(
			tap((conversation) => {
				this.activeConversationSubject.next(conversation);
				this.messagesSubject.next(conversation.messages || []);
			}),
			catchError((error) => {
				this.handleError('Failed to load conversation', error);
				return throwError(() => error);
			}),
		);
	}

	/**
	 * Start a new chat conversation
	 * Creates a temporary conversation object until the first message is sent
	 */
	startNewChat(): void {
		const newConversation: Conversation = {
			id: '', // Will be assigned by the server
			title: 'New Conversation',
			timestamp: new Date(),
		};

		this.activeConversationSubject.next(newConversation);
		this.messagesSubject.next([]);
	}

	/**
	 * Send a message to the active conversation
	 * @param text - The message text to send
	 * @returns Observable of the server response message
	 */
	sendMessage(text: string): Observable<Message> {
		const activeConversation = this.activeConversationSubject.value;

		if (!text.trim()) {
			return throwError(() => new Error('Message cannot be empty'));
		}

		if (!this.selectedAgentId) {
			return throwError(() => new Error('No agent selected'));
		}

		// Create optimistic message for immediate UI update
		const optimisticMessage = this.createOptimisticMessage(text, activeConversation);

		// Add optimistic message to current messages
		this.addMessageToConversation(optimisticMessage);

		// Set streaming state to true
		this.isStreamingSubject.next(true);

		// Create placeholder for assistant response
		const assistantMessage: Message = {
			id: 'streaming-' + Date.now(),
			text: '',
			sender: 'assistant',
			timestamp: new Date(),
			conversationId: activeConversation?.id || '',
		};

		this.addMessageToConversation(assistantMessage);

		// Use Hashbrown streaming service
		this.hashbrown
			.streamChat({
				message: text,
				sessionId: activeConversation?.id || undefined,
				agentId: this.selectedAgentId,
			})
			.subscribe({
				next: (response: StreamResponse) => {
					// Update the streaming message content incrementally
					if (response.chunk) {
						const currentMessages = this.messagesSubject.value;
						const updatedMessages = currentMessages.map((msg) => {
							if (msg.id === assistantMessage.id) {
								return { ...msg, text: msg.text + response.chunk };
							}
							return msg;
						});
						this.messagesSubject.next(updatedMessages);
					}

					// Handle session ID if this is a new conversation
					if (response.sessionId && activeConversation && !activeConversation.id) {
						this.updateNewConversation(activeConversation, response.sessionId);

						// Update the conversation ID for both messages
						const currentMessages = this.messagesSubject.value;
						const updatedMessages = currentMessages.map((msg) => {
							if (msg.id === optimisticMessage.id || msg.id === assistantMessage.id) {
								return {
									...msg,
									conversationId: response.sessionId || msg.conversationId,
								};
							}
							return msg;
						});
						this.messagesSubject.next(updatedMessages);
					}
				},
				error: (error) => {
					this.handleMessageError(optimisticMessage);
					// Remove the streaming message
					const currentMessages = this.messagesSubject.value;
					this.messagesSubject.next(
						currentMessages.filter((msg) => msg.id !== assistantMessage.id),
					);
					this.isStreamingSubject.next(false);
				},
				complete: () => {
					// Replace streaming ID with permanent ID when completed
					const currentMessages = this.messagesSubject.value;
					const updatedMessages = currentMessages.map((msg) => {
						if (msg.id === assistantMessage.id) {
							return { ...msg, id: 'msg-' + Date.now() };
						}
						return msg;
					});
					this.messagesSubject.next(updatedMessages);
					this.isStreamingSubject.next(false);
				},
			});

		// Return an observable that will be immediately completed
		// The actual streaming is handled via the subscription above
		return new Observable<Message>((observer) => {
			observer.next(optimisticMessage);
			observer.complete();
		});
	}

	/**
	 * Send a message without streaming (fallback method)
	 * @param text - The message text to send
	 * @param conversationId - ID of the conversation
	 * @returns Observable of the response
	 */
	sendMessageNonStreaming(text: string): Observable<Message> {
		const activeConversation = this.activeConversationSubject.value;

		if (!this.selectedAgentId) {
			return throwError(() => new Error('No agent selected'));
		}

		return this.api
			.post<Message>('/chat', {
				message: text,
				sessionId: activeConversation?.id || undefined,
				agentId: this.selectedAgentId,
			})
			.pipe(
				tap((response) => {
					if (activeConversation && !activeConversation.id && response.conversationId) {
						this.updateNewConversation(activeConversation, response.conversationId);
					}
				}),
				catchError((error) => {
					this.notificationService.showError('Failed to send message. Please try again.');
					return throwError(() => error);
				}),
			);
	}

	/**
	 * Creates an optimistic message object for immediate UI feedback
	 * @param text - Message text
	 * @param conversation - The active conversation
	 * @returns A new Message object
	 * @private
	 */
	private createOptimisticMessage(text: string, conversation: Conversation | null): Message {
		return {
			id: 'temp-' + Date.now(),
			text,
			sender: 'user',
			timestamp: new Date(),
			conversationId: conversation?.id || '',
		};
	}

	/**
	 * Adds a message to the current message list
	 * @param message - The message to add
	 * @private
	 */
	private addMessageToConversation(message: Message): void {
		const currentMessages = this.messagesSubject.value;
		this.messagesSubject.next([...currentMessages, message]);
	}

	/**
	 * Handles successful message response from the server
	 * @param response - Server response
	 * @param optimisticMessage - The optimistic message to replace
	 * @param activeConversation - The current active conversation
	 * @private
	 */
	private handleMessageResponse(
		response: Message,
		optimisticMessage: Message,
		activeConversation: Conversation | null,
	): void {
		// Replace optimistic message with actual response and add assistant's reply
		const updatedMessages = this.messagesSubject.value
			.filter((msg) => msg.id !== optimisticMessage.id)
			.concat(response);

		this.messagesSubject.next(updatedMessages);

		// Update the active conversation if this is a new conversation
		if (activeConversation && !activeConversation.id && response.conversationId) {
			this.updateNewConversation(activeConversation, response.conversationId);
		}
	}

	/**
	 * Updates the conversation list when a new conversation is created
	 * @param conversation - The current conversation object
	 * @param newId - The server-generated ID for the new conversation
	 * @private
	 */
	private updateNewConversation(conversation: Conversation, newId: string): void {
		const updatedConversation: Conversation = {
			...conversation,
			id: newId,
		};

		// Update active conversation
		this.activeConversationSubject.next(updatedConversation);

		// Update the conversations list
		const conversations = this.conversationsSubject.value;
		this.conversationsSubject.next([updatedConversation, ...conversations]);
	}

	/**
	 * Handles message send error by removing the optimistic message
	 * @param optimisticMessage - The optimistic message to remove
	 * @private
	 */
	private handleMessageError(optimisticMessage: Message): void {
		// Remove the optimistic message from the UI
		const currentMessages = this.messagesSubject.value;
		this.messagesSubject.next(currentMessages.filter((msg) => msg.id !== optimisticMessage.id));

		this.notificationService.showError('Failed to send message. Please try again.');
	}

	/**
	 * Generic error handler for chat operations
	 * @param message - User-friendly error message
	 * @param error - The error object
	 * @private
	 */
	private handleError(message: string, error: any): void {
		console.error(message, error);
		this.notificationService.showError(message);
	}
}
