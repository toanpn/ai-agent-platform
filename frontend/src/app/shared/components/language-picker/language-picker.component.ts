import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule, MatIconRegistry } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
import {
	TranslationService,
	Language,
} from '../../../core/services/translation.service';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
	selector: 'app-language-picker',
	standalone: true,
	imports: [
		CommonModule,
		MatButtonModule,
		MatIconModule,
		MatMenuModule,
		TranslateModule,
	],
	templateUrl: './language-picker.component.html',
	styleUrls: ['./language-picker.component.scss'],
})
export class LanguagePickerComponent {
	private translationService = inject(TranslationService);
	private matIconRegistry = inject(MatIconRegistry);
	private domSanitizer = inject(DomSanitizer);

	availableLanguages: Language[] = this.translationService.getAvailableLanguages();
	currentLanguage: Language;

	constructor() {
		this.currentLanguage =
			this.availableLanguages.find(
				(lang) => lang.code === this.translationService.getCurrentLanguage()
			) || this.availableLanguages[0];

		this.matIconRegistry.addSvgIcon(
			'us-flag',
			this.domSanitizer.bypassSecurityTrustResourceUrl(
				'assets/icons/us-flag.svg'
			)
		);
		this.matIconRegistry.addSvgIcon(
			'vn-flag',
			this.domSanitizer.bypassSecurityTrustResourceUrl(
				'assets/icons/vn-flag.svg'
			)
		);
		this.matIconRegistry.addSvgIcon(
			'arrow-down',
			this.domSanitizer.bypassSecurityTrustResourceUrl(
				'assets/icons/arrow-down.svg'
			)
		);
	}

	selectLanguage(language: Language): void {
		this.translationService.setLanguage(language.code);
		this.currentLanguage = language;
	}

	getFlagIcon(languageCode: string): string {
		return languageCode === 'en' ? 'us-flag' : 'vn-flag';
	}
} 