import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface Language {
  code: string;
  name: string;
  nativeName: string;
}

@Injectable({
  providedIn: 'root'
})
export class TranslationService {
  private currentLanguageSubject = new BehaviorSubject<string>('vi');
  public currentLanguage$ = this.currentLanguageSubject.asObservable();

  public readonly availableLanguages: Language[] = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt' }
  ];

  constructor(private translateService: TranslateService) {
    this.initializeTranslation();
  }

  private initializeTranslation(): void {
    // Set default language to Vietnamese
    this.translateService.setDefaultLang('vi');
    
    // Get stored language or use Vietnamese as default
    const storedLanguage = localStorage.getItem('preferredLanguage') || 'vi';
    this.setLanguage(storedLanguage);
  }

  public setLanguage(languageCode: string): void {
    // Validate language code
    if (!this.availableLanguages.find(lang => lang.code === languageCode)) {
      console.warn(`Language code '${languageCode}' is not supported. Using Vietnamese as fallback.`);
      languageCode = 'vi';
    }

    this.translateService.use(languageCode);
    this.currentLanguageSubject.next(languageCode);
    localStorage.setItem('preferredLanguage', languageCode);
  }

  public getCurrentLanguage(): string {
    return this.currentLanguageSubject.value;
  }

  public getLanguageName(languageCode: string): string {
    const language = this.availableLanguages.find(lang => lang.code === languageCode);
    return language ? language.nativeName : languageCode;
  }

  public getCurrentLanguageName(): string {
    return this.getLanguageName(this.getCurrentLanguage());
  }

  public getAvailableLanguages(): Language[] {
    return [...this.availableLanguages];
  }

  public translate(key: string, params?: any): Observable<string> {
    return this.translateService.get(key, params);
  }

  public instant(key: string, params?: any): string {
    return this.translateService.instant(key, params);
  }

  public onLangChange(): Observable<any> {
    return this.translateService.onLangChange;
  }
} 