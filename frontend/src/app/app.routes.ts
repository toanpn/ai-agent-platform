import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
	{
		path: '',
		redirectTo: 'chat',
		pathMatch: 'full',
	},
	{
		path: 'auth',
		children: [
			{
				path: 'login',
				loadComponent: () =>
					import('./features/auth/login/login.component').then((c) => c.LoginComponent),
			},
		],
	},
	{
		path: 'chat',
		canActivate: [authGuard],
		loadComponent: () =>
			import('./features/chat/chat-view/chat-view.component').then(
				(c) => c.ChatViewComponent,
			),
	},
	{
		path: 'agents',
		canActivate: [authGuard],
		children: [
			{
				path: '',
				loadComponent: () =>
					import('./features/agent-management/agent-list/agent-list.component').then(
						(c) => c.AgentListComponent,
					),
			},
			{
				path: 'new',
				loadComponent: () =>
					import('./features/agent-management/agent-form/agent-form.component').then(
						(c) => c.AgentFormComponent,
					),
			},
			{
				path: 'edit/:id',
				loadComponent: () =>
					import('./features/agent-management/agent-form/agent-form.component').then(
						(c) => c.AgentFormComponent,
					),
			},
			{
				path: ':id',
				loadComponent: () =>
					import('./features/agent-management/agent-detail/agent-detail.component').then(
						(c) => c.AgentDetailComponent,
					),
			},
		],
	},
	{
		path: '**',
		redirectTo: 'chat',
	},
];
