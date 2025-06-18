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
		const agentId = this.route.snapshot.paramMap.get('id');
		if (agentId) {
			this.loadAgent(agentId);
		} else {
			this.errorMessage = 'Agent ID not provided';
			this.loading = false;
		}
	}

	loadAgent(id: string): void {
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
			// Set the selected agent in the chat service
			this.chatService.selectAgent(this.agent.id);

			// Start a new chat
			this.chatService.startNewChat();

			// Navigate to the chat view
			this.router.navigate(['/chat']);
		}
	}

	editAgent(): void {
		if (this.agent) {
			this.router.navigate(['/agents/edit', this.agent.id]);
		}
	}

	deleteAgent(): void {
		if (!this.agent) return;

		if (
			confirm(
				`Are you sure you want to delete "${this.agent.name}"? This action cannot be undone.`,
			)
		) {
			this.agentService.deleteAgent(this.agent.id).subscribe({
				next: () => {
					this.router.navigate(['/agents']);
				},
				error: (error) => {
					console.error('Error deleting agent:', error);
					this.errorMessage = 'Failed to delete agent. Please try again.';
				},
			});
		}
	}
}
