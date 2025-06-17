import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AgentService } from '../../services/agent';
import { Agent, CreateAgentRequest, UpdateAgentRequest } from '../../types/agent';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-agent-form',
  imports: [FormsModule, ReactiveFormsModule, NgIf],
  templateUrl: './agent-form.html',
  styleUrl: './agent-form.css'
})
export class AgentForm implements OnInit {
  agentForm: FormGroup;
  agentService = inject(AgentService);
  router = inject(Router);
  route = inject(ActivatedRoute);
  agentId?: number;
  isEditMode = false;

  constructor(private fb: FormBuilder) {
    this.agentForm = this.fb.group({
      name: ['', [Validators.required]],
      department: ['', [Validators.required]],
      description: [''],
      instructions: ['']
    });
  }

  ngOnInit() {
    this.agentId = this.route.snapshot.params['id'];
    this.isEditMode = !!this.agentId;

    if (this.isEditMode) {
      this.agentService.getAgent(this.agentId!).subscribe(agent => {
        this.agentForm.patchValue(agent);
      });
    }
  }

  onSubmit() {
    if (this.agentForm.valid) {
      if (this.isEditMode) {
        const updateRequest: UpdateAgentRequest = this.agentForm.value;
        this.agentService.updateAgent(this.agentId!, updateRequest).subscribe(() => {
          this.router.navigate(['/agents']);
        });
      } else {
        const createRequest: CreateAgentRequest = this.agentForm.value;
        this.agentService.createAgent(createRequest).subscribe(() => {
          this.router.navigate(['/agents']);
        });
      }
    }
  }
}
