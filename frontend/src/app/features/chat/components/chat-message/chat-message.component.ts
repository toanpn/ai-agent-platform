import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { Message } from '../../../../core/services/chat.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
	selector: 'app-chat-message',
	standalone: true,
	imports: [CommonModule, MatCardModule, TranslateModule],
	templateUrl: './chat-message.component.html',
	styleUrls: ['./chat-message.component.scss'],
})
export class ChatMessageComponent {
	@Input() message!: Message;

	constructor() {}

	get isUserMessage(): boolean {
		return this.message.sender === 'user';
	}

	get formattedTimestamp(): string {
		const date = new Date(this.message.timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}
}
