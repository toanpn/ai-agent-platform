import {
	inject,
	Injectable,
	signal,
} from '@angular/core';

import {
	Observable,
	tap,
} from 'rxjs';

import { ChatStateService } from '../../features/chat/chat-state.service';
import { ApiService } from './api.service';
import { StorageService } from './storage.service';

export interface User {
	id: string;
	username: string;
	email: string;
}

export interface RegisterRequest {
	username: string;
	email: string;
	password: string;
	firstName: string;
	lastName: string;
	registrationKey: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface LoginResponse {
	token: string;
	user: User;
}

@Injectable({
	providedIn: 'root',
})
export class AuthService {
	private api = inject(ApiService);
	private storage = inject(StorageService);
	private chatState = inject(ChatStateService);

	private currentUserSignal = signal<User | null>(null);
	public readonly currentUser = this.currentUserSignal.asReadonly();

	constructor() {}

	init(): void {
		// Try to load user from storage on service initialization
		const savedUser = this.storage.getItem('user');
		if (savedUser) {
			try {
				this.currentUserSignal.set(JSON.parse(savedUser));
				this.chatState.initialize();
			} catch (error) {
				this.storage.removeItem('user');
			}
		}
	}

	/**
	 * Register a new user
	 */
	register(userData: RegisterRequest): Observable<LoginResponse> {
		return this.api.post<LoginResponse>('/auth/register', userData).pipe(
			tap((response) => {
				this.handleAuthSuccess(response);
				this.chatState.initialize();
			}),
		);
	}

	/**
	 * Log in user with username and password
	 */
	login(credentials: LoginRequest): Observable<LoginResponse> {
		return this.api.post<LoginResponse>('/auth/login', credentials).pipe(
			tap((response) => {
				this.handleAuthSuccess(response);
				this.chatState.initialize();
			}),
		);
	}

	/**
	 * Log out the current user
	 */
	logout(): void {
		// Clear stored data
		this.storage.removeItem('token');
		this.storage.removeItem('user');

		// Reset current user
		this.currentUserSignal.set(null);

		// Destroy chat state
		this.chatState.destroy();
	}

	/**
	 * Check if user is logged in
	 */
	isLoggedIn(): boolean {
		return !!this.storage.getItem('token');
	}

	/**
	 * Get the current user's information
	 */
	getCurrentUser(): Observable<User> {
		return this.api.get<User>('/auth/me');
	}

	/**
	 * Get the auth token
	 */
	getToken(): string | null {
		return this.storage.getItem('token');
	}

	private handleAuthSuccess(response: LoginResponse): void {
		// Save token
		this.storage.setItem('token', response.token);

		// Save user
		this.storage.setItem('user', JSON.stringify(response.user));

		// Update current user signal
		this.currentUserSignal.set(response.user);
	}
}
