import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
	selector: 'app-chat-sidebar',
	imports: [RouterLink],
	templateUrl: './chat-sidebar.html',
	styleUrl: './chat-sidebar.css',
})
export class ChatSidebar {
	authService = inject(AuthService);
	router = inject(Router);

	logout() {
		this.authService.logout();
		this.router.navigate(['/login']);
	}
}
