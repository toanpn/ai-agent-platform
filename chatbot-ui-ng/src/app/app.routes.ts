import { Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { ChatView } from './chat/chat-view/chat-view';
import { AgentList } from './agents/agent-list/agent-list';
import { AgentDetail } from './agents/agent-detail/agent-detail';
import { AgentForm } from './agents/agent-form/agent-form';

export const routes: Routes = [
    { path: '', redirectTo: 'chat', pathMatch: 'full' },
    { path: 'login', component: Login },
    { path: 'chat', component: ChatView },
    { path: 'agents', component: AgentList },
    { path: 'agents/new', component: AgentForm },
    { path: 'agents/:id', component: AgentDetail },
    { path: 'agents/:id/edit', component: AgentForm },
];
