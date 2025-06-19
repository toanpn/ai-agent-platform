import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

/**
 * Interface for chat stream response
 */
export interface StreamResponse {
	chunk?: string;
	sessionId?: string;
	done?: boolean;
	error?: string;
}

/**
 * Interface for chat request
 */
export interface ChatRequest {
	message: string;
	sessionId?: string;
	agentId: string;
}

/**
 * Wrapper service for Hashbrown library functionality
 * This provides a simplified interface to interact with the Hashbrown features
 */
@Injectable({
	providedIn: 'root',
})
export class HashbrownService {
	private readonly baseUrl = environment.hashbrown?.config?.baseUrl || '/api';

	constructor(private http: HttpClient) {}

	/**
	 * Stream chat response from the server
	 * @param request - Chat request data
	 * @returns Observable that emits chunks of the response
	 */
	streamChat(request: ChatRequest): Observable<StreamResponse> {
		const url = `${this.baseUrl}/chat`;

		// Create an observable that will emit chunks as they arrive
		return new Observable<StreamResponse>((observer) => {
			// Using EventSource for SSE (Server-Sent Events)
			const eventSource = new EventSource(url);

			// Convert the request to a URL-encoded query string
			const params = new URLSearchParams();
			params.append('message', request.message);
			if (request.sessionId) {
				params.append('sessionId', request.sessionId);
			}
			params.append('agentId', request.agentId);

			// Create headers for fetch
			const headers = new Headers({
				'Content-Type': 'application/json',
			});

			// Initialize reader variable at this scope level
			let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

			// Use fetch for POST with EventStream response
			fetch(url, {
				method: 'POST',
				headers,
				body: JSON.stringify(request),
			})
				.then((response) => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}

					// Get the reader from the response body stream
					reader = response.body!.getReader();
					const decoder = new TextDecoder();

					// Read chunks from the stream
					function readChunk() {
						reader!
							.read()
							.then(({ done, value }) => {
								if (done) {
									observer.next({ done: true });
									observer.complete();
									return;
								}

								// Decode the chunk and process it
								const chunk = decoder.decode(value, { stream: true });

								try {
									// Hashbrown may return either plain text chunks or JSON objects
									try {
										const data = JSON.parse(chunk);
										observer.next(data);
									} catch {
										// If it's not JSON, treat it as a plain text chunk
										observer.next({ chunk });
									}
								} catch (e) {
									console.error('Error parsing chunk:', e);
									observer.next({ chunk });
								}

								// Read the next chunk
								readChunk();
							})
							.catch((error) => {
								observer.error(error);
							});
					}

					// Start reading chunks
					readChunk();
				})
				.catch((error) => {
					observer.error(error);
				});

			// Cleanup function to close the stream when unsubscribed
			return () => {
				if (reader) {
					reader.cancel().catch(console.error);
				}
			};
		});
	}
}
