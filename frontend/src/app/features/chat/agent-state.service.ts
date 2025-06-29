import { Injectable, inject, signal, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Agent, AgentService } from '../../core/services/agent.service';
import { Observable, tap, Subject, switchMap, catchError, EMPTY } from 'rxjs';
import { NotificationService } from '../../core/services/notification.service';

@Injectable({
	providedIn: 'root',
})
export class AgentStateService {
	private agentService = inject(AgentService);
	private notificationService = inject(NotificationService);
	private destroyRef = inject(DestroyRef);
	private readonly agentsState = signal<Agent[]>([]);

	private refreshTrigger$ = new Subject<void>();

	readonly agents = this.agentsState.asReadonly();

	constructor() {
		this.refreshTrigger$
			.pipe(
				switchMap(() =>
					this.agentService.getAgents().pipe(
						catchError(err => {
							console.error('Failed to refresh agents', err);
							this.notificationService.showError('Could not refresh agent list.');
							return EMPTY;
						}),
					),
				),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe(agents => {
				this.agentsState.set(agents);
			});
	}

	initialize(): void {
		this.refreshTrigger$.next();
	}

	destroy(): void {
		this.agentsState.set([]);
	}

	refreshAgents(): void {
		this.refreshTrigger$.next();
	}

	getAgentByName(name: string): Agent | undefined {
		return this.agentsState().find(agent => agent.name === name);
	}
} 