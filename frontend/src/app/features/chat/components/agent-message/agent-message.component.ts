import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../core/services/chat.service';
import { AgentTypeService } from '../../../../core/services/agent-type.service';
import { AgentStateService } from '../../agent-state.service';
import { ExecutionDetailsComponent } from '../execution-details/execution-details.component';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-agent-message',
  standalone: true,
  imports: [CommonModule, ExecutionDetailsComponent, TranslateModule],
  templateUrl: './agent-message.component.html',
  styleUrls: ['./agent-message.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgentMessageComponent {
  message = input.required<Message>();

  private agentTypeService = inject(AgentTypeService);
  private agentStateService = inject(AgentStateService);

  private agent = computed(() => {
    if (!this.message().agentName) {
      return undefined;
    }
    return this.agentStateService.getAgentByName(this.message().agentName!);
  });

  agentType = computed(() => {
    return this.agentTypeService.getAgentType(this.agent());
  });

  formattedTimestamp = computed(() => {
    const date = new Date(this.message().timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  });

  getAgentSpecialty(): string {
    const type = this.agentType();
    switch (type) {
      case 'marketing':
        return 'Marketing';
      case 'finance':
        return 'Finance';
      case 'data':
        return 'Analytics';
      default:
        return type.charAt(0).toUpperCase() + type.slice(1);
    }
  }

  getAgentAvatar(): string {
    return this.agentTypeService.getAgentAvatar(this.agent());
  }
} 