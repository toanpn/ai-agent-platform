import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Agent, CreateAgentRequest, UpdateAgentRequest } from '../types/agent';
import { environment } from '../../environments/environment';

@Injectable({
	providedIn: 'root',
})
export class AgentService {
	private http = inject(HttpClient);
	private apiUrl = `${environment.apiUrl}/agent`;

	getAgents(): Observable<Agent[]> {
		return this.http.get<Agent[]>(this.apiUrl);
	}

	getAgent(id: number): Observable<Agent> {
		return this.http.get<Agent>(`${this.apiUrl}/${id}`);
	}

	createAgent(agent: CreateAgentRequest): Observable<Agent> {
		return this.http.post<Agent>(this.apiUrl, agent);
	}

	updateAgent(id: number, agent: UpdateAgentRequest): Observable<Agent> {
		return this.http.put<Agent>(`${this.apiUrl}/${id}`, agent);
	}

	deleteAgent(id: number): Observable<void> {
		return this.http.delete<void>(`${this.apiUrl}/${id}`);
	}
}
