import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../core/services/chat.service';
import { UserMessageComponent } from '../user-message/user-message.component';
import { AgentMessageComponent } from '../agent-message/agent-message.component';

@Component({
	selector: 'app-chat-message',
	standalone: true,
	imports: [CommonModule, UserMessageComponent, AgentMessageComponent],
	templateUrl: './chat-message.component.html',
	styleUrls: ['./chat-message.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatMessageComponent {
	message = input.required<Message>();

	isUserMessage = computed(() => this.message().sender === 'user');
	isSystemMessage = computed(() => this.message().sender === 'system');
}
