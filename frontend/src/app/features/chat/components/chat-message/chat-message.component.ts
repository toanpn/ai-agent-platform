import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';
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
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatMessageComponent {
	message = input.required<Message>();

	isUserMessage = computed(() => this.message().sender === 'user');
	
	formattedTimestamp = computed(() => {
		const date = new Date(this.message().timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	});
}
