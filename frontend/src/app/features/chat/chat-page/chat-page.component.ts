import { Component, inject, ChangeDetectionStrategy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatSidebarComponent } from '../components/chat-sidebar/chat-sidebar.component';
import { ChatMessagesComponent } from '../components/chat-messages/chat-messages.component';
import { ChatInputComponent } from '../components/chat-input/chat-input.component';
import { AgentParticipantsListComponent } from '../components/agent-participants-list/agent-participants-list.component';
import { ChatStateService } from '../chat-state.service';
import { Conversation } from '../../../core/services/chat.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
	selector: 'app-chat-page',
	standalone: true,
	imports: [
		CommonModule,
		ChatSidebarComponent,
		ChatMessagesComponent,
		ChatInputComponent,
		AgentParticipantsListComponent,
		TranslateModule,
	],
	templateUrl: './chat-page.component.html',
	styleUrls: ['./chat-page.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent {
	readonly chatState = inject(ChatStateService);
	private readonly translate = inject(TranslateService);

	@ViewChild(ChatInputComponent) chatInput!: ChatInputComponent;

	suggestedPrompts = [
		'CHAT.SUGGESTED_PROMPTS.COMPETITORS',
		'CHAT.SUGGESTED_PROMPTS.SEO',
		'CHAT.SUGGESTED_PROMPTS.MARKETING_MIX',
		'CHAT.SUGGESTED_PROMPTS.CONVERSION_RATE',
	];

	onConversationSelected(conversation: Conversation): void {
		this.chatState.selectConversation(conversation);
	}

	onStartNewChat(): void {
		this.chatState.startNewChat();
	}

	onSendMessage(messageText: string): void {
		this.chatState.sendMessage(messageText);
	}

	onPromptClicked(promptKey: string): void {
		const promptText = this.translate.instant(promptKey);
		this.chatInput.setPrompt(promptText);
	}
} 