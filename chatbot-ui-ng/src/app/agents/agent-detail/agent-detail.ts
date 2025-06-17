import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AgentService } from '../../services/agent';
import { Agent } from '../../types/agent';
import { NgIf, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-agent-detail',
  imports: [NgIf, NgFor, RouterLink],
  templateUrl: './agent-detail.html',
  styleUrl: './agent-detail.css'
})
export class AgentDetail implements OnInit {
  agentService = inject(AgentService);
  route = inject(ActivatedRoute);
  router = inject(Router);
  agent?: Agent;

  ngOnInit() {
    const agentId = this.route.snapshot.params['id'];
    this.agentService.getAgent(agentId).subscribe(agent => {
      this.agent = agent;
    });
  }

  deleteAgent() {
    if (this.agent && confirm('Are you sure you want to delete this agent?')) {
      this.agentService.deleteAgent(this.agent.id).subscribe(() => {
        this.router.navigate(['/agents']);
      });
    }
  }
}
