import {
	Component,
	ElementRef,
	ChangeDetectionStrategy,
	inject,
	input,
	output,
	HostListener,
	computed,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DatePipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Conversation } from '../../../../core/services/chat.service';
import { trigger, style, transition, animate, keyframes } from '@angular/animations';
import { ChatStateService } from '../../chat-state.service';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

interface GroupedConversation {
	id: string;
	display: string | Date;
	conversations: Conversation[];
}

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
				animate(
					'1.5s ease-out',
					keyframes([
						style({ boxShadow: '0 0 8px 2px var(--color-primary-light)', offset: 0 }),
						style({ boxShadow: '0 0 8px 2px var(--color-primary-light)', offset: 0.7 }),
						style({ boxShadow: 'none', offset: 1.0 }),
					]),
				),
			]),
		]),
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

	groupedConversations = computed<GroupedConversation[]>(() => {
		const groups: { [key: string]: Conversation[] } = {};
		const conversations = this.conversations();
		const today = new Date();
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);

		conversations.forEach(conversation => {
			const conversationDate = new Date(conversation.timestamp);
			let dateKey: string;

			if (this.isSameDay(conversationDate, today)) {
				dateKey = '1-today';
			} else if (this.isSameDay(conversationDate, yesterday)) {
				dateKey = '2-yesterday';
			} else {
				// We subtract from a large number to sort in descending order
				const sortableKey = 2 ** 53 - conversationDate.getTime();
				dateKey = `3-${sortableKey}`;
			}

			if (!groups[dateKey]) {
				groups[dateKey] = [];
			}
			groups[dateKey].push(conversation);
		});

		return Object.keys(groups)
			.sort()
			.map(key => {
				const firstConv = groups[key][0];
				let display: string | Date;

				if (key === '1-today') {
					display = 'CHAT.DATE_TODAY';
				} else if (key === '2-yesterday') {
					display = 'CHAT.DATE_YESTERDAY';
				} else {
					display = new Date(firstConv.timestamp);
				}
				return {
					id: key,
					display,
					conversations: groups[key],
				};
			});
	});

	private readonly elementRef = inject(ElementRef);

	constructor() {
		this.searchControl.valueChanges.pipe(takeUntilDestroyed()).subscribe(value => {
			this.chatState.searchConversations(value || '');
		});
	}

	isString(value: any): value is string {
		return typeof value === 'string';
	}

	private isSameDay(date1: Date, date2: Date): boolean {
		return (
			date1.getFullYear() === date2.getFullYear() &&
			date1.getMonth() === date2.getMonth() &&
			date1.getDate() === date2.getDate()
		);
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
