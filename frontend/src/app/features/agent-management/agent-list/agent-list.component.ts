import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AgentService, Agent } from '../../../core/services/agent.service';
import { Observable } from 'rxjs';

@Component({
	selector: 'app-agent-list',
	standalone: true,
	imports: [CommonModule, RouterModule],
	templateUrl: './agent-list.component.html',
	styleUrls: ['./agent-list.component.scss'],
})
export class AgentListComponent implements OnInit {
	agents$: Observable<Agent[]>;
	loading = true;

	constructor(private agentService: AgentService) {
		this.agents$ = this.agentService.getAgents();
	}

	ngOnInit(): void {
		this.loadAgents();
	}

	loadAgents(): void {
		this.loading = true;
		this.agents$ = this.agentService.getAgents();
		this.loading = false;
	}

	deleteAgent(id: string, event: Event): void {
		event.stopPropagation();
		if (confirm('Are you sure you want to delete this agent?')) {
			this.agentService.deleteAgent(id).subscribe({
				next: () => {
					this.loadAgents();
				},
				error: (error) => {
					console.error('Error deleting agent:', error);
					alert('Failed to delete agent. Please try again.');
				},
			});
		}
	}
}
