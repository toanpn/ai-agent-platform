import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgentForm } from './agent-form';

describe('AgentForm', () => {
  let component: AgentForm;
  let fixture: ComponentFixture<AgentForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AgentForm);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
