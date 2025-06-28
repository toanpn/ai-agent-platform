import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Agent } from '../../../../core/services/agent.service';
import { AgentTypeService } from '../../../../core/services/agent-type.service';
import { ChatStateService } from '../../chat-state.service';

@Component({
	selector: 'app-agent-participants-list',
	standalone: true,
	imports: [CommonModule, TranslateModule],
	templateUrl: './agent-participants-list.component.html',
	styleUrls: ['./agent-participants-list.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgentParticipantsListComponent {
	private agentTypeService = inject(AgentTypeService);
	private chatState = inject(ChatStateService);

	agents = this.chatState.agents;


	getAgentType(agent?: Agent): string {
		return this.agentTypeService.getAgentType(agent);
	}

	getAgentAvatar(agent?: Agent): string {
		return this.agentTypeService.getAgentAvatar(agent);
	}
} 
