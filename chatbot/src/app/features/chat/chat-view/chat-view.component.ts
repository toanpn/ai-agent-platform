import {
	Component,
	OnInit,
	ViewChild,
	ElementRef,
	AfterViewChecked,
	OnDestroy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatInputComponent } from '../../chat/components/chat-input/chat-input.component';
import { ChatMessageComponent } from '../../chat/components/chat-message/chat-message.component';
import { ChatSidebarComponent } from '../../chat/components/chat-sidebar/chat-sidebar.component';
import { ChatService, Message, Conversation } from '../../../core/services/chat.service';
import { NotificationService } from '../../../core/services/notification.service';
import { Subscription } from 'rxjs';

/**
 * ChatViewComponent serves as the main container for the chat interface.
 * It orchestrates the display of messages, handles user input, and manages
 * the active conversation state.
 */
@Component({
	selector: 'app-chat-view',
	standalone: true,
	imports: [CommonModule, ChatInputComponent, ChatMessageComponent, ChatSidebarComponent],
	templateUrl: './chat-view.component.html',
	styleUrls: ['./chat-view.component.scss'],
})
export class ChatViewComponent implements OnInit, AfterViewChecked, OnDestroy {
	/** Array of messages in the current conversation */
	messages: Message[] = [];

	/** Currently active conversation */
	activeConversation: Conversation | null = null;

	/** Indicates if a message is being processed */
	loading: boolean = false;

	/** Reference to the messages container for auto-scrolling */
	@ViewChild('messagesContainer') private messagesContainer!: ElementRef;

	/** Subscriptions that need to be unsubscribed on component destruction */
	private subscriptions: Subscription[] = [];

	/**
	 * Creates an instance of ChatViewComponent
	 * @param chatService - Service handling chat operations
	 * @param notificationService - Service for displaying notifications
	 */
	constructor(
		private chatService: ChatService,
		private notificationService: NotificationService,
	) {}

	/**
	 * Initializes the component, loads conversations and subscribes to message updates
	 */
	ngOnInit(): void {
		// Load conversations on init
		this.subscriptions.push(this.chatService.loadConversations().subscribe());

		// Subscribe to messages
		this.subscriptions.push(
			this.chatService.messages$.subscribe((messages) => {
				this.messages = messages;
				this.scrollToBottom();
			}),
		);

		// Subscribe to active conversation
		this.subscriptions.push(
			this.chatService.activeConversation$.subscribe((conversation) => {
				this.activeConversation = conversation;
			}),
		);
	}

	/**
	 * Scrolls to the bottom of the messages container after view updates
	 */
	ngAfterViewChecked() {
		this.scrollToBottom();
	}

	/**
	 * Unsubscribes from all subscriptions to prevent memory leaks
	 */
	ngOnDestroy(): void {
		this.subscriptions.forEach((sub) => sub.unsubscribe());
	}

	/**
	 * Scrolls the message container to show the most recent messages
	 */
	private scrollToBottom(): void {
		try {
			if (this.messagesContainer) {
				this.messagesContainer.nativeElement.scrollTop =
					this.messagesContainer.nativeElement.scrollHeight;
			}
		} catch (err) {
			// Silent failure is acceptable here as this is a UI enhancement
		}
	}

	/**
	 * Handles the send message event from the chat input component
	 * @param message - The text message to send
	 */
	onSendMessage(message: string): void {
		if (message.trim()) {
			this.loading = true;
			this.chatService.sendMessage(message).subscribe({
				next: () => {
					this.loading = false;
				},
				error: (error) => {
					this.notificationService.showError('Failed to send message. Please try again.');
					console.error('Error sending message:', error);
					this.loading = false;
				},
			});
		}
	}
}
