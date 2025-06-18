import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';
import { ChatMessage as ChatMessageType } from '../../types/chat';

@Component({
	selector: 'app-chat-message',
	imports: [NgClass],
	templateUrl: './chat-message.html',
	styleUrl: './chat-message.css',
})
export class ChatMessage {
	@Input() message!: ChatMessageType;
}
