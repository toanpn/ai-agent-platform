import { Injectable } from '@angular/core';

/**
 * Service for handling local storage operations
 */
@Injectable({
	providedIn: 'root',
})
export class StorageService {
	constructor() {}

	/**
	 * Get an item from local storage
	 * @param key Storage key
	 */
	getItem(key: string): string | null {
		return localStorage.getItem(key);
	}

	/**
	 * Set an item in local storage
	 * @param key Storage key
	 * @param value Value to store
	 */
	setItem(key: string, value: string): void {
		localStorage.setItem(key, value);
	}

	/**
	 * Remove an item from local storage
	 * @param key Storage key
	 */
	removeItem(key: string): void {
		localStorage.removeItem(key);
	}

	/**
	 * Clear all items from local storage
	 */
	clear(): void {
		localStorage.clear();
	}
}
