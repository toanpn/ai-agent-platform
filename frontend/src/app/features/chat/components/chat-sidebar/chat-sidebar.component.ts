import {
	Component,
	inject,
	input,
	output,
	ChangeDetectionStrategy,
	signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../../../../core/services/auth.service';
import { Conversation } from '../../../../core/services/chat.service';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { ConversationListComponent } from '../conversation-list/conversation-list.component';
import { StorageService } from '../../../../core/services/storage.service';

@Component({
	selector: 'app-chat-sidebar',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		MatListModule,
		MatButtonModule,
		MatIconModule,
		TranslateModule,
		ConversationListComponent,
	],
	templateUrl: './chat-sidebar.component.html',
	styleUrls: ['./chat-sidebar.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatSidebarComponent {
	// Services
	private authService = inject(AuthService);
	private router = inject(Router);
	private storageService = inject(StorageService);

	isCollapsed = signal<boolean>(
		this.storageService.getItem('chat-sidebar-collapsed') === 'true',
	);

	// Inputs
	selectedConversation = input<Conversation | null>(null);

	// Outputs
	conversationSelected = output<Conversation>();
	startNewChat = output<void>();

	onSelectConversation(conversation: Conversation): void {
		this.conversationSelected.emit(conversation);
	}

	onStartNewChat(): void {
		this.startNewChat.emit();
	}

	toggleCollapse(): void {
		this.isCollapsed.set(!this.isCollapsed());
		this.storageService.setItem(
			'chat-sidebar-collapsed',
			String(this.isCollapsed()),
		);
	}

	onLoadMoreConversations(): void {
		// Implement logic to load more conversations
		console.log('Load more conversations triggered');
	}

	logout(): void {
		this.authService.logout();
		this.router.navigate(['/auth/login']);
	}
}
