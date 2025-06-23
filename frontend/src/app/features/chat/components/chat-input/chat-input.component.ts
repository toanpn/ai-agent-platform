import {
	Component,
	ChangeDetectionStrategy,
	input,
	output,
	signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { TranslateModule } from '@ngx-translate/core';

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
		TranslateModule,
	],
	templateUrl: './chat-input.component.html',
	styleUrls: ['./chat-input.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatInputComponent {
	sendMessage = output<string>();
	disabled = input<boolean>(false);
	messageText = signal('');

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

	onMessageTextChanged(event: Event) {
		const value = (event.target as HTMLInputElement).value;
		this.messageText.set(value);
	}
}
