import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { AuthService, LoginRequest, RegisterRequest } from '../../../core/services/auth.service';
import { NotificationService } from '../../../core/services/notification.service';
import { finalize, Subscription } from 'rxjs';

/**
 * LoginComponent handles user authentication through a login form.
 * It manages the login form state, authentication requests, and displays
 * appropriate feedback during the login process.
 */
@Component({
	selector: 'app-login',
	standalone: true,
	imports: [
		CommonModule,
		FormsModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatCardModule,
		MatIconModule,
		MatProgressSpinnerModule,
		MatTabsModule,
	],
	templateUrl: './login.component.html',
	styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnDestroy {
	/** User credentials from the login form */
	loginCredentials: LoginRequest = {
		username: '',
		email: '',
		password: '',
	};

	/** User credentials from the registration form */
	registerCredentials: RegisterRequest = {
		username: '',
		email: '',
		password: '',
		firstName: '',
		lastName: '',
	};

	/** Error message to display in the UI */
	loginError: string = '';
	registerError: string = '';

	/** Loading state for the login/register button */
	loading: boolean = false;

	/** Toggle for password visibility */
	hidePassword: boolean = true;
	hideRegisterPassword: boolean = true;

	/** Currently selected tab index */
	selectedTabIndex: number = 0;

	/** Subscription for auth request */
	private authSubscription?: Subscription;

	/**
	 * Creates an instance of LoginComponent
	 * @param authService - Service for authentication operations
	 * @param router - Angular router for navigation
	 * @param notificationService - Service for displaying notifications
	 */
	constructor(
		private authService: AuthService,
		private router: Router,
		private notificationService: NotificationService,
	) {}

	/**
	 * Cleans up subscriptions when component is destroyed
	 */
	ngOnDestroy(): void {
		if (this.authSubscription) {
			this.authSubscription.unsubscribe();
		}
	}

	/**
	 * Validates form and submits login request
	 */
	login(): void {
		// Validate form inputs
		if (!this.validateLoginForm()) {
			return;
		}

		this.loading = true;
		this.loginError = '';

		this.authSubscription = this.authService
			.login(this.loginCredentials)
			.pipe(finalize(() => (this.loading = false)))
			.subscribe({
				next: () => this.handleAuthSuccess(),
				error: (err) => this.handleLoginError(err),
			});
	}

	/**
	 * Validates form and submits registration request
	 */
	register(): void {
		// Validate form inputs
		if (!this.validateRegisterForm()) {
			return;
		}

		this.loading = true;
		this.registerError = '';

		this.authSubscription = this.authService
			.register(this.registerCredentials)
			.pipe(finalize(() => (this.loading = false)))
			.subscribe({
				next: () => this.handleAuthSuccess(),
				error: (err) => this.handleRegisterError(err),
			});
	}

	/**
	 * Validates the login form fields
	 * @returns true if form is valid, false otherwise
	 */
	private validateLoginForm(): boolean {
		if (!this.loginCredentials.username || !this.loginCredentials.email || !this.loginCredentials.password) {
			this.loginError = 'Please fill out all fields';
			this.notificationService.showWarning('Please fill out all fields');
			return false;
		}

		// Basic email validation
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailPattern.test(this.loginCredentials.email)) {
			this.loginError = 'Please enter a valid email address';
			this.notificationService.showWarning('Please enter a valid email address');
			return false;
		}

		return true;
	}

	/**
	 * Validates the registration form fields
	 * @returns true if form is valid, false otherwise
	 */
	private validateRegisterForm(): boolean {
		if (
			!this.registerCredentials.username ||
			!this.registerCredentials.email ||
			!this.registerCredentials.password ||
			!this.registerCredentials.firstName ||
			!this.registerCredentials.lastName
		) {
			this.registerError = 'Please fill out all fields';
			this.notificationService.showWarning('Please fill out all fields');
			return false;
		}

		// Basic email validation
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailPattern.test(this.registerCredentials.email)) {
			this.registerError = 'Please enter a valid email address';
			this.notificationService.showWarning('Please enter a valid email address');
			return false;
		}

		// Password strength validation (minimum 6 characters)
		if (this.registerCredentials.password.length < 6) {
			this.registerError = 'Password must be at least 6 characters long';
			this.notificationService.showWarning('Password must be at least 6 characters long');
			return false;
		}

		return true;
	}

	/**
	 * Handles successful authentication response (both login and register)
	 */
	private handleAuthSuccess(): void {
		this.notificationService.showSuccess('Login successful');
		this.router.navigate(['/chat']);
	}

	/**
	 * Handles login error response
	 * @param err - The HTTP error response
	 */
	private handleLoginError(err: any): void {
		console.error('Login error:', err);

		// Set the inline error message
		this.loginError = 'Invalid username or password';

		// Show specific login error message
		if (err.status === 401) {
			this.notificationService.showError('Invalid username or password');
		} else {
			this.notificationService.showError('Login failed. Please try again.');
		}
	}

	/**
	 * Handles registration error response
	 * @param err - The HTTP error response
	 */
	private handleRegisterError(err: any): void {
		console.error('Registration error:', err);

		// Set default error message
		this.registerError = 'Registration failed. Please try again.';

		// Show specific registration error message based on status code
		if (err.status === 409) {
			this.registerError = 'Username or email already exists';
			this.notificationService.showError('Username or email already exists');
		} else {
			this.notificationService.showError('Registration failed. Please try again.');
		}
	}
}
