import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import { NotificationService } from './notification.service';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
	providedIn: 'root',
})
export class SpeechService {
	isListening$ = new BehaviorSubject<boolean>(false);
	transcript$ = new Subject<string>();

	private recognition!: SpeechRecognition;
	private readonly isSupported: boolean;
	private currentTranscript = '';
	private hasPermission = false;
	private notificationService = inject(NotificationService);
	private translateService = inject(TranslateService);

	constructor() {
		const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

		if (SpeechRecognition) {
			this.isSupported = true;
			this.recognition = new SpeechRecognition();
			this.recognition.continuous = true;
			this.recognition.interimResults = false;
			this.recognition.maxAlternatives = 1;
			this.setupRecognitionListeners();
		} else {
			this.isSupported = false;
			console.warn('Speech Recognition API not supported in this browser.');
		}
	}

	get isApiSupported(): boolean {
		return this.isSupported;
	}

	async startListening(lang: string = 'en-US'): Promise<void> {
		if (!this.isSupported || this.isListening$.value) {
			return;
		}

		if (!this.hasPermission) {
			const permissionGranted = await this.requestMicrophonePermission();
			if (!permissionGranted) {
				return;
			}
		}

		this.currentTranscript = '';
		this.recognition.lang = this.mapToSpeechLang(lang);
		this.recognition.start();
	}

	stopListening(): void {
		if (this.isSupported) {
			this.recognition.stop();
		}
	}

	private async requestMicrophonePermission(): Promise<boolean> {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			stream.getTracks().forEach((track) => track.stop());
			this.hasPermission = true;
			return true;
		} catch (err) {
			const error = err as DOMException;
			console.error('Microphone permission error:', error);
			this.hasPermission = false;

			let errorKey = 'CHAT.MIC_GENERIC_ERROR';

			if (error.name === 'NotFoundError') {
				errorKey = 'CHAT.MIC_NOT_FOUND_ERROR';
			} else if (error.name === 'NotAllowedError') {
				errorKey = 'CHAT.MIC_PERMISSION_ERROR';
			}

			const errorMessage = this.translateService.instant(errorKey);
			this.notificationService.showError(errorMessage);
			return false;
		}
	}

	private setupRecognitionListeners(): void {
		this.recognition.onstart = () => {
			this.isListening$.next(true);
		};

		this.recognition.onresult = (event: SpeechRecognitionEvent) => {
			const transcript = Array.from(event.results)
				.map((result) => result[0])
				.map((result) => result.transcript)
				.join('');
			this.currentTranscript = transcript;
			this.transcript$.next(this.currentTranscript.trim());
		};

		this.recognition.onerror = this.handleRecognitionError.bind(this);

		this.recognition.onend = () => {
			this.isListening$.next(false);
			this.currentTranscript = '';
		};
	}

	private handleRecognitionError(event: SpeechRecognitionErrorEvent): void {
		if (event.error === 'no-speech') {
			this.isListening$.next(false);
			return;
		}

		console.error('SpeechRecognition Error', event);
		this.isListening$.next(false);

		let errorKey: string;
		switch (event.error) {
			case 'not-allowed':
				errorKey = 'CHAT.MIC_PERMISSION_ERROR';
				this.hasPermission = false; // Reset permission status
				break;
			case 'audio-capture':
				errorKey = 'CHAT.MIC_NOT_FOUND_ERROR';
				break;
			default:
				errorKey = 'CHAT.SPEECH_ERROR';
				break;
		}
		const errorMessage = this.translateService.instant(errorKey, { error: event.error });
		this.notificationService.showError(errorMessage);
	}

	private mapToSpeechLang(lang: string): string {
		switch (lang) {
			case 'vi':
				return 'vi-VN';
			case 'en':
			default:
				return 'en-US';
		}
	}
} 
