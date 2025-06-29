import { CommonModule } from '@angular/common';
import {
	ChangeDetectionStrategy,
	Component,
	inject,
	signal,
} from '@angular/core';
import {
	Router,
	RouterModule,
} from '@angular/router';

import {
	TranslateModule,
	TranslateService,
} from '@ngx-translate/core';

import { AgentTypeService } from '../../../../core/services/agent-type.service';
import { Agent } from '../../../../core/services/agent.service';
import { AuthService } from '../../../../core/services/auth.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { StorageService } from '../../../../core/services/storage.service';
import { ChatStateService } from '../../chat-state.service';

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
	private authService = inject(AuthService);
	private router = inject(Router);
	private notificationService = inject(NotificationService);
	private translate = inject(TranslateService);

	agents = this.chatState.agents;
	private currentUser = this.authService.currentUser;

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

	onAgentClick(agent: Agent): void {
		if (this.canModifyAgent(agent)) {
			this.router.navigate(['/agents', 'edit', agent.id]);
		} else {
			const message = this.translate.instant('AGENTS.AGENT_EDIT_PERMISSION_ERROR');
			this.notificationService.showWarning(message);
		}
	}

	canModifyAgent(agent: Agent): boolean {
		const user = this.currentUser();
		if (!user || !agent.createdBy) {
			return false;
		}
		return agent.createdBy.id === user.id;
	}

	getAgentType(agent?: Agent): string {
		return this.agentTypeService.getAgentType(agent);
	}

	getAgentAvatar(agent?: Agent): string {
		return this.agentTypeService.getAgentAvatar(agent);
	}
} 
