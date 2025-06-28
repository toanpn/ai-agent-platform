import { Injectable, inject, signal } from '@angular/core';
import { Agent, AgentService } from '../../core/services/agent.service';
import { tap } from 'rxjs';

@Injectable({
	providedIn: 'root',
})
export class AgentStateService {
	private agentService = inject(AgentService);
	private agents = signal<Agent[]>([]);

	agents$ = this.agents.asReadonly();

	initialize() {
		return this.agentService.getAgents().pipe(tap(agents => this.agents.set(agents)));
	}

	destroy() {
		this.agents.set([]);
	}

	getAgentByName(name: string): Agent | undefined {
		return this.agents().find(agent => agent.name === name);
	}
} 