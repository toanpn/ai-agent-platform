import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { ChatService, Conversation } from '../../../../core/services/chat.service';

@Component({
	selector: 'app-chat-sidebar',
	standalone: true,
	imports: [
		CommonModule,
		MatButtonModule,
		MatIconModule,
		MatListModule,
		MatDividerModule,
		RouterModule,
	],
	templateUrl: './chat-sidebar.component.html',
	styleUrls: ['./chat-sidebar.component.scss'],
})
export class ChatSidebarComponent implements OnInit {
	conversations: Conversation[] = [];

	constructor(
		public authService: AuthService,
		private chatService: ChatService,
	) {}

	ngOnInit(): void {
		this.chatService.conversations$.subscribe((conversations) => {
			this.conversations = conversations;
		});
	}

	startNewChat(): void {
		this.chatService.startNewChat();
	}

	selectChat(conversationId: string): void {
		this.chatService.loadChat(conversationId).subscribe();
	}

	logout(): void {
		this.authService.logout();
	}
}
