import { Component, EventEmitter, Output, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-chat-welcome',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './chat-welcome.component.html',
  styleUrls: ['./chat-welcome.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatWelcomeComponent {
  @Output() promptClicked = new EventEmitter<string>();

  suggestedPrompts = [
    'CHAT.SUGGESTED_PROMPTS.COMPETITORS',
    'CHAT.SUGGESTED_PROMPTS.SEO',
    'CHAT.SUGGESTED_PROMPTS.MARKETING_MIX',
    'CHAT.SUGGESTED_PROMPTS.CONVERSION_RATE',
  ];

  constructor(private translate: TranslateService) {}

  onPromptClick(promptKey: string): void {
    const promptText = this.translate.instant(promptKey);
    this.promptClicked.emit(promptText);
  }
} 