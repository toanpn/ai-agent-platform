import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface User {
	id: number;
	email: string;
	firstName?: string;
	lastName?: string;
	department?: string;
	isActive: boolean;
	createdAt: Date;
}

export interface AgentFile {
	id: number;
	fileName: string;
	contentType?: string;
	fileSize: number;
	isIndexed: boolean;
	createdAt: Date;
}

export interface AgentFunction {
	id: number;
	name: string;
	description?: string;
	schema?: string;
	endpointUrl?: string;
	httpMethod?: string;
	isActive: boolean;
	createdAt: Date;
}

export interface Agent {
	id: number;
	name: string;
	department: string;
	description?: string;
	instructions?: string;
	isActive: boolean;
	isMainRouter: boolean;
	createdBy: User;
	createdAt: Date;
	updatedAt?: Date;
	files: AgentFile[];
	functions: AgentFunction[];
}

export interface CreateAgentRequest {
	name: string;
	department: string;
	description?: string;
	instructions?: string;
}

export interface UpdateAgentRequest {
	name?: string;
	department?: string;
	description?: string;
	instructions?: string;
	isActive?: boolean;
}

export interface CreateAgentFunctionRequest {
	name: string;
	description?: string;
	schema?: string;
	endpointUrl: string;
	httpMethod?: string;
	headers?: string;
}

@Injectable({
	providedIn: 'root',
})
export class AgentService {
	private readonly endpoint = '/agent';
	private apiService: ApiService = inject(ApiService);

	/**
	 * Get all agents
	 */
	getAgents(): Observable<Agent[]> {
		return this.apiService.get<Agent[]>(this.endpoint);
	}

	/**
	 * Get a specific agent by ID
	 */
	getAgent(id: number): Observable<Agent> {
		return this.apiService.get<Agent>(`${this.endpoint}/${id}`);
	}

	/**
	 * Create a new agent
	 */
	createAgent(agent: CreateAgentRequest): Observable<Agent> {
		return this.apiService.post<Agent>(this.endpoint, agent);
	}

	/**
	 * Update an existing agent
	 */
	updateAgent(id: number, agent: UpdateAgentRequest): Observable<Agent> {
		return this.apiService.put<Agent>(`${this.endpoint}/${id}`, agent);
	}

	/**
	 * Delete an agent
	 */
	deleteAgent(id: number): Observable<void> {
		return this.apiService.delete<void>(`${this.endpoint}/${id}`);
	}

	/**
	 * Add a function to an agent
	 */
	addFunctionToAgent(agentId: number, functionRequest: CreateAgentFunctionRequest): Observable<void> {
		return this.apiService.post<void>(`${this.endpoint}/${agentId}/functions`, functionRequest);
	}
}
