import {
	Component,
	inject,
	input,
	output,
	ChangeDetectionStrategy,
	computed,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
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
		MatTooltipModule,
		RouterModule,
		MatMenuModule,
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
	agents = input<Agent[] | null>([]);
	selectedAgent = input<Agent | null>(null);

	// Outputs
	conversationSelected = output<Conversation>();
	startNewChat = output<void>();
	agentSelected = output<Agent>();

	// Computed
	currentUser = computed(() => this.authService.currentUser());

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
		this.router.navigate(['/auth/login']);
	}
}
