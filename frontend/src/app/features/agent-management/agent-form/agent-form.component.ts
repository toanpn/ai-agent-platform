import { TextFieldModule } from '@angular/cdk/text-field';
import { CommonModule } from '@angular/common';
import {
	ChangeDetectorRef,
	Component,
	DestroyRef,
	inject,
	OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
	FormBuilder,
	FormGroup,
	ReactiveFormsModule,
	Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import {
	MatDialog,
	MatDialogModule,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
	ActivatedRoute,
	Router,
	RouterModule,
} from '@angular/router';

import {
	of,
	Subject,
} from 'rxjs';
import {
	catchError,
	exhaustMap,
	filter,
	finalize,
	switchMap,
	tap,
} from 'rxjs/operators';

import {
	TranslateModule,
	TranslateService,
} from '@ngx-translate/core';

import {
	AgentFile,
	AgentService,
	CreateAgentRequest,
	LlmConfig,
	Tool,
	ToolConfig,
	UpdateAgentRequest,
} from '../../../core/services/agent.service';
import { ChatService } from '../../../core/services/chat.service';
import { FileService } from '../../../core/services/file.service';
import { NotificationService } from '../../../core/services/notification.service';
import { AgentStateService } from '../../../features/chat/agent-state.service';
import {
	ToolConfigDialogComponent,
	ToolConfigDialogData,
} from '../tool-config-dialog/tool-config-dialog.component';

interface UpdateAgentPayload {
	id: number;
	request: UpdateAgentRequest;
}

export interface FileUpload {
	file: File;
	status: 'pending' | 'uploading' | 'success' | 'error';
	error?: string;
}

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
		MatSlideToggleModule,
		MatDialogModule,
		MatListModule,
		TextFieldModule,
		MatInputModule,
	],
	templateUrl: './agent-form.component.html',
	styleUrls: ['./agent-form.component.scss'],
})
export class AgentFormComponent implements OnInit {
	comingSoonTools = [
		{
			id: 'playwright_browser_toolkit',
			name: 'Playwright Browser Toolkit',
			description: 'Automate browser testing with Playwright.',
		},
		{
			id: 'gitlab_toolkit',
			name: 'GitLab Toolkit',
			description: 'Manage code repositories and CI/CD pipelines.',
		},
		{
			id: 'sql_database_toolkit',
			name: 'SQL Database Toolkit',
			description: 'Query and interact with SQL databases.',
		},
		{
			id: 'jenkins_toolkit',
			name: 'Jenkins',
			description: 'Automate builds and deployment with Jenkins.',
		},
	];
	agentForm!: FormGroup;
	isEditMode = false;
	agentId: number | null = null;
	loading = false;
	saveError = '';
	isEnhancingDescription = false;
	isEnhancingInstruction = false;

	// Files
	agentFiles: AgentFile[] = [];
	fileUploadLoading = false;
	fileUploads: FileUpload[] = [];
	isDragging = false;

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
	llmModels: string[] = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.5-pro'];

	// Tools related properties
	tools: Tool[] = [];
	connectedTools: string[] = []; // Track which tools are connected
	loadingTools = false;
	toolsError = '';
	toolConfigs: ToolConfig[] = [];

