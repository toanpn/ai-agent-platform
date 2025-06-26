import {
	HttpErrorResponse,
	HttpHandlerFn,
	HttpInterceptorFn,
	HttpRequest,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '../services/notification.service';
import { Router } from '@angular/router';
import { StorageService } from '../services/storage.service';

/**
 * AuthInterceptor handles authentication headers and error responses for all HTTP requests.
 *
 * It performs two main functions:
 * 1. Adds the JWT authentication token to all outgoing requests if available
 * 2. Intercepts error responses to provide user-friendly notifications and handle auth errors
 *
 * @param req The original HTTP request
 * @param next The next handler in the interceptor chain
 * @returns An observable of the HTTP event stream
 */
export const AuthInterceptor: HttpInterceptorFn = (
	req: HttpRequest<unknown>,
	next: HttpHandlerFn,
) => {
	const storageService = inject(StorageService);
	const notificationService = inject(NotificationService);
	const router = inject(Router);
	const token = storageService.getItem('token');

	// Clone the request and add authorization header if token exists
	let request = req;
	if (token) {
		request = req.clone({
			setHeaders: {
				Authorization: `Bearer ${token}`,
			},
		});
	}

	// Process the request and handle errors
	return next(request).pipe(
		catchError((error: HttpErrorResponse) => {
			handleErrorNotification(error, notificationService);

			// Handle authentication errors by redirecting to login
			if (error.status === 401) {
				storageService.removeItem('token');
				storageService.removeItem('user');
				router.navigate(['/auth/login']);
			}

			// Re-throw the error so it can still be handled by components
			return throwError(() => error);
		}),
	);
};

/**
 * Handles error notifications based on HTTP status codes
 * @param error The HTTP error response
 * @param notificationService The service for displaying notifications
 */
function handleErrorNotification(
	error: HttpErrorResponse,
	notificationService: NotificationService,
): void {
	// Provide user-friendly error messages based on status codes
	if (error.status === 0) {
		notificationService.showError('Network error. Please check your connection.');
	} else if (error.status === 401) {
		notificationService.showError('Session expired. Please log in again.');
	} else if (error.status === 403) {
		notificationService.showError('You do not have permission to perform this action.');
	} else if (error.status === 404) {
		notificationService.showError('The requested resource was not found.');
	} else if (error.status >= 500) {
		notificationService.showError('Server error. Please try again later.');
	} else {
		// For other errors, try to get a message from the response
		const message = error.error?.message || 'An unexpected error occurred.';
		notificationService.showError(message);
	}
}
