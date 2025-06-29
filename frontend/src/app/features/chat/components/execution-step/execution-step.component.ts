import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { ExecutionStep } from '../../../../core/services/chat.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
	selector: 'app-execution-step',
	standalone: true,
	imports: [
		CommonModule,
		MatCardModule,
		MatIconModule,
		MatExpansionModule,
		TranslateModule,
	],
	templateUrl: './execution-step.component.html',
	styleUrls: ['./execution-step.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExecutionStepComponent {
	@Input({ required: true }) step!: ExecutionStep;

	get formattedToolInput(): string {
		if (!this.step.toolInput) {
			return '';
		}
		try {
			// The toolInput is a JSON string, so we parse it to get the actual object.
			const parsedInput = JSON.parse(this.step.toolInput);
			// Then we stringify it back to a formatted JSON string for display.
			// This will correctly handle the Unicode characters.
			return JSON.stringify(parsedInput, null, 2);
		} catch (error) {
			// If it's not a valid JSON string, return it as is.
			return this.step.toolInput;
		}
	}
}
