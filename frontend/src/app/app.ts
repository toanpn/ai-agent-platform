import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from './core/services/auth.service';
import { ThemeService } from './core/services/theme.service';

/**
 * AppComponent is the root component of the chatbot application.
 * It handles the main application layout, authentication state,
 * navigation between different parts of the application, and global theme management.
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
export class AppComponent implements OnInit, OnDestroy {
	private authService = inject(AuthService);
	private themeService = inject(ThemeService);
	private router = inject(Router);
	private destroy$ = new Subject<void>();

	title = 'AI Agent Platform';
	user$ = this.authService.currentUser$;

	// Theme-related properties
	isDarkMode = false;
	currentTheme = 'auto';

	constructor() {}

	ngOnInit(): void {
		this.initTheme();
	}

	ngOnDestroy(): void {
		this.destroy$.next();
		this.destroy$.complete();
	}

	/**
	 * Initialize theme-related subscriptions
	 */
	private initTheme(): void {
		// Subscribe to theme changes
		this.themeService.isDarkMode$.pipe(takeUntil(this.destroy$)).subscribe((isDark) => {
			this.isDarkMode = isDark;
		});

		this.themeService.currentTheme$.pipe(takeUntil(this.destroy$)).subscribe((theme) => {
			this.currentTheme = theme;
		});
	}

	/**
	 * Toggle between light and dark theme
	 */
	toggleTheme(): void {
		this.themeService.toggleTheme();
	}

	/**
	 * Get theme display name for UI
	 */
	getThemeDisplayName(): string {
		return this.themeService.getThemeDisplayName();
	}

	logout(): void {
		this.authService.logout();
		this.router.navigate(['/auth/login']);
	}

	navigateTo(path: string): void {
		this.router.navigate([path]);
	}
}
