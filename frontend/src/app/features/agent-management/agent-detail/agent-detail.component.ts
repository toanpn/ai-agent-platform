import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AgentService, Agent } from '../../../core/services/agent.service';
import { ChatStateService } from '../../chat/chat-state.service';

@Component({
	selector: 'app-agent-detail',
	standalone: true,
	imports: [CommonModule, RouterModule, TranslateModule],
	templateUrl: './agent-detail.component.html',
	styleUrls: ['./agent-detail.component.scss'],
})
export class AgentDetailComponent implements OnInit {
	agent: Agent | null = null;
	loading = true;
	errorMessage = '';

	private agentService = inject(AgentService);
	private chatStateService = inject(ChatStateService);
	private route = inject(ActivatedRoute);
	private router = inject(Router);

	ngOnInit(): void {
		const idParam = this.route.snapshot.paramMap.get('id');
		if (idParam) {
			const agentId = parseInt(idParam, 10);
			if (!isNaN(agentId)) {
				this.loadAgent(agentId);
			} else {
				this.errorMessage = 'AGENTS.INVALID_AGENT_ID';
				this.loading = false;
			}
		} else {
			this.errorMessage = 'AGENTS.AGENT_ID_NOT_PROVIDED';
			this.loading = false;
		}
	}

	loadAgent(id: number): void {
		this.agentService.getAgent(id).subscribe({
			next: (agent) => {
				this.agent = agent;
				this.loading = false;
			},
			error: (error) => {
				console.error('Error loading agent:', error);
				this.errorMessage = 'AGENTS.FAILED_LOAD_AGENT';
				this.loading = false;
			},
		});
	}

	startChat(): void {
		if (this.agent) {
			this.chatStateService.selectAgent(this.agent);
			this.router.navigate(['/chat']);
		}
	}

	editAgent(): void {
		if (this.agent) {
			this.router.navigate(['/agents/edit', this.agent.id]);
		}
	}

	deleteAgent(): void {
		if (this.agent && confirm('AGENTS.CONFIRM_DELETE_AGENT')) {
			this.agentService.deleteAgent(this.agent.id).subscribe({
				next: () => {
					this.router.navigate(['/agents']);
				},
				error: (error) => {
					console.error('Error deleting agent:', error);
					alert('AGENTS.FAILED_CREATE_AGENT');
				},
			});
		}
	}
}
