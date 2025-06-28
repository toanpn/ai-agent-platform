import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../core/services/chat.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
	selector: 'app-chat-message',
	standalone: true,
	imports: [CommonModule, TranslateModule],
	templateUrl: './chat-message.component.html',
	styleUrls: ['./chat-message.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatMessageComponent {
	message = input.required<Message>();

	isUserMessage = computed(() => this.message().sender === 'user');
	
	formattedTimestamp = computed(() => {
		const date = new Date(this.message().timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	});

	getAgentType(agentName?: string): string {
		if (!agentName) return '';
		if (agentName.toLowerCase().includes('marketing')) return 'marketing';
		if (agentName.toLowerCase().includes('financial')) return 'finance';
		if (agentName.toLowerCase().includes('data')) return 'data';
		return 'default';
	}

	getAgentSpecialty(agentName?: string): string {
		if (!agentName) return '';
		const type = this.getAgentType(agentName);
		switch (type) {
			case 'marketing':
				return 'Marketing';
			case 'finance':
				return 'Finance';
			case 'data':
				return 'Analytics';
			default:
				return '';
		}
	}

	getAgentAvatar(agentName?: string): string {
		if (!agentName) return 'assets/icons/agent.svg';
		const type = this.getAgentType(agentName);
		switch (type) {
			case 'marketing':
				return 'assets/icons/agent-marketing-avatar.png';
			case 'finance':
				return 'assets/icons/agent-finance-avatar.png';
			case 'data':
				return 'assets/icons/agent-data-avatar.png';
			default:
				return 'assets/icons/agent.svg';
		}
	}
}