	private fb = inject(FormBuilder);
	private agentService = inject(AgentService);
	private fileService = inject(FileService);
	private chatService = inject(ChatService);
	private notificationService = inject(NotificationService);
	private translateService = inject(TranslateService);
	private agentStateService = inject(AgentStateService);
	private route = inject(ActivatedRoute);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);
	private dialog = inject(MatDialog);
	private cdr = inject(ChangeDetectorRef);

	// Action subjects for declarative patterns
	private enhanceDescriptionTrigger$ = new Subject<string>();
	private enhanceInstructionTrigger$ = new Subject<string>();
	private createAgentTrigger$ = new Subject<CreateAgentRequest>();
	private updateAgentTrigger$ = new Subject<UpdateAgentPayload>();

	ngOnInit(): void {
		this.initForm();
		this.setupEnhanceDescriptionHandler();
		this.setupEnhanceInstructionHandler();
		this.setupCreateAgentHandler();
		this.setupUpdateAgentHandler();

		// Load tools first, then check if we need to load agent data
		this.loadTools();

		// Check if we're in edit mode based on the URL
		const idParam = this.route.snapshot.paramMap.get('id');
		if (idParam) {
			const agentId = parseInt(idParam, 10);
			if (!isNaN(agentId)) {
				this.agentId = agentId;
				this.isEditMode = true;
				// Load agent after tools are loaded
				this.loadAgentAfterTools(agentId);
			} else {
				this.saveError = 'AGENTS.INVALID_AGENT_ID';
			}
		} else {
			// Set default values for new agent
			this.agentForm.get('llmConfig.modelName')?.setValue(this.llmModels[0]);
			this.agentForm.get('llmConfig.temperature')?.setValue(0.7);
			// Initialize empty toolConfigs and connectedTools for new agents
			this.toolConfigs = [];
			this.connectedTools = [];
			this.agentFiles = [];
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
				tap(() => (this.loading = true)),
				exhaustMap(request =>
					this.agentService.createAgent(request).pipe(
						catchError(err => {
							console.error('Error during agent creation process:', err);
							this.saveError = 'AGENTS.CREATE_ERROR';
							this.loading = false;
							this.notificationService.showError('Failed to create agent.');
							return of(null);
						}),
					),
				),
				filter(response => !!response),
				tap(response => {
					this.loading = false;
					if (response) {
						this.agentStateService.refreshAgents();
						this.notificationService.showSuccess('Agent created successfully!');
						this.router.navigate(['/agents/result'], {
							state: { agent: response, action: 'create' },
						});
					}
				}),
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
				tap(() => (this.loading = true)),
				exhaustMap(({ id, request }) => {
					return this.agentService.updateAgent(id, request).pipe(
						catchError(err => {
							console.error('Error during agent update process:', err);
							this.saveError = 'AGENTS.UPDATE_ERROR';
							return of(null);
						}),
					);
				}),
				filter(result => !!result),
				tap(updateResult => {
					this.loading = false;
					if (updateResult) {
						this.agentStateService.refreshAgents();
						this.notificationService.showSuccess('Agent updated successfully!');
						this.router.navigate(['/agents/result'], {
							state: { agent: updateResult, action: 'update' },
						});
						this.fileUploads = []; // Clear any pending/failed uploads
					}
				}),
				finalize(() => (this.loading = false)),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}

	loadAgent(agentId: number): void {
		this.loading = true;
		this.agentService
			.getAgent(agentId)
			.pipe(
				tap((agent) => {
					this.agentForm.patchValue({
						name: agent.name,
						department: agent.department,
						description: agent.description || '',
						instructions: agent.instructions || '',
						llmConfig: {
							modelName: agent.llmConfig?.modelName || this.llmModels[0],
							temperature: agent.llmConfig?.temperature ?? 0.7,
						},
						isPublic: agent.isPublic,
					});
					// Parse toolConfigs from JSON string if it exists
					if (agent.toolConfigs) {
						try {
							const parsedConfigs = typeof agent.toolConfigs === 'string'
								? JSON.parse(agent.toolConfigs)
								: agent.toolConfigs;

							// Convert from dictionary format {toolKey: {config}} to array format
							this.toolConfigs = [];
							if (parsedConfigs && typeof parsedConfigs === 'object') {
								// Handle both old array format and new dictionary format
								if (Array.isArray(parsedConfigs)) {
									// Old format - keep as is
									this.toolConfigs = parsedConfigs;
								} else {
									// New dictionary format - convert to array
									Object.entries(parsedConfigs).forEach(([toolKey, config]) => {
										// Find the tool by name, ID, or a key that matches
										let tool = this.tools.find(t =>
											t.name === toolKey ||
											t.id === toolKey ||
											t.id.replace('_tool', '') === toolKey ||
											t.name.toLowerCase() === toolKey.toLowerCase()
										);

										if (tool) {
											this.toolConfigs.push({
												toolId: tool.id,
												enabled: true,
												configuration: config as { [key: string]: string }
											});
										} else {
											console.warn(`Tool not found for key: ${toolKey}`);
										}
									});
								}
							}
						} catch (error) {
							console.warn('Failed to parse toolConfigs:', error);
							this.toolConfigs = [];
						}
					} else {
						this.toolConfigs = [];
					}
					// Load connected tools array
					this.connectedTools = agent.tools || [];
					this.agentFiles = agent.files || [];
					this.loading = false;
				}),
				catchError((error) => {
					console.error('Error loading agent:', error);
					this.saveError = 'AGENTS.FAILED_LOAD_AGENT';
					this.loading = false;
					return of(null);
				}),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
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

	/**
	 * Load agent data after tools have been loaded
	 */
	private loadAgentAfterTools(agentId: number): void {
		// Wait for tools to be loaded before loading agent
		const checkToolsLoaded = () => {
			if (!this.loadingTools && this.tools.length > 0) {
				this.loadAgent(agentId);
			} else if (!this.loadingTools && this.tools.length === 0 && !this.toolsError) {
				// No tools available, but still load agent
				this.loadAgent(agentId);
			} else if (!this.loadingTools && this.toolsError) {
				// Tools failed to load, but still load agent
				this.loadAgent(agentId);
			} else {
				// Still loading tools, check again in 100ms
				setTimeout(checkToolsLoaded, 100);
			}
		};
		checkToolsLoaded();
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
			isPublic: [false],
		});
	}

	onSubmit(): void {
		this.saveError = '';
		if (this.agentForm.invalid) {
			this.agentForm.markAllAsTouched();
			this.translateService.get('AGENTS.FORM_INVALID_ERROR').subscribe(message => {
				this.notificationService.showError(message);
			});
			return;
		}

		// Prepare tool configurations
		let toolConfigsJson: string | undefined;
		if (this.toolConfigs.length > 0) {
			const toolConfigsDict: { [toolKey: string]: { [key: string]: string } } = {};
			this.toolConfigs.forEach(config => {
				const tool = this.tools.find(t => t.id === config.toolId);
				if (tool) {
					toolConfigsDict[tool.id] = config.configuration;
				}
			});
			toolConfigsJson = JSON.stringify(toolConfigsDict);
		}

		const agentRequest: CreateAgentRequest | UpdateAgentRequest = {
			name: this.agentForm.value.name,
			department: this.agentForm.value.department,
			description: this.agentForm.value.description,
			instructions: this.agentForm.value.instructions,
			llmConfig: this.agentForm.value.llmConfig as LlmConfig,
			isPublic: this.agentForm.value.isPublic,
			tools: this.connectedTools,
			toolConfigs: toolConfigsJson,
		};

		if (this.isEditMode && this.agentId) {
			this.updateAgentTrigger$.next({ id: this.agentId, request: agentRequest });
		} else {
			this.createAgentTrigger$.next(agentRequest as CreateAgentRequest);
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
		return this.connectedTools.includes(toolId);
	}

	toggleToolConnection(tool: Tool): void {
		const isCurrentlyConnected = this.isToolConnected(tool.id);
		const existingConfigIndex = this.toolConfigs.findIndex(c => c.toolId === tool.id);
		const needsConfig = tool.parameters && Object.keys(tool.parameters).length > 0;

		if (isCurrentlyConnected) {
			// It's connected. If it needs config, open dialog to edit. Otherwise, just disconnect.
			if (needsConfig) {
				this.openToolConfigDialog(tool, true);
			} else {
				// Disconnect: remove from both connectedTools and toolConfigs
				this.connectedTools = this.connectedTools.filter(toolId => toolId !== tool.id);
				if (existingConfigIndex > -1) {
					this.toolConfigs.splice(existingConfigIndex, 1);
				}
			}
		} else {
			// Not connected, so let's connect it
			if (needsConfig) {
				this.openToolConfigDialog(tool, false);
			} else {
				// No config needed, just add it directly
				this.connectedTools.push(tool.id);
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
					// Disconnect: remove from both connectedTools and toolConfigs
					this.connectedTools = this.connectedTools.filter(toolId => toolId !== tool.id);
					if (existingConfigIndex > -1) {
						this.toolConfigs.splice(existingConfigIndex, 1);
					}
				} else {
					// Connect: add to connectedTools if not already there
					if (!this.connectedTools.includes(tool.id)) {
						this.connectedTools.push(tool.id);
					}

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
			this.cdr.detectChanges();
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
	 * Check if a connected tool is properly configured (has all required parameters filled)
	 */
	isToolProperlyConfigured(tool: Tool): boolean {
		if (!this.hasRequiredConfig(tool)) return true; // No config needed

		const toolConfig = this.toolConfigs.find(c => c.toolId === tool.id);
		if (!toolConfig) return false;

		// Check if all required parameters are filled
		const requiredParams = Object.entries(tool.parameters || {})
			.filter(([_, param]) => param.required || param.is_credential)
			.map(([key, _]) => key);

		return requiredParams.every(paramKey =>
			toolConfig.configuration[paramKey] &&
			toolConfig.configuration[paramKey].trim() !== ''
		);
	}

	/**
	 * Determine whether to show "Requires configuration" text
	 */
	shouldShowRequiresConfig(tool: Tool): boolean {
		// Don't show if tool doesn't need config
		if (!this.hasRequiredConfig(tool)) return false;

		// Don't show if tool is connected and properly configured
		if (this.isToolConnected(tool.id) && this.isToolProperlyConfigured(tool)) return false;

		// Show if tool needs config and either not connected or not properly configured
		return true;
	}

	/**
	 * Debug method to check tool configuration status
	 */
	debugToolStatus(tool: Tool): void {
		console.log(`=== Debug for ${tool.name} (${tool.id}) ===`);
		console.log('Is connected:', this.isToolConnected(tool.id));
		console.log('Has required config:', this.hasRequiredConfig(tool));
		console.log('Is properly configured:', this.isToolProperlyConfigured(tool));
		console.log('Should show requires config:', this.shouldShowRequiresConfig(tool));

		const toolConfig = this.toolConfigs.find(c => c.toolId === tool.id);
		console.log('Tool config found:', !!toolConfig);
		if (toolConfig) {
			console.log('Configuration:', toolConfig.configuration);
		}

		if (tool.parameters) {
			const requiredParams = Object.entries(tool.parameters)
				.filter(([_, param]) => param.required || param.is_credential)
				.map(([key, _]) => key);
			console.log('Required parameters:', requiredParams);

			if (toolConfig) {
				requiredParams.forEach(param => {
					const value = toolConfig.configuration[param];
					console.log(`${param}: "${value}" (filled: ${!!(value && value.trim())})`);
				});
			}
		}
		console.log('=== End Debug ===');
	}

	/**
	 * Get tool type from file name for display
	 */
	getToolTypeFromFile(fileName: string): string {
		const extension = fileName.split('.').pop()?.toLowerCase();
		switch (extension) {
			case 'json':
				return 'JSON';
			case 'py':
				return 'Python';
			default:
				return 'Tool';
		}
	}

	getToolDisplayName(toolName: string): string {
		const nameMap: { [key: string]: string } = {
			google_search_tool: 'Google Search',
			knowledge_search_tool: 'Knowledge Search',
			gmail_tool: 'Gmail',
			jira_tool: 'Jira',
			confluence_tool: 'Confluence',
		};
		return nameMap[toolName] || toolName;
	}

	/**
	 * Get accessible label for tool card
	 */
	getToolCardAriaLabel(tool: Tool): string {
		const status = this.isToolConnected(tool.id) ? 'connected' : 'disconnected';
		const configRequired = this.hasRequiredConfig(tool) ? ', requires configuration' : '';
		return `${this.getToolDisplayName(tool.name)} tool, ${status}${configRequired}. Click to ${
			this.isToolConnected(tool.id) ? 'disconnect' : 'connect'
		}.`;
	}

	/**
	 * Get accessible label for connection button
	 */
	getConnectionButtonAriaLabel(tool: Tool): string {
		return this.isToolConnected(tool.id)
			? `Disconnect ${this.getToolDisplayName(tool.name)} tool`
			: `Connect ${this.getToolDisplayName(tool.name)} tool`;
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
		if (value <= 0.3) {
			return 'AGENTS.LLM.TEMPERATURE_TOOLTIPS.PRECISE_HINT';
		} else if (value <= 0.7) {
			return 'AGENTS.LLM.TEMPERATURE_TOOLTIPS.BALANCED_HINT';
		} else {
			return 'AGENTS.LLM.TEMPERATURE_TOOLTIPS.CREATIVE_HINT';
		}
	}

	onDragOver(event: DragEvent): void {
		event.preventDefault();
		event.stopPropagation();
		this.isDragging = true;
	}

	onDragLeave(event: DragEvent): void {
		event.preventDefault();
		event.stopPropagation();
		this.isDragging = false;
	}

	onDrop(event: DragEvent): void {
		event.preventDefault();
		event.stopPropagation();
		this.isDragging = false;
		const files = event.dataTransfer?.files;

		if (files && files.length > 0) {
			const newFiles = Array.from(files);
			this.addFiles(newFiles);
		}
	}

	onFileSelected(event: Event): void {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			const newFiles = Array.from(input.files);
			this.addFiles(newFiles);
			input.value = ''; // Reset file input
		}
	}

	private addFiles(newFiles: File[]): void {
		const currentFileNames = new Set([
			...this.fileUploads.map(fu => fu.file.name),
			...this.agentFiles.map(f => f.fileName),
		]);

		const uniqueNewFiles = newFiles.filter(file => !currentFileNames.has(file.name));
		if (uniqueNewFiles.length < newFiles.length) {
			this.notificationService.showWarning('Duplicate files were ignored.');
		}

		const newUploads: FileUpload[] = uniqueNewFiles.map(file => ({
			file,
			status: 'pending',
		}));

		this.fileUploads.push(...newUploads);
		newUploads.forEach(upload => this.uploadFile(upload));
	}

	private uploadFile(upload: FileUpload): void {
		if (!this.agentId) {
			upload.status = 'error';
			upload.error = 'Agent ID is not available.';
			this.notificationService.showError('Cannot upload file: Agent is not saved yet.');
			return;
		}

		upload.status = 'uploading';

		this.fileService
			.uploadFile(this.agentId, upload.file)
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe({
				next: (uploadedFile: AgentFile) => {
					// On success, remove from the upload list
					this.fileUploads = this.fileUploads.filter(fu => fu !== upload);

					// The API response might not contain all file details needed by the UI.
					// We'll merge the API response with the local file info.
					const newFile: AgentFile = {
						...uploadedFile,
						fileName: upload.file.name,
						fileSize: upload.file.size,
					};

					// And add to the permanent agent files list
					this.agentFiles.push(newFile);
					// Manually trigger change detection
					this.cdr.detectChanges();
				},
				error: err => {
					upload.status = 'error';
					upload.error = err.error?.message || 'Upload failed';
					this.notificationService.showError(`Failed to upload file '${upload.file.name}'.`);
					// Manually trigger change detection to show error state
					this.cdr.detectChanges();
				},
			});
	}

	retryUpload(upload: FileUpload): void {
		upload.status = 'pending';
		upload.error = undefined;
		this.uploadFile(upload);
	}

	removeSelectedFile(uploadToRemove: FileUpload): void {
		this.fileUploads = this.fileUploads.filter(upload => upload !== uploadToRemove);
	}

	deleteFile(fileId: number): void {
		this.fileService.deleteFile(fileId).subscribe({
			next: () => {
				this.agentFiles = this.agentFiles.filter(file => file.id !== fileId);
				// Manually trigger change detection
				this.cdr.detectChanges();
			},
			error: err => {
				this.notificationService.showError('Failed to delete file.');
				console.error('File deletion error', err);
			},
		});
	}

	formatFileSize(bytes: number, decimals = 2): string {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const dm = decimals < 0 ? 0 : decimals;
		const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
	}

	getIconForFile(fileName: string): string {
		if (!fileName) {
			return '/assets/icons/icon-file.svg';
		}
		const extension = fileName.split('.').pop()?.toLowerCase();
		switch (extension) {
			case 'pdf':
				return '/assets/icons/icon-pdf.svg';
			case 'doc':
			case 'docx':
				return '/assets/icons/icon-word.svg';
			case 'xls':
			case 'xlsx':
				return '/assets/icons/icon-excel.svg';
			default:
				return '/assets/icons/icon-file.svg'; // Default icon
		}
	}

	getToolIcon(toolId: string): string {
		const iconMap: { [key: string]: string } = {
			google_search_tool: 'assets/icons/google-search.svg',
			knowledge_tool: 'assets/icons/knowledge-tool.svg',
			gmail_tool: 'assets/icons/email.svg',
			jira_tool: 'assets/icons/jira.svg',
			confluence_tool: 'assets/icons/confluence.svg',
			playwright_browser_toolkit: 'assets/icons/playwright.svg',
			gitlab_toolkit: 'assets/icons/gitlab.svg',
			sql_database_toolkit: 'assets/icons/sql.svg',
			jenkins_toolkit: 'assets/icons/jenkins.svg',
		};
		return iconMap[toolId] || 'assets/icons/icon-file.svg';
	}

	getToolKey(toolName: string): string {
		return toolName.toLowerCase().replace(/_/g, '-');
	}
}
