import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { AuthService } from '../../../../core/services/auth.service';
import { Conversation } from '../../../../core/services/chat.service';
import { Agent } from '../../../../core/services/agent.service';

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
		MatMenuModule,
	],
	templateUrl: './chat-sidebar.component.html',
	styleUrls: ['./chat-sidebar.component.scss'],
})
export class ChatSidebarComponent {
	@Input() conversations: Conversation[] | null = [];
	@Input() agents: Agent[] | null = [];
	@Input() selectedAgent: Agent | null = null;
	@Output() conversationSelected = new EventEmitter<Conversation>();
	@Output() startNewChat = new EventEmitter<void>();
	@Output() agentSelected = new EventEmitter<Agent>();

	authService = inject(AuthService);

	onSelectConversation(conversation: Conversation): void {
		this.conversationSelected.emit(conversation);
	}

	onStartNewChat(): void {
		this.startNewChat.emit();
	}

	onSelectAgent(agent: Agent): void {
		this.agentSelected.emit(agent);
	}

	logout(): void {
		this.authService.logout();
	}
}
