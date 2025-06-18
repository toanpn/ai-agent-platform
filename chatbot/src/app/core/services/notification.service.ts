import { Injectable, inject } from '@angular/core';
import {
	MatSnackBar,
	MatSnackBarConfig,
	MatSnackBarRef,
	TextOnlySnackBar,
} from '@angular/material/snack-bar';

/**
 * NotificationService provides a consistent interface for displaying toast notifications
 * throughout the application, utilizing Angular Material's SnackBar component.
 *
 * The service supports four notification types (success, error, info, warning)
 * with appropriate styling and duration for each type.
 */
@Injectable({
	providedIn: 'root',
})
export class NotificationService {
	/** Angular Material SnackBar service for displaying notifications */
	private snackBar = inject(MatSnackBar);

	/** Default duration for notifications in milliseconds */
	private readonly DEFAULT_DURATION = 5000;

	/** Duration for error notifications in milliseconds */
	private readonly ERROR_DURATION = 10000;

	/** Duration for warning notifications in milliseconds */
	private readonly WARNING_DURATION = 7000;

	/** Default configuration for all snackbars */
	private defaultConfig: MatSnackBarConfig = {
		duration: this.DEFAULT_DURATION,
		horizontalPosition: 'end',
		verticalPosition: 'top',
		politeness: 'assertive',
	};

	/**
	 * Show a success notification
	 * @param message The message to display
	 * @param config Optional configuration to override defaults
	 * @returns Reference to the opened snackbar
	 */
	showSuccess(message: string, config?: MatSnackBarConfig): MatSnackBarRef<TextOnlySnackBar> {
		return this.snackBar.open(message, 'Close', {
			...this.defaultConfig,
			...config,
			panelClass: ['success-snackbar'],
		});
	}

	/**
	 * Show an error notification with longer display duration
	 * @param message The message to display
	 * @param config Optional configuration to override defaults
	 * @returns Reference to the opened snackbar
	 */
	showError(message: string, config?: MatSnackBarConfig): MatSnackBarRef<TextOnlySnackBar> {
		return this.snackBar.open(message, 'Close', {
			...this.defaultConfig,
			...config,
			panelClass: ['error-snackbar'],
			duration: this.ERROR_DURATION,
		});
	}

	/**
	 * Show an info notification
	 * @param message The message to display
	 * @param config Optional configuration to override defaults
	 * @returns Reference to the opened snackbar
	 */
	showInfo(message: string, config?: MatSnackBarConfig): MatSnackBarRef<TextOnlySnackBar> {
		return this.snackBar.open(message, 'Close', {
			...this.defaultConfig,
			...config,
			panelClass: ['info-snackbar'],
		});
	}

	/**
	 * Show a warning notification with medium display duration
	 * @param message The message to display
	 * @param config Optional configuration to override defaults
	 * @returns Reference to the opened snackbar
	 */
	showWarning(message: string, config?: MatSnackBarConfig): MatSnackBarRef<TextOnlySnackBar> {
		return this.snackBar.open(message, 'Close', {
			...this.defaultConfig,
			...config,
			panelClass: ['warning-snackbar'],
			duration: this.WARNING_DURATION,
		});
	}

	/**
	 * Dismiss all currently displayed notifications
	 */
	dismissAll(): void {
		this.snackBar.dismiss();
	}
}
