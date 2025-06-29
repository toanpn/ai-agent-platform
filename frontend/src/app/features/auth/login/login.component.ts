import { CommonModule } from '@angular/common';
import {
	Component,
	DestroyRef,
	inject,
	OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
	AbstractControl,
	FormBuilder,
	FormControl,
	FormGroupDirective,
	NgForm,
	ReactiveFormsModule,
	ValidationErrors,
	ValidatorFn,
	Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { ErrorStateMatcher } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import {
	MatIconModule,
	MatIconRegistry,
} from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DomSanitizer } from '@angular/platform-browser';
import {
	Router,
	RouterModule,
} from '@angular/router';

import {
	catchError,
	exhaustMap,
	finalize,
	of,
	Subject,
} from 'rxjs';

import {
	TranslateModule,
	TranslateService,
} from '@ngx-translate/core';

import { AuthService } from '../../../core/services/auth.service';
import { NotificationService } from '../../../core/services/notification.service';
import {
	LanguagePickerComponent,
} from '../../../shared/components/language-picker/language-picker.component';

export const passwordMatchValidator: ValidatorFn = (
	control: AbstractControl
): ValidationErrors | null => {
	const password = control.get('password');
	const confirmPassword = control.get('confirmPassword');

	if (
		!password ||
		!confirmPassword ||
		password.value === confirmPassword.value
	) {
		return null;
	}

	return { passwordMismatch: true };
};

/** Error state matcher for password mismatch validation. */
export class PasswordMismatchErrorStateMatcher implements ErrorStateMatcher {
	isErrorState(
		control: FormControl | null,
		form: FormGroupDirective | NgForm | null
	): boolean {
		const controlTouched = !!(control && (control.dirty || control.touched));
		const parentInvalid = !!(
			control &&
			control.parent &&
			control.parent.invalid &&
			control.parent.hasError('passwordMismatch')
		);

		return (control?.invalid && controlTouched) || (parentInvalid && controlTouched);
	}
}

/**
 * LoginComponent handles user authentication through a login form.
 * It manages the login form state, authentication requests, and displays
 * appropriate feedback during the login process.
 */
@Component({
	selector: 'app-login',
	standalone: true,
	imports: [
		CommonModule,
		ReactiveFormsModule,
		RouterModule,
		MatCardModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatIconModule,
		MatProgressSpinnerModule,
		TranslateModule,
		LanguagePickerComponent,
	],
	templateUrl: './login.component.html',
	styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
	private fb = inject(FormBuilder);
	private authService = inject(AuthService);
	private router = inject(Router);
	private notificationService = inject(NotificationService);
	private translate = inject(TranslateService);
	private destroyRef = inject(DestroyRef);
	private matIconRegistry = inject(MatIconRegistry);
	private domSanitizer = inject(DomSanitizer);

	private loginAction$ = new Subject<void>();
	private registerAction$ = new Subject<void>();

	passwordMatcher = new PasswordMismatchErrorStateMatcher();

	loginForm = this.fb.group({
		email: ['', [Validators.required, Validators.email]],
		password: ['', [Validators.required]],
	});

	registerForm = this.fb.group(
		{
			fullName: ['', [Validators.required]],
			email: ['', [Validators.required, Validators.email]],
			password: ['', [Validators.required, Validators.minLength(6)]],
			confirmPassword: ['', [Validators.required]],
			registrationKey: ['', [Validators.required]],
		},
		{ validators: passwordMatchValidator }
	);

	isLoading = false;
	hidePassword = true;
	hideConfirmPassword = true;
	activeTab: 'login' | 'register' = 'login';

	constructor() {
		this.matIconRegistry.addSvgIcon(
			'email',
			this.domSanitizer.bypassSecurityTrustResourceUrl(
				'assets/icons/email.svg'
			)
		);
		this.matIconRegistry.addSvgIcon(
			'lock',
			this.domSanitizer.bypassSecurityTrustResourceUrl('assets/icons/lock.svg')
		);
		this.matIconRegistry.addSvgIcon(
			'eye',
			this.domSanitizer.bypassSecurityTrustResourceUrl('assets/icons/eye.svg')
		);
		this.matIconRegistry.addSvgIcon(
			'arrow-down',
			this.domSanitizer.bypassSecurityTrustResourceUrl(
				'assets/icons/arrow-down.svg'
			)
		);
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
			'key',
			this.domSanitizer.bypassSecurityTrustResourceUrl('assets/icons/key.svg')
		);
	}

	ngOnInit(): void {
		this.handleLoginAction();
		this.handleRegisterAction();
	}

	login(): void {
		if (this.loginForm.invalid) {
			return;
		}
		this.loginAction$.next();
	}

	register(): void {
		if (this.registerForm.invalid) {
			return;
		}
		this.registerAction$.next();
	}

	private handleLoginAction(): void {
		this.loginAction$
			.pipe(
				exhaustMap(() => {
					this.isLoading = true;
					const rawCreds = this.loginForm.getRawValue();
					const credentials = {
						email: rawCreds.email ?? '',
						password: rawCreds.password ?? ''
					};
					return this.authService.login(credentials).pipe(
						finalize(() => (this.isLoading = false)),
						catchError((err) => {
							this.handleAuthError(err, 'login');
							return of(null);
						})
					);
				}),
				takeUntilDestroyed(this.destroyRef)
			)
			.subscribe((response) => {
				if (response) {
					this.handleAuthSuccess();
				}
			});
	}

	private handleRegisterAction(): void {
		this.registerAction$
			.pipe(
				exhaustMap(() => {
					this.isLoading = true;
					const rawData = this.registerForm.getRawValue();
					const nameParts = (rawData.fullName ?? '').split(' ');
					const firstName = nameParts.shift() || '';
					const lastName = nameParts.join(' ');

					const userData = {
						firstName: firstName,
						lastName: lastName,
						email: rawData.email ?? '',
						password: rawData.password ?? '',
						registrationKey: rawData.registrationKey ?? '',
					};
					return this.authService.register(userData).pipe(
						finalize(() => (this.isLoading = false)),
						catchError((err) => {
							this.handleAuthError(err, 'register');
							return of(null);
						})
					);
				}),
				takeUntilDestroyed(this.destroyRef)
			)
			.subscribe((response) => {
				if (response) {
					this.handleAuthSuccess();
				}
			});
	}

	private handleAuthSuccess(): void {
		const message = this.translate.instant('AUTH.LOGIN_SUCCESS');
		this.notificationService.showSuccess(message);
		this.router.navigate(['/chat']);
	}

	private handleAuthError(err: any, type: 'login' | 'register'): void {
		const messageKey =
			type === 'login' ? 'AUTH.LOGIN_ERROR' : 'AUTH.REGISTER_ERROR';
		const message = this.translate.instant(messageKey);
		this.notificationService.showError(message);
		console.error(`${type} error:`, err);
	}
}
