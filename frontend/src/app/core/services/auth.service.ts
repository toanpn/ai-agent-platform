import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { BehaviorSubject, Observable, tap } from 'rxjs';
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
	private currentUserSubject = new BehaviorSubject<User | null>(null);
	public currentUser$ = this.currentUserSubject.asObservable();

	constructor(
		private api: ApiService,
		private storage: StorageService,
	) {
		// Try to load user from storage on service initialization
		const savedUser = this.storage.getItem('user');
		if (savedUser) {
			try {
				this.currentUserSubject.next(JSON.parse(savedUser));
			} catch (error) {
				this.storage.removeItem('user');
			}
		}
	}

	/**
	 * Log in user with username and password
	 */
	/**
	 * Register a new user
	 */
	register(userData: RegisterRequest): Observable<LoginResponse> {
		return this.api.post<LoginResponse>('/auth/register', userData).pipe(
			tap((response) => {
				// Save token
				this.storage.setItem('token', response.token);

				// Save user
				this.storage.setItem('user', JSON.stringify(response.user));

				// Update current user subject
				this.currentUserSubject.next(response.user);
			}),
		);
	}

	/**
	 * Log in user with username and password
	 */
	login(credentials: LoginRequest): Observable<LoginResponse> {
		return this.api.post<LoginResponse>('/auth/login', credentials).pipe(
			tap((response) => {
				// Save token
				this.storage.setItem('token', response.token);

				// Save user
				this.storage.setItem('user', JSON.stringify(response.user));

				// Update current user subject
				this.currentUserSubject.next(response.user);
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
		this.currentUserSubject.next(null);
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
}
