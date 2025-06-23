import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import {
	AgentService,
	Agent,
	CreateAgentRequest,
	UpdateAgentRequest,
} from '../../../core/services/agent.service';
import { switchMap, of, catchError } from 'rxjs';

@Component({
	selector: 'app-agent-form',
	standalone: true,
	imports: [CommonModule, ReactiveFormsModule, RouterModule, TranslateModule],
	templateUrl: './agent-form.component.html',
	styleUrls: ['./agent-form.component.scss'],
})
export class AgentFormComponent implements OnInit {
	agentForm!: FormGroup;
	isEditMode = false;
	agentId: number | null = null;
	loading = false;
	saveError = '';

	constructor(
		private fb: FormBuilder,
		private agentService: AgentService,
		private route: ActivatedRoute,
		private router: Router,
	) {}

	ngOnInit(): void {
		this.initForm();

		// Check if we're in edit mode based on the URL
		const idParam = this.route.snapshot.paramMap.get('id');
		if (idParam) {
			const agentId = parseInt(idParam, 10);
			if (!isNaN(agentId)) {
				this.agentId = agentId;
				this.isEditMode = true;
				this.loadAgent(agentId);
			} else {
				this.saveError = 'AGENTS.INVALID_AGENT_ID';
			}
		}
	}

	loadAgent(agentId: number): void {
		this.loading = true;
		this.agentService.getAgent(agentId).subscribe({
			next: (agent) => {
				this.agentForm.patchValue({
					name: agent.name,
					department: agent.department,
					description: agent.description || '',
					instructions: agent.instructions || '',
				});
				this.loading = false;
			},
			error: (error) => {
				console.error('Error loading agent:', error);
				this.saveError = 'AGENTS.FAILED_LOAD_AGENT';
				this.loading = false;
			},
		});
	}

	initForm(): void {
		this.agentForm = this.fb.group({
			name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
			department: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
			description: ['', [Validators.maxLength(500)]],
			instructions: ['', [Validators.maxLength(1000)]],
		});
	}

	onSubmit(): void {
		if (this.agentForm.invalid) {
			return;
		}

		this.loading = true;
		this.saveError = '';

		const formValue = this.agentForm.value;

		if (this.isEditMode && this.agentId) {
			// Update existing agent
			const updateRequest: UpdateAgentRequest = {
				name: formValue.name,
				department: formValue.department,
				description: formValue.description || undefined,
				instructions: formValue.instructions || undefined,
			};

			this.agentService.updateAgent(this.agentId, updateRequest).subscribe({
				next: () => {
					this.loading = false;
					this.router.navigate(['/agents', this.agentId]);
				},
				error: (error) => {
					console.error('Error updating agent:', error);
					this.saveError = 'AGENTS.FAILED_UPDATE_AGENT';
					this.loading = false;
				},
			});
		} else {
			// Create new agent
			const createRequest: CreateAgentRequest = {
				name: formValue.name,
				department: formValue.department,
				description: formValue.description || undefined,
				instructions: formValue.instructions || undefined,
			};

			this.agentService.createAgent(createRequest).subscribe({
				next: (agent) => {
					this.loading = false;
					this.router.navigate(['/agents', agent.id]);
				},
				error: (error) => {
					console.error('Error creating agent:', error);
					this.saveError = 'AGENTS.FAILED_CREATE_AGENT';
					this.loading = false;
				},
			});
		}
	}

	cancel(): void {
		if (this.isEditMode && this.agentId) {
			this.router.navigate(['/agents', this.agentId]);
		} else {
			this.router.navigate(['/agents']);
		}
	}
}
