import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
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
		CommonModule,
		ReactiveFormsModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatProgressSpinnerModule,
		MatIconModule,
		TranslateModule,
	],
	templateUrl: './tool-config-dialog.component.html',
	styleUrls: ['./tool-config-dialog.component.scss'],
})
export class ToolConfigDialogComponent implements OnInit {
	configForm: FormGroup;
	tool: Tool;
	parameters: { key: string; details: ToolParameter }[] = [];
	isEditing: boolean;

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

		this.parameters = Object.entries(this.tool.parameters).map(([key, details]) => ({
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

	onCancel(): void {
		this.dialogRef.close();
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
			return `Default: ${param.details.default}`;
		}
		if (param.details.is_credential) {
			return 'Enter secure credential';
		}
		return `Enter ${param.key}`;
	}
}
