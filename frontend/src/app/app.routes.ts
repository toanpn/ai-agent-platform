import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { loginGuard } from './core/guards/login.guard';

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
				canActivate: [loginGuard],
				loadComponent: () =>
					import('./features/auth/login/login.component').then((c) => c.LoginComponent),
			},
		],
	},
	{
		path: 'chat',
		canActivate: [authGuard],
		loadComponent: () =>
			import('./features/chat/chat-page/chat-page.component').then(
				(c) => c.ChatPageComponent,
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
				path: 'result',
				loadComponent: () =>
					import('./features/agent-management/agent-result/agent-result.component').then(
						(m) => m.AgentResultComponent,
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
