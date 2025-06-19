import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AgentService, Agent } from '../../../core/services/agent.service';
import { BehaviorSubject, Subject, EMPTY, merge } from 'rxjs';
import { switchMap, tap, catchError, exhaustMap } from 'rxjs/operators';

interface AgentListAction {
	type: 'LOAD_AGENTS' | 'REFRESH_AGENTS' | 'DELETE_AGENT';
	payload?: any;
}

@Component({
	selector: 'app-agent-list',
	standalone: true,
	imports: [CommonModule, RouterModule],
	templateUrl: './agent-list.component.html',
	styleUrls: ['./agent-list.component.scss'],
})
export class AgentListComponent implements OnInit {
	private agentService = inject(AgentService);
	private destroyRef = inject(DestroyRef);

	// Action subjects
	private loadAgentsAction$ = new Subject<void>();
	private refreshAgentsAction$ = new Subject<void>();
	private deleteAgentAction$ = new Subject<number>();

	// State subjects
	agents$ = new BehaviorSubject<Agent[]>([]);
	loading$ = new BehaviorSubject<boolean>(false);

	ngOnInit(): void {
		this.setupActionHandlers();
		this.dispatch({ type: 'LOAD_AGENTS' });
	}

	/**
	 * Setup action handlers for all component actions
	 */
	private setupActionHandlers(): void {
		// Load/Refresh agents handler
		merge(this.loadAgentsAction$, this.refreshAgentsAction$)
			.pipe(
				tap(() => this.loading$.next(true)),
				switchMap(() =>
					this.agentService.getAgents().pipe(
						tap((agents) => {
							this.agents$.next(agents);
							this.loading$.next(false);
						}),
						catchError((error) => {
							console.error('Error loading agents:', error);
							this.loading$.next(false);
							return EMPTY;
						})
					)
				),
				takeUntilDestroyed(this.destroyRef)
			)
			.subscribe();

		// Delete agent handler
		this.deleteAgentAction$
			.pipe(
				exhaustMap((agentId) =>
					this.agentService.deleteAgent(agentId).pipe(
						tap(() => {
							// Optimistically remove agent from local state
							const currentAgents = this.agents$.value;
							const updatedAgents = currentAgents.filter(agent => agent.id !== agentId);
							this.agents$.next(updatedAgents);
							console.log('Agent deleted successfully');
						}),
						catchError((error) => {
							console.error('Error deleting agent:', error);
							alert('Failed to delete agent. Please try again.');
							return EMPTY;
						})
					)
				),
				takeUntilDestroyed(this.destroyRef)
			)
			.subscribe();
	}

	/**
	 * Dispatch an action
	 */
	private dispatch(action: AgentListAction): void {
		switch (action.type) {
			case 'LOAD_AGENTS':
				this.loadAgentsAction$.next();
				break;
			case 'REFRESH_AGENTS':
				this.refreshAgentsAction$.next();
				break;
			case 'DELETE_AGENT':
				this.deleteAgentAction$.next(action.payload);
				break;
		}
	}

	/**
	 * Load agents from the API
	 */
	loadAgents(): void {
		this.dispatch({ type: 'LOAD_AGENTS' });
	}

	/**
	 * Force refresh agents
	 */
	refreshAgents(): void {
		this.dispatch({ type: 'REFRESH_AGENTS' });
	}

	/**
	 * Delete an agent
	 */
	deleteAgent(id: number, event: Event): void {
		event.stopPropagation();
		
		if (confirm('Are you sure you want to delete this agent?')) {
			this.dispatch({ type: 'DELETE_AGENT', payload: id });
		}
	}
}
