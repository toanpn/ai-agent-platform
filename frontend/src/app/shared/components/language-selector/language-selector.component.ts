import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
import { TranslationService, Language } from '../../../core/services/translation.service';

@Component({
	selector: 'app-language-selector',
	standalone: true,
	imports: [
		CommonModule,
		MatButtonModule,
		MatIconModule,
		MatMenuModule,
		TranslateModule
	],
	template: `
		<button 
			mat-icon-button 
			[matMenuTriggerFor]="languageMenu"
			[attr.aria-label]="'COMMON.LANGUAGE' | translate"
			[title]="'COMMON.LANGUAGE' | translate"
			class="language-selector-btn"
		>
			<mat-icon>language</mat-icon>
		</button>
		
		<mat-menu #languageMenu="matMenu">
			<button 
				mat-menu-item 
				*ngFor="let language of availableLanguages"
				(click)="selectLanguage(language.code)"
				[class.active]="language.code === currentLanguage"
			>
				<span>{{ language.nativeName }}</span>
				<mat-icon *ngIf="language.code === currentLanguage">check</mat-icon>
			</button>
		</mat-menu>
	`,
	styles: [`
		.language-selector-btn {
			margin-left: 8px;
		}
		
		.active {
			font-weight: bold;
		}
		
		mat-menu-item {
			display: flex;
			justify-content: space-between;
			align-items: center;
		}
	`]
})
export class LanguageSelectorComponent {
	private translationService = inject(TranslationService);
	
	availableLanguages: Language[] = this.translationService.getAvailableLanguages();
	currentLanguage: string = this.translationService.getCurrentLanguage();
	
	selectLanguage(languageCode: string): void {
		this.translationService.setLanguage(languageCode);
		this.currentLanguage = languageCode;
	}
} 