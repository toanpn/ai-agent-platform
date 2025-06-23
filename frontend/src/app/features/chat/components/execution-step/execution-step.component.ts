import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { ExecutionStep } from '../../../../core/services/chat.service';

@Component({
	selector: 'app-execution-step',
	standalone: true,
	imports: [CommonModule, MatCardModule, MatIconModule, MatExpansionModule],
	templateUrl: './execution-step.component.html',
	styleUrls: ['./execution-step.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExecutionStepComponent {
	@Input({ required: true }) step!: ExecutionStep;
}
