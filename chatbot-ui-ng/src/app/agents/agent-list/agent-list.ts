import { Component, inject, OnInit } from '@angular/core';
import { AgentService } from '../../services/agent';
import { Agent } from '../../types/agent';
import { NgFor, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
	selector: 'app-agent-list',
	imports: [NgFor, NgIf, RouterLink],
	templateUrl: './agent-list.html',
	styleUrl: './agent-list.css',
})
export class AgentList implements OnInit {
	agentService = inject(AgentService);
	agents: Agent[] = [];
	isLoading = true;
	error: string | null = null;

	ngOnInit() {
		this.agentService.getAgents().subscribe({
			next: (agents) => {
				this.agents = agents;
				this.isLoading = false;
			},
			error: (error) => {
				this.error = 'Failed to load agents. Please try again later.';
				this.isLoading = false;
				console.error('Failed to get agents', error);
			},
		});
	}
}
