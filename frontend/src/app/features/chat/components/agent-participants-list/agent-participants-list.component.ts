import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Agent } from '../../../../core/services/agent.service';

@Component({
	selector: 'app-agent-participants-list',
	standalone: true,
	imports: [CommonModule, TranslateModule],
	templateUrl: './agent-participants-list.component.html',
	styleUrls: ['./agent-participants-list.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgentParticipantsListComponent {
	agents = input<Agent[] | null>([]);

	getAgentType(agentName?: string): string {
		if (!agentName) return '';
		if (agentName.toLowerCase().includes('marketing')) return 'marketing';
		if (agentName.toLowerCase().includes('financial')) return 'finance';
		if (agentName.toLowerCase().includes('data')) return 'data';
		return 'default';
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