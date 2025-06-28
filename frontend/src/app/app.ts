import { Component, inject, ChangeDetectionStrategy, DestroyRef, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from './core/services/auth.service';
import { ThemeService } from './core/services/theme.service';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { LanguagePickerComponent } from './shared/components/language-picker/language-picker.component';
import { HeaderComponent } from './shared/components/header/header.component';

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
		TranslateModule,
		LanguagePickerComponent,
		HeaderComponent,
	],
	templateUrl: './app.html',
	styleUrl: './app.scss',
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit {
	private authService = inject(AuthService);
	private themeService = inject(ThemeService);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);

	title = 'COMMON.TITLE';
	user = this.authService.currentUser;

	// Theme-related properties
	isDarkMode = false;
	currentTheme = 'auto';

	ngOnInit() {
		this.initTheme();
	}

	/**
	 * Initialize theme-related subscriptions
	 */
	private initTheme(): void {
		// Subscribe to theme changes
		this.themeService.isDarkMode$
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe((isDark) => {
				this.isDarkMode = isDark;
			});

		this.themeService.currentTheme$
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe((theme) => {
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
