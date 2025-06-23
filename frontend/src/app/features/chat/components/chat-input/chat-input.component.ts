import {
	Component,
	ChangeDetectionStrategy,
	input,
	output,
	signal,
	inject,
	DestroyRef,
	OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TextFieldModule } from '@angular/cdk/text-field';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';
import { exhaustMap, tap, catchError, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';
import { ChatService } from '../../../../core/services/chat.service';
import { NotificationService } from '../../../../core/services/notification.service';

/**
 * ChatInputComponent handles user input for sending messages in the chat interface.
 * It provides a text input field and a send button, and emits the message content
 * when the user submits a message.
 */
@Component({
	selector: 'app-chat-input',
	standalone: true,
	imports: [
		CommonModule,
		FormsModule,
		MatButtonModule,
		MatIconModule,
		MatInputModule,
		MatFormFieldModule,
		MatProgressSpinnerModule,
		MatTooltipModule,
		TextFieldModule,
		TranslateModule,
	],
	templateUrl: './chat-input.component.html',
	styleUrls: ['./chat-input.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatInputComponent implements OnInit {
	sendMessage = output<string>();
	disabled = input<boolean>(false);
	messageText = signal('');
	isEnhancing = signal(false);

	private chatService = inject(ChatService);
	private notificationService = inject(NotificationService);
	private translateService = inject(TranslateService);
	private destroyRef = inject(DestroyRef);

	// Action subjects for declarative reactive patterns
	private enhancePromptTrigger$ = new Subject<string>();

	ngOnInit(): void {
		this.setupEnhancePromptHandler();
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
						switchMap((enhancedPrompt) => {
							this.messageText.set(enhancedPrompt);
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
}
