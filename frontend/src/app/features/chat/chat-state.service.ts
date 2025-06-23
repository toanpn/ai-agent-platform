import { effect, inject, Injectable, signal, computed, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, forkJoin, lastValueFrom } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { Agent, AgentService } from '../../core/services/agent.service';
import { ChatService, Conversation, Message } from '../../core/services/chat.service';
import { NotificationService } from '../../core/services/notification.service';
import { toObservable } from '@angular/core/rxjs-interop';

@Injectable({
	providedIn: 'root',
})
export class ChatStateService {
	private chatService = inject(ChatService);
	private agentService = inject(AgentService);
	private notificationService = inject(NotificationService);
	private destroyRef = inject(DestroyRef);

	// State Signals
	readonly conversations = signal<Conversation[]>([]);
	readonly activeConversation = signal<Conversation | null>(null);
	readonly messages = signal<Message[]>([]);
	readonly isLoading = signal<boolean>(false);
	readonly agents = signal<Agent[]>([]);
	readonly selectedAgent = signal<Agent | null>(null);

	// Computed Signals
	readonly currentConversationId = computed(() => this.activeConversation()?.id);

	constructor() {
		this.loadInitialData();

		// Effect to load messages when the active conversation changes
		effect(() => {
			const conversation = this.activeConversation();
			if (conversation) {
				this.loadMessagesForConversation(conversation.id);
			} else {
				this.messages.set([]);
			}
		});

		// React to changes in selectedAgent using toObservable
		toObservable(this.selectedAgent)
			.pipe(
				tap((agent) => {
					if (agent) {
						// Logic to handle agent changes if needed in the future
						console.log(`Agent selected: ${agent.name}`);
					}
				}),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	initialize(): void {
		// Initialization logic can be triggered from auth service
		this.loadInitialData();
	}

	destroy(): void {
		this.resetState();
	}

	// --- Public Actions ---

	selectConversation(conversation: Conversation): void {
		this.activeConversation.set(conversation);
	}

	startNewChat(): void {
		this.activeConversation.set(null);
	}

	selectAgent(agent: Agent): void {
		this.selectedAgent.set(agent);
	}

	async sendMessage(messageText: string): Promise<void> {
		const agent = this.selectedAgent();
		if (!messageText.trim()) {
			this.notificationService.showError('Please type a message.');
			return;
		}

		const conversationId = this.currentConversationId();
		const optimisticMessage = this.createOptimisticMessage(messageText, conversationId);

		this.messages.update((msgs) => [...msgs, optimisticMessage]);
		this.isLoading.set(true);

		try {
			const response = await lastValueFrom(
				this.chatService.sendMessageNonStreaming(messageText, agent?.name, conversationId),
			);

			const userMessage: Message = { ...optimisticMessage, id: `msg-user-${Date.now()}` };
			const assistantMessage: Message = {
				id: `msg-assistant-${Date.now()}`,
				text: response.response,
				sender: 'assistant',
				timestamp: new Date(response.timestamp),
				conversationId: response.sessionId.toString(),
				agentName: response.agentName,
				masterAgentThinking: response.masterAgentThinking,
				agentsUsed: response.agentsUsed,
				toolsUsed: response.toolsUsed,
				executionDetails: response.executionDetails,
				metadata: response.metadata,
				error: response.success ? undefined : response.error,
			};

			this.messages.update((msgs) => [
				...msgs.filter((m) => m.id !== optimisticMessage.id),
				userMessage,
				assistantMessage,
			]);

			if (!conversationId) {
				const newConversation = {
					id: response.sessionId.toString(),
					title: `Conversation ${response.sessionId}`,
					timestamp: new Date(),
				};
				this.conversations.update((convos) => [newConversation, ...convos]);
				this.activeConversation.set(newConversation);
			}
		} catch (error) {
			this.notificationService.showError('Failed to send message.');
			this.messages.update((msgs) => msgs.filter((m) => m.id !== optimisticMessage.id));
		} finally {
			this.isLoading.set(false);
		}
	}

	// --- Private Data Loading ---

	private loadInitialData(): void {
		this.isLoading.set(true);
		forkJoin({
			agents: this.agentService.getAgents(),
			conversations: this.chatService.loadConversations(),
		})
			.pipe(
				catchError((error: Error) => {
                    this.notificationService.showError('Failed to load initial data.');
                    console.error('Failed to load initial data.', error);
					return EMPTY;
				}),
				tap(() => this.isLoading.set(false)),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe(({ agents, conversations }) => {
				this.agents.set(agents);
				this.conversations.set(conversations);
			});
	}

	private loadMessagesForConversation(conversationId: string): void {
		this.isLoading.set(true);
		this.chatService
			.loadChat(conversationId)
			.pipe(
				catchError(() => {
					this.notificationService.showError('Failed to load chat messages.');
					return EMPTY;
				}),
				tap(() => this.isLoading.set(false)),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe((chat) => {
				this.messages.set(chat?.messages || []);
			});
	}

	private resetState(): void {
		this.conversations.set([]);
		this.activeConversation.set(null);
		this.messages.set([]);
		this.isLoading.set(false);
		this.agents.set([]);
		this.selectedAgent.set(null);
	}

	private createOptimisticMessage(text: string, conversationId?: string): Message {
		return {
			id: `temp-${Date.now()}`,
			text,
			sender: 'user',
			timestamp: new Date(),
			conversationId: conversationId || '',
		};
	}
}
