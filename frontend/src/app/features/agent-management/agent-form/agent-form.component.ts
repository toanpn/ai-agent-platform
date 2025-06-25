import { Component, OnInit, DestroyRef, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSliderModule } from '@angular/material/slider';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';
import { exhaustMap, tap, catchError, switchMap, finalize } from 'rxjs/operators';
import { of } from 'rxjs';
import {
	AgentService,
	CreateAgentRequest,
	UpdateAgentRequest,
	Tool,
	LlmConfig,
	ToolConfig,
} from '../../../core/services/agent.service';
import { ChatService } from '../../../core/services/chat.service';
import { NotificationService } from '../../../core/services/notification.service';
import {
	ToolConfigDialogComponent,
	ToolConfigDialogData,
} from '../tool-config-dialog/tool-config-dialog.component';

@Component({
	selector: 'app-agent-form',
	standalone: true,
	imports: [
		CommonModule,
		ReactiveFormsModule,
		RouterModule,
		MatButtonModule,
		MatIconModule,
		MatProgressSpinnerModule,
		MatTooltipModule,
		MatSelectModule,
		MatFormFieldModule,
		TranslateModule,
		MatSliderModule,
		MatDialogModule,
	],
	templateUrl: './agent-form.component.html',
	styleUrls: ['./agent-form.component.scss'],
})
export class AgentFormComponent implements OnInit {
	agentForm!: FormGroup;
	isEditMode = false;
	agentId: number | null = null;
	loading = false;
	saveError = '';
	isEnhancingDescription = false;
	isEnhancingInstruction = false;

	// Departments
	departments: string[] = [
		'IT',
		'HR',
		'General',
		'AI Research',
		'OM',
		'CnB',
		'L&D',
		'IC',
		'FnB',
		'Retail',
		'Employee',
		'Booking',
		'KMS',
	];

	// LLM Configuration
	llmModels: string[] = ['gemini-2.0-flash'];

	// Tools related properties
	tools: Tool[] = [];
	loadingTools = false;
	toolsError = '';
	toolConfigs: ToolConfig[] = [];

