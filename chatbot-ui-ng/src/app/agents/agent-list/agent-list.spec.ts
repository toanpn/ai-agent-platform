import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgentList } from './agent-list';

describe('AgentList', () => {
	let component: AgentList;
	let fixture: ComponentFixture<AgentList>;

	beforeEach(async () => {
		await TestBed.configureTestingModule({
			imports: [AgentList],
		}).compileComponents();

		fixture = TestBed.createComponent(AgentList);
		component = fixture.componentInstance;
		fixture.detectChanges();
	});

	it('should create', () => {
		expect(component).toBeTruthy();
	});
});
