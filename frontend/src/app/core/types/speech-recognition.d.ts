// Type definitions for Web Speech API
// See: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

interface SpeechRecognitionEvent extends Event {
	readonly resultIndex: number;
	readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
	readonly length: number;
	item(index: number): SpeechRecognitionResult;
	[index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
	readonly isFinal: boolean;
	readonly length: number;
	item(index: number): SpeechRecognitionAlternative;
	[index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
	readonly transcript: string;
	readonly confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
	readonly error:
		| 'no-speech'
		| 'audio-capture'
		| 'not-allowed'
		| 'network'
		| 'aborted'
		| 'language-not-supported'
		| 'service-not-allowed'
		| 'bad-grammar';
	readonly message: string;
}

interface SpeechRecognitionStatic {
	new (): SpeechRecognition;
}
interface SpeechRecognition extends EventTarget {
	continuous: boolean;
	interimResults: boolean;
	lang: string;
	maxAlternatives: number;
	grammars: SpeechGrammarList;

	start(): void;
	stop(): void;
	abort(): void;

	onaudiostart: (this: SpeechRecognition, ev: Event) => any;
	onaudioend: (this: SpeechRecognition, ev: Event) => any;
	onend: (this: SpeechRecognition, ev: Event) => any;
	onerror: (this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any;
	onnomatch: (this: SpeechRecognition, ev: SpeechRecognitionEvent) => any;
	onresult: (this: SpeechRecognition, ev: SpeechRecognitionEvent) => any;
	onsoundstart: (this: SpeechRecognition, ev: Event) => any;
	onsoundend: (this: SpeechRecognition, ev: Event) => any;
	onspeechstart: (this: SpeechRecognition, ev: Event) => any;
	onspeechend: (this: SpeechRecognition, ev: Event) => any;
	onstart: (this: SpeechRecognition, ev: Event) => any;
}

interface SpeechGrammarList {
	readonly length: number;
	addFromString(string: string, weight?: number): void;
	addFromURI(src: string, weight?: number): void;
	item(index: number): SpeechGrammar;
	[index: number]: SpeechGrammar;
}

interface SpeechGrammar {
	src: string;
	weight: number;
}

// Extend the Window interface
interface Window {
	SpeechRecognition: SpeechRecognitionStatic;
	webkitSpeechRecognition: SpeechRecognitionStatic;
} 
