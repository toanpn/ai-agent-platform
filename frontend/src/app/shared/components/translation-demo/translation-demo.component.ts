import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { TranslationService } from '../../../core/services/translation.service';

@Component({
	selector: 'app-translation-demo',
	standalone: true,
	imports: [
		CommonModule,
		MatCardModule,
		MatButtonModule,
		TranslateModule
	],
	template: `
		<mat-card class="demo-card">
			<mat-card-header>
				<mat-card-title>{{ 'COMMON.TITLE' | translate }}</mat-card-title>
				<mat-card-subtitle>{{ 'COMMON.LANGUAGE' | translate }}: {{ currentLanguageName }}</mat-card-subtitle>
			</mat-card-header>
			
			<mat-card-content>
				<div class="demo-section">
					<h3>{{ 'AUTH.LOGIN' | translate }}</h3>
					<p>{{ 'AUTH.EMAIL' | translate }}: user&#64;example.com</p>
					<p>{{ 'AUTH.PASSWORD' | translate }}: ********</p>
				</div>
				
				<div class="demo-section">
					<h3>{{ 'CHAT.NEW_CHAT' | translate }}</h3>
					<p>{{ 'CHAT.TYPE_MESSAGE' | translate }}</p>
					<p>{{ 'CHAT.ATTACH_FILE' | translate }}</p>
				</div>
				
				<div class="demo-section">
					<h3>{{ 'AGENTS.CREATE_AGENT' | translate }}</h3>
					<p>{{ 'AGENTS.AGENT_NAME' | translate }}: My Agent</p>
					<p>{{ 'AGENTS.AGENT_DESCRIPTION' | translate }}: A helpful AI agent</p>
				</div>
			</mat-card-content>
			
			<mat-card-actions>
				<button mat-button (click)="switchToEnglish()">
					{{ 'COMMON.ENGLISH' | translate }}
				</button>
				<button mat-button (click)="switchToVietnamese()">
					{{ 'COMMON.VIETNAMESE' | translate }}
				</button>
			</mat-card-actions>
		</mat-card>
	`,
	styles: [`
		.demo-card {
			max-width: 600px;
			margin: 20px auto;
			padding: 20px;
		}
		
		.demo-section {
			margin: 20px 0;
			padding: 15px;
			border-left: 4px solid #3f51b5;
			background-color: #f5f5f5;
		}
		
		.demo-section h3 {
			margin-top: 0;
			color: #3f51b5;
		}
		
		mat-card-actions {
			display: flex;
			justify-content: center;
			gap: 10px;
		}
	`]
})
export class TranslationDemoComponent {
	private translationService = inject(TranslationService);
	
	get currentLanguageName(): string {
		return this.translationService.getCurrentLanguageName();
	}
	
	switchToEnglish(): void {
		this.translationService.setLanguage('en');
	}
	
	switchToVietnamese(): void {
		this.translationService.setLanguage('vi');
	}
} 