import { Component, inject, OnInit } from '@angular/core';
import { ChatSidebar } from '../chat-sidebar/chat-sidebar';
import { ChatMessage } from '../chat-message/chat-message';
import { ChatInput } from '../chat-input/chat-input';
import { NgFor } from '@angular/common';
import { ChatService } from '../../services/chat';
import { ChatMessage as ChatMessageType } from '../../types/chat';
import { SendMessageRequest } from '../../types/chat';

@Component({
	selector: 'app-chat-view',
	imports: [ChatSidebar, ChatMessage, ChatInput, NgFor],
	templateUrl: './chat-view.html',
	styleUrl: './chat-view.css',
})
export class ChatView implements OnInit {
	chatService = inject(ChatService);
	messages: ChatMessageType[] = [];
	currentSessionId?: number;

	ngOnInit() {
		this.chatService.getChatHistory(1, 10).subscribe({
			next: (history) => {
				// For simplicity, just display messages from the first session
				if (history.sessions.length > 0) {
					this.messages = history.sessions[0].messages;
					this.currentSessionId = history.sessions[0].id;
				}
			},
			error: (error) => {
				console.error('Failed to get chat history', error);
			},
		});
	}

	handleSendMessage(message: string) {
		const userMessage: ChatMessageType = {
			id: 0, // temp id
			content: message,
			role: 'user',
			createdAt: new Date(),
		};
		this.messages.push(userMessage);

		const request: SendMessageRequest = {
			message: message,
			sessionId: this.currentSessionId,
		};

		this.chatService.sendMessage(request).subscribe({
			next: (response) => {
				const assistantMessage: ChatMessageType = {
					id: 0, // temp id
					content: response.response,
					role: 'assistant',
					agentName: response.agentName,
					createdAt: new Date(response.timestamp),
				};
				this.messages.push(assistantMessage);
				if (!this.currentSessionId) {
					this.currentSessionId = response.sessionId;
				}
			},
			error: (error) => {
				console.error('Failed to send message', error);
			},
		});
	}
}