	private fb = inject(FormBuilder);
	private agentService = inject(AgentService);
	private chatService = inject(ChatService);
	private notificationService = inject(NotificationService);
	private translateService = inject(TranslateService);
	private route = inject(ActivatedRoute);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);
	private dialog = inject(MatDialog);
	private cdr = inject(ChangeDetectorRef);

	// Action subjects for declarative reactive patterns
	private enhanceDescriptionTrigger$ = new Subject<string>();
	private enhanceInstructionTrigger$ = new Subject<string>();
	private createAgentTrigger$ = new Subject<CreateAgentRequest>();
	private updateAgentTrigger$ = new Subject<{ id: number; request: UpdateAgentRequest }>();

	ngOnInit(): void {
		this.initForm();
		this.setupEnhanceDescriptionHandler();
		this.setupEnhanceInstructionHandler();
		this.setupCreateAgentHandler();
		this.setupUpdateAgentHandler();
		this.loadTools();

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
		} else {
			// Set default values for new agent
			this.agentForm.get('llmConfig.modelName')?.setValue(this.llmModels[0]);
			this.agentForm.get('llmConfig.temperature')?.setValue(0.7);
			// Initialize empty toolConfigs for new agents
			this.toolConfigs = [];
		}
	}

	/**
	 * Sets up the declarative handler for enhance description action
	 */
	private setupEnhanceDescriptionHandler(): void {
		const descriptionControl = this.agentForm.get('description');
		this.enhanceDescriptionTrigger$
			.pipe(
				tap(() => {
					this.isEnhancingDescription = true
					descriptionControl?.disable();
				}),
				exhaustMap((description) =>
					this.chatService.enhancePrompt(description).pipe(
						switchMap((enhancedPromptResponse) => {
							descriptionControl?.setValue(enhancedPromptResponse.user_facing_prompt);
							this.isEnhancingDescription = false;
							descriptionControl?.enable();
							return this.translateService.get('AGENTS.DESCRIPTION_ENHANCED_SUCCESS');
						}),
						tap((message) => {
							this.notificationService.showSuccess(message);
						}),
						catchError((error) => {
							console.error('Error enhancing description:', error);
							this.isEnhancingDescription = false;
							descriptionControl?.enable();
							return this.translateService
								.get('AGENTS.DESCRIPTION_ENHANCED_ERROR')
								.pipe(
									tap((errorMessage) => {
										this.notificationService.showError(errorMessage);
									}),
								);
						}),
					),
				),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	/**
	 * Sets up the declarative handler for enhance instruction action
	 */
	private setupEnhanceInstructionHandler(): void {
		const instructionControl = this.agentForm.get('instructions');
		this.enhanceInstructionTrigger$
			.pipe(
				tap(() => {
					this.isEnhancingInstruction = true;
					instructionControl?.disable();
				}),
				exhaustMap((instruction) =>
					this.chatService.enhancePrompt(instruction).pipe(
						switchMap((enhancedPromptResponse) => {
							instructionControl?.setValue(enhancedPromptResponse.user_facing_prompt);
							this.isEnhancingInstruction = false;
							instructionControl?.enable();
							return this.translateService.get('AGENTS.INSTRUCTION_ENHANCED_SUCCESS');
						}),
						tap((message) => {
							this.notificationService.showSuccess(message);
						}),
						catchError((error) => {
							console.error('Error enhancing instruction:', error);
							this.isEnhancingInstruction = false;
							instructionControl?.enable();
							return this.translateService
								.get('AGENTS.INSTRUCTION_ENHANCED_ERROR')
								.pipe(
									tap((errorMessage) => {
										this.notificationService.showError(errorMessage);
									}),
								);
						}),
					),
				),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	/**
	 * Sets up the declarative handler for create agent action
	 */
	private setupCreateAgentHandler(): void {
		this.createAgentTrigger$
			.pipe(
				tap(() => {
					this.loading = true;
					this.saveError = '';
				}),
				exhaustMap((createRequest) =>
					this.agentService.createAgent(createRequest).pipe(
						tap((agent) => {
							this.loading = false;
							this.router.navigate(['/agents', agent.id]);
						}),
						catchError((error) => {
							console.error('Error creating agent:', error);
							this.saveError = 'AGENTS.FAILED_CREATE_AGENT';
							this.loading = false;
							return of(null);
						}),
					),
				),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	/**
	 * Sets up the declarative handler for update agent action
	 */
	private setupUpdateAgentHandler(): void {
		this.updateAgentTrigger$
			.pipe(
				tap(() => {
					this.loading = true;
					this.saveError = '';
				}),
				exhaustMap(({ id, request }) =>
					this.agentService.updateAgent(id, request).pipe(
						tap(() => {
							this.loading = false;
							this.router.navigate(['/agents', id]);
						}),
						catchError((error) => {
							console.error('Error updating agent:', error);
							this.saveError = 'AGENTS.FAILED_UPDATE_AGENT';
							this.loading = false;
							return of(null);
						}),
					),
				),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	loadAgent(agentId: number): void {
		this.loading = true;
		this.agentService
			.getAgent(agentId)
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe({
				next: (agent) => {
					this.agentForm.patchValue({
						name: agent.name,
						department: agent.department,
						description: agent.description || '',
						instructions: agent.instructions || '',
						llmConfig: {
							modelName: agent.llmConfig?.modelName || this.llmModels[0],
							temperature: agent.llmConfig?.temperature ?? 0.7,
						},
					});
					// Parse toolConfigs from JSON string if it exists
					if (agent.toolConfigs) {
						try {
							this.toolConfigs = typeof agent.toolConfigs === 'string'
								? JSON.parse(agent.toolConfigs)
								: agent.toolConfigs;
						} catch (error) {
							console.warn('Failed to parse toolConfigs:', error);
							this.toolConfigs = [];
						}
					} else {
						this.toolConfigs = [];
					}
					this.loading = false;
				},
				error: (error) => {
					console.error('Error loading agent:', error);
					this.saveError = 'AGENTS.FAILED_LOAD_AGENT';
					this.loading = false;
				},
			});
	}

	/**
	 * Load available tools from the API
	 */
	loadTools(): void {
		this.loadingTools = true;
		this.toolsError = '';

		this.agentService
			.getTools()
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe({
				next: (tools) => {
					this.tools = tools;
				},
				error: (error) => {
					console.error('Error loading tools:', error);
					this.toolsError = 'AGENTS.FAILED_LOAD_TOOLS';
					this.loadingTools = false;
					this.cdr.detectChanges();
				},
				complete: () => {
					this.loadingTools = false;
					this.cdr.detectChanges();
				},
			});
	}

	initForm(): void {
		this.agentForm = this.fb.group({
			name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
			department: ['', [Validators.required]],
			description: ['', [Validators.maxLength(500)]],
			instructions: ['', [Validators.maxLength(1000)]],
			llmConfig: this.fb.group({
				modelName: ['', Validators.required],
				temperature: [0.7, [Validators.required, Validators.min(0), Validators.max(1)]],
			}),
		});
	}

	onSubmit(): void {
		if (this.agentForm.invalid) {
			return;
		}

		this.loading = true;
		const formValue = this.agentForm.value;
		const request: CreateAgentRequest | UpdateAgentRequest = {
			name: formValue.name,
			department: formValue.department,
			description: formValue.description,
			instructions: formValue.instructions,
			toolConfigs: this.toolConfigs.length > 0 ? JSON.stringify(this.toolConfigs) : undefined,
			llmConfig: {
				modelName: formValue.llmConfig.modelName,
				temperature: formValue.llmConfig.temperature,
			},
		};

		if (this.isEditMode && this.agentId) {
			this.updateAgentTrigger$.next({ id: this.agentId, request: request });
		} else {
			this.createAgentTrigger$.next(request as CreateAgentRequest);
		}
	}

	cancel(): void {
		if (this.isEditMode && this.agentId) {
			this.router.navigate(['/agents', this.agentId]);
		} else {
			this.router.navigate(['/agents']);
		}
	}

	/**
	 * Triggers the enhance description action
	 * Uses declarative pattern with subject trigger
	 */
	enhanceDescription(): void {
		const descriptionControl = this.agentForm.get('description');
		const currentDescription = descriptionControl?.value?.trim();

		if (!currentDescription || this.isEnhancingDescription) {
			return;
		}

		this.enhanceDescriptionTrigger$.next(currentDescription);
	}

	/**
	 * Triggers the enhance instruction action
	 * Uses declarative pattern with subject trigger
	 */
	enhanceInstruction(): void {
		const instructionControl = this.agentForm.get('instructions');
		const currentInstruction = instructionControl?.value?.trim();

		if (!currentInstruction || this.isEnhancingInstruction) {
			return;
		}

		this.enhanceInstructionTrigger$.next(currentInstruction);
	}

	isToolConnected(toolId: string): boolean {
		const config = this.toolConfigs.find(c => c.toolId === toolId);
		return !!config && config.enabled;
	}

	toggleToolConnection(tool: Tool): void {
		const existingConfigIndex = this.toolConfigs.findIndex(c => c.toolId === tool.id);
		const needsConfig = tool.parameters && Object.keys(tool.parameters).length > 0;

		if (existingConfigIndex > -1) {
			// It's connected. If it needs config, open dialog to edit. Otherwise, just disconnect.
			if (needsConfig) {
				this.openToolConfigDialog(tool, true);
			} else {
				this.toolConfigs.splice(existingConfigIndex, 1);
			}
		} else {
			// Not connected, so let's connect it
			if (needsConfig) {
				this.openToolConfigDialog(tool, false);
			} else {
				// No config needed, just add it directly
				this.toolConfigs.push({
					toolId: tool.id,
					enabled: true,
					configuration: {},
				});
			}
		}
	}

	private openToolConfigDialog(tool: Tool, isEditing: boolean): void {
		const existingConfig = this.toolConfigs.find(c => c.toolId === tool.id);

		const dialogRef = this.dialog.open<
			ToolConfigDialogComponent,
			ToolConfigDialogData,
			{ [key: string]: string } | 'DELETE' | undefined
		>(ToolConfigDialogComponent, {
			width: '500px',
			data: {
				tool: tool,
				existingConfig: existingConfig?.configuration || {},
				isEditing: isEditing,
			},
		});

		dialogRef.afterClosed().subscribe(result => {
			const existingConfigIndex = this.toolConfigs.findIndex(c => c.toolId === tool.id);

			if (result) {
				if (result === 'DELETE') {
					if (existingConfigIndex > -1) {
						this.toolConfigs.splice(existingConfigIndex, 1);
					}
				} else {
					const newConfig = {
						toolId: tool.id,
						enabled: true,
						configuration: result as { [key: string]: string },
					};
					if (existingConfigIndex > -1) {
						// Update existing config
						this.toolConfigs[existingConfigIndex] = newConfig;
					} else {
						// Add new config
						this.toolConfigs.push(newConfig);
					}
				}
			}
			// If result is undefined, user cancelled, so we do nothing.
		});
	}

	/**
	 * Track by function for ngFor to improve performance
	 */
	trackByToolId(index: number, tool: Tool): string {
		return tool.id;
	}

	/**
	 * Check if a tool has required configuration parameters
	 */
	hasRequiredConfig(tool: Tool): boolean {
		if (!tool.parameters) return false;
		return Object.values(tool.parameters).some(param => param.required || param.is_credential);
	}

	/**
	 * Get tool type from file name for display
	 */
	getToolTypeFromFile(fileName: string): string {
		if (fileName.includes('gmail')) return 'Email';
		if (fileName.includes('google_search')) return 'Search';
		if (fileName.includes('jira')) return 'Project Management';
		if (fileName.includes('rag')) return 'Knowledge Base';
		return 'Tool';
	}

	/**
	 * Get accessible label for tool card
	 */
	getToolCardAriaLabel(tool: Tool): string {
		const status = this.isToolConnected(tool.id) ? 'connected' : 'disconnected';
		const configRequired = this.hasRequiredConfig(tool) ? ', requires configuration' : '';
		return `${tool.name} tool, ${status}${configRequired}. Click to ${this.isToolConnected(tool.id) ? 'disconnect' : 'connect'}.`;
	}

	/**
	 * Get accessible label for connection button
	 */
	getConnectionButtonAriaLabel(tool: Tool): string {
		return this.isToolConnected(tool.id)
			? `Disconnect ${tool.name} tool`
			: `Connect ${tool.name} tool`;
	}

	/**
	 * Returns a descriptive tooltip for the temperature value.
	 * @param value The temperature value from the slider.
	 * @returns A translated string explaining the temperature level.
	 */
	getTemperatureTooltip(value: number | null): string {
		if (value === null) {
			return '';
		}
		if (value === 0) {
			return 'AGENTS.LLM.TEMP_TOOLTIP_0';
		}
		if (value >= 0.1 && value <= 0.3) {
			return 'AGENTS.LLM.TEMP_TOOLTIP_1';
		}
		if (value >= 0.4 && value <= 0.6) {
			return 'AGENTS.LLM.TEMP_TOOLTIP_2';
		}
		if (value >= 0.7 && value <= 0.9) {
			return 'AGENTS.LLM.TEMP_TOOLTIP_3';
		}
		if (value === 1) {
			return 'AGENTS.LLM.TEMP_TOOLTIP_4';
		}
		return '';
	}
}
