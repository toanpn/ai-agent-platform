import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Agent } from '../../../core/services/agent.service';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-agent-result',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    TranslateModule,
  ],
  templateUrl: './agent-result.component.html',
  styleUrl: './agent-result.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgentResultComponent implements OnInit {
  agent: Agent | null = null;
  action: 'create' | 'update' | null = null;
  successMessage = '';

  constructor(private router: Router) {
    const navigation = this.router.getCurrentNavigation();
    this.agent = navigation?.extras?.state?.['agent'];
    this.action = navigation?.extras?.state?.['action'];
  }

  ngOnInit(): void {
    if (!this.agent || !this.action) {
      this.router.navigate(['/agents']);
      return;
    }

    this.successMessage = this.action === 'create' ? 'AGENTS.CREATE_SUCCESS_NOTIFICATION' : 'AGENTS.UPDATE_SUCCESS_NOTIFICATION';
  }

  get displayedTools(): string[] {
    if (!this.agent?.tools) {
      return [];
    }
    return this.agent.tools.slice(0, 3);
  }

  get moreToolsCount(): number {
    if (!this.agent?.tools || this.agent.tools.length <= 3) {
      return 0;
    }
    return this.agent.tools.length - 3;
  }

  goToList(): void {
    this.router.navigate(['/agents']);
  }

  startChat(): void {
    this.router.navigate(['/chat'], { queryParams: { agentId: this.agent?.id } });
  }

  getToolDisplayName(toolName: string): string {
    const nameMap: { [key: string]: string } = {
      google_search_tool: 'Google Search',
      knowledge_search_tool: 'Knowledge Search',
      gmail_tool: 'Gmail',
      jira_tool: 'Jira',
    };
    return nameMap[toolName] || toolName;
  }

  getToolKey(toolName: string): string {
    return toolName.toLowerCase().replace(/_/g, '-');
  }
} 