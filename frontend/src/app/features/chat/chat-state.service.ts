import { inject, Injectable } from '@angular/core';
import { BehaviorSubject, throwError, of, Subject } from 'rxjs';
import { catchError, tap, takeUntil, switchMap, withLatestFrom, filter, finalize, map } from 'rxjs/operators';
import { Agent, AgentService } from '../../core/services/agent.service';
import { ChatService, Conversation, Message } from '../../core/services/chat.service';
import { NotificationService } from '../../core/services/notification.service';

@Injectable({
	providedIn: 'root',
})
export class ChatStateService {
	private chatService = inject(ChatService);
	private agentService = inject(AgentService);
	private notificationService = inject(NotificationService);

	private destroy$ = new Subject<void>();

	// Action Subjects
	private selectConversationAction$ = new Subject<Conversation>();
	private sendMessageAction$ = new Subject<string>();
	private startNewChatAction$ = new Subject<void>();

	// State
	private conversations = new BehaviorSubject<Conversation[]>([]);
	private activeConversation = new BehaviorSubject<Conversation | null>(null);
	private messages = new BehaviorSubject<Message[]>([]);
	private isLoading = new BehaviorSubject<boolean>(false);
	private agents = new BehaviorSubject<Agent[]>([]);
	private selectedAgent = new BehaviorSubject<Agent | null>(null);

	// Public Observables
	public conversations$ = this.conversations.asObservable();
	public activeConversation$ = this.activeConversation.asObservable();
	public messages$ = this.messages.asObservable();
	public isLoading$ = this.isLoading.asObservable();
	public agents$ = this.agents.asObservable();
	public selectedAgent$ = this.selectedAgent.asObservable();

	constructor() {
		this.handleSelectConversation();
		this.handleSendMessage();
		this.handleStartNewChat();
	}

	init(initialAgent?: Agent): void {
		if (initialAgent) {
			this.selectedAgent.next(initialAgent);
		}
		this.loadInitialData();
	}

	destroy(): void {
		this.destroy$.next();
		this.destroy$.complete();
		this.destroy$ = new Subject<void>();
		this.resetState();
	}

	// --- Public Action Triggers ---

	selectConversation(conversation: Conversation): void {
		this.selectConversationAction$.next(conversation);
	}

	startNewChat(): void {
		this.startNewChatAction$.next();
	}

	selectAgent(agent: Agent): void {
		this.selectedAgent.next(agent);
	}

	sendMessage(messageText: string): void {
		this.sendMessageAction$.next(messageText);
	}

	// --- Private Stream Handlers ---

	private loadInitialData(): void {
		this.agentService
			.getAgents()
			.pipe(takeUntil(this.destroy$))
			.subscribe((agents) => {
				this.agents.next(agents);
				if (!this.selectedAgent.value && agents.length > 0) {
					this.selectedAgent.next(agents[0]);
				}
			});

		this.chatService
			.loadConversations()
			.pipe(takeUntil(this.destroy$))
			.subscribe((conversations) => this.conversations.next(conversations));
	}

	private handleSelectConversation(): void {
		this.selectConversationAction$
			.pipe(
				tap((conversation) => this.activeConversation.next(conversation)),
				switchMap((conversation) =>
					this.chatService.loadChat(conversation.id).pipe(
						catchError((error) => {
							this.notificationService.showError('Failed to load chat messages.');
							console.error(error);
							return of(null);
						}),
					),
				),
				takeUntil(this.destroy$),
			)
			.subscribe((chat) => {
				this.messages.next(chat?.messages || []);
			});
	}

	private handleSendMessage(): void {
		this.sendMessageAction$
			.pipe(
				withLatestFrom(this.selectedAgent$, this.activeConversation$),
				filter(([messageText, selectedAgent]) => {
					if (!messageText.trim()) return false;
					if (!selectedAgent) {
						this.notificationService.showError('Please select an agent first.');
						return false;
					}
					return true;
				}),
				switchMap(([messageText, selectedAgent, currentConversation]) => {
					const optimisticMessage = this.createOptimisticMessage(
						messageText,
						currentConversation?.id,
					);
					this.messages.next([...this.messages.value, optimisticMessage]);
					this.isLoading.next(true);

					return this.chatService
						.sendMessageNonStreaming(messageText, selectedAgent!.name, currentConversation?.id)
						.pipe(
							switchMap((response) => {
								const assistantMessage: Message = {
									id: `msg-${Date.now()}`,
									text: response.response,
									sender: 'assistant',
									timestamp: new Date(response.timestamp),
									conversationId: response.sessionId.toString(),
									agentName: response.agentName,
								};

								this.messages.next([
									...this.messages.value.filter((m) => m.id !== optimisticMessage.id),
									assistantMessage,
								]);

								if (response.sessionId && !currentConversation?.id) {
									this.activeConversation.next({
										id: response.sessionId.toString(),
										title: `Conversation ${response.sessionId}`,
										timestamp: new Date(),
									});
									return this.chatService
										.loadConversations()
										.pipe(map((convos) => ({ convos })));
								}
								return of({ convos: null });
							}),
							tap(({ convos }) => {
								if (convos) this.conversations.next(convos);
							}),
							finalize(() => {
								this.isLoading.next(false);
							}),
							catchError((err) => {
								this.notificationService.showError('Failed to send message.');
								this.messages.next(this.messages.value.filter((m) => m.id !== optimisticMessage.id));
								return throwError(() => err);
							}),
						);
				}),
				takeUntil(this.destroy$),
			)
			.subscribe();
	}

	private handleStartNewChat(): void {
		this.startNewChatAction$.pipe(takeUntil(this.destroy$)).subscribe(() => {
			this.activeConversation.next(null);
			this.messages.next([]);
		});
	}

	private resetState(): void {
		this.conversations.next([]);
		this.activeConversation.next(null);
		this.messages.next([]);
		this.isLoading.next(false);
		this.agents.next([]);
		this.selectedAgent.next(null);
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