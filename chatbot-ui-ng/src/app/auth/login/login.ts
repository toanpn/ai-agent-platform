import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
	selector: 'app-login',
	imports: [FormsModule, ReactiveFormsModule],
	templateUrl: './login.html',
	styleUrl: './login.css',
})
export class Login {
	loginForm: FormGroup;
	authService = inject(AuthService);
	router = inject(Router);

	constructor(private fb: FormBuilder) {
		this.loginForm = this.fb.group({
			email: ['', [Validators.required, Validators.email]],
			password: ['', [Validators.required]],
		});
	}

	onSubmit() {
		if (this.loginForm.valid) {
			this.authService.login(this.loginForm.value).subscribe({
				next: (response) => {
					console.log('Login successful', response);
					localStorage.setItem('authToken', response.token);
					this.router.navigate(['/chat']);
				},
				error: (error) => {
					console.error('Login failed', error);
					// TODO: Show error message to user
				},
			});
		}
	}
}
