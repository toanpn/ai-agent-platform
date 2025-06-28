import {
	ApplicationConfig,
	importProvidersFrom,
	provideAppInitializer,
	inject,
	provideBrowserGlobalErrorListeners,
	provideZoneChangeDetection,
} from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { AuthInterceptor } from './core/interceptors/auth.interceptor';
import { AuthService } from './core/services/auth.service';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { HttpClient } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { environment } from '../environments/environment';
import { provideHashbrown } from '@hashbrownai/angular';
import { provideMarkdown } from 'ngx-markdown';

// AoT requires an exported function for factories
export function HttpLoaderFactory(http: HttpClient) {
	return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

export const appConfig: ApplicationConfig = {
	providers: [
		provideBrowserGlobalErrorListeners(),
		provideZoneChangeDetection({ eventCoalescing: true }),
		provideRouter(routes, withComponentInputBinding()),
		provideAnimationsAsync(),
		provideHttpClient(withInterceptors([AuthInterceptor])),
		provideMarkdown(),
		provideHashbrown(environment.hashbrown.config),
		// Import Angular Material SnackBar module for the notification service
		importProvidersFrom(MatSnackBarModule),
		// Import translation module
		importProvidersFrom(
			TranslateModule.forRoot({
				loader: {
					provide: TranslateLoader,
					useFactory: HttpLoaderFactory,
					deps: [HttpClient],
				},
				defaultLanguage: 'vi',
			}),
		),
		provideAppInitializer(() => inject(AuthService).init()),
	],
};
