import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatSidebarComponent } from '../components/chat-sidebar/chat-sidebar.component';
import { ChatMessagesComponent } from '../components/chat-messages/chat-messages.component';
import { ChatInputComponent } from '../components/chat-input/chat-input.component';
import { ChatStateService } from '../chat-state.service';
import { Conversation } from '../../../core/services/chat.service';
import { Agent } from '../../../core/services/agent.service';
import { TranslateModule } from '@ngx-translate/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
	selector: 'app-chat-page',
	standalone: true,
	imports: [
		CommonModule,
		ChatSidebarComponent,
		ChatMessagesComponent,
		ChatInputComponent,
		MatButtonModule,
		MatIconModule,
		MatTooltipModule,
		TranslateModule,
	],
	templateUrl: './chat-page.component.html',
	styleUrls: ['./chat-page.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent {
	readonly chatState = inject(ChatStateService);

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