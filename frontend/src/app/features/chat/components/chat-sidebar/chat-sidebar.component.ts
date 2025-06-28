import {
	Component,
	inject,
	input,
	output,
	ChangeDetectionStrategy,
	computed,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../../../../core/services/auth.service';
import { Conversation } from '../../../../core/services/chat.service';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';

@Component({
	selector: 'app-chat-sidebar',
	standalone: true,
	imports: [
		CommonModule,
		DatePipe,
		RouterModule,
		MatListModule,
		MatButtonModule,
		MatIconModule,
		TranslateModule,
	],
	templateUrl: './chat-sidebar.component.html',
	styleUrls: ['./chat-sidebar.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatSidebarComponent {
	// Services
	private authService = inject(AuthService);
	private router = inject(Router);

	// Inputs
	conversations = input<Conversation[] | null>([]);
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

	logout(): void {
		this.authService.logout();
		this.router.navigate(['/auth/login']);
	}
}
