import {
	inject,
	Injectable,
} from '@angular/core';

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

export interface ToolParameter {
	type?: string;
	description?: string;
	required?: boolean;
	default?: any;
	is_credential?: boolean;
}

export interface Tool {
	id: string;
	name: string;
	description?: string;
	file?: string;
	instruction?: string;
	parameters?: { [key: string]: ToolParameter };
}

export interface ToolConfig {
	toolId: string;
	enabled: boolean;
	configuration: { [key: string]: string };
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

export interface LlmConfig {
	modelName: string;
	temperature: number;
}

export interface Agent {
	id: number;
	name: string;
	department: string;
	description?: string;
	instructions?: string;
	llmConfig?: LlmConfig;
	tools?: string[];
	toolConfigs?: string; // JSON string from backend
	isActive: boolean;
	isMainRouter: boolean;
	isPublic: boolean;
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
	llmConfig: LlmConfig;
	tools?: string[];
	toolConfigs?: string; // JSON string sent to backend
	isPublic: boolean;
}

export interface UpdateAgentRequest {
	name?: string;
	department?: string;
	description?: string;
	instructions?: string;
	llmConfig?: LlmConfig;
	tools?: string[];
	toolConfigs?: string; // JSON string sent to backend
	isActive?: boolean;
	isPublic?: boolean;
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
	 * Get all available tools
	 */
	getTools(): Observable<Tool[]> {
		return this.apiService.get<Tool[]>('/tool');
	}

	/**
	 * Add a function to an agent
	 */
	addFunctionToAgent(agentId: number, functionRequest: CreateAgentFunctionRequest): Observable<void> {
		return this.apiService.post<void>(`${this.endpoint}/${agentId}/functions`, functionRequest);
	}
}
