import { Component, inject, OnInit } from '@angular/core';
import { AgentService } from '../../services/agent';
import { Agent } from '../../types/agent';
import { NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-agent-list',
  imports: [NgFor, RouterLink],
  templateUrl: './agent-list.html',
  styleUrl: './agent-list.css'
})
export class AgentList implements OnInit {
  agentService = inject(AgentService);
  agents: Agent[] = [];

  ngOnInit() {
    this.agentService.getAgents().subscribe({
      next: (agents) => {
        this.agents = agents;
      },
      error: (error) => {
        console.error('Failed to get agents', error);
      }
    });
  }
}
