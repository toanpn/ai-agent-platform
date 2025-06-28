import { Component, ElementRef, ChangeDetectionStrategy, inject, input, output, HostListener } from '@angular/core';
import { DatePipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Conversation } from '../../../../core/services/chat.service';

@Component({
  selector: 'app-conversation-list',
  standalone: true,
  imports: [DatePipe, TranslateModule],
  templateUrl: './conversation-list.component.html',
  styleUrls: ['./conversation-list.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConversationListComponent {
  conversations = input.required<Conversation[]>();
  selectedConversation = input<Conversation | null>(null);

  selectConversation = output<Conversation>();
  loadMore = output<void>();

  private readonly elementRef = inject(ElementRef);

  onSelectConversation(conversation: Conversation): void {
    this.selectConversation.emit(conversation);
  }

  @HostListener('scroll')
  onScroll(): void {
    const element = this.elementRef.nativeElement as HTMLElement;
    if (element.scrollHeight - element.scrollTop < element.clientHeight + 150) {
      this.loadMore.emit();
    }
  }
} 
