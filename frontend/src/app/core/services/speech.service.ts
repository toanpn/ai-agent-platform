import { Injectable, signal } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

export interface SpeechTranscript {
	text: string;
	isFinal: boolean;
}

@Injectable({
	providedIn: 'root',
})
export class SpeechService {
	isListening$ = new BehaviorSubject<boolean>(false);
	isSpeaking$ = new BehaviorSubject<boolean>(false);
	transcript$ = new Subject<SpeechTranscript>();
	error$ = new Subject<string>();
	isTextToSpeechEnabled = signal<boolean>(true);

	private recognition: any;
	private synthesizer: SpeechSynthesis;
	private readonly isSupported: boolean;
	private currentTranscript = '';

	constructor() {
		const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
		this.synthesizer = window.speechSynthesis;

		if (SpeechRecognition && this.synthesizer) {
			this.isSupported = true;
			this.recognition = new SpeechRecognition();
			this.recognition.continuous = false;
			this.recognition.interimResults = true;
			this.setupRecognitionListeners();
		} else {
			this.isSupported = false;
			console.warn('Speech Recognition or Synthesis API not supported in this browser.');
		}
	}

	get isApiSupported(): boolean {
		return this.isSupported;
	}

	startListening(lang: string = 'en-US'): void {
		if (this.isSupported && !this.isListening$.value) {
			this.currentTranscript = '';
			this.recognition.lang = this.mapToSpeechLang(lang);
			this.recognition.start();
		}
	}

	stopListening(): void {
		if (this.isSupported) {
			this.recognition.stop();
		}
	}

	speak(text: string, lang: string = 'en-US'): void {
		if (!this.isSupported || !this.isTextToSpeechEnabled()) {
			return;
		}

		if (this.synthesizer.speaking) {
			this.synthesizer.cancel();
		}

		if (text) {
			const utterance = new SpeechSynthesisUtterance(text);
			utterance.lang = this.mapToSpeechLang(lang);
			utterance.onstart = () => this.isSpeaking$.next(true);
			utterance.onend = () => this.isSpeaking$.next(false);
			utterance.onerror = (event) => {
				console.error('SpeechSynthesis Error', event);
				this.isSpeaking$.next(false);
			};
			this.synthesizer.speak(utterance);
		}
	}

	cancel(): void {
		if (this.isSupported && this.synthesizer.speaking) {
			this.synthesizer.cancel();
		}
	}

	toggleTextToSpeech(): void {
		this.isTextToSpeechEnabled.update((enabled) => !enabled);
		if (!this.isTextToSpeechEnabled()) {
			this.cancel();
		}
	}

	private setupRecognitionListeners(): void {
		this.recognition.onstart = () => {
			this.isListening$.next(true);
		};

		this.recognition.onresult = (event: any) => {
			let interimTranscript = '';
			let finalTranscript = '';

			for (let i = event.resultIndex; i < event.results.length; ++i) {
				const transcriptPart = event.results[i][0].transcript;
				if (event.results[i].isFinal) {
					finalTranscript += transcriptPart;
				} else {
					interimTranscript += transcriptPart;
				}
			}

			// Keep track of the full transcript
			this.currentTranscript += finalTranscript || interimTranscript;

			if (finalTranscript) {
				this.transcript$.next({ text: this.currentTranscript.trim(), isFinal: true });
				this.currentTranscript = ''; // Reset for next utterance
			} else {
				this.transcript$.next({ text: this.currentTranscript, isFinal: false });
			}
		};

		this.recognition.onend = () => {
			this.isListening$.next(false);
			this.currentTranscript = ''; // Clean up on end
		};

		this.recognition.onerror = (event: any) => {
			this.error$.next(event.error);
			this.isListening$.next(false);
			console.error('SpeechRecognition Error', event);
		};
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