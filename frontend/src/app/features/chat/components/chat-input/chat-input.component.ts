import {
	Component,
	ChangeDetectionStrategy,
	input,
	output,
	signal,
	inject,
	DestroyRef,
	OnInit,
	ViewChild,
	ElementRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';
import { exhaustMap, tap, catchError, switchMap } from 'rxjs/operators';
import { ChatService } from '../../../../core/services/chat.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { SpeechService } from '../../../../core/services/speech.service';

/**
 * ChatInputComponent handles user input for sending messages in the chat interface.
 * It provides a text input field and a send button, and emits the message content
 * when the user submits a message.
 */
@Component({
	selector: 'app-chat-input',
	standalone: true,
	imports: [CommonModule, FormsModule, TranslateModule],
	templateUrl: './chat-input.component.html',
	styleUrls: ['./chat-input.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatInputComponent implements OnInit {
	sendMessage = output<string>();
	typing = output<boolean>();
	disabled = input<boolean>(false);
	messageText = signal('');
	isEnhancing = signal(false);

	private chatService = inject(ChatService);
	private notificationService = inject(NotificationService);
	private translateService = inject(TranslateService);
	private destroyRef = inject(DestroyRef);
	private speechService = inject(SpeechService);

	isSpeechSupported = this.speechService.isApiSupported;
	isListening = toSignal(this.speechService.isListening$, { initialValue: false });

	@ViewChild('promptInput') promptInput!: ElementRef<HTMLTextAreaElement>;

	// Action subjects for declarative reactive patterns
	private enhancePromptTrigger$ = new Subject<string>();

	ngOnInit(): void {
		this.setupEnhancePromptHandler();
		this.setupTranscriptHandler();
	}

	/**
	 * Sets up the handler for speech recognition transcripts.
	 */
	private setupTranscriptHandler(): void {
		if (!this.isSpeechSupported) {
			return;
		}

		this.speechService.transcript$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((transcript) => {
			this.messageText.set(transcript);
		});
	}

	/**
	 * Sets up the declarative handler for enhance prompt action
	 */
	private setupEnhancePromptHandler(): void {
		this.enhancePromptTrigger$
			.pipe(
				tap(() => this.isEnhancing.set(true)),
				exhaustMap((text) =>
					this.chatService.enhancePrompt(text).pipe(
						switchMap((enhancedPromptResponse) => {
							this.messageText.set(enhancedPromptResponse.user_facing_prompt);
							this.isEnhancing.set(false);
							return this.translateService.get('CHAT.PROMPT_ENHANCED_SUCCESS');
						}),
						tap((message) => {
							this.notificationService.showSuccess(message);
						}),
						catchError((error) => {
							console.error('Error enhancing prompt:', error);
							this.isEnhancing.set(false);
							return this.translateService.get('CHAT.PROMPT_ENHANCED_ERROR').pipe(
								tap((errorMessage) => {
									this.notificationService.showError(errorMessage);
								})
							);
						})
					)
				),
				takeUntilDestroyed(this.destroyRef)
			)
			.subscribe();
	}

	/**
	 * Handles the send button click event
	 * Emits the message text if it's not empty and the input is not disabled
	 */
	onSendClick(): void {
		const text = this.messageText().trim();
		if (text && !this.disabled()) {
			this.sendMessage.emit(text);
			this.messageText.set('');
		}
	}

	/**
	 * Handles keyboard events in the input field
	 * Allows sending messages with Enter key (without Shift for new lines)
	 * @param event - The keyboard event
	 */
	onKeyDown(event: KeyboardEvent): void {
		if (event.key === 'Enter' && !event.shiftKey && !this.disabled()) {
			event.preventDefault();
			this.onSendClick();
		}
	}

	onMessageTextChanged(event: Event): void {
		const value = (event.target as HTMLInputElement).value;
		this.messageText.set(value);
		this.typing.emit(!!value);
	}

	/**
	 * Triggers the enhance prompt action
	 * Uses declarative pattern with subject trigger
	 */
	onEnhanceClick(): void {
		const text = this.messageText().trim();
		if (!text || this.disabled() || this.isEnhancing()) {
			return;
		}

		this.enhancePromptTrigger$.next(text);
	}

	/**
	 * Toggles speech recognition on and off.
	 */
	toggleListening(): void {
		if (!this.isSpeechSupported) {
			return;
		}

		if (this.isListening()) {
			this.speechService.stopListening();
		} else {
			const currentLang = this.translateService.currentLang || this.translateService.defaultLang;
			this.speechService.startListening(currentLang);
		}
	}

	setPrompt(promptText: string): void {
		this.messageText.set(promptText);
		this.promptInput.nativeElement.focus();
	}
}
