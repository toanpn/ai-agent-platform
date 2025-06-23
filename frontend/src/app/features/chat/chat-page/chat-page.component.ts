import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ChatSidebarComponent } from '../components/chat-sidebar/chat-sidebar.component';
import { ChatMessagesComponent } from '../components/chat-messages/chat-messages.component';
import { ChatInputComponent } from '../components/chat-input/chat-input.component';
import { ChatStateService } from '../chat-state.service';
import { Conversation } from '../../../core/services/chat.service';
import { Agent } from '../../../core/services/agent.service';

@Component({
	selector: 'app-chat-page',
	standalone: true,
	imports: [CommonModule, ChatSidebarComponent, ChatMessagesComponent, ChatInputComponent],
	templateUrl: './chat-page.component.html',
	styleUrls: ['./chat-page.component.scss'],
})
export class ChatPageComponent implements OnInit, OnDestroy {
	chatState = inject(ChatStateService);
	private router = inject(Router);

	private initialAgent: Agent | undefined;

	constructor() {
		const navigation = this.router.getCurrentNavigation();
		this.initialAgent = navigation?.extras.state?.['agent'] as Agent;
	}

	ngOnInit(): void {
		if (this.initialAgent) {
			this.chatState.selectAgent(this.initialAgent);
		}
	}

	ngOnDestroy(): void {
		// The lifecycle is now managed by AuthService
	}

	onConversationSelected(conversation: Conversation): void {
		this.chatState.selectConversation(conversation);
	}

	onStartNewChat(): void {
		this.chatState.startNewChat();
	}

	onSendMessage(messageText: string): void {
		this.chatState.sendMessage(messageText);
	}

	onAgentSelected(agent: Agent): void {
		this.chatState.selectAgent(agent);
	}
} 