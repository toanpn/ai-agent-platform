import { Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { ChatView } from './chat/chat-view/chat-view';

export const routes: Routes = [
    { path: '', redirectTo: 'chat', pathMatch: 'full' },
    { path: 'login', component: Login },
    { path: 'chat', component: ChatView },
];
