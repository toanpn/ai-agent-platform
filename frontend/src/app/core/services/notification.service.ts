import { Injectable, inject } from '@angular/core';
import { ActiveToast, IndividualConfig, ToastrService } from 'ngx-toastr';

/**
 * NotificationService provides a consistent interface for displaying toast notifications
 * throughout the application, utilizing ngx-toastr.
 *
 * The service supports four notification types (success, error, info, warning)
 * with appropriate styling and duration for each type.
 */
@Injectable({
	providedIn: 'root',
})
export class NotificationService {
	/** ngx-toastr service for displaying notifications */
	private toastr = inject(ToastrService);

	/**
	 * Show a success notification
	 * @param message The message to display
	 * @param title Optional title for the toast
	 * @param override Optional configuration to override defaults
	 * @returns Reference to the opened toast
	 */
	showSuccess(
		message: string,
		title?: string,
		override?: Partial<IndividualConfig>,
	): ActiveToast<any> {
		return this.toastr.success(message, title, override);
	}

	/**
	 * Show an error notification with longer display duration
	 * @param message The message to display
	 * @param title Optional title for the toast
	 * @param override Optional configuration to override defaults
	 * @returns Reference to the opened toast
	 */
	showError(
		message: string,
		title?: string,
		override?: Partial<IndividualConfig>,
	): ActiveToast<any> {
		return this.toastr.error(message, title, override);
	}

	/**
	 * Show an info notification
	 * @param message The message to display
	 * @param title Optional title for the toast
	 * @param override Optional configuration to override defaults
	 * @returns Reference to the opened toast
	 */
	showInfo(
		message: string,
		title?: string,
		override?: Partial<IndividualConfig>,
	): ActiveToast<any> {
		return this.toastr.info(message, title, override);
	}

	/**
	 * Show a warning notification with medium display duration
	 * @param message The message to display
	 * @param title Optional title for the toast
	 * @param override Optional configuration to override defaults
	 * @returns Reference to the opened toast
	 */
	showWarning(
		message: string,
		title?: string,
		override?: Partial<IndividualConfig>,
	): ActiveToast<any> {
		return this.toastr.warning(message, title, override);
	}

	/**
	 * Dismiss all currently displayed notifications
	 */
	dismissAll(): void {
		this.toastr.clear();
	}
}
