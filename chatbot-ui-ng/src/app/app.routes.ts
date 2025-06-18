import { Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { ChatView } from './chat/chat-view/chat-view';
import { AgentList } from './agents/agent-list/agent-list';
import { AgentDetail } from './agents/agent-detail/agent-detail';
import { AgentForm } from './agents/agent-form/agent-form';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
	{ path: '', redirectTo: 'chat', pathMatch: 'full' },
	{ path: 'login', component: Login },
	{ path: 'chat', component: ChatView, canActivate: [authGuard] },
	{ path: 'agents', component: AgentList, canActivate: [authGuard] },
	{ path: 'agents/new', component: AgentForm, canActivate: [authGuard] },
	{ path: 'agents/:id', component: AgentDetail, canActivate: [authGuard] },
	{ path: 'agents/:id/edit', component: AgentForm, canActivate: [authGuard] },
];
