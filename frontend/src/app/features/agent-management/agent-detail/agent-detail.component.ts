import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule, ParamMap } from '@angular/router';
import { toSignal, takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { TranslateModule } from '@ngx-translate/core';
import { AgentService, Agent } from '../../../core/services/agent.service';
import { ChatStateService } from '../../chat/chat-state.service';
import { of, switchMap, Observable, Subject, exhaustMap, tap, catchError } from 'rxjs';

@Component({
	selector: 'app-agent-detail',
	standalone: true,
	imports: [CommonModule, RouterModule, TranslateModule],
	templateUrl: './agent-detail.component.html',
	styleUrls: ['./agent-detail.component.scss'],
})
export class AgentDetailComponent implements OnInit {
	private agentService = inject(AgentService);
	private chatStateService = inject(ChatStateService);
	private route = inject(ActivatedRoute);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);

	private deleteTrigger$ = new Subject<number>();

	private agent$: Observable<Agent | undefined> = this.route.paramMap.pipe(
		switchMap((params: ParamMap) => {
			const id = params.get('id');
			if (id) {
				return this.agentService.getAgent(+id);
			}
			return of(undefined);
		}),
	);
	
	agent = toSignal(this.agent$);

	ngOnInit(): void {
		this.handleAgentDeletion();
	}

	startChat(): void {
		const currentAgent = this.agent();
		if (currentAgent) {
			this.chatStateService.selectAgent(currentAgent);
			this.router.navigate(['/chat']);
		}
	}

	editAgent(): void {
		const currentAgent = this.agent();
		if (currentAgent) {
			this.router.navigate(['/agents/edit', currentAgent.id]);
		}
	}

	deleteAgent(): void {
		const currentAgent = this.agent();
		if (currentAgent && confirm('AGENTS.CONFIRM_DELETE_AGENT')) {
			this.deleteTrigger$.next(currentAgent.id);
		}
	}

	private handleAgentDeletion(): void {
		this.deleteTrigger$
			.pipe(
				exhaustMap((agentId) =>
					this.agentService.deleteAgent(agentId).pipe(
						catchError((error) => {
							console.error('Error deleting agent:', error);
							alert('AGENTS.FAILED_DELETE_AGENT');
							return of(null); // Keep the stream alive
						}),
					),
				),
				tap((result) => {
					if (result !== null) {
						this.router.navigate(['/agents']);
					}
				}),
				takeUntilDestroyed(this.destroyRef),
			)
			.subscribe();
	}
}
