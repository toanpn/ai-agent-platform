import { effect, inject, Injectable, signal, computed, DestroyRef } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { EMPTY, forkJoin, lastValueFrom, BehaviorSubject, Subject } from 'rxjs';
import { catchError, tap, debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { Agent } from '../../core/services/agent.service';
import { ChatService, Conversation, Message } from '../../core/services/chat.service';
import { NotificationService } from '../../core/services/notification.service';
import { AgentStateService } from './agent-state.service';

@Injectable({
	providedIn: 'root',
})
export class ChatStateService {
	private chatService = inject(ChatService);
	private notificationService = inject(NotificationService);
	private destroyRef = inject(DestroyRef);
	private agentState = inject(AgentStateService);

	// --- Private state management ---
	private readonly searchTrigger = new BehaviorSubject<string>('');
	private readonly loadMessagesTrigger = new Subject<string | null>();

	// State Signals
	readonly conversations = signal<Conversation[]>([]);
	readonly activeConversation = signal<Conversation | null>(null);
	readonly messages = signal<Message[]>([]);
	readonly isLoading = signal<boolean>(false);
	readonly isSearching = signal<boolean>(false);
	readonly agents = this.agentState.agents$;
	readonly selectedAgent = signal<Agent | null>(null);

	// Computed Signals
	readonly currentConversationId = computed(() => this.activeConversation()?.id);

	constructor() {
		// Effect to trigger message loading when the active conversation changes
		effect(() => {
			const conversation = this.activeConversation();
			this.loadMessagesTrigger.next(conversation?.id ?? null);
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

		// Reactive conversation loading
		this.searchTrigger
			.pipe(
				debounceTime(300),
				distinctUntilChanged(),
				tap(() => this.isSearching.set(true)),
				switchMap((query) => {
					const request = query
						? this.chatService.searchConversations(query)
						: this.chatService.loadConversations();

					return request.pipe(
						catchError((error: Error) => {
							this.notificationService.showError('Failed to load conversations.');
							console.error('Failed to search or load conversations.', error);
							return EMPTY;
						}),
					);
				}),
				tap(() => this.isSearching.set(false)),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe((conversations) => {
				this.conversations.set(conversations);
			});

		// Reactive message loading
		this.loadMessagesTrigger
			.pipe(
				distinctUntilChanged(),
				tap((conversationId) => {
					if (conversationId) {
						this.conversations.update((convos) =>
							convos.map((c) => (c.id === conversationId ? { ...c, loading: true } : c)),
						);
					}
				}),
				switchMap((conversationId) => {
					if (!conversationId) {
						this.messages.set([]);
						return EMPTY;
					}
					return this.chatService.loadChat(conversationId).pipe(
						catchError((error: Error) => {
							this.notificationService.showError('Failed to load chat messages.');
							this.conversations.update((convos) =>
								convos.map((c) => (c.id === conversationId ? { ...c, loading: false } : c)),
							);
							return EMPTY;
						}),
					);
				}),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe((chat) => {
				this.messages.set(chat?.messages || []);
				this.conversations.update((convos) =>
					convos.map((c) => (c.id === chat.id ? { ...c, loading: false } : c)),
				);
			});
	}

	initialize(): void {
		// Initialization logic can be triggered from auth service
		this.loadConversations();
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
		if (conversationId) {
			this.conversations.update((convos) =>
				convos.map((c) => (c.id === conversationId ? { ...c, loading: true } : c)),
			);
		}

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
					title: response.sessionTitle || `Conversation #${response.sessionId}`,
					timestamp: new Date(),
				};
				this.conversations.update((convos) => [newConversation, ...convos]);
				this.activeConversation.set(newConversation);
			} else if (response.sessionTitle) {
				this.conversations.update((convos) =>
					convos.map((c) => (c.id === conversationId ? { ...c, title: response.sessionTitle! } : c)),
				);
				if (this.activeConversation()?.id === conversationId) {
					this.activeConversation.update((ac) => (ac ? { ...ac, title: response.sessionTitle! } : null));
				}
			}

			// Move conversation to the top
			const convos = this.conversations();
			const updatedConvo = convos.find(c => c.id === conversationId);
			if (updatedConvo) {
				const filteredConvos = convos.filter(c => c.id !== conversationId);
				this.conversations.set([{...updatedConvo, timestamp: new Date()}, ...filteredConvos]);
			}
		} catch (error) {
			this.notificationService.showError('Failed to send message.');
			this.messages.update((msgs) => msgs.filter((m) => m.id !== optimisticMessage.id));
		} finally {
			this.isLoading.set(false);
			if (conversationId) {
				// Stop loading indicator
				this.conversations.update((convos) =>
					convos.map((c) => (c.id === conversationId ? { ...c, loading: false } : c)),
				);
				
				// Move updated conversation to the top
				const conversations = this.conversations();
				const conversationToMove = conversations.find(c => c.id === conversationId);
				if (conversationToMove) {
					const otherConversations = conversations.filter(c => c.id !== conversationId);
					this.conversations.set([
						{ ...conversationToMove, timestamp: new Date() }, 
						...otherConversations
					]);
				}
			}
		}
	}

	async deleteConversation(conversationId: string): Promise<void> {
		try {
			await lastValueFrom(this.chatService.deleteConversation(conversationId));

			this.conversations.update((convos) => convos.filter((c) => c.id !== conversationId));

			if (this.activeConversation()?.id === conversationId) {
				this.activeConversation.set(null);
				this.messages.set([]);
			}

			this.notificationService.showSuccess('Conversation deleted successfully.');
		} catch (error) {
			this.notificationService.showError('Failed to delete conversation.');
			console.error('Failed to delete conversation', error);
		}
	}

	// --- Public Data Loading ---
	loadConversations(): void {
		this.searchTrigger.next('');
	}

	searchConversations(query: string): void {
		this.searchTrigger.next(query);
	}

	private resetState(): void {
		this.conversations.set([]);
		this.activeConversation.set(null);
		this.messages.set([]);
		this.isLoading.set(false);
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
