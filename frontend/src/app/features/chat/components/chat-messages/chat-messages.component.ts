import { Component, Input, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
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
})
export class ChatMessagesComponent implements AfterViewChecked {
	@Input() messages: Message[] | null = [];
	@Input() isLoading: boolean | null = false;

	@ViewChild('messagesContainer') private messagesContainer!: ElementRef;

	ngAfterViewChecked() {
		this.scrollToBottom();
	}

	private scrollToBottom(): void {
		try {
			if (this.messagesContainer) {
				this.messagesContainer.nativeElement.scrollTop =
					this.messagesContainer.nativeElement.scrollHeight;
			}
		} catch (err) {
			// ignore
		}
	}
} 