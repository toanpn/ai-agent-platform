import {
	Component,
	ElementRef,
	ChangeDetectionStrategy,
	inject,
	input,
	output,
	HostListener,
} from '@angular/core';
import { DatePipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Conversation } from '../../../../core/services/chat.service';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { ChatStateService } from '../../chat-state.service';

@Component({
	selector: 'app-conversation-list',
	standalone: true,
	imports: [DatePipe, TranslateModule],
	templateUrl: './conversation-list.component.html',
	styleUrls: ['./conversation-list.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
	animations: [
		trigger('titleChanged', [
			transition((fromState, toState) => fromState !== 'void' && fromState !== toState, [
				style({ backgroundColor: 'var(--color-primary-light)', opacity: 1 }),
				animate('1.5s ease-out', style({ backgroundColor: 'transparent', opacity: 1 })),
			]),
		]),
	],
})
export class ConversationListComponent {
	private readonly chatState = inject(ChatStateService);
	readonly conversations = this.chatState.conversations;
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
