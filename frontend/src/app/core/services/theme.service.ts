import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable } from 'rxjs';
import { StorageService } from './storage.service';

export type Theme = 'light' | 'dark' | 'auto';

/**
 * ThemeService manages the application's theme state and provides utilities
 * for switching between light, dark, and auto themes.
 */
@Injectable({
	providedIn: 'root',
})
export class ThemeService {
	private readonly THEME_KEY = 'app-theme';
	private currentThemeSubject = new BehaviorSubject<Theme>('auto');
	private isDarkModeSubject = new BehaviorSubject<boolean>(false);

	/** Observable for the current theme setting (light, dark, auto) */
	public currentTheme$ = this.currentThemeSubject.asObservable();

	/** Observable for whether dark mode is currently active */
	public isDarkMode$ = this.isDarkModeSubject.asObservable();

	private mediaQueryList?: MediaQueryList;

	constructor(
		private storage: StorageService,
		@Inject(PLATFORM_ID) private platformId: Object,
	) {
		if (isPlatformBrowser(this.platformId)) {
			this.initializeTheme();
		}
	}

	/**
	 * Initialize the theme service by loading saved theme and setting up listeners
	 */
	private initializeTheme(): void {
		// Load saved theme preference
		const savedTheme = this.storage.getItem(this.THEME_KEY) as Theme;
		const initialTheme: Theme = savedTheme && ['light', 'dark', 'auto'].includes(savedTheme) 
			? savedTheme 
			: 'auto';

		// Set up media query listener for system preference changes
		this.mediaQueryList = window.matchMedia('(prefers-color-scheme: dark)');
		this.mediaQueryList.addEventListener('change', this.onSystemThemeChange.bind(this));

		// Apply the initial theme
		this.setTheme(initialTheme);
	}

	/**
	 * Get the current theme setting
	 */
	getCurrentTheme(): Theme {
		return this.currentThemeSubject.value;
	}

	/**
	 * Check if dark mode is currently active
	 */
	isDarkMode(): boolean {
		return this.isDarkModeSubject.value;
	}

	/**
	 * Set the theme
	 * @param theme The theme to set ('light', 'dark', or 'auto')
	 */
	setTheme(theme: Theme): void {
		this.currentThemeSubject.next(theme);
		this.storage.setItem(this.THEME_KEY, theme);
		this.applyTheme(theme);
	}

	/**
	 * Toggle between light and dark theme
	 * If currently in auto mode, switches to light or dark based on current system preference
	 */
	toggleTheme(): void {
		const currentTheme = this.getCurrentTheme();
		const isDark = this.isDarkMode();

		if (currentTheme === 'auto') {
			// If in auto mode, switch to the opposite of current system preference
			this.setTheme(isDark ? 'light' : 'dark');
		} else if (currentTheme === 'light') {
			this.setTheme('dark');
		} else {
			this.setTheme('light');
		}
	}

	/**
	 * Apply the theme to the document
	 */
	private applyTheme(theme: Theme): void {
		if (!isPlatformBrowser(this.platformId)) {
			return;
		}

		const body = document.body;
		const isDark = this.calculateIsDarkMode(theme);

		// Remove existing theme classes
		body.classList.remove('light-theme', 'dark-theme');

		// Add appropriate theme class
		if (theme !== 'auto') {
			body.classList.add(`${theme}-theme`);
		}

		// Update dark mode state
		this.isDarkModeSubject.next(isDark);

		// Update meta theme-color for mobile browsers
		this.updateMetaThemeColor(isDark);
	}

	/**
	 * Calculate whether dark mode should be active based on theme setting
	 */
	private calculateIsDarkMode(theme: Theme): boolean {
		if (theme === 'dark') {
			return true;
		} else if (theme === 'light') {
			return false;
		} else {
			// Auto mode - use system preference
			return this.getSystemPrefersDark();
		}
	}

	/**
	 * Get system dark mode preference
	 */
	private getSystemPrefersDark(): boolean {
		if (!isPlatformBrowser(this.platformId)) {
			return false;
		}
		return window.matchMedia('(prefers-color-scheme: dark)').matches;
	}

	/**
	 * Handle system theme preference changes
	 */
	private onSystemThemeChange(event: MediaQueryListEvent): void {
		// Only update if we're in auto mode
		if (this.getCurrentTheme() === 'auto') {
			this.isDarkModeSubject.next(event.matches);
			this.updateMetaThemeColor(event.matches);
		}
	}

	/**
	 * Update the meta theme-color tag for mobile browsers
	 */
	private updateMetaThemeColor(isDark: boolean): void {
		if (!isPlatformBrowser(this.platformId)) {
			return;
		}

		let metaThemeColor = document.querySelector('meta[name="theme-color"]');
		if (!metaThemeColor) {
			metaThemeColor = document.createElement('meta');
			metaThemeColor.setAttribute('name', 'theme-color');
			document.head.appendChild(metaThemeColor);
		}

		// Use the color palette values
		const lightColor = '#fafafa'; // --color-neutral-50 in light mode
		const darkColor = '#121212';  // --color-neutral-50 in dark mode
		
		metaThemeColor.setAttribute('content', isDark ? darkColor : lightColor);
	}

	/**
	 * Get theme display name for UI
	 */
	getThemeDisplayName(theme?: Theme): string {
		const currentTheme = theme || this.getCurrentTheme();
		switch (currentTheme) {
			case 'light':
				return 'Light';
			case 'dark':
				return 'Dark';
			case 'auto':
				return 'Auto';
			default:
				return 'Auto';
		}
	}

	/**
	 * Get available themes
	 */
	getAvailableThemes(): Theme[] {
		return ['light', 'dark', 'auto'];
	}

	/**
	 * Cleanup method to remove event listeners
	 */
	ngOnDestroy(): void {
		if (this.mediaQueryList) {
			this.mediaQueryList.removeEventListener('change', this.onSystemThemeChange.bind(this));
		}
	}
} 