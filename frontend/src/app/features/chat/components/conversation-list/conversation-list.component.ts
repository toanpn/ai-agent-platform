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
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Conversation } from '../../../../core/services/chat.service';
import { trigger, state, style, transition, animate } from '@angular/animations';
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
	],
})
export class ConversationListComponent {
	private readonly chatState = inject(ChatStateService);
	private readonly translate = inject(TranslateService);
	readonly conversations = this.chatState.conversations;
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
