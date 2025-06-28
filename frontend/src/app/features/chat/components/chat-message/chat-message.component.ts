import { Component, input, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../core/services/chat.service';
import { TranslateModule } from '@ngx-translate/core';
import { AgentTypeService } from '../../../../core/services/agent-type.service';
import { AgentStateService } from '../../agent-state.service';

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
	private agentTypeService = inject(AgentTypeService);
	private agentStateService = inject(AgentStateService);

	isUserMessage = computed(() => this.message().sender === 'user');

	private agent = computed(() => {
		if (this.isUserMessage() || !this.message().agentName) {
			return undefined;
		}
		return this.agentStateService.getAgentByName(this.message().agentName!);
	});

	agentType = computed(() => {
		return this.agentTypeService.getAgentType(this.agent());
	});

	formattedTimestamp = computed(() => {
		const date = new Date(this.message().timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	});

	getAgentSpecialty(): string {
		const type = this.agentType();
		switch (type) {
			case 'marketing':
				return 'Marketing';
			case 'finance':
				return 'Finance';
			case 'data':
				return 'Analytics';
			default:
				// Return a capitalized version of the type for other cases
				return type.charAt(0).toUpperCase() + type.slice(1);
		}
	}

	getAgentAvatar(): string {
		return this.agentTypeService.getAgentAvatar(this.agent());
	}
}
