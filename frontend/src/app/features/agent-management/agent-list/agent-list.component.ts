import {
	CommonModule,
	NgClass,
} from '@angular/common';
import {
	AfterViewInit,
	Component,
	DestroyRef,
	inject,
	OnInit,
	ViewChild,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
	FormControl,
	ReactiveFormsModule,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatMenuModule } from '@angular/material/menu';
import {
	MatPaginator,
	MatPaginatorModule,
} from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
	Router,
	RouterModule,
} from '@angular/router';

import {
	BehaviorSubject,
	combineLatest,
	EMPTY,
	merge,
	Observable,
	Subject,
} from 'rxjs';
import {
	catchError,
	debounceTime,
	distinctUntilChanged,
	exhaustMap,
	map,
	startWith,
	switchMap,
	tap,
} from 'rxjs/operators';

import { TranslateModule } from '@ngx-translate/core';

import { AgentTypeService } from '../../../core/services/agent-type.service';
import {
	Agent,
	AgentService,
} from '../../../core/services/agent.service';
import {
	AuthService,
	User,
} from '../../../core/services/auth.service';
import {
	ConfirmationDialogComponent,
	ConfirmationDialogData,
} from '../../../shared/components/confirmation-dialog/confirmation-dialog.component';

interface AgentListAction {
	type: 'LOAD_AGENTS' | 'REFRESH_AGENTS' | 'DELETE_AGENT';
	payload?: any;
}

@Component({
	selector: 'app-agent-list',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		TranslateModule,
		NgClass,
		ReactiveFormsModule,
		// Angular Material Modules
		MatButtonModule,
		MatCardModule,
		MatIconModule,
		MatTooltipModule,
		MatFormFieldModule,
		MatInputModule,
		MatSelectModule,
		MatProgressSpinnerModule,
		MatPaginatorModule,
		MatButtonToggleModule,
		MatMenuModule,
	],
	templateUrl: './agent-list.component.html',
	styleUrls: ['./agent-list.component.scss'],
})
export class AgentListComponent implements OnInit, AfterViewInit {
	private agentService = inject(AgentService);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);
	private dialog = inject(MatDialog);
	private agentTypeService = inject(AgentTypeService);
	private authService = inject(AuthService);

	// Action subjects
	private loadAgentsAction$ = new Subject<void>();
	private refreshAgentsAction$ = new Subject<void>();
	private deleteAgentAction$ = new Subject<number>();

	// State subjects
	private masterAgents$ = new BehaviorSubject<Agent[]>([]);
	filteredAgents$!: Observable<Agent[]>;
	paginatedAgents$!: Observable<Agent[]>;
	loading$ = new BehaviorSubject<boolean>(false);
	viewMode$ = new BehaviorSubject<'grid' | 'list'>('grid');
	
	private currentUser: User | null = null;

	// Filter controls
	departmentFilterControl = new FormControl('all');
	searchControl = new FormControl('');
	
	// Data for filters
	departments = ["IT", "HR", "General", "AI Research", "OM", "CnB", "L&D", "IC", "FnB", "Retail", "Employee", "Booking", "KMS"];
	statuses = ['Public', 'Private'];

	@ViewChild(MatPaginator) paginator!: MatPaginator;

	ngOnInit(): void {
		this.currentUser = this.authService.currentUser();
		this.loadViewMode();
		this.setupActionHandlers();
		this.setupFiltering();
		this.paginatedAgents$ = this.filteredAgents$.pipe(map(agents => agents.slice(0, 6)));
		this.dispatch({ type: 'LOAD_AGENTS' });
	}

	ngAfterViewInit(): void {
		this.paginatedAgents$ = combineLatest([
			this.filteredAgents$,
			this.paginator.page.pipe(startWith({ pageIndex: 0, pageSize: 6, length: 0 })),
		]).pipe(
			map(([agents]) => {
				// Since this runs in AfterViewInit, paginator is available
				const startIndex = this.paginator.pageIndex * this.paginator.pageSize;
				const endIndex = startIndex + this.paginator.pageSize;
				return agents.slice(startIndex, endIndex);
			}),
			takeUntilDestroyed(this.destroyRef)
		);
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
							this.masterAgents$.next(agents);
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
							const currentAgents = this.masterAgents$.value;
							const updatedAgents = currentAgents.filter(agent => agent.id !== agentId);
							this.masterAgents$.next(updatedAgents);
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

	private loadViewMode(): void {
		const savedViewMode = localStorage.getItem('agent_view_mode') as 'grid' | 'list';
		if (savedViewMode) {
			this.viewMode$.next(savedViewMode);
		}
	}

	setViewMode(mode: 'grid' | 'list'): void {
		this.viewMode$.next(mode);
		localStorage.setItem('agent_view_mode', mode);
	}

	private setupFiltering(): void {
		this.filteredAgents$ = combineLatest([
			this.masterAgents$,
			this.departmentFilterControl.valueChanges.pipe(startWith('all')),
			this.searchControl.valueChanges.pipe(startWith(''), debounceTime(300), distinctUntilChanged()),
		]).pipe(
			map(([agents, department, searchTerm]) => {
				let filteredAgents = agents;
				const lowerCaseSearchTerm = searchTerm?.toLowerCase() ?? '';

				// Filter by department
				if (department && department !== 'all') {
					filteredAgents = filteredAgents.filter(agent => agent.department === department);
				}

				// Filter by search term
				if (lowerCaseSearchTerm) {
					filteredAgents = filteredAgents.filter(agent =>
						agent.name.toLowerCase().includes(lowerCaseSearchTerm) ||
						(agent.description && agent.description.toLowerCase().includes(lowerCaseSearchTerm))
					);
				}

				return filteredAgents;
			}),
			takeUntilDestroyed(this.destroyRef)
		);
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
	 * Navigate back to the chat page
	 */
	goBackToChat(): void {
		this.router.navigate(['/chat']);
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

	editAgent(id: number): void {
		this.router.navigate(['/agents', 'edit', id]);
	}

	deleteAgent(id: number): void {
		const dialogData: ConfirmationDialogData = {
			title: 'AGENTS.CONFIRM_DELETE_AGENT',
			message: 'AGENTS.CONFIRM_DELETE_AGENT_MESSAGE',
			confirmButtonText: 'COMMON.DELETE',
			cancelButtonText: 'COMMON.CANCEL',
		};

		const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
			data: dialogData,
			width: '400px',
		});

		dialogRef.afterClosed().subscribe(result => {
			if (result) {
				this.dispatch({ type: 'DELETE_AGENT', payload: id });
			}
		});
	}

	/**
	 * Returns a CSS class based on the department name for styling the avatar.
	 */
	getDepartmentClass(department: string): string {
		if (!department) return '';
		return `department-${department.toLowerCase()}`;
	}

	getAgentType(agent?: Agent): string {
		return this.agentTypeService.getAgentType(agent);
	}

	getAgentAvatar(agent?: Agent): string {
		return this.agentTypeService.getAgentAvatar(agent);
	}

	canModifyAgent(agent: Agent): boolean {
		return this.currentUser?.id === agent.createdBy?.id;
	}
}
