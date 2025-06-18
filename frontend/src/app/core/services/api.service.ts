import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
	providedIn: 'root',
})
export class ApiService {
	private apiUrl = environment.apiUrl;    
    private readonly http = inject(HttpClient);


	/**
	 * Creates headers for API requests
	 */
	private createHeaders(): HttpHeaders {
		return new HttpHeaders({
			'Content-Type': 'application/json',
		});
	}

	/**
	 * GET request
	 * @param endpoint API endpoint path
	 * @param params Optional HTTP parameters
	 */
	get<T>(endpoint: string, params?: HttpParams): Observable<T> {
		return this.http.get<T>(`${this.apiUrl}${endpoint}`, {
			headers: this.createHeaders(),
			params,
		});
	}

	/**
	 * POST request
	 * @param endpoint API endpoint path
	 * @param body Request body
	 */
	post<T>(endpoint: string, body: any): Observable<T> {
		return this.http.post<T>(`${this.apiUrl}${endpoint}`, JSON.stringify(body), {
			headers: this.createHeaders(),
		});
	}

	/**
	 * PUT request
	 * @param endpoint API endpoint path
	 * @param body Request body
	 */
	put<T>(endpoint: string, body: any): Observable<T> {
		return this.http.put<T>(`${this.apiUrl}${endpoint}`, JSON.stringify(body), {
			headers: this.createHeaders(),
		});
	}

	/**
	 * DELETE request
	 * @param endpoint API endpoint path
	 */
	delete<T>(endpoint: string): Observable<T> {
		return this.http.delete<T>(`${this.apiUrl}${endpoint}`, {
			headers: this.createHeaders(),
		});
	}
}
