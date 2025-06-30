import { Component, Inject, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Tool, ToolParameter } from '../../../core/services/agent.service';

export interface ToolConfigDialogData {
	tool: Tool;
	existingConfig: { [key: string]: string };
	isEditing: boolean;
}

@Component({
	selector: 'app-tool-config-dialog',
	standalone: true,
	imports: [
		TranslateModule,
		CommonModule,
		ReactiveFormsModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatProgressSpinnerModule,
		MatIconModule,
	],
	templateUrl: './tool-config-dialog.component.html',
	styleUrls: ['./tool-config-dialog.component.scss'],
})
export class ToolConfigDialogComponent implements OnInit {
	configForm: FormGroup;
	tool: Tool;
	parameters: { key: string; details: ToolParameter }[] = [];
	isEditing: boolean;

	private translateService = inject(TranslateService);

	constructor(
		private fb: FormBuilder,
		public dialogRef: MatDialogRef<ToolConfigDialogComponent>,
		@Inject(MAT_DIALOG_DATA) public data: ToolConfigDialogData,
	) {
		this.tool = data.tool;
		this.isEditing = !!data.existingConfig && Object.keys(data.existingConfig).length > 0;
		this.configForm = this.fb.group({});
	}

	ngOnInit(): void {
		this.buildForm();
	}

	private buildForm(): void {
		if (!this.tool.parameters) {
			return;
		}

		let ignoredKeys = ['query'];
		// For tools like Confluence and Jira that use an action/parameters pattern,
		// we don't want to show those in the configuration pop-up.
		if (this.tool.id === 'confluence_tool' || this.tool.id === 'jira_tool') {
			ignoredKeys = ['query', 'action', 'parameters'];
		}

		this.parameters = Object.entries(this.tool.parameters)
			.filter(([key]) => !ignoredKeys.includes(key.toLowerCase()))
			.map(([key, details]) => ({
				key,
				details,
			}));

		for (const { key, details } of this.parameters) {
			const initialValue = this.data.existingConfig[key] || details.default || '';
			const validators = details.required ? [Validators.required] : [];
			this.configForm.addControl(key, this.fb.control(initialValue, validators));
		}
	}

	onSave(): void {
		if (this.configForm.valid) {
			this.dialogRef.close(this.configForm.value);
		}
	}

	onDisconnect(): void {
		this.dialogRef.close('DELETE');
	}

	onTestConnection(): void {
		// TODO: Implement test connection logic
		console.log('Test connection:', this.configForm.value);
	}

	onCancel(): void {
		this.dialogRef.close();
	}

	getParameterLabel(paramKey: string): string {
		const toolKey = this.tool.id.replace(/_tool$/, '');
		return `AGENTS.TOOLS_CONFIG.PARAMS.${toolKey}.${paramKey}`;
	}

	get toolDisplayName(): string {
		const toolKey = this.tool.id.replace(/_tool$/, '');
		const translationKey = `AGENTS.TOOL_NAMES.${toolKey}`;
		const translation = this.translateService.instant(translationKey);

		if (translation === translationKey) {
			return this.tool.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
		}

		return translation;
	}

	/**
	 * Track by function for parameter list
	 */
	trackByParameterKey(index: number, param: { key: string; details: ToolParameter }): string {
		return param.key;
	}

	/**
	 * Get placeholder text for parameter input
	 */
	getParameterPlaceholder(param: { key: string; details: ToolParameter }): string {
		if (param.details.default) {
			return this.translateService.instant('AGENTS.TOOLS_CONFIG.PLACEHOLDERS.DEFAULT', {
				defaultValue: param.details.default,
			});
		}
		if (param.details.is_credential) {
			return this.translateService.instant('AGENTS.TOOLS_CONFIG.PLACEHOLDERS.ENTER_CREDENTIAL');
		}

		const paramLabelKey = this.getParameterLabel(param.key);
		let paramName = this.translateService.instant(paramLabelKey);

		if (paramName === paramLabelKey) {
			paramName = param.key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
		}

		return this.translateService.instant('AGENTS.TOOLS_CONFIG.PLACEHOLDERS.ENTER_VALUE', { paramName });
	}
}
