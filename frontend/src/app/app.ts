import { Component, inject } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { CommonModule } from '@angular/common';
import { AuthService } from './core/services/auth.service';

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
		MatButtonModule,
		MatIconModule,
		MatMenuModule,
	],
	templateUrl: './app.html',
	styleUrl: './app.scss',
})
export class AppComponent {
	private authService = inject(AuthService);
	private router = inject(Router);

	title = 'AI Agent Platform';
	user$ = this.authService.currentUser$;

	logout(): void {
		this.authService.logout();
		this.router.navigate(['/auth/login']);
	}
}
