import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule, MatSidenav } from '@angular/material/sidenav';
import { MatDividerModule } from '@angular/material/divider';
import { Subscription } from 'rxjs';

import { AuthService, User } from './core/services/auth.service';
import { NotificationService } from './core/services/notification.service';
import { ChatSidebarComponent } from './features/chat/components/chat-sidebar/chat-sidebar.component';

/**
 * AppComponent is the root component of the chatbot application.
 * It handles the main application layout, authentication state,
 * and navigation between different parts of the application.
 */
@Component({
	selector: 'app-root',
	standalone: true,
	imports: [
		CommonModule,
		RouterOutlet,
		MatToolbarModule,
		MatIconModule,
		MatButtonModule,
		MatSidenavModule,
		MatDividerModule,
		ChatSidebarComponent,
	],
	templateUrl: './app.html',
	styleUrl: './app.scss',
})
export class AppComponent implements OnInit, OnDestroy {
	/** Application title */
	protected title = 'chatbot-ui';

	/** Whether the user is currently logged in */
	isLoggedIn: boolean = false;

	/** Whether the sidebar is currently open */
	sidebarOpen: boolean = true;

	/** The currently logged-in user */
	user: User | null = null;

	/** Reference to the material sidenav component */
	@ViewChild('sidenav') sidenav!: MatSidenav;

	/** Subscription to the user state changes */
	private userSubscription?: Subscription;

	/**
	 * Creates an instance of AppComponent
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
	 * Initializes the component and subscribes to authentication state
	 */
	ngOnInit(): void {
		this.initializeAuthState();
	}

	/**
	 * Cleans up subscriptions when component is destroyed
	 */
	ngOnDestroy(): void {
		if (this.userSubscription) {
			this.userSubscription.unsubscribe();
		}
	}

	/**
	 * Toggles the sidebar open/closed state
	 */
	toggleSidebar(): void {
		this.sidebarOpen = !this.sidebarOpen;
	}

	/**
	 * Logs the user out and redirects to the login page
	 */
	logout(): void {
		this.authService.logout();
		this.notificationService.showSuccess('You have been logged out successfully');
		this.router.navigate(['/auth/login']);
	}

	/**
	 * Initializes the authentication state by subscribing to user changes
	 * and checking if the user is already logged in
	 * @private
	 */
	private initializeAuthState(): void {
		// Subscribe to auth state changes
		this.userSubscription = this.authService.currentUser$.subscribe((user) => {
			this.user = user;
			this.isLoggedIn = !!user;
		});

		// Check if user is already logged in
		this.isLoggedIn = this.authService.isLoggedIn();
	}
}
