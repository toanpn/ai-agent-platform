import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { ExecutionDetails } from '../../../../core/services/chat.service';
import { ExecutionStepComponent } from '../execution-step/execution-step.component';
import { TranslateModule } from '@ngx-translate/core';

@Component({
	selector: 'app-execution-details',
	standalone: true,
	imports: [
		CommonModule,
		MatCardModule,
		MatIconModule,
		MatExpansionModule,
		ExecutionStepComponent,
		TranslateModule,
	],
	templateUrl: './execution-details.component.html',
	styleUrls: ['./execution-details.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExecutionDetailsComponent {
	@Input({ required: true }) details!: ExecutionDetails;
}
