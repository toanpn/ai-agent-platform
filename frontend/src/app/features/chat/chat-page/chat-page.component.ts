import { Component, inject, ChangeDetectionStrategy, ViewChild, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatSidebarComponent } from '../components/chat-sidebar/chat-sidebar.component';
import { ChatMessagesComponent } from '../components/chat-messages/chat-messages.component';
import { ChatInputComponent } from '../components/chat-input/chat-input.component';
import { AgentParticipantsListComponent } from '../components/agent-participants-list/agent-participants-list.component';
import { ChatWelcomeComponent } from '../components/chat-welcome/chat-welcome.component';
import { ChatStateService } from '../chat-state.service';
import { Conversation } from '../../../core/services/chat.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
	selector: 'app-chat-page',
	standalone: true,
	imports: [
		CommonModule,
		ChatSidebarComponent,
		ChatMessagesComponent,
		ChatInputComponent,
		AgentParticipantsListComponent,
		ChatWelcomeComponent,
		TranslateModule,
	],
	templateUrl: './chat-page.component.html',
	styleUrls: ['./chat-page.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent implements OnInit {
	readonly chatState = inject(ChatStateService);
	isTyping = signal(false);

	@ViewChild(ChatInputComponent) chatInput!: ChatInputComponent;

	ngOnInit(): void {
		this.chatState.loadConversations();
	}

	onConversationSelected(conversation: Conversation): void {
		this.chatState.selectConversation(conversation);
		this.isTyping.set(false);
		if (this.chatInput) {
			this.chatInput.messageText.set('');
		}
	}

	onStartNewChat(): void {
		this.chatState.startNewChat();
		this.isTyping.set(false);
		if (this.chatInput) {
			this.chatInput.messageText.set('');
		}
	}

	onSendMessage(messageText: string): void {
		this.chatState.sendMessage(messageText);
		this.isTyping.set(false);
	}

	onPromptClicked(promptText: string): void {
		this.chatInput.setPrompt(promptText);
		this.isTyping.set(true);
	}

	onTyping(isTyping: boolean): void {
		this.isTyping.set(isTyping);
	}
} 