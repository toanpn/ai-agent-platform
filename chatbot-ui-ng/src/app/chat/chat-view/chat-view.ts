import { Component } from '@angular/core';
import { ChatSidebar } from '../chat-sidebar/chat-sidebar';
import { ChatMessage } from '../chat-message/chat-message';
import { ChatInput } from '../chat-input/chat-input';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-chat-view',
  imports: [ChatSidebar, ChatMessage, ChatInput, NgFor],
  templateUrl: './chat-view.html',
  styleUrl: './chat-view.css'
})
export class ChatView {
  messages = [
    { text: 'Hi! How can I help you?', sender: 'assistant' },
    { text: 'I need to know the policy...', sender: 'user' },
  ];
}
