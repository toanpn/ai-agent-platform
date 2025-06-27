import { CommonModule } from '@angular/common';
import {
	Component,
	OnDestroy,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';

import {
	finalize,
	Subscription,
} from 'rxjs';

import { TranslateModule } from '@ngx-translate/core';

import {
	AuthService,
	LoginRequest,
	RegisterRequest,
} from '../../../core/services/auth.service';
import { NotificationService } from '../../../core/services/notification.service';

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
		MatProgressSpinnerModule,
		TranslateModule,
	],
	templateUrl: './login.component.html',
	styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnDestroy {
	/** User credentials from the login form */
	loginCredentials: LoginRequest = {
		email: '',
		password: '',
	};

	/** User credentials from the registration form */
	registerCredentials: RegisterRequest = {
		email: '',
		password: '',
		firstName: '',
		lastName: '',
		registrationKey: '',
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
	activeTab: 'login' | 'register' = 'login';

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
		if (!this.loginCredentials.email || !this.loginCredentials.password) {
			this.loginError = 'AUTH.FILL_ALL_FIELDS';
			this.notificationService.showWarning('AUTH.FILL_ALL_FIELDS');
			return false;
		}

		// Basic email validation
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailPattern.test(this.loginCredentials.email)) {
			this.loginError = 'AUTH.VALID_EMAIL';
			this.notificationService.showWarning('AUTH.VALID_EMAIL');
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
			!this.registerCredentials.email ||
			!this.registerCredentials.password ||
			!this.registerCredentials.firstName ||
			!this.registerCredentials.registrationKey
		) {
			this.registerError = 'AUTH.FILL_ALL_FIELDS';
			this.notificationService.showWarning('AUTH.FILL_ALL_FIELDS');
			return false;
		}

		// Basic email validation
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailPattern.test(this.registerCredentials.email)) {
			this.registerError = 'AUTH.VALID_EMAIL';
			this.notificationService.showWarning('AUTH.VALID_EMAIL');
			return false;
		}

		// Password strength validation (minimum 6 characters)
		if (this.registerCredentials.password.length < 6) {
			this.registerError = 'AUTH.PASSWORD_MIN_LENGTH';
			this.notificationService.showWarning('AUTH.PASSWORD_MIN_LENGTH');
			return false;
		}

		return true;
	}

	/**
	 * Handles successful authentication response (both login and register)
	 */
	private handleAuthSuccess(): void {
		this.notificationService.showSuccess('AUTH.LOGIN_SUCCESS');
		this.router.navigate(['/chat']);
	}

	/**
	 * Handles login error response
	 * @param err - Error response from the server
	 */
	private handleLoginError(err: any): void {
		console.error('Login error:', err);
		this.loginError = 'AUTH.LOGIN_ERROR';
		this.notificationService.showError('AUTH.LOGIN_ERROR');
	}

	/**
	 * Handles registration error response
	 * @param err - Error response from the server
	 */
	private handleRegisterError(err: any): void {
		console.error('Registration error:', err);
		this.registerError = 'AUTH.REGISTER_ERROR';
		this.notificationService.showError('AUTH.REGISTER_ERROR');
	}
}
