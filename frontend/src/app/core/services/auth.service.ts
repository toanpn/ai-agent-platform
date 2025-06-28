import { Injectable, inject, signal } from '@angular/core';
import { ApiService } from './api.service';
import { Observable, tap, of, catchError, concatMap, map } from 'rxjs';
import { StorageService } from './storage.service';
import { ChatStateService } from '../../features/chat/chat-state.service';
import { Router } from '@angular/router';
import { AgentStateService } from '../../features/chat/agent-state.service';

export interface User {
	id: number;
	email: string;
	firstName?: string;
	lastName?: string;
	department?: string;
	name?: string;
	avatar?: string;
}

export interface AuthResponse {
	token: string;
	expiresAt: Date;
	user: User;
}

@Injectable({
	providedIn: 'root',
})
export class AuthService {
	private apiService = inject(ApiService);
	private storageService = inject(StorageService);
	private router = inject(Router);
	private chatState = inject(ChatStateService);
	private agentState = inject(AgentStateService);

	private currentUserSignal = signal<User | null>(null);
	readonly currentUser = this.currentUserSignal.asReadonly();

	constructor() {
		// No longer calling initialization here
	}

	init(): Observable<boolean | null> {
		const token = this.storageService.getItem('authToken');
		if (!token) {
			return of(null);
		}

		return this.getCurrentUser().pipe(
			tap((user) => {
				this.currentUserSignal.set(this.formatUser(user));
				this.chatState.initialize();
				this.agentState.initialize().subscribe();
			}),
			map(() => true),
			catchError(() => {
				this.logout();
				return of(null);
			})
		);
	}

	login(credentials: { email: string; password: string }): Observable<AuthResponse> {
		return this.apiService.post<AuthResponse>('/auth/login', credentials).pipe(
			tap((response) => {
				this.storageService.setItem('authToken', response.token);
			}),
			concatMap((response) => this.getCurrentUser().pipe(
				map((user) => ({
					response,
					user,
				}))
			)),
			tap(({ user }) => {
				this.currentUserSignal.set(this.formatUser(user));
				this.chatState.initialize();
				this.agentState.initialize().subscribe();
			}),
			map(({ response }) => response)
		);
	}

	getCurrentUser(): Observable<User> {
		return this.apiService.get<User>('/user/me');
	}

	register(userInfo: Omit<User, 'id'>): Observable<AuthResponse> {
		return this.apiService.post<AuthResponse>('/auth/register', userInfo).pipe(
			tap((response) => {
				this.storageService.setItem('authToken', response.token);
			}),
			concatMap((response) => this.getCurrentUser().pipe(
				map((user) => ({
					response,
					user,
				}))
			)),
			tap(({ user }) => {
				this.currentUserSignal.set(this.formatUser(user));
				this.chatState.initialize();
				this.agentState.initialize().subscribe();
			}),
			map(({ response }) => response)
		);
	}

	logout(): void {
		this.storageService.removeItem('authToken');
		this.currentUserSignal.set(null);
		this.chatState.destroy();
		this.agentState.destroy();
		this.router.navigate(['/auth/login']);
	}

	isAuthenticated(): boolean {
		return !!this.storageService.getItem('authToken');
	}

	private formatUser(user: User): User {
		return {
			...user,
			name: `${user.firstName || ''} ${user.lastName || ''}`.trim() || user.email,
			department: user.department || 'General',
		};
	}
}
