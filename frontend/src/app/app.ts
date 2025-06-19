import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';

/**
 * AppComponent is the root component of the chatbot application.
 * It handles the main application layout, authentication state,
 * and navigation between different parts of the application.
 */
@Component({
	selector: 'app-root',
	standalone: true,
	imports: [RouterOutlet, MatToolbarModule],
	templateUrl: './app.html',
	styleUrl: './app.scss',
})
export class AppComponent {
	title = 'AI Agent Platform';
}
