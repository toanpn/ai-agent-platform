import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../core/services/chat.service';

@Component({
  selector: 'app-user-message',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-message.component.html',
  styleUrls: ['./user-message.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserMessageComponent {
  message = input.required<Message>();

  formattedTimestamp = computed(() => {
    const date = new Date(this.message().timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  });
} 