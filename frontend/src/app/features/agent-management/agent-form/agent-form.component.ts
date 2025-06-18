import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
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
	imports: [CommonModule, ReactiveFormsModule, RouterModule],
	templateUrl: './agent-form.component.html',
	styleUrls: ['./agent-form.component.scss'],
})
export class AgentFormComponent implements OnInit {
	agentForm!: FormGroup;
	isEditMode = false;
	agentId: string | null = null;
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
		this.agentId = this.route.snapshot.paramMap.get('id');
		this.isEditMode = !!this.agentId;

		if (this.isEditMode && this.agentId) {
			this.loading = true;
			this.agentService.getAgent(this.agentId).subscribe({
				next: (agent) => {
					this.agentForm.patchValue({
						name: agent.name,
						description: agent.description,
						capabilities: agent.capabilities.join(', '),
						configuration: JSON.stringify(agent.configuration, null, 2),
					});
					this.loading = false;
				},
				error: (error) => {
					console.error('Error loading agent:', error);
					this.saveError = 'Failed to load agent details. Please try again.';
					this.loading = false;
				},
			});
		}
	}

	initForm(): void {
		this.agentForm = this.fb.group({
			name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
			description: [
				'',
				[Validators.required, Validators.minLength(10), Validators.maxLength(500)],
			],
			capabilities: [''],
			configuration: ['{}', this.validateJson],
		});
	}

	validateJson(control: any) {
		try {
			JSON.parse(control.value);
			return null;
		} catch (e) {
			return { invalidJson: true };
		}
	}

	onSubmit(): void {
		if (this.agentForm.invalid) {
			return;
		}

		this.loading = true;
		this.saveError = '';

		const formValue = this.agentForm.value;

		// Parse capabilities string into array
		const capabilities = formValue.capabilities
			? formValue.capabilities
					.split(',')
					.map((cap: string) => cap.trim())
					.filter((cap: string) => cap)
			: [];

		// Parse configuration JSON
		let configuration;
		try {
			configuration = JSON.parse(formValue.configuration || '{}');
		} catch (e) {
			this.saveError = 'Invalid JSON in configuration field';
			this.loading = false;
			return;
		}

		if (this.isEditMode && this.agentId) {
			// Update existing agent
			const updateRequest: UpdateAgentRequest = {
				name: formValue.name,
				description: formValue.description,
				capabilities,
				configuration,
			};

			this.agentService.updateAgent(this.agentId, updateRequest).subscribe({
				next: () => {
					this.loading = false;
					this.router.navigate(['/agents', this.agentId]);
				},
				error: (error) => {
					console.error('Error updating agent:', error);
					this.saveError = 'Failed to update agent. Please try again.';
					this.loading = false;
				},
			});
		} else {
			// Create new agent
			const createRequest: CreateAgentRequest = {
				name: formValue.name,
				description: formValue.description,
				capabilities,
				configuration,
			};

			this.agentService.createAgent(createRequest).subscribe({
				next: (agent) => {
					this.loading = false;
					this.router.navigate(['/agents', agent.id]);
				},
				error: (error) => {
					console.error('Error creating agent:', error);
					this.saveError = 'Failed to create agent. Please try again.';
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
