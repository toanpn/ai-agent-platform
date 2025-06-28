import {
	Component,
	ElementRef,
	ChangeDetectionStrategy,
	inject,
	input,
	output,
	HostListener
} from '@angular/core';
import { DatePipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Conversation } from '../../../../core/services/chat.service';
import { trigger, style, transition, animate, keyframes } from '@angular/animations';
import { ChatStateService } from '../../chat-state.service';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
	selector: 'app-conversation-list',
	standalone: true,
	imports: [DatePipe, TranslateModule, ReactiveFormsModule],
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
		trigger('justMoved', [
			transition(':increment', [
				animate('1.5s ease-out', keyframes([
					style({ boxShadow: '0 0 8px 2px var(--color-primary-light)', offset: 0 }),
					style({ boxShadow: '0 0 8px 2px var(--color-primary-light)', offset: 0.7 }),
					style({ boxShadow: 'none', offset: 1.0 })
				]))
			])
		])
	],
})
export class ConversationListComponent {
	private readonly chatState = inject(ChatStateService);
	readonly conversations = this.chatState.conversations;
	readonly isSearching = this.chatState.isSearching;
	selectedConversation = input<Conversation | null>(null);

	selectConversation = output<Conversation>();
	loadMore = output<void>();
	searchControl = new FormControl('');

	private readonly elementRef = inject(ElementRef);

	constructor() {
		this.searchControl.valueChanges.pipe(
			takeUntilDestroyed()
		).subscribe(value => {
			this.chatState.searchConversations(value || '');
		});
	}

	onSelectConversation(conversation: Conversation): void {
		this.selectConversation.emit(conversation);
	}

	deleteConversation(conversationId: string, event: MouseEvent): void {
		event.stopPropagation();
		this.chatState.deleteConversation(conversationId);
	}

	@HostListener('scroll')
	onScroll(): void {
		const element = this.elementRef.nativeElement as HTMLElement;
		if (element.scrollHeight - element.scrollTop < element.clientHeight + 150) {
			this.loadMore.emit();
		}
	}
}
