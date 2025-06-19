import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AgentService, Agent } from '../../../core/services/agent.service';
import { ChatService } from '../../../core/services/chat.service';

@Component({
	selector: 'app-agent-detail',
	standalone: true,
	imports: [CommonModule, RouterModule],
	templateUrl: './agent-detail.component.html',
	styleUrls: ['./agent-detail.component.scss'],
})
export class AgentDetailComponent implements OnInit {
	agent: Agent | null = null;
	loading = true;
	errorMessage = '';

	constructor(
		private agentService: AgentService,
		private chatService: ChatService,
		private route: ActivatedRoute,
		private router: Router,
	) {}

	ngOnInit(): void {
		const idParam = this.route.snapshot.paramMap.get('id');
		if (idParam) {
			const agentId = parseInt(idParam, 10);
			if (!isNaN(agentId)) {
				this.loadAgent(agentId);
			} else {
				this.errorMessage = 'Invalid agent ID';
				this.loading = false;
			}
		} else {
			this.errorMessage = 'Agent ID not provided';
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
				this.errorMessage = 'Failed to load agent details. Please try again.';
				this.loading = false;
			},
		});
	}

	startChat(): void {
		if (this.agent) {
			this.chatService.selectAgent(this.agent.id.toString());
			this.router.navigate(['/chat']);
		}
	}

	editAgent(): void {
		if (this.agent) {
			this.router.navigate(['/agents/edit', this.agent.id]);
		}
	}

	deleteAgent(): void {
		if (this.agent && confirm('Are you sure you want to delete this agent?')) {
			this.agentService.deleteAgent(this.agent.id).subscribe({
				next: () => {
					this.router.navigate(['/agents']);
				},
				error: (error) => {
					console.error('Error deleting agent:', error);
					alert('Failed to delete agent. Please try again.');
				},
			});
		}
	}
}
