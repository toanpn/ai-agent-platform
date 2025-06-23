import {
	Component,
	input,
	ChangeDetectionStrategy,
	viewChild,
	ElementRef,
	effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Message } from '../../../../core/services/chat.service';
import { ChatMessageComponent } from '../chat-message/chat-message.component';

@Component({
	selector: 'app-chat-messages',
	standalone: true,
	imports: [CommonModule, ChatMessageComponent, TranslateModule],
	templateUrl: './chat-messages.component.html',
	styleUrls: ['./chat-messages.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatMessagesComponent {
	messages = input.required<Message[]>();
	isLoading = input<boolean>(false);

	private messagesContainer = viewChild<ElementRef>('messagesContainer');

	constructor() {
		effect(() => {
			// Trigger scrolling when messages change
			this.scrollToBottom();
		});
	}

	private scrollToBottom(): void {
		try {
			const container = this.messagesContainer();
			if (container) {
				container.nativeElement.scrollTop = container.nativeElement.scrollHeight;
			}
		} catch (err) {
			console.error('Could not scroll to bottom:', err);
		}
	}
} 