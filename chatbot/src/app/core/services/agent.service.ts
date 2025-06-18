import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Agent {
	id: string;
	name: string;
	description: string;
	capabilities: string[];
	configuration: any;
	createdAt: Date;
	updatedAt: Date;
}

export interface CreateAgentRequest {
	name: string;
	description: string;
	capabilities?: string[];
	configuration?: any;
}

export interface UpdateAgentRequest {
	name?: string;
	description?: string;
	capabilities?: string[];
	configuration?: any;
}

@Injectable({
	providedIn: 'root',
})
export class AgentService {
	private readonly endpoint = '/agents';

	constructor(private api: ApiService) {}

	/**
	 * Get all agents
	 */
	getAgents(): Observable<Agent[]> {
		return this.api.get<Agent[]>(this.endpoint);
	}

	/**
	 * Get a specific agent by ID
	 */
	getAgent(id: string): Observable<Agent> {
		return this.api.get<Agent>(`${this.endpoint}/${id}`);
	}

	/**
	 * Create a new agent
	 */
	createAgent(agent: CreateAgentRequest): Observable<Agent> {
		return this.api.post<Agent>(this.endpoint, agent);
	}

	/**
	 * Update an existing agent
	 */
	updateAgent(id: string, agent: UpdateAgentRequest): Observable<Agent> {
		return this.api.put<Agent>(`${this.endpoint}/${id}`, agent);
	}

	/**
	 * Delete an agent
	 */
	deleteAgent(id: string): Observable<void> {
		return this.api.delete<void>(`${this.endpoint}/${id}`);
	}
}
