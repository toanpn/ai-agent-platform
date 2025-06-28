import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Agent } from '../../../../core/services/agent.service';
import { AgentTypeService } from '../../../../core/services/agent-type.service';
import { ChatStateService } from '../../chat-state.service';
import { RouterModule } from '@angular/router';
import { StorageService } from '../../../../core/services/storage.service';

@Component({
	selector: 'app-agent-participants-list',
	standalone: true,
	imports: [CommonModule, TranslateModule, RouterModule],
	templateUrl: './agent-participants-list.component.html',
	styleUrls: ['./agent-participants-list.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgentParticipantsListComponent {
	private agentTypeService = inject(AgentTypeService);
	private chatState = inject(ChatStateService);
	private storageService = inject(StorageService);

	agents = this.chatState.agents;

	isCollapsed = signal<boolean>(
		this.storageService.getItem('agent-participants-list-collapsed') === 'true',
	);

	toggleCollapse(): void {
		this.isCollapsed.set(!this.isCollapsed());
		this.storageService.setItem(
			'agent-participants-list-collapsed',
			String(this.isCollapsed()),
		);
	}

	getAgentType(agent?: Agent): string {
		return this.agentTypeService.getAgentType(agent);
	}

	getAgentAvatar(agent?: Agent): string {
		return this.agentTypeService.getAgentAvatar(agent);
	}
} 
