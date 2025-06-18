import { User } from './auth';

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
